import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def test_h5ad_paths():
    """Return the path to the test h5ad file."""
    directory = Path(__file__).parent / "data"
    return directory.glob("*.h5ad")


@pytest.fixture(scope="session")
def test_h5ad_objects(test_h5ad_paths):
    """Return the test h5ad objects."""
    import anndata as ad

    return [ad.read_h5ad(file_path) for file_path in test_h5ad_paths]
