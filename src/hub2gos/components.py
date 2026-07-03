"""
Handles Gosling Track configurations for different data types (BigWig, BED, BigInteract).
"""

from abc import ABC, abstractmethod
import sys
import gosling as gos

# Layout defaults
CONDENSED_WIDTH = 1180
EXPANDED_WIDTH = 590
CONDENSED_HEIGHT = 25
EXPANDED_HEIGHT = 50

class TrackSpec(ABC):
    def __init__(self, data_url, color="steelblue", title="", ident="", visibility="full"):
        self.data_url = data_url
        self.color = color
        self.width = EXPANDED_WIDTH
        self.height = EXPANDED_HEIGHT
        self.title = title
        self.ident = ident or title
        self.visibility = visibility

        if self.visibility == "hide":
            self.height = 0
        elif self.visibility == "full":
            self.height *= 1.5

    @abstractmethod
    def get_encoding(self, width, height, prefix="", is_child=False):
        pass

    def render(self, prefix=""):
        if self.visibility == "hide":
            return None
        return self.get_encoding(self.width, self.height, prefix=prefix, is_child=False)

class BigWigSpec(TrackSpec):
    def get_encoding(self, width, height, prefix="", is_child=False):
        # Your existing code, cleanly isolated
        bigwig_data = gos.bigwig(url=self.data_url)
        track = (
            gos.Track(data=bigwig_data)
            .mark_area()
            .encode(
                color=gos.Color(value=self.color),
                tooltip=[
                    gos.Tooltip(field="position", type="genomic", alt="Position"),
                    gos.Tooltip(field="value", type="quantitative", alt="Peak value", format=".2"),
                ],
                x=gos.X(field="start", type="genomic", axis="none"),
                xe=gos.X(field="end", type="genomic"),
                y=gos.Y(field="value", type="quantitative", axis="right", aggregate="count"),
            )
            .properties(
                width=width,
                id=f"{prefix}track-{self.ident}",
            )
        )
        if not is_child:
            track = track.properties(height=height, title=self.title)
        return track

class BedSpec(TrackSpec):
    def get_encoding(self, width, height, prefix="", is_child=False):
        bed_data = gos.bed(url=self.data_url, indexUrl=f"{self.data_url}.tbi")
        track = (
            gos.Track(data=bed_data)
            .mark_rect()
            .encode(
                x=gos.X(field="start", type="genomic", axis="none"),
                xe=gos.X(field="end", type="genomic"),
                size=gos.Size(value=10),
                color=gos.Color(value=self.color),
            ).properties(
                width=width,
                id=f"{prefix}track-{self.ident}",
            )
        )
        if not is_child:
            track = track.properties(height=height, title=self.title)
        return track

class BigInteractSpec(TrackSpec):
    def get_encoding(self, width, height, prefix="", is_child=False):
        sashimi_data = os_data = gos.beddb(
            url=self.data_url,
            genomicFields=[
                {"index": 1, "name": "start"},
                {"index": 2, "name": "end"}
            ],
            valueFields=[
                {"index": 3, "name": "strand", "type": "nominal"},
            ],
        )
        track = (
            gos.Track(data=sashimi_data)
            .mark_withinLink()
            .encode(
                x=gos.X(field="start", type="genomic", axis="none"),
                xe=gos.X(field="end", type="genomic"),
                color=gos.Color(value=self.color),
            ).properties(
                width=width,
                id=f"{prefix}track-{self.ident}",
            )
        )
        if not is_child:
            track = track.properties(height=height, title=self.title)
        return track

class HiCSpec(TrackSpec):
    def get_encoding(self, width, height, prefix="", is_child=False):
        url = self.data_url
        #color = self.color  # colorscale instead of single color

        """Accepted HiGlass color ranges (others will not work)
            viridis: interpolateViridis,
            grey: interpolateGreys,
            warm: interpolateWarm,
            spectral: interpolateSpectral,
            cividis: interpolateCividis,
            bupu: interpolateBuPu,
            rdbu: interpolateRdBu,
            hot: interpolateYlOrBr,
            pink: interpolateRdPu
        """

        hic_data = gos.matrix(url=url)

        hic_track = (
            gos.Track(
                data=hic_data,  # pyright: ignore[reportArgumentType]
            )
            .mark_bar()
            .encode(
                x=gos.X(field="xs", type="genomic", axis="bottom"),  # pyright: ignore[reportArgumentType]
                xe=gos.Xe(field="xe", type="genomic", axis="none"),  # pyright: ignore[reportArgumentType]
                y=gos.Y(field="ys", type="genomic", axis="none"),  # pyright: ignore[reportArgumentType]
                ye=gos.Ye(field="ye", type="genomic", axis="none"),  # pyright: ignore[reportArgumentType]
                color=gos.Color(field="value", type="quantitative", range="bupu", legend=True),  # pyright: ignore[reportArgumentType]
                style=gos.Style(matrixExtent="full"), # pyright: ignore[reportArgumentType]
            ).properties(
                width=width,
                id=f"{prefix}track-{self.ident}",  # Use the file name without extension as the ID
            )
        )

        if not is_child:
            hic_track = hic_track.properties(
                height=height,
                title=self.title
                )

        return hic_track