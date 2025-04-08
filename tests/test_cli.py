import subprocess
import importlib.metadata

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
    assert "--version" in result.stdout, "Expected --version option not found in output."
    assert "--help" in result.stdout, "Expected --help option not found in output."
    assert "hugo-unifier" in result.stdout, "Expected 'hugo-unifier' in output."
    assert "h5ad" in result.stdout, "Expected 'h5ad' in output."

