"""
Functions that don't really fit in any other module, but are used in multiple places.
"""

import logging

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

def find_node_by_id(spec: dict | list, id: str) -> dict | None:
    """
    Recursively search a Gosling specification for a specific 'id'.
    Returns the node if found, otherwise returns None.
    """
    if isinstance(spec, dict):
        if spec.get("id") == id:
            return spec
        for key, value in spec.items():
            result = find_node_by_id(value, id)
            if result is not None:
                return result
    elif isinstance(spec, list):
        for item in spec:
            result = find_node_by_id(item, id)
            if result is not None:
                return result
    return None

def replace_node_by_id(node: dict | list, target_id: str, replacement: dict) -> dict | list:
    """
    Recursively search a Gosling specification for a specific 'id' and replace that node.
    """
    if isinstance(node, dict):
        # If this is the node we are looking for, swap it.
        if node.get("id") == target_id:
            return replacement

        # Otherwise, keep digging into the dictionary keys and values.
        return {k: replace_node_by_id(v, target_id, replacement) for k, v in node.items()}

    elif isinstance(node, list):
        # If it's a list (like the "tracks" or "views" array), check every item.
        return [replace_node_by_id(item, target_id, replacement) for item in node]

    else:
        # Base case: primitive types (strings, ints, booleans)
        return node