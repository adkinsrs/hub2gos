"""
Command line interface to convert UCSC TrackHub trackDb files into Gosling JSON specifications.
"""

import argparse
import logging
import sys

from .parser import load_hub
from .compiler import compile_track_stanzas

logger = logging.getLogger(__name__)

def main():

    parser = argparse.ArgumentParser(description="Convert UCSC TrackHub track information to a Gosling Spec")
    parser.add_argument("hub_file", help="Path to local hub.txt file. Supports both standard and useOneFile modes.")
    parser.add_argument("-o", "--output", help="Output JSON file path (prints to stdout if omitted)")
    parser.add_argument("-c", "--coords", help="Optional coordinates to set starting domain of tracks. Must be in the format 'chr:start-end' (e.g., 'chr1:1000000-2000000')", default="NA")
    parser.add_argument("-a", "--assembly", help="Optional genome assembly (e.g., 'hg38', 'mm10'). If not provided, will throw an error in standard mode. This value is not used in useOneFile mode.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable detailed logging output")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

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
    stanzas = load_hub(args.hub_file, args.assembly)
    gos_view = compile_track_stanzas(stanzas, args.coords)
    json_output = gos_view.to_json(indent=2)

    if args.output:
        with open(args.output, "w") as out:
            out.write(json_output)
    else:
        print(json_output)

if __name__ == "__main__":
    main()