import unittest,tempfile,json,shutil
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from esiilfire.governance import decision_gaps,review_public_release
from esiilfire.monitoring import paired_changes,summarize_pairs
from esiilfire.history import normalize_events,summarize_window
from esiilfire.validate import validate_public
from esiilfire import ROOT

def observations(n=1):
    rows=[]
    for pair in range(n):
        for role,values in [("treated",[10,14]),("comparison",[8,9])]:
            for period,date,value in zip(["before","after"],["2023-05-01","2024-05-01"],values):
                rows.append(dict(pair_id=f"p{pair}",unit_id=f"p{pair}-{role}",role=role,period=period,observed_at=date,indicator="test indicator",value=float(value),unit="test units",method="test method",quality_flag="accepted"))
    return pd.DataFrame(rows)

class MonitoringTests(unittest.TestCase):
    def test_known_paired_arithmetic_and_small_sample(self):
        result=paired_changes(observations())
        self.assertEqual(result.paired_contrast.iloc[0],3)
        self.assertIsNone(summarize_pairs(result)["interval"])
    def test_identical_independent_pairs_have_known_interval(self):
        result=summarize_pairs(paired_changes(observations(10)))
        self.assertEqual(result["independent_pairs"],10)
        self.assertEqual(result["interval"],[3,3])
    def test_missing_pair_cell_fails(self):
        with self.assertRaisesRegex(ValueError,"four"):paired_changes(observations().iloc[:-1])
    def test_duplicate_cells_fail(self):
        f=observations()
        with self.assertRaisesRegex(ValueError,"duplicate"):paired_changes(pd.concat([f,f.iloc[:1]]))
    def test_reused_comparison_units_fail(self):
        f=observations(2)
        f.loc[f.role.eq("comparison"),"unit_id"]="shared"
        with self.assertRaisesRegex(ValueError,"reused"):paired_changes(f)
    def test_mixed_units_and_method_fail(self):
        for col in ["unit","method"]:
            f=observations();f.loc[0,col]="different"
            with self.assertRaises(ValueError):paired_changes(f)
    def test_dates_quality_and_nonfinite_values_fail(self):
        for col,value in [("observed_at","2025-05-01"),("quality_flag","pending"),("value",np.inf),("pair_id","")]:
            f=observations();f.loc[0,col]=value
            with self.assertRaises(ValueError):paired_changes(f)
    def test_no_data_does_not_estimate(self):
        with self.assertRaisesRegex(ValueError,"No observations"):paired_changes(observations().iloc[:0])

class HistoryTests(unittest.TestCase):
    def fixture(self):
        return gpd.GeoDataFrame({"Event_ID":["one","one"],"Incid_Name":["public example","public example"],"Incid_Type":["Prescribed Fire","Prescribed Fire"],"Ig_Date":["2020-06-01","2020-06-01"]},geometry=[box(-101,43,-100,44),box(-101,43,-100,44)],crs=4326)
    def test_duplicate_perimeters_count_once_and_keep_prescribed_type(self):
        normalized=normalize_events(self.fixture())
        self.assertEqual(len(normalized),1)
        self.assertEqual(normalized["type"].iloc[0],"Prescribed Fire")
        clipped,annual=summarize_window(normalized,[-101,43,-100.5,44],1984,2024)
        self.assertEqual(annual.mapped_events.sum(),1)
        self.assertLess(clipped.acres_in_window.iloc[0],normalized.to_crs(5070).area.iloc[0]/4046.8564224)
    def test_empty_window_preserves_zero_cells_in_known_coverage(self):
        _,annual=summarize_window(normalize_events(self.fixture()),[-110,40,-109,41],1984,2024)
        self.assertEqual(len(annual),41*4)
        self.assertEqual(annual.mapped_events.sum(),0)
    def test_conflicting_event_metadata_fails(self):
        f=self.fixture();f.loc[1,"Incid_Type"]="Wildfire"
        with self.assertRaisesRegex(ValueError,"Conflicting"):normalize_events(f)
    def test_invalid_dates_fail(self):
        f=self.fixture();f.loc[0,"Ig_Date"]="unknown"
        with self.assertRaisesRegex(ValueError,"dates"):normalize_events(f)

class GovernanceTests(unittest.TestCase):
    def test_blank_plan_and_pending_release_do_not_pass(self):
        self.assertEqual(len(decision_gaps({})),9)
        self.assertFalse(review_public_release({"decision":"pending"})["release_allowed"])
    def test_documented_release_needs_every_field_and_explicit_decision(self):
        record={k:"test documentation" for k in ["asset","owner","purpose","audience","approved_by","approved_on","approval_reference"]}
        record.update(classification="public",decision="approved")
        self.assertTrue(review_public_release(record)["release_allowed"])
        record["classification"]="private"
        self.assertFalse(review_public_release(record)["release_allowed"])

class PublicDataTests(unittest.TestCase):
    def test_actual_public_snapshot_reconciles(self):
        self.assertEqual(len(validate_public()["regions"]),4)
    def test_zero_mapped_events_are_valid_not_missing_data(self):
        from esiilfire.history import digest,TYPES
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel in ["data/public","data/processed","notebooks"]:shutil.copytree(ROOT/rel,root/rel)
            shutil.copy2(ROOT/"project.yml",root/"project.yml")
            key="northern-plains"
            geometry=root/"data/processed"/f"history_{key}.geojson"
            geometry.write_text(json.dumps({"type":"FeatureCollection","features":[]}),encoding="utf-8")
            table=root/"data/processed"/f"history_{key}.csv"
            annual=pd.read_csv(table);annual["mapped_events"]=0;annual["acres_in_window"]=0;annual.to_csv(table,index=False)
            manifest=root/"data/processed/history_manifest.json"
            m=json.loads(manifest.read_text(encoding="utf-8"));m["regions"][key]["mapped_events"]=0;m["regions"][key]["by_type"]={t:0 for t in TYPES}
            for p in [geometry,table]:m["product_sha256"][p.name]=digest(p)
            manifest.write_text(json.dumps(m),encoding="utf-8")
            self.assertEqual(validate_public(root)["regions"][key]["mapped_events"],0)

    def test_changed_product_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel in ["data/public","data/processed","notebooks"]:shutil.copytree(ROOT/rel,root/rel)
            shutil.copy2(ROOT/"project.yml",root/"project.yml")
            with (root/"data/processed/history_northern-plains.csv").open("a") as stream:stream.write("corrupted")
            with self.assertRaisesRegex(ValueError,"changed"):validate_public(root)

if __name__=="__main__":unittest.main()

