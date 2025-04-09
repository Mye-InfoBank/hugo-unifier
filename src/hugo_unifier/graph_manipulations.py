import networkx as nx
import pandas as pd
from typing import List


def remove_self_edges(G: nx.DiGraph) -> None:
    # Remove all self edges
    for node in G.nodes():
        if G.has_edge(node, node):
            G.remove_edge(node, node)


def remove_loose_ends(G: nx.DiGraph) -> None:
    # Remove all approved nodes that only have one incoming edge, whose source is also approved
    for node in G.nodes():
        if G.nodes[node]["type"] != "approvedSymbol":
            continue
        if len(G.nodes[node]["samples"]) > 0:
            continue
        in_edges = list(G.in_edges(node))
        if len(in_edges) > 1:
            continue
        source_node = in_edges[0][0]
        if G.nodes[source_node]["type"] != "approvedSymbol":
            continue
        G.remove_edge(source_node, node)


def __decide_successor__(G: nx.DiGraph, successors: List[str]):
    if len(successors) == 1:
        return successors[0]

    successor_samples = {
        successor: G.nodes[successor]["samples"] for successor in successors
    }
    nonempty_successors = {
        successor: samples
        for successor, samples in successor_samples.items()
        if len(samples) > 0
    }

    if len(nonempty_successors) == 1:
        return list(nonempty_successors)[0]
    if len(nonempty_successors) > 1:
        print("Collision")
    return None


def resolve_unapproved(G: nx.DiGraph, df: pd.DataFrame) -> None:
    for node in list(G.nodes()):
        if G.nodes[node]["type"] == "approvedSymbol":
            continue

        successor = __decide_successor__(G, list(G.successors(node)))

        if successor is None:
            continue

        node_samples = G.nodes[node]["samples"]
        successor_samples = G.nodes[successor]["samples"]
        has_intersection = len(node_samples.intersection(successor_samples)) > 0

        G.nodes[successor]["samples"].update(node_samples)
        if not has_intersection:
            # Delete node
            G.remove_node(node)


def aggregate_approved(G: nx.DiGraph, df: pd.DataFrame) -> None:
    marks = []

    for node in list(G.nodes()):
        if G.nodes[node]["type"] != "approvedSymbol":
            continue
        predecessors = list(G.predecessors(node))

        if len(predecessors) == 0:
            continue

        predecessor_samples = {
            predecessor: G.nodes[predecessor]["samples"] for predecessor in predecessors
        }

        union = G.nodes[node]["samples"].copy()
        largest_subset = G.nodes[node]["samples"]
        for samples in predecessor_samples.values():
            union.update(samples)
            if len(samples) > len(largest_subset):
                largest_subset = samples

        if len(union) == 0:
            continue

        improvement_ratio = len(union) / len(largest_subset)
        if improvement_ratio < 1.5:
            continue

        marks.append(node)

    for mark in marks:
        predecessors = list(G.predecessors(mark))
        if any([predecessor in marks for predecessor in predecessors]):
            raise ValueError("Conflict")

        union = G.nodes[node]["samples"]
        for predecessor in predecessors:
            union.update(G.nodes[predecessor]["samples"])
