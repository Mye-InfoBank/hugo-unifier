import networkx as nx
import pandas as pd


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


def __decide_successor__(G: nx.DiGraph, node: str, df: pd.DataFrame) -> str:
    successors = list(G.successors(node))

    if len(successors) == 1:
        return successors[0]

    node_samples = G.nodes[node]["samples"]

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
        df.loc[len(df)] = [
            None,
            "conflict",
            node,
            None,
            f"The unapproved symbol {node} is present in {node_samples} and has multiple connections to approved symbols, and multiple of them are present in samples: {', '.join([f'{successor} ({samples}' for successor, samples in nonempty_successors.items()])}. We cannot decide which one to use.",
        ]
    return None


def resolve_unapproved(G: nx.DiGraph, df: pd.DataFrame) -> pd.DataFrame:
    for node in list(G.nodes()):
        if G.nodes[node]["type"] == "approvedSymbol":
            continue

        successor = __decide_successor__(G, node, df)
        if successor is None:
            continue

        node_samples = G.nodes[node]["samples"]
        successor_samples = G.nodes[successor]["samples"]
        edge_type = G[node][successor]["type"]

        has_overlap = len(node_samples & successor_samples) > 0
        global_action = "copy" if has_overlap else "rename"

        for sample in node_samples:
            if sample in successor_samples:
                # The sample already has both symbols → conflict
                df.loc[len(df)] = [
                    sample,
                    "conflict",
                    node,
                    successor,
                    f"Conflict: both {node} and {successor} are present in sample {sample}. Skipping change.",
                ]
                continue

            # If safe: apply rename or copy depending on global situation
            df.loc[len(df)] = [
                sample,
                global_action,
                node,
                successor,
                f"{edge_type.capitalize().replace('_', ' ')}, {global_action} from {node} to {successor} in sample {sample}.",
            ]
            G.nodes[successor]["samples"].add(sample)

        # If all samples are now transferred, remove node
        if G.nodes[node]["samples"].issubset(G.nodes[successor]["samples"]):
            G.remove_node(node)



def aggregate_approved(G: nx.DiGraph, df: pd.DataFrame) -> pd.DataFrame:
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
        intersection = set(predecessors).intersection(marks)
        if len(intersection) > 0:
            df.loc[len(df)] = [
                None,
                "conflict",
                mark,
                None,
                f"The approved symbol {mark} could increase the overlap by pulling in other symbols ({predecessors}), however at least one of the other symbols ({intersection}) would also perform this operation. Two-level aggregation is not currently not supported.",
            ]

        for predecessor in predecessors:
            G.nodes[node]["samples"].update(G.nodes[predecessor]["samples"])
            edge_type = G[predecessor][mark]["type"]

            for sample in G.nodes[predecessor]["samples"]:
                if sample in G.nodes[mark]["samples"]:
                    df.loc[len(df)] = [
                        sample,
                        "conflict",
                        predecessor,
                        mark,
                        f"Conflict: both {predecessor} and {mark} are present in sample {sample}. Cannot aggregate.",
                    ]
                    continue

                
                df.loc[len(df)] = [
                    sample,
                    "copy",
                    predecessor,
                    mark,
                    f"{predecessor} is a {G.nodes[predecessor]['type']} and also a {edge_type} of {mark}. Copying because it improves overlap (> 50%).",
                ]