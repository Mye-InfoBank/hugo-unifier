import requests
import pandas as pd
from typing import List


# Assume fetch_symbol_check_results remains the same as provided
def fetch_symbol_check_results(symbols: List[str]) -> pd.DataFrame:
    """
    Fetch symbol check results from the genenames.org API.

    Args:
        symbols (List[str]): List of gene symbols to check.

    Returns:
        pd.DataFrame: DataFrame containing the API response. Includes columns
                    like 'input', 'matchType', 'approvedSymbol', 'location'.
                    Returns an empty DataFrame if the input list is empty or
                    if the API call fails silently (though it tries to raise status).
                    Note: The API might return multiple rows for a single input
                    symbol if multiple match types are found.
    """
    if not symbols:
        # Return an empty DataFrame with expected columns if no symbols are provided
        return pd.DataFrame(
            columns=["input", "matchType", "approvedSymbol", "location"]
        )  # Add other relevant columns if known

    assert all(isinstance(symbol, str) and symbol for symbol in symbols)

    url = "https://www.genenames.org/cgi-bin/tools/symbol-check"
    # Ensure data payload is correctly structured for the POST request
    data = [
        ("approved", "true"),
        ("case", "insensitive"),
        (
            "output",
            "json",
        ),  # Changed output to json for easier parsing with pd.DataFrame
        *[
            ("queries[]", symbol) for symbol in set(symbols)
        ],  # Use set to avoid duplicates
        ("synonyms", "true"),
        ("unmatched", "true"),  # Include symbols that didn't match anything
        ("withdrawn", "true"),
        ("previous", "true"),
    ]
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
        # It seems the API returns JSON directly, suitable for pd.DataFrame
        # Handle potential empty response or non-JSON response
        try:
            # The actual data is typically nested under a key, often 'response' or similar
            # Inspect the actual API response structure if this fails.
            # Assuming the JSON response is a list of records:
            results = response.json()
            if (
                isinstance(results, dict) and "results" in results
            ):  # Adjust 'results' if the key is different
                return pd.DataFrame(results["results"])
            elif isinstance(results, list):
                return pd.DataFrame(results)
            else:
                # Handle unexpected JSON structure
                print(f"Warning: Unexpected JSON structure from API: {results}")
                return pd.DataFrame(
                    columns=["input", "matchType", "approvedSymbol", "location"]
                )

        except (
            ValueError,
            TypeError,
        ) as e:  # Catches JSONDecodeError and potential type issues
            print(f"Warning: Could not decode JSON response or invalid format: {e}")
            return pd.DataFrame(
                columns=["input", "matchType", "approvedSymbol", "location"]
            )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching symbol check results: {e}")
        # Return an empty DataFrame on request failure
        return pd.DataFrame(
            columns=["input", "matchType", "approvedSymbol", "location"]
        )
