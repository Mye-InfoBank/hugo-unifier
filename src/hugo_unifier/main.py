import rich_click as click
from importlib.metadata import version
import os

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
    click.echo(f"Input file: {input}")
    click.echo(f"Output file: {output}")
    click.echo(f"Column: {column}")


def main():
    """Entry point for the hugo-unifier application."""
    cli()

if __name__ == "__main__":
    main()