import subprocess


def test_cli_get_changes(test_h5ad_paths, tmp_path):
    """Test the CLI 'get' command for generating changes."""
    # Define paths for input and output
    input_files = test_h5ad_paths
    output_dir = tmp_path / "output"

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare the CLI command
    cmd = ["hugo-unifier", "get", "--outdir", str(output_dir)]

    for input_file in input_files:
        cmd.extend(["--input", str(input_file)])

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Assert the command ran successfully
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"

    # Check that output files are created
    output_files = list(output_dir.glob("*.csv"))
    for input_file in input_files:
        expected_output = output_dir / f"{input_file.stem}.csv"
        assert (
            expected_output.exists()
        ), f"Output file {expected_output} was not created."

    # Optionally, validate the content of one of the output files
    for output_file in output_files:
        assert output_file.stat().st_size > 0, f"Output file {output_file} is empty."


def test_cli_get_with_aliases(test_h5ad_paths, tmp_path):
    """Test the CLI 'get' command for generating changes."""
    # Define paths for input and output
    input_files = test_h5ad_paths
    output_dir = tmp_path / "output"

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare the CLI command
    cmd = ["hugo-unifier", "get", "--outdir", str(output_dir)]

    for i, input_file in enumerate(input_files):
        cmd.extend(["--input", f"ds{i}:{input_file}"])

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Assert the command ran successfully
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"

    # Check that output files are created
    output_files = list(output_dir.glob("*.csv"))
    for i, input_file in enumerate(input_files):
        expected_output = output_dir / f"ds{i}.csv"
        assert (
            expected_output.exists()
        ), f"Output file {expected_output} was not created."

    # Optionally, validate the content of one of the output files
    for output_file in output_files:
        assert output_file.stat().st_size > 0, f"Output file {output_file} is empty."
