"""
Takes parsed UCSC Trackhub file track stanzas and returns a vertical Gosling View containing all tracks and containers.
"""

import gosling as gos
from .factory import TrackSpecFactory
from .containers import MultiWigSpec
from .utils import parse_position_str

def compile_track_stanzas(track_descriptors: list, coords: str|None=None) -> gos.View:
    """
    Compiles a list of UCSC Trackhub track stanzas into a vertical Gosling View.

    Args:
        track_descriptors (list): A list of dictionaries, each representing a UCSC Trackhub track stanza.
        coords (str, optional): A string representing the initial genomic coordinates for the view in the format (chromosome, start, end). Defaults to None.

    Returns:
        gos.View: A vertical Gosling View containing all tracks and containers.
    """
    rendered_tracks = []
    multiwig_groups = {}

    # Step 1: Separate MultiWig parents from normal tracks
    for track in track_descriptors:
        if track.get("container") == "multiWig":
            multiwig_groups[track["track"]] = {
                "visibility": track.get("visibility", "dense"),
                "tracks": [],
                "index": len(rendered_tracks)
            }
            rendered_tracks.append(None)
            continue

        parent = track.get("parent")
        if parent and parent in multiwig_groups and track.get("type") == "bigWig":
            multiwig_groups[parent]["tracks"].append(track)
            continue

        # Use the factory to instantiate the class
        spec_instance = TrackSpecFactory.create_track(track)
        if spec_instance:
            rendered_track = spec_instance.render()
            if rendered_track:
                rendered_tracks.append(rendered_track)

    # Step 2: Handle container overlays
    for parent_id, group in multiwig_groups.items():
        if not group["tracks"]:
            continue

        multiwig_view = MultiWigSpec(title=parent_id, ident=parent_id, visibility=group["visibility"])
        for track in group["tracks"]:
            child_instance = TrackSpecFactory.create_track(track)
            if child_instance:
                multiwig_view.add_member(child_instance)

        rendered_tracks[group["index"]] = multiwig_view.render()

    final_tracks = [t for t in rendered_tracks if t is not None]

    final_view = gos.vertical(*final_tracks)

    if coords:
        return zoom_view_to_domain(final_view, coords)
    return final_view

def zoom_view_to_domain(view, position_str):
    """
    Zooms a Gosling view to a specified genomic domain with padding.

    Args:
        view: A Gosling view object to be updated.
        position_str (str): A string representing the genomic position in the format expected by `parse_position_str`.

    Returns:
        The updated Gosling view object with its xDomain set to the specified genomic coordinates plus padding.

    Notes:
        Adds a base padding of 1500 base pairs to both sides of the specified genomic interval.
    """

    BASE_PADDING = 1500  # base padding on each side of gene

    chrom, start, end = parse_position_str(position_str)

    # Set the x domain of the track to the gene coordinates
    view = view.properties(
        xDomain=gos.GenomicDomain(
            chromosome=chrom, interval=[start - BASE_PADDING, end + BASE_PADDING]
        )
    )
    return view