import json
from . import ROOT
def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))
def cases(): return load_json("data/public/cases.json")
def sources(): return load_json("data/public/sources.json")
def history_manifest(): return load_json("data/processed/history_manifest.json")
