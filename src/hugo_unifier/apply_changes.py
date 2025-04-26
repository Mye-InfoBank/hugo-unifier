import anndata as ad
import pandas as pd


def apply_changes(adata: ad.AnnData, df_changes: pd.DataFrame):
    """
    Apply changes to the AnnData object based on the changes DataFrame.

    Parameters
    ----------
    adata : anndata.AnnData
        The AnnData object to apply changes to.
    df_changes : pandas.DataFrame
        DataFrame containing the changes to apply. It should have columns 'action', 'symbol', and 'new'.

    Returns
    -------
    None
    """
    adata = adata.copy()
    for _, row in df_changes.iterrows():
        action = row["action"]
        symbol = row["symbol"]
        new_symbol = row["new"]

        if action == "conflict":
            print(f"Conflict for {symbol} -> {new_symbol}")
            continue

        assert (
            symbol in adata.var.index
        ), f"Symbol {symbol} not found in AnnData object."
        assert (
            new_symbol not in adata.var.index
        ), f"New symbol {new_symbol} already exists in AnnData object."

        assert action in [
            "rename",
            "copy",
        ], f"Action {action} not recognized. Expected 'rename' or 'copy'."

        if action == "rename":
            # Update the index value in a single row
            adata.var.rename(index={symbol: new_symbol}, inplace=True)
        elif action == "copy":
            # Add a new row to the AnnData object
            adata_row = adata[:, adata.var.index == symbol].copy()
            adata_row.var.index = [new_symbol]
            adata = ad.concat(
                [adata, adata_row], axis="var", merge="unique", uns_merge="unique"
            )

    return adata
