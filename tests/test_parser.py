"""Unit tests for hub2gos.parser module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from hub2gos.parser import (
    _is_safe_public_http_url,
    _normalize_track_dict,
    _parse_track_stanzas,
    _get_parent,
    _read_contents,
    _join_path,
    parse_hub_from_file,
    parse_tracks_from_trackdb,
    validate_hub_contents,
    validate_track_contents,
    fetch_trackdb_path
)

DATA_DIR = Path(__file__).parent / "data"
DATA_URL = "https://raw.githubusercontent.com/adkinsrs/hub2gos/refs/heads/main/tests/data"  # Not currently used. MagicMock is used instead

class TestParserFunctions:

    def test_parse_hub_from_file(self):
        hub_path = DATA_DIR / "oneFileMode" / "hub.txt"
        if not hub_path.exists():
            pytest.skip("Test data not found")

        hub_txt = hub_path.read_text()
        hub_json, track_stanzas = parse_hub_from_file(hub_txt)

        assert isinstance(hub_json, dict)
        assert "hub" in hub_json
        assert isinstance(track_stanzas, list)
        assert len(track_stanzas) > 0

    def test_parse_tracks_from_trackdb(self):
        trackdb_path = DATA_DIR / "normalMode" / "trackDb.txt"
        if not trackdb_path.exists():
            pytest.skip("Test data not found")

        trackdb_txt = trackdb_path.read_text()
        tracks = parse_tracks_from_trackdb(trackdb_txt, "http://example.com/")

        assert isinstance(tracks, list)
        assert len(tracks) > 0
        assert "track" in tracks[0]

    def test_fetch_trackdb_path(self):
        genomes_txt = "genome mm10\ntrackDb mm10/trackDb.txt\n"
        path = fetch_trackdb_path(genomes_txt, "mm10")
        assert path == "mm10/trackDb.txt"

    def test_fetch_trackdb_path_raises_value_error(self):
        genomes_txt = "genome mm10\ntrackDb mm10/trackDb.txt\n"
        with pytest.raises(ValueError):
            fetch_trackdb_path(genomes_txt, "hg38")

class TestValidateHubContents:

    @pytest.fixture
    def valid_hub_json(self):
        return {
            "hub": "test", "shortLabel": "Test", "longLabel": "Test",
            "email": "a@b.com", "useOneFile": "on", "genome": "mm10"
        }

    def test_valid_contents(self, valid_hub_json):
        assert validate_hub_contents(valid_hub_json) is True

    def test_invalid_missing_hub_field(self):
        hub_json = {"shortLabel": "Test"} # Missing "hub", "genome", etc.
        assert validate_hub_contents(hub_json) is False

class TestValidateTrackContents:

    @pytest.fixture
    def valid_track_stanzas(self):
        return [
            {"track": "t1", "type": "bigWig", "shortLabel": "t1",
             "longLabel": "t1", "visibility": "dense", "bigDataUrl": "url"},
            {"track": "t2", "type": "bigWig", "shortLabel": "t2",
             "longLabel": "t2", "visibility": "dense", "bigDataUrl": "url"}
        ]

    def test_valid_contents(self, valid_track_stanzas):
        assert validate_track_contents(valid_track_stanzas) is True

    def test_invalid_missing_data_url_or_container(self):
        track_stanzas = [{
            "track": "t1", "type": "bigWig", "shortLabel": "t1",
            "longLabel": "t1", "visibility": "dense"
        }]
        assert validate_track_contents(track_stanzas) is False

    def test_invalid_unsupported_track_type(self):
        track_stanzas = [{
            "track": "t1", "type": "unsupportedType", "shortLabel": "t1",
            "longLabel": "t1", "visibility": "dense", "bigDataUrl": "url"
        }]
        assert validate_track_contents(track_stanzas) is False


class TestIsSafePublicHttpUrl:

    def test_valid_public_url_returns_true(self):
        with patch("hub2gos.parser.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("8.8.8.8", None))]
            assert _is_safe_public_http_url("https://example.com/file.bigWig") is True

    def test_private_ip_returns_false(self):
        with patch("hub2gos.parser.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("192.168.1.1", None))]
            assert _is_safe_public_http_url("https://internal.example.com/file.bigWig") is False

    def test_loopback_ip_returns_false(self):
        with patch("hub2gos.parser.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("127.0.0.1", None))]
            assert _is_safe_public_http_url("https://localhost/file.bigWig") is False

    def test_non_http_scheme_returns_false(self):
        assert _is_safe_public_http_url("ftp://example.com/file.bigWig") is False

    def test_empty_string_returns_false(self):
        assert _is_safe_public_http_url("") is False

    def test_dns_exception_returns_false(self):
        with patch("hub2gos.parser.socket.getaddrinfo", side_effect=Exception("DNS failure")):
            assert _is_safe_public_http_url("https://example.com/file.bigWig") is False

    def test_development_env_allows_local(self):
        with patch("hub2gos.parser.os.getenv", return_value="development"):
            with patch("hub2gos.parser.socket.getaddrinfo") as mock_dns:
                mock_dns.return_value = [(None, None, None, None, ("127.0.0.1", None))]
                assert _is_safe_public_http_url("http://localhost/file.bigWig") is True


class TestNormalizeTrackDict:

    @pytest.fixture
    def minimal_track(self):
        return {
            "track": "test_track",
            "type": "bigWig",
            "bigDataUrl": "https://example.com/test.bigWig",
            "shortLabel": "Test",
            "longLabel": "Test Track",
            "visibility": "dense"
        }

    def test_returns_dict(self, minimal_track):
        result = _normalize_track_dict(minimal_track)
        assert isinstance(result, dict)

    def test_preserves_standard_fields(self, minimal_track):
        result = _normalize_track_dict(minimal_track)
        assert result["track"] == "test_track"
        assert result["type"] == "bigWig"
        assert result["bigDataUrl"] == "https://example.com/test.bigWig"

    def test_normalizes_color_to_rgb(self):
        track = {
            "track": "t1", "type": "bigWig", "bigDataUrl": "url",
            "shortLabel": "t1", "longLabel": "t1", "visibility": "dense",
            "color": "31,119,180"
        }
        result = _normalize_track_dict(track)
        assert result["color"] == "rgb(31,119,180)"

    def test_does_not_double_wrap_rgb_color(self):
        track = {
            "track": "t1", "type": "bigWig", "bigDataUrl": "url",
            "shortLabel": "t1", "longLabel": "t1", "visibility": "dense",
            "color": "rgb(31,119,180)"
        }
        result = _normalize_track_dict(track)
        assert result["color"] == "rgb(31,119,180)"

    def test_preserves_gos_fields(self):
        track = {
            "track": "t1", "type": "bigWig", "bigDataUrl": "url",
            "shortLabel": "t1", "longLabel": "t1", "visibility": "dense",
            "gos_height": "100"
        }
        result = _normalize_track_dict(track)
        assert result["gos_height"] == "100"

    def test_missing_track_field_raises_value_error(self):
        track = {"type": "bigWig", "bigDataUrl": "url"}
        with pytest.raises(ValueError):
            _normalize_track_dict(track)

    def test_container_track_returns_early_without_bigdataurl(self):
        track = {
            "track": "container1", "type": "bigWig",
            "shortLabel": "c1", "longLabel": "c1",
            "visibility": "dense", "container": "multiWig"
        }
        result = _normalize_track_dict(track)
        assert "bigDataUrl" not in result
        assert result["container"] == "multiWig"


class TestParseTrackStanzas:

    def test_parses_single_track(self):
        lines = [
            "track test_track",
            "type bigWig",
            "bigDataUrl https://example.com/test.bigWig",
            "shortLabel Test",
            "longLabel Test Track",
            "visibility dense"
        ]
        result = _parse_track_stanzas(lines)
        assert len(result) == 1
        assert result[0]["track"] == "test_track"

    def test_parses_multiple_tracks(self):
        lines = [
            "track track1",
            "type bigWig",
            "bigDataUrl https://example.com/1.bigWig",
            "shortLabel t1",
            "longLabel t1",
            "visibility dense",
            "",
            "track track2",
            "type bigWig",
            "bigDataUrl https://example.com/2.bigWig",
            "shortLabel t2",
            "longLabel t2",
            "visibility dense"
        ]
        result = _parse_track_stanzas(lines)
        assert len(result) == 2
        assert result[1]["track"] == "track2"

    def test_skips_comment_lines(self):
        lines = [
            "# this is a comment",
            "track test_track",
            "type bigWig",
            "bigDataUrl https://example.com/test.bigWig",
            "shortLabel Test",
            "longLabel Test Track",
            "visibility dense"
        ]
        result = _parse_track_stanzas(lines)
        assert len(result) == 1

    def test_skips_blank_lines(self):
        lines = [
            "",
            "track test_track",
            "type bigWig",
            "bigDataUrl https://example.com/test.bigWig",
            "shortLabel Test",
            "longLabel Test Track",
            "visibility dense",
            ""
        ]
        result = _parse_track_stanzas(lines)
        assert len(result) == 1

    def test_parses_gos_fields(self):
        lines = [
            "track test_track",
            "type bigWig",
            "bigDataUrl https://example.com/test.bigWig",
            "shortLabel Test",
            "longLabel Test Track",
            "visibility dense",
            "gos_height 100"
        ]
        result = _parse_track_stanzas(lines)
        assert result[0]["gos_height"] == "100"

    def test_empty_input_returns_empty_list(self):
        result = _parse_track_stanzas([])
        assert result == []


class TestGetParent:

    def test_local_path_returns_parent_dir(self):
        result = _get_parent("/some/path/to/hub.txt")
        assert result == "/some/path/to"

    def test_url_returns_parent_url(self):
        result = _get_parent("https://example.com/hubs/hub.txt", is_url=True)
        assert result == "https://example.com/hubs/"

    def test_local_nested_path(self):
        result = _get_parent("/a/b/c/d/hub.txt")
        assert result == "/a/b/c/d"


class TestReadContents:

    def test_reads_local_file(self, tmp_path):
        test_file = tmp_path / "hub.txt"
        test_file.write_text("hub test\n")
        result = _read_contents(str(test_file))
        assert result == "hub test\n"

    def test_raises_file_not_found_for_missing_local_file(self):
        with pytest.raises(FileNotFoundError):
            _read_contents("/nonexistent/path/hub.txt")

    def test_reads_url(self):
        mock_response = MagicMock()
        mock_response.text = "hub test\n"
        with patch("hub2gos.parser.requests.get", return_value=mock_response):
            result = _read_contents("https://example.com/hub.txt", is_url=True)
        assert result == "hub test\n"

    def test_url_raises_on_bad_status(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404")
        with patch("hub2gos.parser.requests.get", return_value=mock_response):
            with pytest.raises(Exception):
                _read_contents("https://example.com/hub.txt", is_url=True)


class TestJoinPath:

    def test_joins_local_paths(self):
        result = _join_path("/some/dir", "genomes.txt", is_url=False)
        assert result == "/some/dir/genomes.txt"

    def test_joins_url_paths(self):
        result = _join_path("https://example.com/hubs/", "genomes.txt", is_url=True)
        assert result == "https://example.com/hubs/genomes.txt"

    def test_joins_nested_local_path(self):
        result = _join_path("/some/dir", "mm10/trackDb.txt", is_url=False)
        assert result == "/some/dir/mm10/trackDb.txt"

    def test_joins_nested_url_path(self):
        result = _join_path("https://example.com/hubs/", "mm10/trackDb.txt", is_url=True)
        assert result == "https://example.com/hubs/mm10/trackDb.txt"