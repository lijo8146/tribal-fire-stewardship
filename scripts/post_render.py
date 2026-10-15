"""The rendered figures use standalone HTML, not a notebook AMD loader."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
for page in (root/"_site").rglob("*.html"):
    text=page.read_text(encoding="utf-8")
    text=re.sub(r'<script[^>]+src="https://cdn\.jsdelivr\.net/npm/requirejs@[^" ]+/require\.min\.js"[^>]*></script>', '',text)
    text=re.sub(r"<script[^>]*>define\('jquery', \[\],function\(\) \{return window\.jQuery;\}\)</script>", '',text)
    page.write_text(text,encoding="utf-8")

# Publish readable source previews next to the clean downloadable notebooks.
# Do not execute notebooks here: partner observations must stay local.
import html
import nbformat
from nbconvert import HTMLExporter
exporter = HTMLExporter(template_name="lab")
for source in sorted((root / "notebooks").glob("*.ipynb")):
    notebook = nbformat.read(source, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    body, _ = exporter.from_notebook_node(notebook)
    banner = (
        '<nav aria-label="Notebook navigation" style="padding:1rem 2rem;'
        'background:#e4ebe3;color:#203d3a">'
        '<a href="../resources.html">Sources &amp; downloads</a> · '
        f'<a href="{html.escape(source.name)}" download>Download .ipynb</a>'
        '<p>Notebook source preview: text and code, without execution results. '
        'Run from the project in JupyterLab using the supplied environment.</p></nav>'
    )
    body = re.sub(r"(<body[^>]*>)", lambda match: match.group(1) + banner, body, count=1)
    destination = root / "_site/notebooks" / source.with_suffix(".html").name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body, encoding="utf-8")
