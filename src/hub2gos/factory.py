"""
Takes an existing UCSC Trackhub track stanza and returns the appropriate Gosling Track or View Spec subclass instance.
"""

import logging

from .components import BamSpec, BigWigSpec, BedSpec, BigInteractSpec, VcfSpec, HiCSpec
from .containers import MultiWigSpec

logger = logging.getLogger(__name__)

TRACK_TYPE_MAP = {
    "bam": BamSpec,
    "bigWig": BigWigSpec,
    "bigBed": BedSpec,
    "bigInteract": BigInteractSpec,
    "vcfTabix": VcfSpec,
    "hic": HiCSpec,
}

VIEW_TYPE_MAP = {
    "multiWig": "MultiWigSpec",
}

class TrackSpecFactory:
    """
    Factory class to create Gosling TrackSpec instances based on UCSC Trackhub track stanzas.
    """

    @staticmethod
    def create_track(stanza: dict) -> getattr:
        """
        Create a Gosling TrackSpec instance based on the provided UCSC Trackhub track stanza.
        """
        track_type = stanza.get("type")
        spec_class = TRACK_TYPE_MAP.get(track_type)

        if not spec_class:
            return None

        logger.info(f"Creating {spec_class.__name__} for track: {stanza.get('track')} with type: {track_type}")
        logger.debug(f"Track stanza: {stanza}")

        # Dynamically unpack properties into your existing TrackSpec constructor
        return spec_class(
            data_url=stanza.get("gos_url") or stanza.get("bigDataUrl"),
            color=stanza.get("color", "orange"),
            title=stanza.get("shortLabel") or stanza.get("longLabel") or "Track",
            ident=stanza.get("track"),
            visibility=stanza.get("visibility", "dense")
        )

class ViewSpecFactory:
    """
    Factory class to create Gosling ViewSpec instances based on UCSC Trackhub view stanzas.
    """

    @staticmethod
    def create_view(stanza: dict) -> getattr:
        """
        Create a Gosling ViewSpec instance based on the provided UCSC Trackhub view stanza.
        """
        view_type = stanza.get("container")
        if view_type == "multiWig":
            return MultiWigSpec(
                title=stanza.get("shortLabel") or stanza.get("longLabel") or "MultiWig View",
                ident=stanza.get("track"),
                visibility=stanza.get("visibility", "dense")
            )
        return None
