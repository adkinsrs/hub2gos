"""
Takes an existing UCSC Trackhub track stanza and returns the appropriate Gosling TrackSpec subclass instance.
"""

from .components import BigWigSpec, BedSpec, BigInteractSpec, VcfSpec, HiCSpec
from .containers import MultiWigSpec, HiCViewSpec

TRACK_TYPE_MAP = {
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
    @staticmethod
    def create_track(stanza: dict) -> getattr:
        track_type = stanza.get("type")
        spec_class = TRACK_TYPE_MAP.get(track_type)

        if not spec_class:
            return None

        # Dynamically unpack properties into your existing TrackSpec constructor
        return spec_class(
            data_url=stanza.get("gos_url") or stanza.get("bigDataUrl"),
            color=stanza.get("color", "orange"),
            title=stanza.get("shortLabel") or stanza.get("longLabel") or "Track",
            ident=stanza.get("track"),
            visibility=stanza.get("visibility", "dense")
        )

class ViewSpecFactory:
    @staticmethod
    def create_view(stanza: dict) -> getattr:
        view_type = stanza.get("container")
        if view_type == "multiWig":
            return MultiWigSpec(
                title=stanza.get("shortLabel") or stanza.get("longLabel") or "MultiWig View",
                ident=stanza.get("track"),
                visibility=stanza.get("visibility", "dense")
            )
        return None
