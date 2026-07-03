"""Unit tests for hub2gos.containers module."""

import pytest
import gosling as gos
from hub2gos.containers import ViewSpec, MultiWigSpec
from hub2gos.components import BigWigSpec, CONDENSED_WIDTH, CONDENSED_HEIGHT

TEST_URL = "https://example.com/test_file"


# ---------------------------------------------------------------------------
# ViewSpec
# ---------------------------------------------------------------------------

class TestViewSpec:
    @pytest.fixture
    def view(self):
        return ViewSpec(title="My View", ident="view1")

    def test_title_stored(self, view):
        assert view.title == "My View"

    def test_ident_stored(self, view):
        assert view.ident == "view1"

    def test_ident_falls_back_to_title(self):
        view = ViewSpec(title="fallback")
        assert view.ident == "fallback"

    def test_default_visibility_is_full(self):
        view = ViewSpec()
        assert view.visibility == "full"

    def test_default_width_is_condensed(self):
        view = ViewSpec()
        assert view.width == CONDENSED_WIDTH

    def test_default_height_is_condensed(self):
        view = ViewSpec()
        assert view.height == CONDENSED_HEIGHT

    def test_members_starts_empty(self, view):
        assert view.members == []

    def test_add_member_appends_track(self, view):
        track = BigWigSpec(data_url=TEST_URL, ident="bw1")
        view.add_member(track)
        assert len(view.members) == 1
        assert view.members[0] is track

    def test_add_multiple_members(self, view):
        view.add_member(BigWigSpec(data_url=TEST_URL, ident="bw1"))
        view.add_member(BigWigSpec(data_url=TEST_URL, ident="bw2"))
        assert len(view.members) == 2


# ---------------------------------------------------------------------------
# MultiWigSpec — render()
# ---------------------------------------------------------------------------

class TestMultiWigSpec:
    @pytest.fixture
    def two_track_view(self):
        view = MultiWigSpec(title="Multi View", ident="mv1")
        view.add_member(BigWigSpec(data_url=TEST_URL, ident="bw1", title="Track 1"))
        view.add_member(BigWigSpec(data_url=TEST_URL, ident="bw2", title="Track 2"))
        return view

    @pytest.fixture
    def single_track_view(self):
        view = MultiWigSpec(title="Single View", ident="sv1")
        view.add_member(BigWigSpec(data_url=TEST_URL, ident="bw1", title="Track 1"))
        return view

    def test_render_returns_none_when_hidden(self):
        view = MultiWigSpec(title="Hidden", ident="h1", visibility="hide")
        view.add_member(BigWigSpec(data_url=TEST_URL, ident="bw1"))
        assert view.render() is None

    def test_render_returns_object_when_visible(self, single_track_view):
        result = single_track_view.render()
        assert result is not None

    def test_render_result_is_gos_object(self, two_track_view):
        result = two_track_view.render()
        # gosling-python overlay produces a View-like object with to_dict()
        assert hasattr(result, "to_dict")

    def test_render_title_in_dict(self, two_track_view):
        result = two_track_view.render()
        d = result.to_dict()
        assert d.get("title") == "Multi View"

    def test_render_id_uses_ident(self, two_track_view):
        result = two_track_view.render()
        d = result.to_dict()
        assert d.get("id") == "view-mv1"

    def test_render_id_uses_prefix(self, two_track_view):
        result = two_track_view.render(prefix="mm10-")
        d = result.to_dict()
        assert d.get("id") == "mm10-view-mv1"

    def test_render_width_in_dict(self, two_track_view):
        result = two_track_view.render()
        d = result.to_dict()
        assert d.get("width") == CONDENSED_WIDTH

    def test_render_height_in_dict(self, two_track_view):
        result = two_track_view.render()
        d = result.to_dict()
        assert d.get("height") == CONDENSED_HEIGHT

    def test_render_has_opacity(self, two_track_view):
        result = two_track_view.render()
        d = result.to_dict()
        assert d.get("opacity", {}).get("value") == 0.5

    def test_render_tracks_count_matches_members(self, two_track_view):
        result = two_track_view.render()
        d = result.to_dict()
        # gosling overlay serialises children under "tracks"
        tracks = d.get("tracks", [])
        assert len(tracks) == 2

    def test_first_member_retains_y_axis(self, two_track_view):
        """Only subsequent members should have their y-axis suppressed."""
        result = two_track_view.render()
        d = result.to_dict()
        first_track = d["tracks"][0]
        assert first_track.get("y", {}).get("axis") != "none"

    def test_subsequent_members_have_y_axis_none(self, two_track_view):
        """Members after the first should have y axis set to 'none'."""
        result = two_track_view.render()
        d = result.to_dict()
        second_track = d["tracks"][1]
        assert second_track.get("y", {}).get("axis") == "none"