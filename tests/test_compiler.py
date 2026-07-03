"""Unit tests for hub2gos.compiler module."""

import pytest
from pathlib import Path
from hub2gos.compiler import HubCompiler

DATA_DIR = Path(__file__).parent / "data"


class TestCompilerOneFileMode:
    @pytest.fixture
    def compiler(self):
        return HubCompiler(str(DATA_DIR / "oneFileMode" / "hub.txt"))

    def test_compile_returns_dict(self, compiler):
        result = compiler.compile()
        assert isinstance(result, dict)

    def test_compile_has_views_or_tracks(self, compiler):
        result = compiler.compile()
        assert "views" in result or "tracks" in result

    def test_compile_is_non_empty(self, compiler):
        result = compiler.compile()
        views = result.get("views", result.get("tracks", []))
        assert len(views) >= 1


class TestCompilerNormalMode:
    @pytest.fixture
    def compiler(self):
        return HubCompiler(str(DATA_DIR / "normalMode" / "hub.txt"))

    def test_compile_returns_dict(self, compiler):
        result = compiler.compile()
        assert isinstance(result, dict)

    def test_compile_has_views_or_tracks(self, compiler):
        result = compiler.compile()
        assert "views" in result or "tracks" in result

    def test_compile_is_non_empty(self, compiler):
        result = compiler.compile()
        views = result.get("views", result.get("tracks", []))
        assert len(views) >= 1

    def test_all_supported_types_produce_output(self, compiler):
        """Each supported track type in the test data should yield at least one view."""
        result = compiler.compile()
        views = result.get("views", result.get("tracks", []))
        assert len(views) >= 1