from typing import Dict, List, Tuple, Union, Callable
import pandas as pd
import networkx as nx

from hugo_unifier.symbol_manipulations import manipulation_mapping
from hugo_unifier.orchestrated_fetch import orchestrated_fetch
from hugo_unifier.create_graph import create_graph
from hugo_unifier.graph_manipulations import (
    remove_self_edges,
    remove_loose_ends,
    resolve_unapproved,
)


def get_changes(
    symbols: Dict[str, List[str]],
    manipulations: List[str] = ["identity", "dot_to_dash", "discard_after_dot"],
) -> Union[List[str], Tuple[List[str], Dict[str, int]]]:
    """
    Unify gene symbols in a list of symbols.

    Parameters
    ----------
    symbols : List[str]
        List of gene symbols to unify.
    manipulations : List[str]
        List of manipulation names to apply.

    Returns
    -------
    Sample changes : Dict[str, pd.DataFrame]
        Dictionary of sample changes, where the key is the sample name and the value is a DataFrame with the changes.
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

    G = create_graph(df_hugo, symbols)
    remove_self_edges(G)
    remove_loose_ends(G)

    graph_manipulations: List[Callable[[nx.DiGraph, pd.DataFrame]]] = [
        resolve_unapproved,
        # aggregate_approved,
    ]

    df_changes = pd.DataFrame(columns=["sample", "action", "symbol", "new", "reason"])

    for manipulation in graph_manipulations:
        # Apply the manipulation to the graph
        manipulation(G, df_changes)

    sample_changes = {
        sample: df_changes[df_changes["sample"] == sample]
        .copy()
        .drop(["sample"], axis=1)
        for sample in symbols.keys()
    }

    return G, sample_changes
