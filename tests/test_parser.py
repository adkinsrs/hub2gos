"""Unit tests for hub2gos.parser module."""

import pytest
from pathlib import Path
from hub2gos.parser import (
    parse_hub_from_file,
    parse_tracks_from_trackdb,
    validate_hub_contents,
    fetch_trackdb_path
)

DATA_DIR = Path(__file__).parent / "data"

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
        track_stanzas = [{
            "track": "t1", "type": "bigWig", "shortLabel": "t1",
            "longLabel": "t1", "visibility": "dense", "bigDataUrl": "url"
        }]
        assert validate_hub_contents(valid_hub_json, track_stanzas) is True

    def test_invalid_missing_hub_field(self):
        hub_json = {"shortLabel": "Test"} # Missing "hub", "genome", etc.
        track_stanzas = [{"track": "t1", "type": "bigWig", "shortLabel": "t1", "longLabel": "t1", "visibility": "dense", "bigDataUrl": "url"}]
        assert validate_hub_contents(hub_json, track_stanzas) is False

    def test_invalid_missing_data_url_or_container(self, valid_hub_json):
        track_stanzas = [{
            "track": "t1", "type": "bigWig", "shortLabel": "t1",
            "longLabel": "t1", "visibility": "dense"
        }]
        assert validate_hub_contents(valid_hub_json, track_stanzas) is False

    def test_invalid_unsupported_track_type(self, valid_hub_json):
        track_stanzas = [{
            "track": "t1", "type": "unsupportedType", "shortLabel": "t1",
            "longLabel": "t1", "visibility": "dense", "bigDataUrl": "url"
        }]
        assert validate_hub_contents(valid_hub_json, track_stanzas) is False