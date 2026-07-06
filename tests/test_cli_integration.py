"""Integration tests for hub2gos CLI (cli.py)."""

import json
import pytest
import traceback
from pathlib import Path

# Import your CLI's entry point directly
from hub2gos.cli import main

DATA_DIR = Path(__file__).parent / "data"
DATA_URL = "https://raw.githubusercontent.com/adkinsrs/hub2gos/refs/heads/main/tests/data"  # Not currently used.

ONE_FILE_HUB = str(DATA_DIR / "oneFileMode" / "hub.txt")
NORMAL_HUB = str(DATA_DIR / "normalMode" / "hub.txt")


@pytest.fixture
def run_cli(monkeypatch, capsys):
    """
    Fixture that returns a helper function to invoke the CLI in-process.
    This allows pytest-cov to track execution while mimicking the subprocess API.
    """
    def _run_cli(*args):
        # Mock sys.argv as if invoked from the command line
        monkeypatch.setattr("sys.argv", ["hub2gos.cli", *args])

        try:
            # Execute the CLI logic inside the same process
            main()
            captured = capsys.readouterr()
            # Return a mock object mimicking subprocess.CompletedProcess
            return type('MockResult', (), {'returncode': 0, 'stdout': captured.out, 'stderr': captured.err})

        except SystemExit as e:
            # argparse calls sys.exit() on errors and --help. We must catch it
            # so the test runner doesn't crash.
            captured = capsys.readouterr()

            if isinstance(e.code, int):
                code = e.code
            elif e.code is None:
                code = 0
            else:
                code = 1

            return type('MockResult', (), {'returncode': code, 'stdout': captured.out, 'stderr': captured.err})

        except Exception:
            # Catch standard Python runtime errors (FileNotFoundError, ValueError, etc.)
            # Print the traceback so capsys catches it, then simulate a crash exit code.
            traceback.print_exc()
            captured = capsys.readouterr()
            return type('MockResult', (), {'returncode': 1, 'stdout': captured.out, 'stderr': captured.err})
    return _run_cli


# ---------------------------------------------------------------------------
# One-file mode
# ---------------------------------------------------------------------------

class TestCliOneFileMode:
    def test_runs_without_error(self, run_cli):
        result = run_cli(ONE_FILE_HUB)
        assert result.returncode == 0, result.stderr

    def test_outputs_valid_json(self, run_cli):
        result = run_cli(ONE_FILE_HUB)
        assert result.returncode == 0, result.stderr
        spec = json.loads(result.stdout)
        assert isinstance(spec, dict)

    def test_output_has_views_or_tracks(self, run_cli):
        result = run_cli(ONE_FILE_HUB)
        spec = json.loads(result.stdout)
        assert "views" in spec or "tracks" in spec
        if "views" in spec:
            assert len(spec["views"]) > 0
        if "tracks" in spec:
            assert len(spec["tracks"]) > 0

    def test_output_file_flag_short(self, run_cli, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(ONE_FILE_HUB, "-o", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists()
        spec = json.loads(out_file.read_text())
        assert isinstance(spec, dict)

    def test_output_file_flag_long(self, run_cli, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(ONE_FILE_HUB, "--output", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists()


# ---------------------------------------------------------------------------
# Normal mode
# ---------------------------------------------------------------------------

class TestCliNormalMode:
    def test_missing_assembly_failure(self, run_cli):
        result = run_cli(NORMAL_HUB)
        assert result.returncode != 0
        assert "assembly genome must be passed" in result.stderr.lower()

    def test_runs_without_error(self, run_cli):
        result = run_cli(NORMAL_HUB, "-a", "mm10")
        assert result.returncode == 0, result.stderr

    def test_outputs_valid_json(self, run_cli):
        result = run_cli(NORMAL_HUB, "-a", "mm10")
        assert result.returncode == 0, result.stderr
        spec = json.loads(result.stdout)
        assert isinstance(spec, dict)

    def test_output_has_views_or_tracks(self, run_cli):
        result = run_cli(NORMAL_HUB, "-a", "mm10")
        spec = json.loads(result.stdout)
        assert "views" in spec or "tracks" in spec
        if "views" in spec:
            assert len(spec["views"]) > 0
        if "tracks" in spec:
            assert len(spec["tracks"]) > 0

    def test_output_file_flag_short(self, run_cli, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(NORMAL_HUB, "-a", "mm10", "-o", str(out_file))
        assert result.returncode == 0, result.stderr
        assert out_file.exists()
        spec = json.loads(out_file.read_text())
        assert isinstance(spec, dict)

    def test_coords_flag_short(self, run_cli):
        result = run_cli(NORMAL_HUB, "-a", "mm10", "-c", "chr1:1000000-2000000")
        assert result.returncode == 0, result.stderr

    def test_coords_flag_long(self, run_cli):
        result = run_cli(NORMAL_HUB, "-a", "mm10", "--coords", "chr1:1000000-2000000")
        assert result.returncode == 0, result.stderr

    def test_coords_output_is_valid_json(self, run_cli):
        result = run_cli(NORMAL_HUB, "-a", "mm10", "-c", "chr1:1000000-2000000")
        spec = json.loads(result.stdout)
        assert isinstance(spec, dict)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestCliEdgeCases:
    def test_missing_hub_file_exits_nonzero(self, run_cli):
        result = run_cli("/nonexistent/trackDb.txt")
        assert result.returncode != 0

    def test_missing_hub_file_reports_error(self, run_cli):
        result = run_cli("/nonexistent/trackDb.txt")
        assert result.stderr != ""

    def test_help_flag(self, run_cli):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "trackhub" in result.stdout.lower()

    def test_no_args_exits_zero(self, run_cli):
        result = run_cli()
        assert result.returncode == 0

    def test_stdout_is_empty_when_output_file_given(self, run_cli, tmp_path):
        out_file = tmp_path / "out.json"
        result = run_cli(ONE_FILE_HUB, "-o", str(out_file))
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == ""