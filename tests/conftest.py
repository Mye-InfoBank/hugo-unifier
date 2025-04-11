import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def test_h5ad_paths():
    """Return the path to the test h5ad file."""
    directory = Path(__file__).parent / "data"
    return list(directory.glob("*.h5ad"))


@pytest.fixture(scope="session")
def test_h5ad_objects(test_h5ad_paths):
    """Return the test h5ad objects."""
    import anndata as ad

    return [ad.read_h5ad(file_path) for file_path in test_h5ad_paths]


@pytest.fixture(scope="session")
def uzzan_h5ad():
    """Fixture for the uzzan.h5ad test file."""
    return Path("tests/data/uzzan.h5ad")


@pytest.fixture(scope="session")
def uzzan_csv():
    """Fixture for the uzzan.csv test file."""
    return Path("tests/data/uzzan.csv")
