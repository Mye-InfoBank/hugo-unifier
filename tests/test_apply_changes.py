import pandas as pd
import anndata as ad
from hugo_unifier.apply_changes import apply_changes


def test_apply_changes(uzzan_h5ad, uzzan_csv):
    """Test the apply_changes function."""
    # Load the test AnnData object
    adata = ad.read_h5ad(uzzan_h5ad)

    # Load the test changes DataFrame
    df_changes = pd.read_csv(uzzan_csv)

    # Apply the changes
    updated_adata = apply_changes(adata, df_changes)

    # Validate the changes
    for _, row in df_changes.iterrows():
        action = row["action"]
        symbol = row["symbol"]
        new_symbol = row["new"]

        if action == "rename":
            assert (
                new_symbol in updated_adata.var.index
            ), f"{new_symbol} not found after rename."
            assert (
                symbol not in updated_adata.var.index
            ), f"{symbol} still exists after rename."
        elif action == "copy":
            assert (
                new_symbol in updated_adata.var.index
            ), f"{new_symbol} not found after copy."
            assert symbol in updated_adata.var.index, f"{symbol} missing after copy."

    # Ensure no unexpected changes occurred
    assert len(updated_adata.var.index) == len(adata.var.index) + len(
        df_changes[df_changes["action"] == "copy"]
    ), "Unexpected number of rows in updated AnnData object."

    # Ensure all observation columns are preserved
    assert set(adata.obs.columns) == set(
        updated_adata.obs.columns
    ), "Observation columns changed after applying changes"
