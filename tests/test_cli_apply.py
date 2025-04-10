import subprocess


def test_cli_apply_changes(uzzan_h5ad, uzzan_csv, tmp_path):
    """Test the CLI 'apply' command for applying changes."""
    # Define paths for input and output
    input_file = uzzan_h5ad
    changes_file = uzzan_csv
    output_file = tmp_path / "uzzan_updated.h5ad"

    # Prepare the CLI command
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

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Assert the command ran successfully
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"

    # Check that the output file was created
    assert output_file.exists(), "Output file was not created."
