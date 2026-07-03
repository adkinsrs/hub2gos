"""Unit tests for hub2gos.components module."""

import pytest
import gosling as gos
from hub2gos.components import (
    BamSpec,
    BigWigSpec,
    BedSpec,
    BigInteractSpec,
    HiCSpec,
    VcfSpec,
    CONDENSED_WIDTH,
    EXPANDED_WIDTH,
    CONDENSED_HEIGHT,
    EXPANDED_HEIGHT,
)

TEST_URL = "https://example.com/test_file"


# ---------------------------------------------------------------------------
# Shared constructor / base-class behaviour
# ---------------------------------------------------------------------------

class TestTrackSpecConstructor:
    """Tests for the shared TrackSpec.__init__ logic."""

    def test_default_color_is_steelblue(self):
        spec = BigWigSpec(data_url=TEST_URL)
        assert spec.color == "steelblue"

    def test_custom_color_stored(self):
        spec = BigWigSpec(data_url=TEST_URL, color="red")
        assert spec.color == "red"

    def test_title_defaults_to_empty(self):
        spec = BigWigSpec(data_url=TEST_URL)
        assert spec.title == ""

    def test_ident_falls_back_to_title(self):
        spec = BigWigSpec(data_url=TEST_URL, title="my-track")
        assert spec.ident == "my-track"

    def test_explicit_ident_overrides_title(self):
        spec = BigWigSpec(data_url=TEST_URL, title="my-track", ident="custom-id")
        assert spec.ident == "custom-id"

    def test_visibility_hide_sets_height_zero(self):
        spec = BigWigSpec(data_url=TEST_URL, visibility="hide")
        assert spec.height == 0

    def test_visibility_full_inflates_height(self):
        spec = BigWigSpec(data_url=TEST_URL, visibility="full")
        assert spec.height == EXPANDED_HEIGHT * 1.5

    def test_visibility_dense_keeps_base_height(self):
        spec = BigWigSpec(data_url=TEST_URL, visibility="dense")
        assert spec.height == EXPANDED_HEIGHT

    def test_data_url_stored(self):
        spec = BigWigSpec(data_url=TEST_URL)
        assert spec.data_url == TEST_URL


# ---------------------------------------------------------------------------
# render() behaviour
# ---------------------------------------------------------------------------

class TestTrackSpecRender:
    def test_render_returns_none_when_hidden(self):
        spec = BigWigSpec(data_url=TEST_URL, visibility="hide")
        assert spec.render() is None

    def test_render_returns_track_when_visible(self):
        spec = BigWigSpec(data_url=TEST_URL, visibility="full")
        result = spec.render()
        assert result is not None

    def test_render_with_prefix(self):
        spec = BigWigSpec(data_url=TEST_URL, ident="bw1", visibility="full")
        track = spec.render(prefix="genome-")
        # The gosling Track object should serialise with the prefixed id
        spec_dict = track.to_dict()
        assert spec_dict.get("id") == "genome-track-bw1"


# ---------------------------------------------------------------------------
# BigWigSpec
# ---------------------------------------------------------------------------

class TestBigWigSpec:
    @pytest.fixture
    def spec(self):
        return BigWigSpec(data_url=TEST_URL, title="BigWig Track", ident="bw1")

    def test_get_encoding_returns_gos_track(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert isinstance(track, gos.Track)

    def test_data_type_is_bigwig(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        d = track.to_dict()
        assert d["data"]["type"] == "bigwig"

    def test_data_url_in_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["url"] == TEST_URL

    def test_mark_is_area(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["mark"] == "area"

    def test_title_set_when_not_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=False)
        assert track.to_dict().get("title") == "BigWig Track"

    def test_title_absent_when_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=True)
        assert "title" not in track.to_dict()

    def test_id_uses_prefix_and_ident(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, prefix="pfx-")
        assert track.to_dict()["id"] == "pfx-track-bw1"

    def test_has_x_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert "x" in track.to_dict()

    def test_has_y_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert "y" in track.to_dict()

    def test_has_tooltip(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert "tooltip" in track.to_dict()


# ---------------------------------------------------------------------------
# BedSpec
# ---------------------------------------------------------------------------

class TestBedSpec:
    @pytest.fixture
    def spec(self):
        return BedSpec(data_url=TEST_URL, title="BED Track", ident="bed1")

    def test_get_encoding_returns_gos_track(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert isinstance(track, gos.Track)

    def test_data_type_is_bed(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["type"] == "bed"

    def test_data_url_in_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["url"] == TEST_URL

    def test_index_url_appends_tbi(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["indexUrl"] == f"{TEST_URL}.tbi"

    def test_mark_is_rect(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["mark"] == "rect"

    def test_title_set_when_not_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=False)
        assert track.to_dict().get("title") == "BED Track"

    def test_title_absent_when_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=True)
        assert "title" not in track.to_dict()


# ---------------------------------------------------------------------------
# BigInteractSpec
# ---------------------------------------------------------------------------

class TestBigInteractSpec:
    @pytest.fixture
    def spec(self):
        return BigInteractSpec(data_url=TEST_URL, title="Interact Track", ident="bi1")

    def test_get_encoding_returns_gos_track(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert isinstance(track, gos.Track)

    def test_data_type_is_beddb(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["type"] == "beddb"

    def test_data_url_in_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["url"] == TEST_URL

    def test_mark_is_withinLink(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["mark"] == "withinLink"

    def test_genomic_fields_present(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        genomic_fields = track.to_dict()["data"]["genomicFields"]
        names = [f["name"] for f in genomic_fields]
        assert "start" in names
        assert "end" in names

    def test_title_set_when_not_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=False)
        assert track.to_dict().get("title") == "Interact Track"

    def test_title_absent_when_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=True)
        assert "title" not in track.to_dict()


# ---------------------------------------------------------------------------
# HiCSpec
# ---------------------------------------------------------------------------

class TestHiCSpec:
    @pytest.fixture
    def spec(self):
        return HiCSpec(data_url=TEST_URL, title="HiC Track", ident="hic1")

    def test_get_encoding_returns_gos_track(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert isinstance(track, gos.Track)

    def test_data_type_is_matrix(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["type"] == "matrix"

    def test_data_url_in_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["url"] == TEST_URL

    def test_mark_is_bar(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["mark"] == "bar"

    def test_color_field_is_value(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["color"]["field"] == "value"

    def test_title_set_when_not_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=False)
        assert track.to_dict().get("title") == "HiC Track"

    def test_title_absent_when_child(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT, is_child=True)
        assert "title" not in track.to_dict()


# ---------------------------------------------------------------------------
# BamSpec (WIP — tests document current behaviour without being overly strict)
# ---------------------------------------------------------------------------

class TestBamSpec:
    @pytest.fixture
    def spec(self):
        return BamSpec(data_url=TEST_URL, title="BAM Track", ident="bam1")

    def test_get_encoding_returns_gos_track(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert isinstance(track, gos.Track)

    def test_data_type_is_bam(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["type"] == "bam"

    def test_data_url_in_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["url"] == TEST_URL

    def test_index_url_appends_bai(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["indexUrl"] == f"{TEST_URL}.bai"


# ---------------------------------------------------------------------------
# VcfSpec (WIP — tests document current behaviour without being overly strict)
# ---------------------------------------------------------------------------

class TestVcfSpec:
    @pytest.fixture
    def spec(self):
        return VcfSpec(data_url=TEST_URL, title="VCF Track", ident="vcf1")

    def test_get_encoding_returns_gos_track(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert isinstance(track, gos.Track)

    def test_data_type_is_vcf(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["type"] == "vcf"

    def test_data_url_in_encoding(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["url"] == TEST_URL

    def test_index_url_appends_tbi(self, spec):
        track = spec.get_encoding(EXPANDED_WIDTH, EXPANDED_HEIGHT)
        assert track.to_dict()["data"]["indexUrl"] == f"{TEST_URL}.tbi"