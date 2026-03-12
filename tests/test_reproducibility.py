"""Tests to ensure output reproducibility by running the pipeline twice and comparing results."""

import anndata as ad
import pandas as pd

from hugo_unifier import get_changes, apply_changes


def test_get_changes_reproducibility(test_h5ad_objects, test_h5ad_paths):
    """
    Test that get_changes produces identical output across two consecutive runs.

    Runs get_changes twice with the same input and asserts the results are equal,
    verifying reproducibility without depending on hardcoded expected values.
    """
    symbols_dict = {
        path.stem: adata.var.index.tolist()
        for path, adata in zip(test_h5ad_paths, test_h5ad_objects)
    }

    _, sample_changes_1 = get_changes(symbols_dict)
    _, sample_changes_2 = get_changes(symbols_dict)

    assert set(sample_changes_1.keys()) == set(sample_changes_2.keys()), (
        "The two runs returned different sample keys."
    )

    for sample_name in sample_changes_1:
        df1 = sample_changes_1[sample_name].reset_index(drop=True)
        df2 = sample_changes_2[sample_name].reset_index(drop=True)
        pd.testing.assert_frame_equal(
            df1,
            df2,
            check_like=True,
            obj=f"sample '{sample_name}'",
        )


def test_apply_changes_reproducibility(uzzan_h5ad, uzzan_csv):
    """
    Test that apply_changes produces identical output across two consecutive runs.

    Runs apply_changes twice with the same inputs and asserts the var indices are
    equal, verifying reproducibility without depending on hardcoded expected values.
    """
    adata = ad.read_h5ad(uzzan_h5ad)
    df_changes = pd.read_csv(uzzan_csv)

    result_1 = apply_changes(adata, df_changes)
    result_2 = apply_changes(adata, df_changes)

    assert sorted(result_1.var.index.tolist()) == sorted(result_2.var.index.tolist()), (
        "The two runs of apply_changes produced different var indices."
    )
