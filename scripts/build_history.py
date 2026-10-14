"""Build small regional products from an independently downloaded MTBS snapshot."""
import argparse,sys,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import yaml
from esiilfire import ROOT
from esiilfire.history import build_history
parser=argparse.ArgumentParser()
parser.add_argument("--mtbs",required=True,type=Path,help="Local MTBS shapefile or GeoPackage; never a Tribal private dataset")
args=parser.parse_args()
config=yaml.safe_load((ROOT/"project.yml").read_text(encoding="utf-8"))
with tempfile.TemporaryDirectory(dir=ROOT/"data",prefix="history-build-") as tmp:
    staged=Path(tmp)/"processed"
    result=build_history(args.mtbs,config["regions"],staged)
    target=ROOT/"data/processed";backup=ROOT/"data/processed.previous"
    if backup.exists():raise RuntimeError("Inspect an interrupted promotion before rebuilding")
    if target.exists():target.rename(backup)
    try:staged.rename(target)
    except Exception:
        if backup.exists():backup.rename(target)
        raise
    if backup.exists():shutil.rmtree(backup)
print(f"Built {len(result['regions'])} regional windows from {result['start_year']}–{result['end_year']} real MTBS data")
