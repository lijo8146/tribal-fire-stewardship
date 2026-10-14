"""Public-source build checks. Partner monitoring outputs are never auto-published."""
import json
import pandas as pd
import geopandas as gpd
from . import ROOT
from .history import digest,TYPES
from .io import cases,sources,history_manifest

def validate_public(root=ROOT):
    root=__import__("pathlib").Path(root)
    for source_path in root.rglob("*"):
        if not source_path.is_file() or any(part in source_path.parts for part in [".git","work","_site",".quarto","__pycache__","private","raw"]):continue
        if source_path.suffix not in {".qmd",".py",".md",".json",".yml",".ipynb"}:continue
        text=source_path.read_text(encoding="utf-8-sig")
        markers=["\u00c2\u00b7","\u00e2\u20ac","\ufffd"]
        if any(marker in text for marker in markers):raise ValueError("Encoding artifact in "+str(source_path))
    registry=json.loads((root/"data/public/sources.json").read_text(encoding="utf-8"))
    ids=[s["id"] for s in registry]
    if len(ids)!=len(set(ids)):raise ValueError("Duplicate source identifiers")
    for source in registry:
        if not source["url"].startswith("https://") or not source.get("reviewed_on"):raise ValueError("Source lacks provenance")
    profiles=json.loads((root/"data/public/cases.json").read_text(encoding="utf-8"))
    if len({c["id"] for c in profiles}) != len(profiles): raise ValueError("Duplicate case identifiers")
    for case in profiles:
        if not set(case["sources"]).issubset(ids):raise ValueError("Case cites an unknown source")
        if not case["relationship"] or not case["question"]:raise ValueError("Case must distinguish evidence and proposed participation")
    m=json.loads((root/"data/processed/history_manifest.json").read_text(encoding="utf-8"))
    if m.get("mode")!="real_public_data" or not m.get("source_files"):raise ValueError("History requires a real snapshot and source hashes")
    import yaml
    configured=yaml.safe_load((root/"project.yml").read_text(encoding="utf-8"))["regions"]
    if set(m["regions"])!=set(configured):raise ValueError("Regional outputs do not match the declared study windows")
    allowed={"history_manifest.json"}
    for key,region in m["regions"].items():
        expected_files={f"history_{key}.csv",f"history_{key}.geojson"}
        if set(region["files"])!=expected_files:raise ValueError("Unexpected regional output inventory")
        if region["bounds"]!=configured[key]["bbox"]:raise ValueError("Regional bounds do not match the project configuration")
        allowed.update(region["files"])
        for filename in region["files"]:
            path=(root/"data/processed"/filename).resolve()
            if path.parent!=(root/"data/processed").resolve() or digest(path)!=m["product_sha256"][filename]:raise ValueError("Missing, changed or unsafe history product")
        annual=pd.read_csv(root/"data/processed"/f"history_{key}.csv")
        if len(annual)!=(m["end_year"]-m["start_year"]+1)*len(TYPES):raise ValueError("Annual table is incomplete")
        if annual.duplicated(["year","type"]).any() or not annual.year.between(m["start_year"],m["end_year"]).all() or not annual["type"].isin(TYPES).all():raise ValueError("Invalid annual table cells")
        if (annual.mapped_events<0).any() or (annual.acres_in_window<0).any():raise ValueError("Negative history values")
        if int(annual.mapped_events.sum())!=region["mapped_events"]:raise ValueError("Summary counts do not reconcile")
        features=gpd.read_file(root/"data/processed"/f"history_{key}.geojson")
        if len(features)!=region["mapped_events"] or (len(features) and features.event_id.duplicated().any()):raise ValueError("Event count or uniqueness failure")
        if region["by_type"]!={kind:int(features["type"].eq(kind).sum()) if len(features) else 0 for kind in TYPES}:raise ValueError("Incident type counts do not reconcile")
        if len(features) and not features.geometry.is_valid.all():raise ValueError("Invalid display geometry")
    unexpected={p.name for p in (root/"data/processed").iterdir()}-allowed
    if unexpected:raise ValueError("Unexpected public outputs: "+", ".join(sorted(unexpected)))
    expected_notebooks={"01_questions_and_authority.ipynb","02_fire_history_and_limits.ipynb","03_stewardship_and_exchange.ipynb","04_monitoring_outcomes.ipynb"}
    if {p.name for p in (root/"notebooks").glob("*.ipynb")}!=expected_notebooks:raise ValueError("Expected four clean research notebooks")
    for notebook in (root/"notebooks").glob("*.ipynb"):
        n=json.loads(notebook.read_text(encoding="utf-8"))
        if any(c.get("outputs") for c in n["cells"] if c["cell_type"]=="code"):raise ValueError("Clear notebook outputs before sharing; private observations must stay local")
    return m
