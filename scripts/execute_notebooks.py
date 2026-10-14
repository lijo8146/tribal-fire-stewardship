"""Execute notebooks using this interpreter; preserve clean source notebooks."""
import os,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
kernel=ROOT/"work/jupyter/kernels/esiil-series"
kernel.mkdir(parents=True,exist_ok=True)
(kernel/"kernel.json").write_text(json.dumps({"argv":[sys.executable,"-m","ipykernel_launcher","-f","{connection_file}"],"display_name":"ESIIL validation","language":"python"}),encoding="utf-8")
os.environ["JUPYTER_PATH"]=str(ROOT/"work/jupyter")+os.pathsep+os.environ.get("JUPYTER_PATH","")
import nbformat
from nbclient import NotebookClient
out=ROOT/"work/executed_notebooks";out.mkdir(parents=True,exist_ok=True)
for source in sorted((ROOT/"notebooks").glob("*.ipynb")):
    notebook=nbformat.read(source,as_version=4)
    NotebookClient(notebook,timeout=180,kernel_name="esiil-series",resources={"metadata":{"path":str(ROOT)}}).execute()
    nbformat.write(notebook,out/source.name)
    print("Executed:",source.name,flush=True)
