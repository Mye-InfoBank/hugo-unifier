from hugo_unifier.hugo_fetch import fetch_symbol_check_results


def test_cox1():
    symbols = ["COX1", "MT-CO1"]

    df = fetch_symbol_check_results(symbols)
    assert len(df) == 3
