from typing import Callable, Dict


def identity(symbol: str) -> str:
    """
    Return the symbol unchanged.
    """
    return symbol


def discard_after_dot(symbol: str) -> str:
    """
    Discard any text after the first dot in a symbol.
    """
    return symbol.split(".")[0]


def dot_to_dash(symbol: str) -> str:
    """
    Replace any dots in a symbol with dashes.
    """
    return symbol.replace(".", "-")


manipulation_mapping: Dict[str, Callable[[str], str]] = {
    "identity": identity,
    "discard_after_dot": discard_after_dot,
    "dot_to_dash": dot_to_dash,
}
