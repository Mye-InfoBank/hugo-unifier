import subprocess
import importlib.metadata


def test_cli_version():
    """Test the CLI version command."""
    cmd = ["hugo-unifier", "--version"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    version = importlib.metadata.version("hugo-unifier")
    assert version in result.stdout, f"Expected version {version} not found in output."


def test_cli_root_help():
    """Test the root CLI help command."""
    cmd = ["hugo-unifier", "--help"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    assert "Usage:" in result.stdout, "Expected usage information not found in output."
    assert "Commands" in result.stdout, "Expected commands section not found in output."
    assert "get" in result.stdout, "Expected 'get' command not found in output."
    assert "apply" in result.stdout, "Expected 'apply' command not found in output."


def test_cli_get_help():
    """Test the CLI help for the 'get' command."""
    cmd = ["hugo-unifier", "get", "--help"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    assert "Usage:" in result.stdout, "Expected usage information not found in output."
    assert "--input" in result.stdout, "Expected --input option not found in output."
    assert "--outdir" in result.stdout, "Expected --outdir option not found in output."
    assert (
        "Get changes for the input .h5ad files." in result.stdout
    ), "Expected description for 'get' command not found in output."


def test_cli_apply_help():
    """Test the CLI help for the 'apply' command."""
    cmd = ["hugo-unifier", "apply", "--help"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    assert "Usage:" in result.stdout, "Expected usage information not found in output."
    assert "--input" in result.stdout, "Expected --input option not found in output."
    assert (
        "--changes" in result.stdout
    ), "Expected --changes option not found in output."
    assert "--output" in result.stdout, "Expected --output option not found in output."
    assert (
        "Apply changes to the input .h5ad file." in result.stdout
    ), "Expected description for 'apply' command not found in output."


def test_cli_full_pipeline(test_h5ad_paths, tmp_path):
    """Test the full pipeline of the CLI."""
    get_dir = tmp_path / "get"
    get_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["hugo-unifier", "get", "--outdir", str(get_dir)]
    for input_file in test_h5ad_paths:
        cmd.extend(["--input", str(input_file)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"

    apply_dir = tmp_path / "apply"
    apply_dir.mkdir(parents=True, exist_ok=True)

    sample_to_apply = "uzzan"
    input_file = next(
        input_file
        for input_file in test_h5ad_paths
        if sample_to_apply in input_file.stem
    )

    changes_file = get_dir / f"{sample_to_apply}.csv"
    assert changes_file.exists(), f"Changes file {changes_file} not found."

    output_file = apply_dir / f"{sample_to_apply}.h5ad"
    assert not output_file.exists(), f"Output file {output_file} already exists."

    cmd = [
        "hugo-unifier",
        "apply",
        "--input",
        str(input_file),
        "--changes",
        str(changes_file),
        "--output",
        str(output_file),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    assert output_file.exists(), f"Output file {output_file} not created."
