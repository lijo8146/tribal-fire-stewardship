"""Keep shareable notebook sources separate from local execution results."""
import json
from pathlib import Path

def clear_execution(notebook):
    """Remove execution results/metadata in place, preserving code and prose."""
    notebook.get("metadata", {}).pop("widgets", None)
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
            for key in ["execution", "ExecuteTime", "collapsed", "scrolled"]:
                cell.get("metadata", {}).pop(key, None)
    return notebook

def check_clean_notebook(path):
    path = Path(path)
    notebook = json.loads(path.read_text(encoding="utf-8"))
    dirty = [
        str(index) for index, cell in enumerate(notebook["cells"], 1)
        if cell["cell_type"] == "code"
        and (cell.get("outputs") or cell.get("execution_count") is not None)
    ]
    if dirty or "widgets" in notebook.get("metadata", {}):
        detail = "code cells " + ", ".join(dirty) if dirty else "widget metadata"
        raise ValueError(
            f"{path.name}: saved execution state ({detail}). "
            "Run python scripts/clear_notebook_outputs.py before committing. "
            "Executed copies belong in ignored work/; private observations must stay local."
        )
