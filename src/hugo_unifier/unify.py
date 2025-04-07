import requests
import pandas as pd
from typing import Callable, Dict, List, Tuple

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

# New find_best_match function
# Behaviour: 
# If the gene name is approved or previous symbol: it is kept
# If the gene name is an alias:
#   If the gene has an alias is in the approved genes, it is kept as the original name
#   If the gene has only one alias which is not in the approved genes, it is kept
#   If the gene has multiple aliases, either the original symbol is kept (keep_gene_multiple_aliases = True) or discarded to avoid ambiguity (keep_gene_multiple_aliases = False)


def find_best_match(
    symbols: list[str],
    manipulations: List[Tuple[str, Callable[[str], str]]],
    keep_gene_multiple_aliases: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    
    original_symbols_set = set(symbols)
    df_result = pd.DataFrame(index=symbols, columns=[
        "resolution", "manipulation", "approved_symbol", "matchType", "location"])
    df_result["original_symbol"] = df_result.index

    # Base function
    ##########################################
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

    # Changed flag
    ##########################################
    df_result["changed"] = (
        df_result["resolution"].notna() &
        (df_result.index != df_result["approved_symbol"])
    )

    # Removal of unnecessary manipulations
    ##########################################
    
    # 1: manipulation on unchanged genes (es a manipulation returned an existing symbol)   
    mask_remove = (df_result["resolution"].isin(["discard_after_dot", "dot_to_dash"])) & (df_result["changed"] == False)
    df_result = df_result.loc[~mask_remove]

    # 2: manipulations flagged even if nothing was changed in the gene
    mask_false_manipulations = (df_result["resolution"].isin(["discard_after_dot", "dot_to_dash"])) & (df_result["original_symbol"] == df_result["manipulation"])
    df_result.loc[mask_false_manipulations, "changed"] = False
    df_result.loc[mask_false_manipulations, "resolution"] = "identity"
    
    # Split of the match types
    ##########################################
    df_result_approved = df_result[df_result["matchType"].isin(["Approved symbol", "Previous symbol"])]
    df_result_alias = df_result[df_result["matchType"] == "Alias symbol"]
    df_result_unmatched = df_result[df_result["matchType"].isna()]

    approved_symbols = set(df_result_approved["approved_symbol"].dropna())
    df_alias_clean = df_result_alias.copy()
    
    # Cleaning of alias set
    ##########################################
    
    # 1: Remove genes which have an alias that's already in the dataset
    mask_alias_conflict = df_alias_clean["approved_symbol"].isin(approved_symbols)
    aliases_to_keep_as_identity = df_alias_clean[mask_alias_conflict].copy()
    
    identity_alias_conflicts = pd.DataFrame(index=aliases_to_keep_as_identity["original_symbol"].unique())
    identity_alias_conflicts["original_symbol"] = identity_alias_conflicts.index
    identity_alias_conflicts["resolution"] = "identity"
    identity_alias_conflicts["manipulation"] = identity_alias_conflicts.index
    identity_alias_conflicts["approved_symbol"] = identity_alias_conflicts.index
    identity_alias_conflicts["matchType"] = "Alias_discarded_existing_approved"
    identity_alias_conflicts["location"] = pd.NA
    identity_alias_conflicts["changed"] = False
    
    df_alias_clean = df_alias_clean.loc[~mask_alias_conflict]

    n_alias_discarded_existing_approved = len(identity_alias_conflicts)
    
    # 2: Fix aliases where approved == original
    # This has a very low incidence but it happens
    mask_same = df_alias_clean["original_symbol"] == df_alias_clean["approved_symbol"]
    n_corrected_alias_same = mask_same.sum()
    df_alias_clean.loc[mask_same, "matchType"] = "Approved symbol"
    
    # 3: Identify duplicates in aliases
    alias_counts = df_alias_clean["original_symbol"].value_counts()
    accepted_alias_symbols = alias_counts[alias_counts == 1].index
    duplicated_alias_symbols = alias_counts[alias_counts > 1].index

    # Keep the genes that have only one alias
    df_alias_accepted = df_alias_clean[df_alias_clean["original_symbol"].isin(accepted_alias_symbols)].copy()

    # Handle genes with multiple aliases
    ##########################################
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

        # Add identity rows to accepted aliases
        df_alias_accepted = pd.concat([df_alias_accepted, identity_fill])
    else:
        identity_fill = pd.DataFrame()  # empty

    # Split alias dataframe into accepted/unaccepted
    accepted_indices = df_alias_accepted.index
    df_alias_unaccepted = df_result_alias.drop(index=accepted_indices, errors="ignore").copy()

    # Combined result
    ##########################################
    
    df_alias_accepted["changed"] = True
    df_final = pd.concat([df_result_approved, df_alias_accepted, df_result_unmatched])

    # Stats collection
    ##########################################
    stats = {
        # input genes
        "n_input_genes": len(symbols),
        # ... of which approved:
        "n_approved_symbol": (df_result_approved["matchType"] == "Approved symbol").sum(),
        # ... of which previous
        "n_previous_symbol": (df_result_approved["matchType"] == "Previous symbol").sum(),
        # ... of which aliases
        "n_alias_symbol": len(df_result_alias),
        # ... of which unmatched
        "n_unmatched": len(df_result_unmatched),
        # genes kept as original because alias present in approved symbols
        "n_alias_retained_identity_existing_approved": n_alias_discarded_existing_approved,
        # aliases where alias symbol = original symbol (rare but happens)
        "n_alias_corrected_same_name": n_corrected_alias_same,
        # genes with > 1 alias (removed if keep_gene_multiple_aliases = False)
        "n_alias_removed_duplicate": len(df_alias_clean[df_alias_clean["approved_symbol"].isin(duplicated_alias_symbols)]),
        
        # Changed genes
        # Changed with previous symbol
        "n_changed_previous_symbol": len(df_final[(df_final["changed"]) & (df_final["matchType"] == "Previous symbol")]),
        # Changed with an alias
        "n_changed_alias": len(df_final[(df_final["matchType"] == "Alias symbol")]),
        # Changed because approved gene found after removing "."
        "n_changed_dot": len(df_final[(df_final["resolution"] == "discard_after_dot")]),
        # Changed because approved gene found after replacing "." with "-"
        "n_changed_dash": len(df_final[(df_final["resolution"] == "dot_to_dash")]),
        # The manipulation returned an existing symbol
        "n_removed_duplicates_after_fix": mask_remove.sum(),
        # The amnipulation was flagged but nothing was changed
        "n_false_manipulations": mask_false_manipulations.sum()
        
    }

    return df_final, df_alias_unaccepted, stats
