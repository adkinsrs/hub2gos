"""
Handles Gosling Track configurations for different data types (BigWig, BED, BigInteract).
"""

from abc import ABC, abstractmethod
import gosling as gos

# Layout defaults
CONDENSED_WIDTH = 1180
EXPANDED_WIDTH = 590
CONDENSED_HEIGHT = 25
EXPANDED_HEIGHT = 50

class TrackSpec(ABC):
    """
    Abstract base class for Gosling Track specifications. Subclasses should implement the get_encoding method to define how the track is rendered.
    """

    def __init__(self, data_url, color="steelblue", title="", ident="", visibility="full"):
        """
        Initializes a TrackSpec instance.

        Args:
            data_url (str): The URL to the data file (e.g., BigWig, BED, etc.).
            color (str): The color to use for the track. Defaults to "steelblue".
            title (str): The title of the track. Defaults to an empty string.
            ident (str): An identifier for the track. Defaults to the title if not provided.
            visibility (str): The visibility of the track ("full", "dense", "hide").
        """
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
        """
        Abstract method to be implemented by subclasses to return the Gosling encoding for the track.

        Args:
            width (int): The width of the track.
            height (int): The height of the track.
            prefix (str): A prefix to be added to the track ID.
            is_child (bool): Whether the track is a child track in a composite view.

        Returns:
            gos.Track: A Gosling Track object representing the track encoding.
        """
        pass

    def render(self, prefix=""):
        """
        Renders the track encoding if the visibility is not set to "hide".

        Args:
            prefix (str): A prefix to be added to the track ID.

        Returns:
            gos.Track or None: The Gosling Track object if visibility is not "hide", otherwise
        """
        if self.visibility == "hide":
            return None
        return self.get_encoding(self.width, self.height, prefix=prefix, is_child=False)

class BigWigSpec(TrackSpec):
    """
    Represents a Gosling Track specification for BigWig files.
    """

    def get_encoding(self, width, height, prefix="", is_child=False):
        """
        Gets the Gosling encoding for the BigWig track.

        Args:
            width (int): The width of the track.
            height (int): The height of the track.
            prefix (str, optional): A prefix to be added to the track ID. Defaults to "".
            is_child (bool, optional): Whether the track is a child track in a composite view. Defaults to False.

        Returns:
            gos.Track: A Gosling Track object representing the track encoding.
        """
        bigwig_data = gos.BigWigData(type="bigwig", url=self.data_url)
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
    """
    Represents a Gosling Track specification for BED files.
    Since BigBed files are not directly supported in Gosling, this method uses a gzipped BED file for visualization.
    An index file is required for this track type and is assumed to be located at the same URL with a BGZF-formatted .tbi extension.
    """

    def get_encoding(self, width, height, prefix="", is_child=False):
        """
        Gets the Gosling encoding for the BigBed track.

        Args:
            width (int): The width of the track.
            height (int): The height of the track.
            prefix (str, optional): A prefix to be added to the track ID. Defaults to "".
            is_child (bool, optional): Whether the track is a child track in a composite view. Defaults to False.

        Returns:
            gos.Track: A Gosling Track object representing the track encoding.
        """
        bed_data = gos.BedData(type="bed", url=self.data_url, indexUrl=f"{self.data_url}.tbi")
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
    """
    Represents a Gosling Track specification for BigInteract (chromatin interaction) files.
    This class is designed to handle BigInteract data visualization using a BEDDB-formatted file, which is typically stored on a HiGlass server.
    """

    def get_encoding(self, width, height, prefix="", is_child=False):
        """
        Gets the Gosling encoding for the BigInteract track.
        Since BigInteract files are only compatible with UCSC, this method uses a BEDDB-formatted file for visualization.

        Args:
            width (int): The width of the track.
            height (int): The height of the track.
            prefix (str, optional): A prefix to be added to the track ID. Defaults to "".
            is_child (bool, optional): Whether the track is a child track in a composite view. Defaults to False.

        Returns:
            gos.Track: A Gosling Track object representing the track encoding.
        """
        biginteract_data = gos.BeddbData(
            type="beddb",
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
            gos.Track(data=biginteract_data)
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
    """
    Represents a Gosling Track specification for HiC (chromatin interaction) files.
    This class is designed to handle HiC data visualization using a cooler-formatted file, which is typically stored on a HiGlass server.
    """

    def get_encoding(self, width, height, prefix="", is_child=False):
        """
        Gets the Gosling encoding for the HiC track.
        Since HiC files are only compatible with UCSC, this method uses a cooler-formatted file for visualization.

        Args:
            width (int): The width of the track.
            height (int): The height of the track.
            prefix (str, optional): A prefix to be added to the track ID. Defaults to "".
            is_child (bool, optional): Whether the track is a child track in a composite view. Defaults to False.

        Returns:
            gos.Track: A Gosling Track object representing the track encoding.
        """
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

        hic_data = gos.MatrixData(type="matrix", url=url)

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

# Work in Progress
class BamSpec(TrackSpec):
    """
    This class is a work in progress and may not be fully functional.

    Represents a Gosling Track specification for BAM (Binary Alignment/Map) files.
    An index file is required for this track type and is assumed to be located at the same URL with a .bai extension.
    """

    def get_encoding(self, width, height, prefix="", is_child=False):
        """
        Gets the Gosling encoding for the Bam track.

        Args:
            width (int): The width of the track.
            height (int): The height of the track.
            prefix (str, optional): A prefix to be added to the track ID. Defaults to "".
            is_child (bool, optional): Whether the track is a child track in a composite view. Defaults to False.

        Returns:
            gos.Track: A Gosling Track object representing the track encoding.
        """
        bam_data = gos.BamData(type="bam", url=self.data_url, indexUrl=f"{self.data_url}.bai")
        track = (
            gos.Track(data=bam_data)
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

# Work in Progress
class VcfSpec(TrackSpec):
    """
    This class is a work in progress and may not be fully functional.

    Represents a Gosling Track specification for VCF (Variant Call Format) files.  The file must be gzipped
    An index file is required for this track type and is assumed to be located at the same URL with a BGZF-formatted .tbi extension.
    """

    def get_encoding(self, width, height, prefix="", is_child=False):
        """
        Gets the Gosling encoding for the VCF track.

        Args:
            width (int): The width of the track.
            height (int): The height of the track.
            prefix (str, optional): A prefix to be added to the track ID. Defaults to "".
            is_child (bool, optional): Whether the track is a child track in a composite view. Defaults to False.

        Returns:
            gos.Track: A Gosling Track object representing the track encoding.
        """
        vcf_data = gos.VcfData(type="vcf", url=self.data_url, indexUrl=f"{self.data_url}.tbi")
        track = (
            gos.Track(data=vcf_data)
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