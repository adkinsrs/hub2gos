"""
Parse a UCSC Trackhub file and return a list of track stanzas as dictionaries.

Can accept UCSC useOneFile mode trackhub files or the more common multi-file trackhub format.
"""

import ipaddress
import logging
import os
import requests
import socket
import sys
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

VALID_TYPES = ["bigWig", "bigBed", "hic", "vcfTabix"]
VALID_CONTAINER_TYPES = ["multiWig"]

# These are the fields that we will use for Gosling, though other fields will be preserved for compatibility with the UCSC Genome Browser.
HUB_FIELDS = ["hub", "shortLabel", "longLabel", "email", "useOneFile", "genome", "genomesFile"]
TRACK_FIELDS = ["track", "name", "type", "bigDataUrl", "shortLabel", "longLabel", "visibility", "color", "autoScale", "container", "parent"]


def fetch_trackdb_path(genomes_txt: str, assembly: str) -> str:
    """
    Extract the trackDb path for a specified genome assembly from UCSC genomes.txt format.

    Args:
        genomes_txt (str): The contents of a UCSC genomes.txt file as a string.
        assembly (str): The genome assembly identifier to search for (e.g., 'hg38', 'mm10').

    Returns:
        str: The trackDb path for the specified assembly.

    Raises:
        ValueError: If the assembly is not found or trackDb entry is missing.

    """
    for line in genomes_txt.splitlines():
        if line.startswith(f"genome {assembly}"):
            lines = genomes_txt.splitlines()
            next_line_index = lines.index(line) + 1
            if next_line_index < len(lines):
                next_line = lines[next_line_index]
                if next_line.startswith("trackDb"):
                    return next_line.split(" ", 1)[1]

    raise ValueError(f"Assembly {assembly} not found in genomes.txt or trackDb entry is missing.")

def _is_safe_public_http_url(url: str) -> bool:
    """Return True if URL is HTTP(S) and resolves only to public IP addresses."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False

        # Allow all URLs in development environment to facilitate testing with local servers.
        if os.getenv("ENVIRONMENT", "production").lower() == "development":
            return True

        host = parsed.hostname
        addrinfo = socket.getaddrinfo(host, None)

        for info in addrinfo:
            ip_str = info[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
            ):
                return False

        return True
    except Exception:
        return False


def _normalize_track_dict(track: dict, resolve_urls: bool = False, trackdb_url: str = "") -> dict:
    """
    Normalize a track dictionary to consistent field names and formats.

    Args:
        track (dict): Raw track dictionary from parsing.
        resolve_urls (bool): Whether to resolve relative URLs (for trackDb parsing).
        trackdb_url (str): Base URL for resolving relative URLs.

    Returns:
        dict: Normalized track dictionary with consistent keys.
    """
    normalized = {}

    # Copy standard fields
    for key in TRACK_FIELDS:
        if key in track:
            normalized[key] = track[key]

    if "track" not in normalized:
        logger.warning(f"Track stanza is missing 'track' field. Skipping track: {track}")
        raise ValueError("Track stanza is missing required 'track' field")

    # Normalize color format to rgb()
    if "color" in normalized and not normalized["color"].startswith("rgb("):
        normalized["color"] = f"rgb({normalized['color']})"

    # Container tracks don't have bigDataUrl, so we can return early
    if "container" in normalized and normalized["container"] in VALID_CONTAINER_TYPES:
        return normalized

    # Handle bigDataUrl with optional URL resolution
    if "bigDataUrl" in track:
        url = track["bigDataUrl"]
        if resolve_urls:
            # Resolve relative URLs
            if not url.startswith("http://") and not url.startswith("https://"):
                url = urljoin(trackdb_url, url)
            # Follow redirects only for safe public HTTP(S) URLs
            try:
                if _is_safe_public_http_url(url):
                    response = requests.head(url, allow_redirects=True, timeout=10)
                    if response.status_code == 200 and _is_safe_public_http_url(response.url):
                        url = response.url
                else:
                    logger.warning(f"Skipping unsafe URL resolution for track '{normalized.get('track')}': {url}")
            except Exception as e:
                logger.warning(f"Could not resolve URL for track '{normalized.get('track')}': {e}")
        normalized["bigDataUrl"] = url

    return normalized

def _parse_track_stanzas(lines, resolve_urls: bool = False, trackdb_url: str = "") -> list:
    """
    Internal helper to parse track stanzas from any line-based format.

    Handles the common pattern of parsing "track" blocks with consistent field extraction.
    Used by both trackDb.txt and hub.txt (useOneFile) parsers.

    Args:
        lines (list): Lines to parse (typically from splitlines()).
        resolve_urls (bool): Whether to resolve relative URLs.
        trackdb_url (str): Base URL for URL resolution.

    Returns:
        list: List of normalized track dictionaries.
    """
    track_list = []
    current_track = {}

    for line in lines:
        line = line.strip()

        # Skip empty lines and finalize current track if present
        if not line:
            if current_track:
                track_list.append(_normalize_track_dict(current_track, resolve_urls, trackdb_url))
                current_track = {}
            continue

        # Start of new track stanza
        if line.startswith("track "):
            if current_track:
                track_list.append(_normalize_track_dict(current_track, resolve_urls, trackdb_url))
            current_track = {"track": line.split(" ", 1)[1]}

        # Parse track fields (only if we're inside a track stanza)
        elif current_track:
            for field in TRACK_FIELDS:
                if line.startswith(f"{field} "):
                    current_track[field] = line.split(" ", 1)[1]
                    break

    # Don't forget the last track
    if current_track:
        track_list.append(_normalize_track_dict(current_track, resolve_urls, trackdb_url))

    return track_list

def parse_tracks_from_trackdb(trackdb_txt: str, trackdb_url: str) -> list[dict]:
    """
    Parse track stanzas from a UCSC trackDb.txt file.

    Args:
        trackdb_txt (str): The contents of a UCSC trackDb.txt file.
        trackdb_url (str): The base URL of the trackDb.txt file (used to resolve relative URLs).

    Returns:
        list: A list of dictionaries, each representing a track with keys like 'track', 'type',
              'bigDataUrl', 'shortLabel', 'longLabel', 'color', 'visibility', etc.

    Example track dict:
        {
            "name": "P1HC_ATAC_1",
            "type": "bigWig",
            "bigDataUrl": "https://example.com/P1HC_ATAC_1.bigwig",
            "shortLabel": "ATAC-seq 1st replicate",
            "longLabel": "ATAC-seq 1st replicate",
            "color": "rgb(31,119,180)",
            "visibility": "dense",
        }
    """
    return _parse_track_stanzas(trackdb_txt.splitlines(), resolve_urls=True, trackdb_url=trackdb_url)

def parse_hub_from_file(hub_txt: str) -> tuple[dict, list[dict]]:
    """
    Parse hub.txt file in useOneFile mode into hub metadata and track stanzas.

    Args:
        hub_txt (str): The contents of a hub.txt file in useOneFile mode.

    Returns:
        tuple: (hub_dict, track_stanzas_list)
            - hub_dict: Dictionary with hub metadata (hub, shortLabel, longLabel, email, useOneFile, genome)
            - track_stanzas_list: List of track dictionaries

    Notes:
        In useOneFile mode, the hub.txt file contains both hub metadata and track definitions.
        Track stanzas begin with 'track <name>' and are separated by blank lines.
    """
    hub_json = {}
    track_list = []
    lines = hub_txt.splitlines()

    # Parse hub metadata and tracks
    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Parse hub metadata
        for field in HUB_FIELDS:
            if line.startswith(f"{field} "):
                hub_json[field] = line.split(" ", 1)[1]
                break

        # If it's a track stanza, stop parsing hub metadata
        if line.startswith("track "):
            break

    # Parse track stanzas (rest of the file after hub metadata)
    track_start_idx = next(
        (i for i, l in enumerate(lines) if l.strip().startswith("track ")),
        len(lines)
    )
    track_list = _parse_track_stanzas(lines[track_start_idx:], resolve_urls=False, trackdb_url="")

    return hub_json, track_list

def validate_hub_contents(hub_json: dict, track_stanzas: list) -> bool:
    """
    Validate the contents of a UCSC Trackhub hub.txt file and its track stanzas.

    Args:
        hub_json (dict): Dictionary containing hub metadata.
        track_stanzas (list): List of dictionaries, each representing a track stanza.

    Returns:
        bool: True if the hub contents are valid, False otherwise.
    """

    required_hub_fields = ["hub", "shortLabel", "longLabel", "email", "useOneFile", "genome"]
    for field in required_hub_fields:
        if field not in hub_json:
            logger.error(f"Missing required field '{field}' in hub.txt content.")
            return False

    for track in track_stanzas:
        required_track_fields = ["track", "type", "shortLabel", "longLabel", "visibility"]
        exclusive_track_fields = ["bigDataUrl", "container"]
        for field in required_track_fields:
            if field not in track:
                logger.error(f"Missing required field '{field}' in track stanza.")
                return False
        # Must have one of the exclusive fields (bigDataUrl for data tracks, container for container tracks)
        if not any(field in track for field in exclusive_track_fields):
            logger.error(f"Track '{track['track']}' must have either 'bigDataUrl' or 'container' field.")
            return False
        if track["type"] not in VALID_TYPES:
            logger.error(f"Invalid track type '{track['type']}'.")
            return False

        # Currently we only support container type "multiwig", which is for grouping bigWig tracks.
        if "container" in track:
            # Remove container if it's null to avoid confusion
            if track["container"] is None:
                track.pop("container")
            else:
                if track["container"] not in VALID_CONTAINER_TYPES:
                    logger.error(f"Invalid container type '{track['container']}' in track '{track['track']}'.")
                    return False

        # If "parent" is in track, ensure the referenced parent track exists and is a container
        if "parent" in track:
            parent_name = track["parent"]
            # If parent is null or empty, treat it as no parent
            if parent_name is None:
                track.pop("parent")
            else:
                parent_track = next((t for t in track_stanzas if t.get("track") == parent_name), None)
                if not parent_track:
                    logger.error(f"Track '{track['track']}' references non-existent parent '{parent_name}'.")
                    return False
                if "container" not in parent_track or parent_track["container"] not in VALID_CONTAINER_TYPES:
                    logger.error(f"Track '{track['track']}' references parent '{parent_name}' which is not a valid container.")
                    return False
    return True
