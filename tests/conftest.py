import pytest
import scanpy as sc
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the directory with test data."""
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def test_h5ad_path(test_data_dir):
    """Return the path to the test h5ad file."""
    path = test_data_dir / "test.h5ad"
    if not path.exists():
        # Create the test data directory if it doesn't exist
        test_data_dir.mkdir(exist_ok=True, parents=True)

        # If the test.h5ad file doesn't exist, create a small test AnnData object
        adata = sc.datasets.pbmc3k_processed()
        # Save the test data
        adata.write_h5ad(path)

    return path

@pytest.fixture(scope="session")
def test_h5ad(test_h5ad_path):
    """Return the test AnnData object."""
    adata = sc.read_h5ad(test_h5ad_path)
    return adata