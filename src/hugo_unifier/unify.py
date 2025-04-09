from typing import Dict, List, Tuple, Union

from hugo_unifier.symbol_manipulations import manipulation_mapping
from hugo_unifier.orchestrated_fetch import orchestrated_fetch
from hugo_unifier.ingest_symbols import ingest_symbols
from hugo_unifier.create_graph import create_graph
from hugo_unifier.graph_manipulations import (
    remove_self_edges,
    remove_loose_ends,
    resolve_unapproved,
    aggregate_approved,
)


def unify(
    symbols: Dict[str, List[str]],
    manipulations: List[str] = ["identity", "dot_to_dash", "discard_after_dot"],
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

    symbol_union = set()
    for sample_symbols in symbols.values():
        symbol_union.update(sample_symbols)
    symbol_union = list(symbol_union)

    # Process the symbols
    df_hugo = orchestrated_fetch(symbol_union, selected_manipulations)
    df_symbols = ingest_symbols(df_hugo, symbols)

    G = create_graph(df_symbols)

    graph_manipulations = [
        remove_self_edges,
        remove_loose_ends,
        resolve_unapproved,
        aggregate_approved,
    ]

    for manipulation in graph_manipulations:
        # Apply the manipulation to the graph
        G = manipulation(G)

    return G
