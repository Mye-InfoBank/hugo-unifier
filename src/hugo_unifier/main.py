import rich_click as click
from importlib.metadata import version
import anndata as ad
import os
import pandas as pd
from pathlib import Path

from hugo_unifier import get_changes, apply_changes


@click.group()
@click.version_option(version("hugo-unifier"))
def cli():
    """CLI for the hugo-unifier."""
    pass


@cli.command()
@click.option(
    "--input",
    "-i",
    type=str,
    required=True,
    multiple=True,
    help="Paths to the input .h5ad files with optional dataset names (e.g., dataset1:test1.h5ad).",
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(file_okay=False, writable=True),
    required=True,
    help="Path to the output directory for change DataFrames.",
)
def get(input, outdir):
    """Get changes for the input .h5ad files."""

    # Create output directory if it doesn't exist
    os.makedirs(outdir, exist_ok=True)

    # Build a dictionary from file names and adata.var.index
    symbols_dict = {}
    for item in input:
        if ":" in item:
            dataset_name, file_path = item.split(":", 1)
        else:
            file_path = item

            dataset_name = Path(file_path).stem

        # Validate the file path
        if not os.path.isfile(file_path):
            raise click.BadParameter(f"File {file_path} does not exist.")
        if not file_path.endswith(".h5ad"):
            raise click.BadParameter(f"File {file_path} must have a .h5ad suffix.")

        if dataset_name in symbols_dict:
            raise click.BadParameter(
                f"Dataset name {dataset_name} is duplicated in the input."
            )

        adata = ad.read_h5ad(file_path, backed="r")
        symbols_dict[dataset_name] = adata.var.index.tolist()

    # Process the symbols using get_changes
    _, sample_changes = get_changes(symbols_dict)

    # Save the change DataFrames into the output directory
    for dataset_name, df_changes in sample_changes.items():
        output_file = os.path.join(outdir, f"{dataset_name}.csv")
        df_changes.to_csv(output_file, index=False)


@cli.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True),
    required=True,
    help="Path to the input .h5ad file.",
)
@click.option(
    "--changes",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Path to the changes CSV file.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    required=True,
    help="Path to save the updated .h5ad file.",
)
def apply(input, changes, output):
    """Apply changes to the input .h5ad file."""

    # Validate the input file
    if not input.endswith(".h5ad"):
        raise click.BadParameter("Input file must have a .h5ad suffix.")

    # Load the AnnData object and changes DataFrame
    adata = ad.read_h5ad(input)
    df_changes = pd.read_csv(changes)

    # Apply the changes
    updated_adata = apply_changes(adata, df_changes)

    # Save the updated AnnData object
    updated_adata.write_h5ad(output)


def main():
    """Entry point for the hugo-unifier application."""
    cli()


if __name__ == "__main__":
    main()
