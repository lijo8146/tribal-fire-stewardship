import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from esiilfire.validate import validate_public
m=validate_public()
print(f"Public build validated: {len(m['regions'])} real-data regional windows, source provenance, reconciled counts, clean notebook sources")
