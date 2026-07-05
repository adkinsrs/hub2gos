"""
Command line interface to convert UCSC TrackHub trackDb files into Gosling JSON specifications.
"""

import logging
import argparse

from pathlib import Path

from .parser import fetch_trackdb_path, parse_hub_from_file, parse_tracks_from_trackdb
from .compiler import compile_track_stanzas

logger = logging.getLogger(__name__)

def main():

    parser = argparse.ArgumentParser(description="Convert UCSC TrackHub trackDb to a Gosling Spec")
    parser.add_argument("hub_file", help="Path to local hub.txt file. Supports both standard and useOneFile modes.")
    parser.add_argument("-o", "--output", help="Output JSON file path (prints to stdout if omitted)")
    parser.add_argument("-c", "--coords", help="Optional coordinates to set starting domain of tracks. Must be in the format 'chr:start-end' (e.g., 'chr1:1000000-2000000')", default="NA")
    parser.add_argument("-a", "--assembly", help="Optional genome assembly (e.g., 'hg38', 'mm10'). If not provided, will throw an error in standard mode. This value is not used in useOneFile mode.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable detailed logging output")

    args = parser.parse_args()

    # Determine log level based on the command line flag
    log_level = logging.DEBUG if args.verbose else logging.WARNING

    # Configure the logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )

    if args.coords == "NA":
        args.coords = None

    logger.info(f"Running hub2gos with hub_file={args.hub_file}, output={args.output}, coords={args.coords}, assembly={args.assembly}")

    # Run the pipeline

    # TODO: Move all this to the "parser"
    with open(args.hub_file, "r") as f:
        hub_contents = f.read()

    hub_json, stanzas = parse_hub_from_file(hub_contents)

    logger.debug(f"Parsed hub.json: {hub_json}")

    if hub_json.get("useOneFile", "") == "on":
        gos_view = compile_track_stanzas(stanzas, args.coords)
    else:
        # Traditional mode: parse genomes.txt and trackDb.txt
        hub_dir = Path(args.hub_file).parent

        genomes_file_name = hub_json.get("genomesFile", "genomes.txt")

        genomes_file = hub_dir / genomes_file_name

        logger.debug(f"Looking for genomes.txt at {genomes_file}")
        if not genomes_file.is_file():
            raise FileNotFoundError(f"genomes.txt not found at {genomes_file}")

        with open(genomes_file, "r") as f:
            genomes_file_contents = f.read()

            trackdb_path = Path(fetch_trackdb_path(genomes_file_contents, args.assembly))

        trackdb_file = hub_dir / trackdb_path

        logger.debug(f"Looking for trackDb.txt at {trackdb_file}")
        if not trackdb_file.is_file():
            raise FileNotFoundError(f"trackDb.txt not found at {trackdb_file}")
        with open(trackdb_file, "r") as f:
            trackdb_contents = f.read()

        try:
            stanzas =  parse_tracks_from_trackdb(trackdb_contents, trackdb_file)
        except ValueError as e:
            raise ValueError(f"Failed to parse trackDb from {trackdb_file}: {str(e)}") from e
        gos_view = compile_track_stanzas(stanzas, args.coords)

    json_output = gos_view.to_json(indent=2)

    if args.output:
        with open(args.output, "w") as out:
            out.write(json_output)
    else:
        print(json_output)

if __name__ == "__main__":
    main()