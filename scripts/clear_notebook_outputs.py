"""Explicitly clear source outputs before committing; never run silently in CI."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from esiilfire.notebooks import clear_execution

for source in sorted((ROOT / "notebooks").glob("*.ipynb")):
    notebook = json.loads(source.read_text(encoding="utf-8"))
    before = json.dumps(notebook, ensure_ascii=False)
    clear_execution(notebook)
    if json.dumps(notebook, ensure_ascii=False) != before:
        source.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
                          encoding="utf-8", newline="\n")
        print("Cleared:", source.name)
    else:
        print("Already clean:", source.name)
