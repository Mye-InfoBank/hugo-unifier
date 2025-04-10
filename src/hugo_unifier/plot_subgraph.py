import networkx as nx
import matplotlib.pyplot as plt


def plot_symbol_subgraph(G: nx.DiGraph, symbol: str):
    """
    Plot the subgraph containing the symbol and its related nodes.
    Args:
        G (nx.DiGraph): The directed graph containing the symbol.
        symbol (str): The symbol to plot.
    """

    components = list(nx.weakly_connected_components(G))
    component = next((c for c in components if symbol in c), None)
    if component is None:
        print(f"Symbol '{symbol}' not found in any connected component.")
        return

    plot_subgraph(G.subgraph(component))


def plot_subgraph(subgraph):
    pos = nx.spring_layout(subgraph)

    # Extract edge labels from "type" attribute
    edge_labels = {(u, v): d["type"] for u, v, d in subgraph.edges(data=True)}

    TYPE_COLORS = {
        "original": "lightblue",
        "input": "salmon",
        "approvedSymbol": "lightgreen",
    }

    def create_composite_label(node, attr):
        """Combine node ID and tools list into a multi-line label"""
        tools_str = "\n".join(attr["samples"]) if attr["samples"] else "No samples"
        return f"{node}\n{tools_str}"

    node_colors = [TYPE_COLORS[subgraph.nodes[n]["type"]] for n in subgraph.nodes]
    node_sizes = [100 + 300 * len(subgraph.nodes[n]["samples"]) for n in subgraph.nodes]

    labels = {n: create_composite_label(n, subgraph.nodes[n]) for n in subgraph.nodes}

    plt.figure()
    nx.draw(
        subgraph,
        pos,
        with_labels=True,
        labels=labels,
        node_color=node_colors,
        node_size=node_sizes,
        edge_color="gray",
        arrows=True,
        arrowsize=20,
    )

    # Draw edge labels
    nx.draw_networkx_edge_labels(
        subgraph,
        pos,
        edge_labels=edge_labels,
        font_size=10,
        font_color="red",
        label_pos=0.5,
        rotate=False,
    )

    # Add some padding
    plt.margins(0.3)
