"""Tests to ensure output reproducibility via hash comparison."""

import hashlib

import anndata as ad
import pandas as pd

from hugo_unifier import get_changes, apply_changes


def compute_file_hash(file_path) -> str:
    """Compute SHA256 hash of a file's contents."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()


def compute_dataframe_hash(df) -> str:
    """Compute SHA256 hash of a DataFrame's CSV representation."""
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(csv_bytes).hexdigest()


def compute_adata_hash(adata) -> str:
    """Compute SHA256 hash of an AnnData object's key components."""
    # Hash the var index (gene names) which is what apply_changes modifies
    var_index_bytes = ",".join(sorted(adata.var.index.tolist())).encode("utf-8")
    return hashlib.sha256(var_index_bytes).hexdigest()


# Expected hashes for get_changes output CSV files
EXPECTED_GET_HASHES = {
    "boland-b": "c59f0ef6de4569991c98d566997522bb2ccb267b5f0956b79a7cf6ce1bdfb8e8",
    "devlin": "2a2e77fbbeb6d4145a17c7047068ab2f768c2356ee9c25f4971689066ff0813d",
    "elmentaite": "3d864788afa6a6d76323509644fc11ee839cca587ae65ca79376bd703af07b16",
    "garrido": "89a769618e119c6c6266c445b4de83c0570502264c9bfa87b0e60ac668ab52e0",
    "kinchen": "cd88f69372ca0cb92f8ff552dedbc9e8275d29819540980a8d4eee8ba5332e1b",
    "kong": "9a5edb3d886c98bda3051e238311573d8e2e279343acdbcae465b341302dfe50",
    "korsunsky": "ec3af0d99c70dbf399d828c28c2cc2016883245629cdd3a8e087bf9e91307a6a",
    "martin": "cd88f69372ca0cb92f8ff552dedbc9e8275d29819540980a8d4eee8ba5332e1b",
    "parikh": "cd88f69372ca0cb92f8ff552dedbc9e8275d29819540980a8d4eee8ba5332e1b",
    "smillie": "7b3331e6048bdd00ac9df595db2df616e3fb581ddd7f7651c16e6fac5ca4e421",
    "unpublished": "7900e44e6f7d66d51911101e172b705e25a45948e642640d5a7fd59972839f93",
    "uzzan": "47879f2650f5ce18efe1e292667fc71288ae03c14b0e99855a64be523a75a8ba",
}

# Expected hash for apply_changes output (uzzan dataset)
EXPECTED_APPLY_HASH = "2cbe8133760e35e224714a1a4dc73623cd482da3fdd71a96c0ffad9fbfbd215e"


def test_get_changes_hash_stability(test_h5ad_objects, test_h5ad_paths):
    """
    Test that get_changes produces stable output across compute environments.
    
    This test runs get_changes once and compares the output hashes against
    saved expected hashes to ensure reproducibility across different machines.
    """
    # Build symbols dict from test data (sorted for deterministic order)
    sorted_paths = sorted(test_h5ad_paths)
    symbols_dict = {}
    for path in sorted_paths:
        # Find the matching adata object
        idx = list(test_h5ad_paths).index(path)
        adata = test_h5ad_objects[idx]
        symbols_dict[path.stem] = adata.var.index.tolist()
    
    # Run get_changes once
    _, sample_changes = get_changes(symbols_dict)
    
    # Compare hashes against expected values
    mismatches = []
    actual_hashes = {}
    
    for sample_name, expected_hash in EXPECTED_GET_HASHES.items():
        if sample_name not in sample_changes:
            mismatches.append(f"{sample_name}: not found in output")
            continue
        
        df = sample_changes[sample_name]
        actual_hash = compute_dataframe_hash(df)
        actual_hashes[sample_name] = actual_hash
        
        if actual_hash != expected_hash:
            mismatches.append(
                f"{sample_name}: expected {expected_hash}, got {actual_hash}"
            )
    
    if mismatches:
        # Print all actual hashes for easy updating
        print("\n\nActual hashes (copy to update EXPECTED_GET_HASHES):")
        print("EXPECTED_GET_HASHES = {")
        for name in sorted(actual_hashes.keys()):
            print(f'    "{name}": "{actual_hashes[name]}",')
        print("}")
        
        assert False, "Hash mismatches found:\n" + "\n".join(mismatches)


def test_apply_changes_hash_stability(uzzan_h5ad, uzzan_csv):
    """
    Test that apply_changes produces stable output across compute environments.
    
    This test runs apply_changes once and compares the output hash against
    a saved expected hash to ensure reproducibility across different machines.
    """
    # Load the test AnnData object and changes
    adata = ad.read_h5ad(uzzan_h5ad)
    df_changes = pd.read_csv(uzzan_csv)
    
    # Apply the changes
    updated_adata = apply_changes(adata, df_changes)
    
    # Compute hash of the result
    actual_hash = compute_adata_hash(updated_adata)
    
    if actual_hash != EXPECTED_APPLY_HASH:
        print("\n\nActual hash (copy to update EXPECTED_APPLY_HASH):")
        print(f'EXPECTED_APPLY_HASH = "{actual_hash}"')
        
        assert False, (
            f"Hash mismatch for apply_changes output:\n"
            f"  expected: {EXPECTED_APPLY_HASH}\n"
            f"  got: {actual_hash}"
        )
