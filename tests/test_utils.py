"""Unit tests for hub2gos.utils module."""

import pytest
from hub2gos.utils import resolve_url, normalize_track_type


class TestResolveUrl:
    def test_absolute_url_unchanged(self):
        url = "https://example.com/path/file.bw"
        assert resolve_url(url, base="https://example.com/path/") == url

    def test_relative_url_resolved(self):
        result = resolve_url("file.bw", base="https://example.com/hub/")
        assert result == "https://example.com/hub/file.bw"

    def test_none_base_returns_url_as_is(self):
        url = "https://example.com/file.bw"
        assert resolve_url(url, base=None) == url


class TestNormalizeTrackType:
    @pytest.mark.parametrize("raw,expected", [
        ("bigWig", "bigWig"),
        ("bigwig", "bigWig"),
        ("BIGWIG", "bigWig"),
        ("bigBed", "bigBed"),
        ("vcfTabix", "vcfTabix"),
        ("bigBarChart", "bigBarChart"),
        ("bigInteract", "bigInteract"),
    ])
    def test_normalizes_case(self, raw, expected):
        assert normalize_track_type(raw) == expected