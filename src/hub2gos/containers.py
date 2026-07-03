"""
Handles Gosling specialty View configurations (i.e. grouping multiple tracks into a single view).
"""

import gosling as gos
from .components import TrackSpec, CONDENSED_WIDTH, CONDENSED_HEIGHT

class ViewSpec:
    def __init__(self, title="", ident="", visibility="full"):
        self.title = title
        self.ident = ident or title
        self.visibility = visibility
        self.width = CONDENSED_WIDTH
        self.height = CONDENSED_HEIGHT
        self.members = []

    def add_member(self, track: TrackSpec):
        self.members.append(track)

class MultiWigSpec(ViewSpec):
    def render(self, prefix=""):
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