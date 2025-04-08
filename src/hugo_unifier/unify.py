import pandas as pd
import anndata as ad
from typing import Callable, Dict, List, Tuple, Set
import requests

from hugo_unifier.rules import manipulation_mapping
from hugo_unifier.helpers import process


def unify(
        obj: pd.DataFrame | ad.AnnData,
        column: str,
        manipulations: List[str],
        keep_gene_multiple_aliases: bool = False
) -> Tuple[pd.DataFrame | ad.AnnData, Dict[str, int]]:
    """
    Unify gene symbols in a DataFrame or AnnData object.

    Parameters
    ----------
    df : pd.DataFrame | ad.AnnData
        DataFrame or AnnData object containing gene symbols.
    column : str
        Column name containing gene symbols. Set to "index" to use the index.
    manipulations : List[Tuple[str, Callable[[str], str]]]
        List of tuples containing manipulation names and functions.
    keep_gene_multiple_aliases : bool, optional
        Whether to keep genes with multiple aliases, by default False.

    Returns
    -------
    pd.DataFrame | ad.AnnData
        DataFrame or AnnData object with unified gene symbols.
    """
    # Assert all manipulations are valid
    for manipulation in manipulations:
        assert manipulation in manipulation_mapping, f"Manipulation {manipulation} is not valid. Choose from {list(manipulation_mapping.keys())}."

    selected_manipulations = [(name, manipulation_mapping[name]) for name in manipulations]

    is_anndata = False
    if isinstance(obj, ad.AnnData):
        is_anndata = True
        df = obj.var.copy()
    else:
        df = obj.copy()
    
    assert isinstance(df, pd.DataFrame), "Input must be a pandas DataFrame or AnnData object."
    assert column == "index" or column in obj.columns, f"Column {column} not found in input."

    if column == "index":
        symbols = df.index.tolist()
    else:
        symbols = df[column].tolist()

    df_final, df_unaccepted, stats = process(symbols, selected_manipulations, keep_gene_multiple_aliases)

    df_final = df_final[~df_final["approved_symbol"].isna()].copy()
    mapping = df_final["approved_symbol"].to_dict()

    if column == "index":
        df.index = df.index.map(lambda x: mapping.get(x, x))
    else:
        df[column] = df[column].map(lambda x: mapping.get(x, x))

    if is_anndata:
        obj.var = df
        return obj, stats
    else:
        return df, stats
