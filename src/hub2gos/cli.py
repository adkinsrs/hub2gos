"""
Command line interface to convert UCSC TrackHub trackDb files into Gosling JSON specifications.
"""

import argparse
from .parser import parse_tracks_from_trackdb
from .compiler import compile_track_stanzas

def main():
    parser = argparse.ArgumentParser(description="Convert UCSC TrackHub trackDb to a Gosling Spec")
    parser.add_argument("trackdb", help="Path to local trackDb.txt file")
    parser.add_argument("-o", "--output", help="Output JSON file path (prints to stdout if omitted)")
    parser.add_argument("-c", "--coords", help="Optional coordinates to set starting domain of tracks. Must be in the format 'chr:start-end' (e.g., 'chr1:1000000-2000000')", default="NA")

    args = parser.parse_args()

    if args.coords == "NA":
        args.coords = None

    # Run the pipeline
    with open(args.trackdb, "r") as f:
        raw_text = f.read()

    stanzas = parse_tracks_from_trackdb(raw_text, trackdb_url="")
    gos_view = compile_track_stanzas(stanzas, args.coords)
    json_output = gos_view.to_json(indent=2)

    if args.output:
        with open(args.output, "w") as out:
            out.write(json_output)
    else:
        print(json_output)

if __name__ == "__main__":
    main()