import rich_click as click
from importlib.metadata import version
import anndata as ad
import json
import pandas as pd

from hugo_unifier import unify


def validate_h5ad(ctx, param, value):
    """Validate that the file has a .h5ad suffix."""
    if value and not value.endswith(".h5ad"):
        raise click.BadParameter(f"{param.name} must be a file with a .h5ad suffix.")
    return value


@click.command()
@click.version_option(version("hugo-unifier"))
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True),
    required=True,
    callback=validate_h5ad,
    help="Path to the input .h5ad file.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    callback=validate_h5ad,
    help="Path to the output .h5ad file.",
)
@click.option("--stats", "-s", type=click.Path(), help="Path to the output stats file.")
@click.option("--column", "-c", type=str, required=True, help="Column name to process.")
def cli(input, output, column, stats):
    """CLI for the hugo-unifier."""
    adata = ad.read_h5ad(input)

    # Determine if the column is in the index or a column
    if column == "index":
        symbols = adata.var.index.tolist()
    else:
        assert column in adata.var.columns, f"Column {column} not found in input."
        symbols = adata.var[column].tolist()

    updated_symbols, stats_dict = unify(
        symbols,
        ["identity", "discard_after_dot", "dot_to_dash"],
        keep_gene_multiple_aliases=False,
        return_stats=True,
    )

    # Update the AnnData object
    if column == "index":
        adata.var.index = updated_symbols
    else:
        adata.var[column] = updated_symbols

    # Save stats if requested
    if stats:
        with open(stats, "w") as f:
            json.dump(stats_dict, f, indent=4)

    # Write the updated AnnData object to the output file
    adata.write_h5ad(output)


def main():
    """Entry point for the hugo-unifier application."""
    cli()


if __name__ == "__main__":
    main()
