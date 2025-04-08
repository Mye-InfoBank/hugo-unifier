from typing import Dict, List, Tuple, Union

from hugo_unifier.rules import manipulation_mapping
from hugo_unifier.helpers import process


def unify(
    symbols: List[str],
    manipulations: List[str] = ["identity", "discard_after_dot", "dot_to_dash"],
    keep_gene_multiple_aliases: bool = False,
    return_stats: bool = False,
) -> Union[List[str], Tuple[List[str], Dict[str, int]]]:
    """
    Unify gene symbols in a list of symbols.

    Parameters
    ----------
    symbols : List[str]
        List of gene symbols to unify.
    manipulations : List[str]
        List of manipulation names to apply.
    keep_gene_multiple_aliases : bool, optional
        Whether to keep genes with multiple aliases, by default False.
    return_stats : bool, optional
        Whether to return statistics about the unification process, by default False.

    Returns
    -------
    List[str]
        Updated list of unified gene symbols.
    Tuple[List[str], Dict[str, int]]
        Updated list of unified gene symbols and statistics (if return_stats is True).
    """
    # Assert all manipulations are valid
    for manipulation in manipulations:
        assert (
            manipulation in manipulation_mapping
        ), f"Manipulation {manipulation} is not valid. Choose from {list(manipulation_mapping.keys())}."

    selected_manipulations = [
        (name, manipulation_mapping[name]) for name in manipulations
    ]

    # Process the symbols
    df_final, _, stats = process(
        symbols, selected_manipulations, keep_gene_multiple_aliases
    )

    # Create a mapping of original symbols to approved symbols
    df_final = df_final[~df_final["approved_symbol"].isna()].copy()
    mapping = df_final["approved_symbol"].to_dict()

    # Update the symbols list
    updated_symbols = [mapping.get(symbol, symbol) for symbol in symbols]

    if return_stats:
        return updated_symbols, stats
    return updated_symbols
