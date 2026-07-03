"""Unit tests for hub2gos.factory module."""

import pytest
from hub2gos.factory import ComponentFactory
from hub2gos.components import (
    BamSpec,
    BigWigSpec,
    BedSpec,
    BigInteractSpec,
    HiCSpec,
    VcfSpec,
)


@pytest.fixture
def factory():
    return ComponentFactory()


@pytest.mark.parametrize("track_type,expected_class", [
    ("bam", BamSpec),
    ("bigWig", BigWigSpec),
    ("bigBed", BedSpec),
    ("bigInteract", BigInteractSpec),
    ("vcfTabix", VcfSpec),
    ("hic", HiCSpec),
])

def test_factory_returns_correct_component(factory, track_type, expected_class):
    comp = factory.create(
        track_type=track_type,
        track_name="test_track",
        url="https://example.com/file",
        short_label="Label",
        genome="mm39",
    )
    assert isinstance(comp, expected_class)


def test_factory_raises_for_unsupported_type(factory):
    with pytest.raises((KeyError, ValueError, NotImplementedError)):
        factory.create(
            track_type="unsupportedType",
            track_name="test",
            url="https://example.com/file",
            short_label="Label",
            genome="mm39",
        )