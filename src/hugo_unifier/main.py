import rich_click as click
from importlib.metadata import version
import anndata as ad

from hugo_unifier import unify

def validate_h5ad(ctx, param, value):
    """Validate that the file has a .h5ad suffix."""
    if value and not value.endswith(".h5ad"):
        raise click.BadParameter(f"{param.name} must be a file with a .h5ad suffix.")
    return value

@click.command()
@click.version_option(version("hugo-unifier"))
@click.option("--input", "-i", type=click.Path(exists=True), required=True, callback=validate_h5ad, help="Path to the input .h5ad file.")
@click.option("--output", "-o", type=click.Path(), required=True, callback=validate_h5ad, help="Path to the output .h5ad file.")
@click.option("--column", "-c", type=str, required=True, help="Column name to process.")
def cli(input, output, column):
    """CLI for the hugo-unifier."""
    adata = ad.read_h5ad(input)

    unify(adata, column, ["identity", "discard_after_dot", "dot_to_dash"], keep_gene_multiple_aliases=False)


def main():
    """Entry point for the hugo-unifier application."""
    cli()

if __name__ == "__main__":
    main()