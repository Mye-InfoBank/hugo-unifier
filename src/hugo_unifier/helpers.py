import requests
import pandas as pd
from typing import Callable, Dict, List, Tuple


def fetch_symbol_check_results(symbols: List[str]) -> pd.DataFrame:
    """
    Fetch symbol check results from the genenames.org API.

    Args:
        symbols (List[str]): List of gene symbols to check.

    Returns:
        pd.DataFrame: DataFrame containing the API response.
    """
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
    response.raise_for_status()
    return pd.DataFrame(response.json())


def apply_manipulations(
    symbols: List[str],
    manipulations: List[Tuple[str, Callable[[str], str]]]
) -> pd.DataFrame:
    """
    Apply manipulations to symbols and fetch symbol check results.

    Args:
        symbols (List[str]): List of gene symbols.
        manipulations (List[Tuple[str, Callable[[str], str]]]): List of manipulations to apply.

    Returns:
        pd.DataFrame: DataFrame with manipulation results.
    """
    df_result = pd.DataFrame(index=symbols, columns=[
        "resolution", "manipulation", "approved_symbol", "matchType", "location"
    ])
    df_result["original_symbol"] = df_result.index

    for manipulation_name, manipulation in manipulations:
        unresolved_mask = df_result["resolution"].isna()
        df_result.loc[unresolved_mask, "manipulation"] = df_result[unresolved_mask].index.map(manipulation)

        manipulated_symbols = df_result.loc[unresolved_mask, "manipulation"].unique().tolist()
        df_symbol_check = fetch_symbol_check_results(manipulated_symbols)

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

    return df_result


def remove_conflicting_aliases(
    df_result_alias: pd.DataFrame, approved_symbols: set
) -> Tuple[pd.DataFrame, int]:
    """
    Remove aliases that conflict with approved symbols.

    Args:
        df_result_alias (pd.DataFrame): DataFrame containing alias symbols.
        approved_symbols (set): Set of approved symbols.

    Returns:
        Tuple[pd.DataFrame, int]: Cleaned alias DataFrame and count of discarded aliases.
    """
    mask_alias_conflict = df_result_alias["approved_symbol"].isin(approved_symbols)
    df_alias_clean = df_result_alias.loc[~mask_alias_conflict]
    n_alias_discarded_existing_approved = mask_alias_conflict.sum()
    return df_alias_clean, n_alias_discarded_existing_approved


def correct_same_aliases(df_alias_clean: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Correct aliases where the approved symbol matches the original symbol.

    Args:
        df_alias_clean (pd.DataFrame): DataFrame containing cleaned alias symbols.

    Returns:
        Tuple[pd.DataFrame, int]: Updated alias DataFrame and count of corrected aliases.
    """
    mask_same = df_alias_clean["original_symbol"] == df_alias_clean["approved_symbol"]
    n_corrected_alias_same = mask_same.sum()
    df_alias_clean.loc[mask_same, "matchType"] = "Approved symbol"
    return df_alias_clean, n_corrected_alias_same


def handle_duplicate_aliases(
    df_alias_clean: pd.DataFrame, keep_gene_multiple_aliases: bool
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Handle duplicate aliases by either keeping or discarding them.

    Args:
        df_alias_clean (pd.DataFrame): DataFrame containing cleaned alias symbols.
        keep_gene_multiple_aliases (bool): Whether to keep genes with multiple aliases.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Accepted aliases and identity-filled DataFrame for duplicates.
    """
    alias_counts = df_alias_clean["original_symbol"].value_counts()
    accepted_alias_symbols = alias_counts[alias_counts == 1].index
    duplicated_alias_symbols = alias_counts[alias_counts > 1].index

    df_alias_accepted = df_alias_clean[df_alias_clean["original_symbol"].isin(accepted_alias_symbols)].copy()

    if keep_gene_multiple_aliases:
        duplicated_alias_genes = df_alias_clean[df_alias_clean["original_symbol"].isin(duplicated_alias_symbols)].copy()

        identity_fill = pd.DataFrame(index=duplicated_alias_genes["original_symbol"].unique())
        identity_fill["original_symbol"] = identity_fill.index
        identity_fill["resolution"] = "identity"
        identity_fill["manipulation"] = identity_fill.index
        identity_fill["approved_symbol"] = identity_fill.index
        identity_fill["matchType"] = "Alias_discarded"
        identity_fill["location"] = pd.NA
        identity_fill["changed"] = False

        df_alias_accepted = pd.concat([df_alias_accepted, identity_fill])
    else:
        identity_fill = pd.DataFrame()  # Empty DataFrame if duplicates are discarded

    return df_alias_accepted, identity_fill


def clean_aliases(
    df_result: pd.DataFrame,
    keep_gene_multiple_aliases: bool
) -> Tuple[pd.DataFrame, pd.DataFrame, int, int]:
    """
    Clean alias symbols by resolving conflicts and handling duplicates.

    Args:
        df_result (pd.DataFrame): DataFrame with symbol check results.
        keep_gene_multiple_aliases (bool): Whether to keep genes with multiple aliases.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, int, int]: Cleaned alias DataFrame, unaccepted aliases,
                                                     count of discarded aliases, and corrected aliases.
    """
    df_result_alias = df_result[df_result["matchType"] == "Alias symbol"]
    approved_symbols = set(df_result[df_result["matchType"].isin(["Approved symbol", "Previous symbol"])]["approved_symbol"].dropna())

    # Step 1: Remove aliases that conflict with approved symbols
    df_alias_clean, n_alias_discarded_existing_approved = remove_conflicting_aliases(df_result_alias, approved_symbols)

    # Step 2: Correct aliases where approved == original
    df_alias_clean, n_corrected_alias_same = correct_same_aliases(df_alias_clean)

    # Step 3: Handle duplicate aliases
    df_alias_accepted, identity_fill = handle_duplicate_aliases(df_alias_clean, keep_gene_multiple_aliases)

    # Step 4: Split alias DataFrame into accepted and unaccepted
    accepted_indices = df_alias_accepted.index
    df_alias_unaccepted = df_result_alias.drop(index=accepted_indices, errors="ignore").copy()

    return df_alias_accepted, df_alias_unaccepted, n_alias_discarded_existing_approved, n_corrected_alias_same


def collect_statistics(
    df_result: pd.DataFrame,
    df_alias_unaccepted: pd.DataFrame,
    n_alias_discarded_existing_approved: int,
    n_corrected_alias_same: int
) -> Dict[str, int]:
    """
    Collect statistics about the symbol resolution process.

    Args:
        df_result (pd.DataFrame): Final DataFrame with resolved symbols.
        df_alias_unaccepted (pd.DataFrame): DataFrame with unaccepted aliases.
        n_alias_discarded_existing_approved (int): Count of discarded aliases due to conflicts.
        n_corrected_alias_same (int): Count of corrected aliases with the same name.

    Returns:
        Dict[str, int]: Dictionary of statistics.
    """
    stats = {
        "n_input_genes": len(df_result),
        "n_approved_symbol": (df_result["matchType"] == "Approved symbol").sum(),
        "n_previous_symbol": (df_result["matchType"] == "Previous symbol").sum(),
        "n_alias_symbol": len(df_result[df_result["matchType"] == "Alias symbol"]),
        "n_unmatched": len(df_result[df_result["matchType"].isna()]),
        "n_alias_retained_identity_existing_approved": n_alias_discarded_existing_approved,
        "n_alias_corrected_same_name": n_corrected_alias_same,
        "n_unaccepted_aliases": len(df_alias_unaccepted),
    }
    int_stats = {k: int(v) for k, v in stats.items()}
    return int_stats


def process(
    symbols: List[str],
    manipulations: List[Tuple[str, Callable[[str], str]]],
    keep_gene_multiple_aliases: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """
    Main function to find the best match for gene symbols.

    Args:
        symbols (List[str]): List of gene symbols.
        manipulations (List[Tuple[str, Callable[[str], str]]]): List of manipulations to apply.
        keep_gene_multiple_aliases (bool): Whether to keep genes with multiple aliases.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]: Final DataFrame, unaccepted aliases, and statistics.
    """
    df_result = apply_manipulations(symbols, manipulations)
    df_alias_accepted, df_alias_unaccepted, n_alias_discarded_existing_approved, n_corrected_alias_same = clean_aliases(
        df_result, keep_gene_multiple_aliases
    )

    df_final = pd.concat([df_result[df_result["matchType"].isin(["Approved symbol", "Previous symbol"])],
                          df_alias_accepted, df_result[df_result["matchType"].isna()]])

    stats = collect_statistics(df_final, df_alias_unaccepted, n_alias_discarded_existing_approved, n_corrected_alias_same)

    return df_final, df_alias_unaccepted, stats