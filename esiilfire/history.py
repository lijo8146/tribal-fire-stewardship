"""Regional summaries of a public MTBS perimeter snapshot, with explicit coverage."""
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
from pyproj import Transformer
from shapely.geometry import box
from shapely import make_valid, set_precision
from . import ROOT

FIELDS = ["Event_ID","Incid_Name","Incid_Type","Ig_Date"]
TYPES = ["Wildfire","Prescribed Fire","Wildland Fire Use","Unknown"]
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def normalize_events(frame):
    if frame.crs is None: raise ValueError("Perimeters lack a coordinate reference system")
    if not set(FIELDS).issubset(frame.columns): raise ValueError("Unexpected MTBS perimeter schema")
    f=frame[FIELDS+["geometry"]].copy().to_crs(4326)
    f=f.rename(columns={"Event_ID":"event_id","Incid_Name":"name","Incid_Type":"type","Ig_Date":"date"})
    if f.event_id.isna().any() or f.event_id.astype(str).str.strip().eq("").any():raise ValueError("Event identifiers are missing")
    f["date"]=pd.to_datetime(f.date,errors="coerce",format="ISO8601")
    if f.date.isna().any():raise ValueError("Unparseable ignition dates; do not infer them from names")
    f["year"]=f.date.dt.year
    f["type"]=f["type"].fillna("Unknown")
    if not f["type"].isin(TYPES).all():raise ValueError("Unrecognized incident type; review the source schema")
    for field in ["year","type"]:
        if (f.groupby("event_id")[field].nunique()>1).any():raise ValueError("Conflicting versions for one event")
    f["geometry"]=f.geometry.apply(make_valid)
    if f.geometry.is_empty.any() or f.geometry.isna().any():raise ValueError("Missing perimeter geometry")
    return f.dissolve("event_id",aggfunc="first").reset_index()

def summarize_window(events,bounds,start_year,end_year):
    f=events.copy()
    f["geometry"]=f.geometry.intersection(box(*bounds))
    f=f[~f.geometry.is_empty].copy()
    f["acres_in_window"]=f.to_crs(5070).area/4046.8564224
    f=f[f.acres_in_window>0].copy()
    if not f.year.between(start_year,end_year).all():raise ValueError("Event year outside declared snapshot coverage")
    index=pd.MultiIndex.from_product([range(start_year,end_year+1),TYPES],names=["year","type"])
    annual=f.groupby(["year","type"]).agg(mapped_events=("event_id","nunique"),acres_in_window=("acres_in_window","sum")).reindex(index,fill_value=0).reset_index()
    return f,annual

def build_history(path,regions,outdir):
    path=Path(path);outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    info=pyogrio.read_info(path)
    if info["crs"] is None:raise ValueError("Source CRS is required")
    attributes=pyogrio.read_dataframe(path,read_geometry=False,columns=["Ig_Date"])
    dates=pd.to_datetime(attributes.Ig_Date,errors="coerce")
    if dates.isna().any():raise ValueError("Snapshot contains invalid dates")
    start,end=int(dates.dt.year.min()),int(dates.dt.year.max())
    if set(range(start,end+1))-set(dates.dt.year):raise ValueError("Snapshot has missing calendar years")
    transformer=Transformer.from_crs(4326,info["crs"],always_xy=True)
    result={"mode":"real_public_data","source":"MTBS burned-area perimeter snapshot","source_url":"https://www.mtbs.gov/direct-download","snapshot_observed_utc":datetime.now(timezone.utc).isoformat(),"original_download_date":"unknown","start_year":start,"end_year":end,"source_records":int(info["features"]),"source_crs":info["crs"],"source_files":{},"regions":{}}
    companions=[path] if path.suffix.lower()!=".shp" else [path.with_suffix(s) for s in ['.shp','.dbf','.shx','.prj']]
    for component in companions:
        if not component.exists():raise ValueError("Missing source component: "+component.name)
        result["source_files"][component.name]=digest(component)
    for key,region in regions.items():
        bbox=transformer.transform_bounds(*region["bbox"],densify_pts=21)
        raw=gpd.read_file(path,bbox=bbox,columns=FIELDS,engine="pyogrio")
        events=normalize_events(raw)
        clipped,annual=summarize_window(events,region["bbox"],start,end)
        # Analysis uses full geometry; map display is simplified in meters.
        display=clipped[["event_id","name","type","year","acres_in_window","geometry"]].copy()
        display["geometry"]=display.to_crs(5070).geometry.simplify(100).to_crs(4326).apply(make_valid).apply(lambda g:set_precision(g,1e-7))
        display.to_file(outdir/f"history_{key}.geojson",driver="GeoJSON",COORDINATE_PRECISION=7)
        annual.to_csv(outdir/f"history_{key}.csv",index=False,lineterminator="\n")
        roundtrip=gpd.read_file(outdir/f"history_{key}.geojson")
        if len(roundtrip)!=len(clipped) or (len(roundtrip) and (roundtrip.event_id.duplicated().any() or not roundtrip.geometry.is_valid.all())):
            raise ValueError("Serialized regional geometry failed validation")
        if int(annual.mapped_events.sum())!=len(clipped):raise ValueError("Regional annual count mismatch")
        result["regions"][key]={"label":region["label"],"bounds":region["bbox"],"mapped_events":int(len(clipped)),"by_type":{kind:int(clipped["type"].eq(kind).sum()) for kind in TYPES},"files":[f"history_{key}.geojson",f"history_{key}.csv"],"note":region["note"]}
    # Hash the products so the publication gate can detect mismatched snapshots.
    result["product_sha256"]={name:digest(outdir/name) for r in result["regions"].values() for name in r["files"]}
    (outdir/"history_manifest.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result

