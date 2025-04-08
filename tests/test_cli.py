import subprocess
import importlib.metadata
import pytest
from pathlib import Path
import json


@pytest.fixture
def temp_output_h5ad():
    """Fixture to create a temporary output file."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".h5ad") as temp_file:
        yield temp_file.name
    # Cleanup the file after the test
    Path(temp_file.name).unlink(missing_ok=True)


@pytest.fixture
def temp_output_stats():
    """Fixture to create a temporary output file for stats."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        yield temp_file.name
    # Cleanup the file after the test
    Path(temp_file.name).unlink(missing_ok=True)


def test_cli_version():
    """Test the CLI version command."""
    cmd = ["hugo-unifier", "--version"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    version = importlib.metadata.version("hugo-unifier")
    assert version in result.stdout, f"Expected version {version} not found in output."


def test_cli_help():
    """Test the CLI help command."""
    cmd = ["hugo-unifier", "--help"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    assert "Usage:" in result.stdout, "Expected usage information not found in output."
    assert "--input" in result.stdout, "Expected --input option not found in output."
    assert "--output" in result.stdout, "Expected --output option not found in output."
    assert "--column" in result.stdout, "Expected --column option not found in output."
    assert "--stats" in result.stdout, "Expected --stats option not found in output."
    assert "--version" in result.stdout, (
        "Expected --version option not found in output."
    )
    assert "--help" in result.stdout, "Expected --help option not found in output."
    assert "hugo-unifier" in result.stdout, "Expected 'hugo-unifier' in output."
    assert "h5ad" in result.stdout, "Expected 'h5ad' in output."


def test_cli_valid(test_h5ad_path, temp_output_h5ad, temp_output_stats):
    """Test the CLI with a valid input file."""
    cmd = [
        "hugo-unifier",
        "--input",
        str(test_h5ad_path),
        "--output",
        temp_output_h5ad,
        "--stats",
        temp_output_stats,
        "--column",
        "index",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    assert Path(temp_output_h5ad).exists(), "Output file was not created."
    assert Path(temp_output_stats).exists(), "Stats file was not created."
    with open(temp_output_stats, "r") as f:
        stats = json.load(f)
    assert isinstance(stats, dict), "Stats file is not a valid JSON."
    assert "n_input_genes" in stats, "Total genes not found in stats."
    assert "n_approved_symbol" in stats, "Unified genes not found in stats."
