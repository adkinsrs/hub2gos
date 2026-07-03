"""
Handles Gosling specialty View configurations (i.e. grouping multiple tracks into a single view).
"""

import gosling as gos
from .components import TrackSpec, CONDENSED_WIDTH, CONDENSED_HEIGHT

class ViewSpec:
    """
    Represents a Gosling View specification that can contain multiple tracks.
    """

    def __init__(self, title="", ident="", visibility="full"):
        """
        Initializes a ViewSpec instance.

        Args:
            title (str): The title of the view.
            ident (str): An identifier for the view. If not provided, defaults to the title.
            visibility (str): The visibility state of the view. Can be "full", "hide", or "condensed".
        """
        self.title = title
        self.ident = ident or title
        self.visibility = visibility
        self.width = CONDENSED_WIDTH
        self.height = CONDENSED_HEIGHT
        self.members = []

    def add_member(self, track: TrackSpec):
        """
        Adds a TrackSpec member to the view.
        """
        self.members.append(track)

class MultiWigSpec(ViewSpec):
    """
    Represents a Gosling View specification that can contain multiple wiggle tracks.
    """

    def render(self, prefix=""):
        """
        Renders the Gosling view specification for the MultiWigSpec.

        Args:
            prefix (str): A prefix to be added to the view's identifier.

        Returns:
            A Gosling overlay object representing the view, or None if the view is hidden.
        """
        if self.visibility == "hide":
            return None

        rendered_members = [
            m.get_encoding(width=self.width, height=self.height, prefix=prefix, is_child=True)
            for m in self.members
        ]

        for i in range(1, len(rendered_members)):
            if rendered_members[i] is not None:
                rendered_members[i] = rendered_members[i].properties(
                    y=gos.Y(field="value", type="quantitative", axis="none", aggregate="count")
                )

        return gos.overlay(*rendered_members).properties(
            title=self.title,
            width=self.width,
            height=self.height,
            opacity=gos.Opacity(value=0.5),
            id=f"{prefix}view-{self.ident}"
        )