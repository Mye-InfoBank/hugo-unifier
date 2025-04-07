def identity(symbol: str) -> str:
    """
    Return the symbol unchanged.
    """
    return symbol

def discard_after_dot(symbol: str) -> str:
    """
    Discard any text after the last dot in a symbol.
    """
    return symbol.split(".")[0]

def dot_to_dash(symbol: str) -> str:
    """
    Replace any dots in a symbol with dashes.
    """
    return symbol.replace(".", "-")
