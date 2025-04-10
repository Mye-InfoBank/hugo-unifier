import subprocess


def test_cli_get_changes(test_h5ad_paths, tmp_path):
    """Test the CLI 'get' command for generating changes."""
    # Define paths for input and output
    input_files = list(test_h5ad_paths)
    output_dir = tmp_path / "output"

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare the CLI command
    cmd = ["hugo-unifier", "get"]
    for file in input_files:
        cmd.extend(["--input", str(file)])
    cmd.extend(["--outdir", str(output_dir)])

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Assert the command ran successfully
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"

    # Check that output files are created
    output_files = list(output_dir.glob("*_changes.csv"))
    assert len(output_files) > 0, "No output files were generated."

    # Optionally, validate the content of one of the output files
    for output_file in output_files:
        assert output_file.stat().st_size > 0, f"Output file {output_file} is empty."
