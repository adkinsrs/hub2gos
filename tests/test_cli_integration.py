"""Integration tests for hub2gos CLI (cli.py)."""

import json
import os
import subprocess
import sys
import pytest  # noqa: F401
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ONE_FILE_HUB = str(DATA_DIR / "oneFileMode" / "hub.txt")
NORMAL_HUB = str(DATA_DIR / "normalMode" / "hub.txt")


def run_cli(*args):
    """Helper to invoke the CLI as a subprocess and return the CompletedProcess."""

    # Find the absolute path to your 'src' directory relative to this test file
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "src"

    # Copy your current system environment variables and inject the PYTHONPATH rule
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_dir)

    return subprocess.run(
        [sys.executable, "-m", "hub2gos.cli", *args],
        capture_output=True,
        text=True,
        env=env
    )


# ---------------------------------------------------------------------------
# One-file mode
# ---------------------------------------------------------------------------

class TestCliOneFileMode:
    def test_runs_without_error(self):
        result = run_cli(ONE_FILE_HUB)
        assert result.returncode == 0, result.stderr

    def test_outputs_valid_json(self):
        result = run_cli(ONE_FILE_HUB)
        assert result.returncode == 0, result.stderr
        spec = json.loads(result.stdout)
        assert isinstance(spec, dict)

    def test_output_has_views_or_tracks(self):
        result = run_cli(ONE_FILE_HUB)
        spec = json.loads(result.stdout)
        assert "views" in spec or "tracks" in spec
        # assert that the "views" or "tracks" have contents
        if "views" in spec:
            assert len(spec["views"]) > 0
        if "tracks" in spec:
            assert len(spec["tracks"]) > 0

    def test_output_file_flag_short(self, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(ONE_FILE_HUB, "-o", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists()
        spec = json.loads(out_file.read_text())
        assert isinstance(spec, dict)

    def test_output_file_flag_long(self, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(ONE_FILE_HUB, "--output", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists()


# ---------------------------------------------------------------------------
# Normal mode
# ---------------------------------------------------------------------------

class TestCliNormalMode:
    def test_missing_assembly_failure(self):
        result = run_cli(NORMAL_HUB)
        assert result.returncode != 0
        assert "assembly must be specified" in result.stderr.lower()

    def test_runs_without_error(self):
        result = run_cli(NORMAL_HUB, "-a", "mm10")
        assert result.returncode == 0, result.stderr

    def test_outputs_valid_json(self):
        result = run_cli(NORMAL_HUB, "-a", "mm10")
        assert result.returncode == 0, result.stderr
        spec = json.loads(result.stdout)
        assert isinstance(spec, dict)

    def test_output_has_views_or_tracks(self):
        result = run_cli(NORMAL_HUB, "-a", "mm10")
        spec = json.loads(result.stdout)
        assert "views" in spec or "tracks" in spec
        # assert that the "views" or "tracks" have contents
        if "views" in spec:
            assert len(spec["views"]) > 0
        if "tracks" in spec:
            assert len(spec["tracks"]) > 0

    def test_output_file_flag_short(self, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(NORMAL_HUB, "-a", "mm10", "-o", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists()
        spec = json.loads(out_file.read_text())
        assert isinstance(spec, dict)

    def test_coords_flag_short(self):
        result = run_cli(NORMAL_HUB, "-a", "mm10", "-c", "chr1:1000000-2000000")
        assert result.returncode == 0, result.stderr

    def test_coords_flag_long(self):
        result = run_cli(NORMAL_HUB, "-a", "mm10", "--coords", "chr1:1000000-2000000")
        assert result.returncode == 0, result.stderr

    def test_coords_output_is_valid_json(self):
        result = run_cli(NORMAL_HUB, "-a", "mm10", "-c", "chr1:1000000-2000000")
        spec = json.loads(result.stdout)
        assert isinstance(spec, dict)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestCliEdgeCases:
    def test_missing_hub_file_exits_nonzero(self):
        result = run_cli("/nonexistent/trackDb.txt")
        assert result.returncode != 0

    def test_missing_hub_file_reports_error(self):
        result = run_cli("/nonexistent/trackDb.txt")
        # argparse / open() will write an error to stderr
        assert result.stderr != ""

    def test_help_flag(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "trackdb" in result.stdout.lower()

    def test_no_args_exits_nonzero(self):
        result = run_cli()
        assert result.returncode != 0

    def test_stdout_is_empty_when_output_file_given(self, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(ONE_FILE_HUB, "-o", str(out_file))
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == ""