"""Record the tested direct Python dependency versions."""
from pathlib import Path
from importlib.metadata import version
root=Path(__file__).resolve().parents[1]
names=[line.split(">=")[0].strip() for line in (root/"requirements.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
(root/"constraints.txt").write_text("# Tested direct dependencies with Python 3.11; not a complete transitive lock.\n"+"\n".join(f"{name}=={version(name)}" for name in sorted(names))+"\n",encoding="utf-8")
