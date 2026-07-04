"""Unit tests for hub2gos.compiler module."""

import pytest
import gosling as gos
from hub2gos.compiler import compile_track_stanzas, zoom_view_to_domain

@pytest.fixture
def mock_bigwig_stanza():
    return {
        "track": "test_signal",
        "type": "bigWig",
        "bigDataUrl": "https://example.com/test.bigWig",
        "shortLabel": "Test Signal",
        "longLabel": "Test Signal Track",
        "visibility": "dense"
    }

@pytest.fixture
def mock_multiwig_hierarchy():
    return [
        {
            "track": "multiwig_parent",
            "container": "multiWig",
            "shortLabel": "Overlay Group",
            "longLabel": "Overlay Container Group",
            "visibility": "dense"
        },
        {
            "track": "child_track_1",
            "parent": "multiwig_parent",
            "type": "bigWig",
            "bigDataUrl": "https://example.com/child1.bigWig",
            "shortLabel": "Child 1",
            "longLabel": "Child 1 Track",
            "visibility": "dense"
        }
    ]

class TestCompileTrackStanzas:
    def test_compile_empty_list_returns_empty_view(self):
        result = compile_track_stanzas([])
        assert isinstance(result, gos.View)
        assert isinstance(result.to_dict(), dict)

    def test_compile_single_track(self, mock_bigwig_stanza):
        result = compile_track_stanzas([mock_bigwig_stanza])
        assert isinstance(result, gos.View)
        result_dict = result.to_dict()
        assert "tracks" in result_dict or "views" in result_dict

    def test_compile_multiwig_container(self, mock_multiwig_hierarchy):
        result = compile_track_stanzas(mock_multiwig_hierarchy)
        assert isinstance(result, gos.View)
        serialized_str = str(result.to_dict())
        assert "multiwig_parent" in serialized_str

    def test_compile_with_coords_triggers_zoom(self, mock_bigwig_stanza):
        coords_str = "chr2:5000-10000"
        result = compile_track_stanzas([mock_bigwig_stanza], coords=coords_str)
        result_dict = result.to_dict()
        assert "xDomain" in result_dict
        assert result_dict["xDomain"]["chromosome"] == "chr2"

class TestZoomViewToDomain:
    @pytest.fixture
    def empty_base_view(self):
        return gos.vertical()

    def test_returns_view_object(self, empty_base_view):
        result = zoom_view_to_domain(empty_base_view, "chr1:1000-2000")
        assert isinstance(result, gos.View)

    def test_sets_x_domain_with_exact_chromosome(self, empty_base_view):
        result = zoom_view_to_domain(empty_base_view, "chr7:5000-6000")
        result_dict = result.to_dict()
        assert result_dict["xDomain"]["chromosome"] == "chr7"

    def test_x_domain_applies_base_padding(self, empty_base_view):
        BASE_PADDING = 1500
        start, end = 5000, 6000
        result = zoom_view_to_domain(empty_base_view, f"chr14:{start}-{end}")
        result_dict = result.to_dict()
        interval = result_dict["xDomain"]["interval"]
        assert interval[0] == start - BASE_PADDING
        assert interval[1] == end + BASE_PADDING