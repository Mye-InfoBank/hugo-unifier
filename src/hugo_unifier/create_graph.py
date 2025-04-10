import pandas as pd
import networkx as nx
from typing import Dict, List


def create_graph(df: pd.DataFrame, sample_symbols: Dict[str, List[str]]) -> nx.DiGraph:
    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_node(row["input"], type="input", samples=set())
        G.add_node(row["approvedSymbol"], type="approvedSymbol", samples=set())
        G.add_node(row["original"], type="original", samples=set())

    # For each node, if it does not have the samples attribute, set it to empty
    for sample, symbols in sample_symbols.items():
        for symbol in symbols:
            if symbol not in G.nodes:
                continue
            G.nodes[symbol]["samples"].add(sample)

    for approved_symbol in df["approvedSymbol"].unique():
        # Set type to "approvedSymbol" for all nodes with this symbol
        G.nodes[approved_symbol]["type"] = "approvedSymbol"

    for _, row in df[df["resolution"] != "identity"].iterrows():
        G.add_edge(row["original"], row["input"], type=row["resolution"])

    for match_type in df["matchType"].unique():
        for _, row in df[df["matchType"] == match_type].iterrows():
            G.add_edge(row["input"], row["approvedSymbol"], type=match_type)

    return G
