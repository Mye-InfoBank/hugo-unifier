from hugo_unifier import get_changes


def test_cox1():
    sample_symbols = {"sample1": ["COX1"], "sample2": ["MT-CO1"]}

    _, sample_changes = get_changes(sample_symbols)
    assert len(sample_changes) == 2

    sample1_changes = sample_changes["sample1"]
    assert len(sample1_changes) == 1
    assert sample1_changes.iloc[0]["action"] == "rename"
    assert sample1_changes.iloc[0]["symbol"] == "COX1"
    assert sample1_changes.iloc[0]["new"] == "MT-CO1"

    sample2_changes = sample_changes["sample2"]
    assert len(sample2_changes) == 0


def test_cox1_and_co1():
    sample_symbols = {"sample1": ["COX1"], "sample2": ["MT-CO1", "COX1"]}

    _, sample_changes = get_changes(sample_symbols)
    assert len(sample_changes) == 2

    sample1_changes = sample_changes["sample1"]
    assert len(sample1_changes) == 1
    assert sample1_changes.iloc[0]["action"] == "copy"
    assert sample1_changes.iloc[0]["symbol"] == "COX1"
    assert sample1_changes.iloc[0]["new"] == "MT-CO1"

    sample2_changes = sample_changes["sample2"]
    assert len(sample2_changes) == 0


def test_single_sample():
    sample_symbols = {"sample1": ["COX1"]}

    _, sample_changes = get_changes(sample_symbols)
    assert len(sample_changes) == 1

    sample1_changes = sample_changes["sample1"]
    # This does not change, because COX1 could refer to PTGS1 or MT-CO1
    # And we do not have another sample to base the decision on
    assert len(sample1_changes) == 0


def test_meg8():
    sample_symbols = {
        "sample1": ["MEG8", "AL132709.8", "SNHG24", "SNHG23"],
        "sample2": ["MEG8", "AL132709.8"],
    }

    G, sample_changes = get_changes(sample_symbols)
    assert len(sample_changes) == 2

    meg8_node = G.nodes["MEG8"]
    assert len(meg8_node["samples"]) == 2

    sample1_changes = sample_changes["sample1"]
    assert len(sample1_changes) == 0
