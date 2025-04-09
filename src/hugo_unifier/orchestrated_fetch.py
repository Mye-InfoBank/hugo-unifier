import pandas as pd
from typing import Callable, List, Tuple
from hugo_unifier.hugo_fetch import fetch_symbol_check_results


def fetch_manipulation(
    original_symbols: List[str], manipulation: Callable[[str], str]
) -> pd.DataFrame:
    df_manipulation = pd.DataFrame(original_symbols, columns=["original"])
    df_manipulation["input"] = df_manipulation["original"].apply(manipulation)

    df_result = fetch_symbol_check_results(df_manipulation["input"].tolist())

    df = df_manipulation.merge(df_result, how="inner", on="input")
    df = df[
        df["matchType"].isin(["Approved symbol", "Previous symbol", "Alias symbol"])
    ]
    return df


def orchestrated_fetch(
    original_symbols: List[str], manipulations: List[Tuple[str, Callable[[str], str]]]
) -> pd.DataFrame:
    results = []
    remaining_symbols = original_symbols
    for name, manipulation in manipulations:
        # If no symbols remain, break the loop
        if not remaining_symbols:
            break

        df = fetch_manipulation(remaining_symbols, manipulation)

        # Remove values in df["input"] from remaining_symbols
        remaining_symbols = [
            symbol
            for symbol in remaining_symbols
            if symbol not in df["original"].values
        ]

        df["resolution"] = name
        results.append(df)

    # Concatenate all results into a single DataFrame
    df_final = pd.concat(results, ignore_index=True)
    return df_final
