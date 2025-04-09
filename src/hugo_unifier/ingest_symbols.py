import pandas as pd
from typing import Dict, List


def ingest_symbols(
    df: pd.DataFrame, sample_symbols: Dict[str, List[str]]
) -> pd.DataFrame:
    sample_dfs = []

    for sample, symbols in sample_symbols.items():
        # Create a DataFrame for each sample
        sample_df = pd.DataFrame(columns=["original", "sample"])
        sample_df["original"] = symbols
        sample_df["sample"] = sample
        sample_dfs.append(sample_df)

    df_samples = (
        pd.concat(sample_dfs, ignore_index=True)
        .groupby("original")
        .agg(lambda x: list(set(x)))
        .reset_index()
    )

    return df.merge(df_samples, on="original")
