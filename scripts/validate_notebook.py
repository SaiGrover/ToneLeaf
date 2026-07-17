"""Validate Toneleaf's executed notebook without trusting embedded output text."""

from __future__ import annotations

import ast
import json
from pathlib import Path


NOTEBOOK = Path("notebooks/Toneleaf_Sentiment_Analysis.ipynb")


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    for index, cell in enumerate(code_cells, start=1):
        ast.parse("".join(cell["source"]), filename=f"code-cell-{index}")

    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    executed = sum(cell.get("execution_count") is not None for cell in code_cells)
    assert notebook["nbformat"] == 4
    assert executed == len(code_cells), "Every code cell must have current output"
    assert not errors, f"Notebook contains {len(errors)} execution error(s)"

    print(f"Notebook JSON valid: {NOTEBOOK.name}")
    print(f"Code cells parsed: {len(code_cells)}")
    print(f"Executed code cells: {executed}/{len(code_cells)}")
    print("Output errors: 0")


if __name__ == "__main__":
    main()
