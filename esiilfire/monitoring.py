"""Paired before/after contrasts. No observations are bundled with the site."""
import numpy as np
import pandas as pd
REQUIRED = ["pair_id", "unit_id", "role", "period", "observed_at", "indicator", "value", "unit", "method", "quality_flag"]

def paired_changes(frame):
    missing = set(REQUIRED) - set(frame.columns)
    if missing: raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    if frame.empty: raise ValueError("No observations supplied; no contrast can be estimated")
    f = frame.copy()
    if f[REQUIRED].isna().any().any(): raise ValueError("Missing observation fields")
    if not f.role.isin(["treated", "comparison"]).all() or not f.period.isin(["before", "after"]).all():
        raise ValueError("Roles must be treated/comparison and periods before/after")
    if not f.quality_flag.eq("accepted").all(): raise ValueError("Resolve all quality flags before estimation")
    for column in ["indicator", "unit", "method"]:
        if f[column].nunique() != 1: raise ValueError("Analyze one indicator, unit and method at a time")
    for column in REQUIRED:
        if column != "value" and f[column].astype(str).str.strip().eq("").any():
            raise ValueError("Blank observation fields")
    f["value"] = pd.to_numeric(f.value, errors="raise")
    if not np.isfinite(f.value).all(): raise ValueError("Observation values must be finite")
    f["observed_at"] = pd.to_datetime(f.observed_at, errors="raise", utc=True)
    if f.duplicated(["pair_id", "role", "period"]).any(): raise ValueError("Supply one predeclared aggregate per unit-period; duplicate cells found")
    if (f.groupby("unit_id").pair_id.nunique() > 1).any(): raise ValueError("A comparison or treated unit cannot be reused across independent pairs")
    rows = []
    cells = {(r,p) for r in ["treated","comparison"] for p in ["before","after"]}
    for pair, group in f.groupby("pair_id", sort=True):
        if set(zip(group.role, group.period)) != cells: raise ValueError(f"Pair {pair} needs all four role-period cells")
        if group.unit_id.nunique() != 2 or (group.groupby("role").unit_id.nunique() != 1).any():
            raise ValueError(f"Pair {pair} requires two distinct and stable units")
        for role, observations in group.groupby("role"):
            dates = observations.set_index("period").observed_at
            if not dates["before"] < dates["after"]: raise ValueError(f"Pair {pair} has invalid observation order")
        values = group.set_index(["role", "period"]).value
        treated = float(values["treated", "after"] - values["treated", "before"])
        comparison = float(values["comparison", "after"] - values["comparison", "before"])
        rows.append({"pair_id":pair,"treated_change":treated,"comparison_change":comparison,"paired_contrast":treated-comparison})
    return pd.DataFrame(rows)

def summarize_pairs(changes, seed=2026):
    values = changes.paired_contrast.to_numpy(dtype=float)
    if not len(values) or not np.isfinite(values).all(): raise ValueError("No finite pair contrasts")
    result = {"independent_pairs":len(values),"mean_contrast":float(values.mean()),"median_contrast":float(np.median(values)),"interval":None}
    if len(values) >= 10:
        rng = np.random.default_rng(seed)
        means = rng.choice(values, size=(2000,len(values)), replace=True).mean(axis=1)
        result["interval"] = np.quantile(means,[0.025,0.975]).tolist()
    result["interpretation"] = "Descriptive paired contrast. A pair bootstrap interval is provided only for 10+ independently selected pairs."
    return result
