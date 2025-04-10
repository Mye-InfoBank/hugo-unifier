import rich_click as click
from importlib.metadata import version
import anndata as ad
import os

from hugo_unifier import get_changes


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


@click.command()
@click.version_option(version("hugo-unifier"))
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True),
    multiple=True,
    required=True,
    callback=validate_h5ad,
    help="Paths to the input .h5ad files (can specify multiple).",
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(file_okay=False, writable=True),
    required=True,
    help="Path to the output directory for change DataFrames.",
)
def cli(input, outdir):
    """CLI for the hugo-unifier."""

    # Create output directory if it doesn't exist
    os.makedirs(outdir, exist_ok=True)

    # Build a dictionary from file names and adata.var.index
    symbols_dict = {}
    for file_path in input:
        adata = ad.read_h5ad(file_path)
        file_name = os.path.basename(file_path)
        symbols_dict[file_name] = adata.var.index.tolist()

    # Process the symbols using get_changes
    updated_symbols_dict, _ = get_changes(symbols_dict)

    # Save the change DataFrames into the output directory
    for file_name, df_changes in updated_symbols_dict.items():
        output_file = os.path.join(outdir, f"{file_name}_changes.csv")
        df_changes.to_csv(output_file, index=False)


def main():
    """Entry point for the hugo-unifier application."""
    cli()


if __name__ == "__main__":
    main()
