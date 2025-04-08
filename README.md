# hugo-unifier

This python package can unify gene symbols based on the [HUGO database](https://www.genenames.org/tools/multi-symbol-checker/).

## Installation

The package can be installed via pip, or any other Python package manager.

```bash
pip install hugo-unifier
```

## Usage

The package can be used both as a command line tool and as a library.

### Command Line Tool

Currently, the command line tool only supports unifying the entries of a column in an AnnData objects `var` attribute. The input file and column name must be passed as an argument. The tool will update the column in place and save the AnnData object to a new file.

Check the help message for more information:
```bash
hugo-unifier --help
```

### Library
The package can be used as a library to unify gene symbols in a pandas DataFrame. The `unify` function takes a list of gene symbols and returns a list of unified gene symbols. The function can be used as follows:

```python
from hugo_unifier import unify
gene_symbols = ["TP53", "BRCA1", "EGFR"]
unified_symbols = unify(gene_symbols)
print(unified_symbols)
```

## How it works

Different datasets sometimes use different gene symbols for the same gene. Sometimes, the same gene symbol occurs
with slight modifications, such as dashes, underscores, or other characters. The `hugo-unifier` iteratively applies attempts to manipulate the gene symbols and check them against the HUGO database.

The following manipulations are applied in the following order:
1. `identity`: Use the gene symbol as is.
2. `dot-to-dash`: Replace dots with dashes.
3. `discard-after-dot`: Discard everything after the first dot.

More conservative manipulations are applied first. The first manipulation that returns a valid gene symbol is used.

### Resolution of aliases

When resolving aliases, the following steps are applied:

1. **Remove Conflicting Aliases**:  
   Aliases that conflict with already approved symbols are removed. For example, if an alias maps to a symbol that is already approved, it is discarded to avoid conflicts.

2. **Correct Same Aliases**:  
   If an alias maps to the same symbol as its original symbol, it is corrected and marked as an approved symbol. This ensures that aliases that are effectively the same as the original symbol are treated as valid.

3. **Handle Duplicate Aliases**:  
   If multiple aliases map to the same original symbol:
   - By default, only one alias is retained, and the rest are discarded.
   - If the `keep_gene_multiple_aliases` option is enabled, all aliases are retained, and an identity mapping is created for the duplicates.

4. **Unaccepted Aliases**:  
   Any aliases that cannot be resolved or conflict with the above rules are marked as unaccepted and excluded from the final results.

These steps ensure that aliases are resolved in a consistent and conflict-free manner, prioritizing approved symbols and avoiding ambiguity in the mapping process.
