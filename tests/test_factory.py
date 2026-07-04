"""Unit tests for hub2gos.factory module."""

import pytest
from hub2gos.factory import TrackSpecFactory, ViewSpecFactory
from hub2gos.containers import MultiWigSpec
from hub2gos.components import (
    BamSpec,
    BigWigSpec,
    BedSpec,
    BigInteractSpec,
    HiCSpec,
    VcfSpec,
)

@pytest.mark.parametrize("track_type,expected_class", [
    ("bam", BamSpec),
    ("bigWig", BigWigSpec),
    ("bigBed", BedSpec),
    ("bigInteract", BigInteractSpec),
    ("vcfTabix", VcfSpec),
    ("hic", HiCSpec),
])
def test_track_factory_returns_correct_component(track_type, expected_class):
    stanza = {
        "type": track_type,
        "track": "test_track",
        "bigDataUrl": "https://example.com/file",
        "shortLabel": "Label"
    }
    comp = TrackSpecFactory.create_track(stanza)
    assert isinstance(comp, expected_class)

def test_track_factory_returns_none_for_unsupported_type():
    stanza = {
        "type": "unsupportedType",
        "track": "test_track"
    }
    comp = TrackSpecFactory.create_track(stanza)
    assert comp is None

def test_view_factory_returns_multiwig_spec():
    stanza = {
        "container": "multiWig",
        "track": "multiwig_group",
        "shortLabel": "Overlay Group"
    }
    comp = ViewSpecFactory.create_view(stanza)
    assert isinstance(comp, MultiWigSpec)

def test_view_factory_returns_none_for_unsupported_container():
    stanza = {
        "container": "unsupportedContainer",
        "track": "group"
    }
    comp = ViewSpecFactory.create_view(stanza)
    assert comp is None