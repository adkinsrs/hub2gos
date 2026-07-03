"""Unit tests for hub2gos.parser module."""

import pytest
from pathlib import Path
from hub2gos.parser import HubParser

DATA_DIR = Path(__file__).parent / "data"
ONE_FILE_DIR = DATA_DIR / "oneFileMode"
NORMAL_DIR = DATA_DIR / "normalMode"


class TestHubParserOneFileMode:
    """Tests for parsing a useOneFile-mode hub."""

    @pytest.fixture
    def parser(self):
        return HubParser(str(ONE_FILE_DIR / "hub.txt"))

    def test_is_one_file_mode(self, parser):
        assert parser.is_one_file_mode is True

    def test_hub_short_label(self, parser):
        assert parser.hub.short_label is not None

    def test_hub_long_label(self, parser):
        assert parser.hub.long_label is not None

    def test_genomes_parsed(self, parser):
        assert len(parser.genomes) >= 1

    def test_tracks_parsed(self, parser):
        all_tracks = [t for g in parser.genomes for t in g.tracks]
        assert len(all_tracks) >= 1

    def test_track_types_present(self, parser):
        all_tracks = [t for g in parser.genomes for t in g.tracks]
        track_types = {t.track_type for t in all_tracks}
        # At least one supported type should be present
        supported = {"bigWig", "bigBed", "vcfTabix", "bigBarChart", "bigInteract"}
        assert track_types & supported, f"No supported track types found in {track_types}"


class TestHubParserNormalMode:
    """Tests for parsing a standard (multi-file) hub."""

    @pytest.fixture
    def parser(self):
        return HubParser(str(NORMAL_DIR / "hub.txt"))

    def test_is_not_one_file_mode(self, parser):
        assert parser.is_one_file_mode is False

    def test_hub_short_label(self, parser):
        assert parser.hub.short_label is not None

    def test_genomes_parsed(self, parser):
        assert len(parser.genomes) >= 1

    def test_mm10_genome_present(self, parser):
        genome_names = [g.genome for g in parser.genomes]
        assert "mm10" in genome_names

    def test_tracks_parsed(self, parser):
        all_tracks = [t for g in parser.genomes for t in g.tracks]
        assert len(all_tracks) >= 1

    def test_track_types_present(self, parser):
        all_tracks = [t for g in parser.genomes for t in g.tracks]
        track_types = {t.track_type for t in all_tracks}
        supported = {"bigWig", "bigBed", "vcfTabix", "bigBarChart", "bigInteract"}
        assert track_types & supported, f"No supported track types found in {track_types}"

    def test_trackdb_url_resolved(self, parser):
        """Each genome entry should have its trackDb path resolved."""
        for genome in parser.genomes:
            assert genome.trackdb_path is not None