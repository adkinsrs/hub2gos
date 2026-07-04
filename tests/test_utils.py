"""Unit tests for hub2gos.utils module."""

import pytest  # noqa: F401
from hub2gos.utils import parse_position_str, find_node_by_id, replace_node_by_id

class TestParsePositionStr:
    def test_valid_position_string(self):
        chrom, start, end = parse_position_str("chr1:1000-2000")
        assert chrom == "chr1"
        assert start == 1000
        assert end == 2000

    def test_invalid_format_missing_colon(self):
        chrom, start, end = parse_position_str("chr1-1000-2000")
        assert chrom is None
        assert start is None
        assert end is None

    def test_invalid_format_non_integer(self):
        chrom, start, end = parse_position_str("chr1:1000-end")
        assert chrom is None
        assert start is None
        assert end is None


class TestFindNodeById:
    def test_finds_node_at_root(self):
        spec = {"id": "target", "value": 42}
        result = find_node_by_id(spec, "target")
        assert result == spec

    def test_finds_node_in_nested_dict(self):
        target_node = {"id": "target", "value": 42}
        spec = {"layout": {"view": target_node}}
        result = find_node_by_id(spec, "target")
        assert result == target_node

    def test_finds_node_in_list(self):
        target_node = {"id": "target", "value": 42}
        spec = {"views": [{"id": "other"}, target_node]}
        result = find_node_by_id(spec, "target")
        assert result == target_node

    def test_returns_none_if_not_found(self):
        spec = {"views": [{"id": "other1"}, {"id": "other2"}]}
        result = find_node_by_id(spec, "target")
        assert result is None


class TestReplaceNodeById:
    def test_replaces_node_at_root(self):
        spec = {"id": "target", "value": 42}
        replacement = {"id": "new_target", "value": 100}
        result = replace_node_by_id(spec, "target", replacement)
        assert result == replacement

    def test_replaces_node_in_nested_dict(self):
        spec = {"layout": {"view": {"id": "target", "value": 42}}}
        replacement = {"id": "new", "value": 100}
        result = replace_node_by_id(spec, "target", replacement)
        assert result["layout"]["view"] == replacement

    def test_replaces_node_in_list(self):
        spec = {"views": [{"id": "other"}, {"id": "target"}]}
        replacement = {"id": "new"}
        result = replace_node_by_id(spec, "target", replacement)
        assert result["views"][1] == replacement
        assert result["views"][0] == {"id": "other"}

    def test_leaves_unmatched_nodes_alone(self):
        spec = {"views": [{"id": "other1"}, {"id": "other2"}]}
        replacement = {"id": "new"}
        result = replace_node_by_id(spec, "target", replacement)
        assert result == spec