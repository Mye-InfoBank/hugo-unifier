import pandas as pd
import anndata as ad
from typing import Callable, Dict, List, Tuple, Set
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

def find_matches(symbols: Set[str], manipulations: List[Tuple[str, Callable[[str], str]]]) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """
    Find matches for gene symbols using the specified manipulations.

    Parameters
    ----------
    symbols : Set[str]
        Set of gene symbols to check.
    manipulations : List[Tuple[str, Callable[[str], str]]]
        List of tuples containing manipulation names and functions.

    Returns
    -------
    pd.DataFrame
        DataFrame with results. Contains columns:
        - resolution: Name of the manipulation that resolved the symbol.
        - manipulation: The manipulated symbol.
        - approved_symbol: The approved symbol detected by HUGO.
        - matchType: Type of match (e.g., Approved symbol, Previous symbol, Alias symbol).
        - location: Location of the symbol in the HUGO database.
        - original_symbol: Original symbol before manipulation.
        - changed: Boolean indicating if the symbol was changed (a resolution was found and approved_symbol != original_symbol).
    """
    df_result = pd.DataFrame(index=symbols, columns=[
        "resolution", "manipulation", "approved_symbol", "matchType", "location"])
    df_result["original_symbol"] = df_result.index

    for manipulation_name, manipulation in manipulations:
        unresolved_mask = df_result["resolution"].isna()
        df_result.loc[unresolved_mask, "manipulation"] = df_result[unresolved_mask].index.map(manipulation)

        manipulated_symbols = df_result.loc[unresolved_mask, "manipulation"].unique().tolist()
        df_symbol_check = get_symbol_check_results(manipulated_symbols)

        df_symbol_check_filtered = df_symbol_check[
            df_symbol_check["matchType"].isin(["Approved symbol", "Previous symbol", "Alias symbol"])
        ].copy()

        df_symbol_check_filtered.index = df_symbol_check_filtered["input"]
        input_symbol_mapping = df_symbol_check_filtered["approvedSymbol"].to_dict()
        match_type_mapping = df_symbol_check_filtered["matchType"].to_dict()
        location_mapping = df_symbol_check_filtered["location"].to_dict()

        approved_mask = df_result["manipulation"].isin(input_symbol_mapping.keys())

        df_result.loc[approved_mask, "resolution"] = manipulation_name
        df_result.loc[approved_mask, "approved_symbol"] = df_result.loc[approved_mask, "manipulation"].map(input_symbol_mapping)
        df_result.loc[approved_mask, "matchType"] = df_result.loc[approved_mask, "manipulation"].map(match_type_mapping)
        df_result.loc[approved_mask, "location"] = df_result.loc[approved_mask, "manipulation"].map(location_mapping)
    
    df_result["changed"] = (
        df_result["resolution"].notna() &
        (df_result.index != df_result["approved_symbol"])
    )

    return df_result

def clean_up(df_result: pd.DataFrame) -> pd.DataFrame:
    """
    Clean up the DataFrame by removing unnecessary manipulations and false flags.

    Parameters
    ----------
    df_result : pd.DataFrame
        DataFrame with results.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    # Removal of unnecessary manipulations
    mask_remove = (df_result["resolution"].isin(["discard_after_dot", "dot_to_dash"])) & (df_result["changed"] == False)
    df_result = df_result.loc[~mask_remove].copy()

    # 2: manipulations flagged even if nothing was changed in the gene
    mask_false_manipulations = (df_result["resolution"].isin(["discard_after_dot", "dot_to_dash"])) & (df_result["original_symbol"] == df_result["manipulation"])
    df_result.loc[mask_false_manipulations, "changed"] = False
    df_result.loc[mask_false_manipulations, "resolution"] = "identity"

    return df_result

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
    
    assert isinstance(df, pd.DataFrame), "Input must be a pandas DataFrame or AnnData object."
    assert column == "index" or column in obj.columns, f"Column {column} not found in input."

    if column == "index":
        symbols = df.index.tolist()
    else:
        symbols = df[column].tolist()

    df_result = find_matches(symbols, selected_manipulations)
    df_result = clean_up(df_result)

    df_result.to_csv("result.tsv", sep="\t")
