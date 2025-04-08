import pandas as pd
import anndata as ad
from typing import Callable, Dict, List, Tuple
import requests

from hugo_unifier.rules import manipulation_mapping

def get_symbol_check_results(symbols):
    url = "https://www.genenames.org/cgi-bin/tools/symbol-check"
    data = [
        ("approved", "true"),
        ("case", "insensitive"),
        ("output", "html"),
        *[("queries[]", symbol) for symbol in symbols],
        ("synonyms", "true"),
        ("unmatched", "true"),
        ("withdrawn", "true"),
        ("previous", "true"),
    ]
    response = requests.post(url, data=data)
    res_json = response.json()

    return pd.DataFrame(res_json)

def unify(
        obj: pd.DataFrame | ad.AnnData,
        column: str,
        manipulations: List[str],
        keep_gene_multiple_aliases: bool = False
):
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

    print(type(df))
    
    assert isinstance(df, pd.DataFrame), "Input must be a pandas DataFrame or AnnData object."
    assert column == "index" or column in obj.columns, f"Column {column} not found in input."

    if column == "index":
        symbols = df.index.tolist()
    else:
        symbols = df[column].tolist()

    print(symbols)
