"""
Functions that don't really fit in any other module, but are used in multiple places.
"""

import logging
import sys

logger = logging.getLogger(__name__)

def parse_position_str(position_str: str) -> tuple:
    """
    Parses a position string in the format 'chromosome:start-end' and returns its components.

    Args:
        position_str (str): The position string to parse.

    Returns:
        tuple: A tuple containing (assembly, chromosome, start, end) if parsing is successful,
            otherwise (None, None, None) on failure.
    """
    try:
        chromosome, positions = position_str.split(":")
        start, end = positions.split("-")
        return chromosome, int(start), int(end)
    except Exception as e:
        logger.error(f"Failed to parse position string '{position_str}': {e}")
        return None, None, None