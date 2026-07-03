"""
Takes parsed UCSC Trackhub file track stanzas and returns a vertical Gosling View containing all tracks and containers.
"""

import gosling as gos
from .factory import TrackSpecFactory
from .containers import MultiWigSpec

def compile_track_stanzas(track_descriptors: list, coords=None) -> gos.View:
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
    return gos.vertical(*final_tracks)