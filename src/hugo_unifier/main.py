import rich_click as click
from importlib.metadata import version
import anndata as ad
import os
import pandas as pd

from hugo_unifier import get_changes, apply_changes


def validate_h5ad(ctx, param, value):
    """Validate that the file has a .h5ad suffix."""
    if value:
        if isinstance(value, tuple):
            for v in value:
                if not v.endswith(".h5ad"):
                    raise click.BadParameter(
                        f"{param.name} must be files with a .h5ad suffix."
                    )
        elif not value.endswith(".h5ad"):
            raise click.BadParameter(
                f"{param.name} must be a file with a .h5ad suffix."
            )
    return value


@click.group()
@click.version_option(version("hugo-unifier"))
def cli():
    """CLI for the hugo-unifier."""
    pass


@cli.command()
@click.argument(
    "input",
    type=click.Path(exists=True),
    required=True,
    nargs=-1,
    callback=validate_h5ad,
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
    for file_path in input:
        adata = ad.read_h5ad(file_path)
        file_name = os.path.basename(file_path)
        symbols_dict[file_name] = adata.var.index.tolist()

    # Process the symbols using get_changes
    _, sample_changes = get_changes(symbols_dict)

    # Save the change DataFrames into the output directory
    for file_name, df_changes in sample_changes.items():
        output_file = os.path.join(outdir, f"{file_name}_changes.csv")
        df_changes.to_csv(output_file, index=False)


@cli.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True),
    required=True,
    callback=validate_h5ad,
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
