# Tribal-led Fire Stewardship

**An ESIIL synthesis and learning series is a public-source discussion prototype, v0.1.0.** Prepared by Lilly Jones, PhD.                           
This is a standalone adaptation of the [Tribal Fire Science sandbox](https://github.com/daearconsulting/tribal_fire_science) from Daear Consulting, and is not yet approved by ESIIL.

## Start here

The Quarto companion has four modules, six distinct case pages, a teaching pathway and source/download pages. Four source notebooks use the same helpers. The bundled history is real public MTBS data from four broad regional windows; there are no synthetic substitutes in the public examples and no Tribal monitoring records or cultural-site locations.

1. Questions and authority.
2. Fire history and its limits.
3. Stewardship and exchange.
4. Monitoring outcomes.

Case contexts include partner-selected Lakota/Oceti Sakowin Nations, San Carlos Apache, Southern Ute, Ute Mountain Ute, Yurok/CFMC and Karuk. Existing public relationships are distinguished from proposed participation. Each Nation defines its own questions, study areas and governance.

## Local preview

Install Quarto 1.8.27 or newer, then from this repository:

```powershell
conda env create -f environment.yml
conda activate esiil-fire-stewardship
python scripts/check_public.py
quarto preview
```

Alternatively install the Python packages in a suitable environment with `python -m pip install -r requirements.txt -c constraints.txt`. The constraints record tested direct package versions; they do not lock all transitive packages. No API key is required. Static charts are self-contained; interactive basemaps need internet and provide a data-only option. Print/Save PDF provides a browser print version with static maps.

## Run the notebooks

Open a notebook in JupyterLab from this repository, or execute all four into ignored `work/`:

```powershell
python scripts/execute_notebooks.py
```

Before committing notebooks edited in Jupyter, clear their saved outputs and counters:

~~~powershell
python scripts/clear_notebook_outputs.py
python scripts/check_public.py
~~~

This preserves code and Markdown. For saved execution results, use the runner above; it writes to ignored work/executed_notebooks/. CI reports the notebook filename and rejects saved execution state.

Source notebooks have no saved outputs. The runner uses the current interpreter and leaves source notebooks untouched. Module 04 reports that no estimates are available until observations and a completed protocol are supplied locally. It never exports partner results to the public site.

## Data and reproducibility

The included MTBS snapshot covers 1984-2024. Its original download date is unknown. The inspection date, source-component hashes, output hashes, incident types and regional counts are retained in `data/processed/history_manifest.json`. All regional event counts reconcile to the annual tables and display features.                                                                    

To rebuild from an independently downloaded MTBS shapefile or GeoPackage:

```powershell
python scripts/build_history.py --mtbs "C:\path\to\mtbs_perims_DD.shp"
python scripts/check_public.py
```

See the [MTBS download page](https://www.mtbs.gov/direct-download). The national archive can be large. Regional products, rather than the large raw archive, are bundled here. Region boxes in `project.yml` are descriptive contexts only, not Tribal territory or treatment boundaries. Source thresholds and detection limits are explained on the history page.

## Partner-directed work

Copy blank worksheets from `templates/` into a partner-chosen private location. `data/private/`, raw data, executed notebooks and `.env` are ignored by Git. Do not put restricted data in this repository without an agreed stewardship arrangement. CARE supports the conversation; a Nation's own protocols govern it.                                         

## Validate and publish

```powershell
python -m unittest discover -s tests -v
python scripts/check_public.py
python scripts/execute_notebooks.py
quarto render
```

The CI workflow runs those checks and builds the site. A separate Pages workflow is manual only; enable Settings - Pages - GitHub Actions before using it. Set `website.site-url` in `_quarto.yml` to its Pages URL.

## Project layout

- `*.qmd`, `cases/`: readable website and distinct public-source case contexts.
- `notebooks/`: four research/teaching notebooks with clean source outputs.
- `esiilfire/`: history, governance, monitoring, provenance and presentation helpers.
- `data/public/`: curated case/source registers with review dates.
- `data/processed/`: small validated public MTBS subsets.
- `templates/`, `docs/`: blank worksheets, facilitator guide and release checks.
- `tests/`: numerical, schema, governance and data-integrity checks.

## Attribution and limits

The starting sandbox was developed by Lilly Jones in consultation with James Sanovia. See the [original software citation](https://doi.org/10.5281/zenodo.19265139). This independently structured first release retains the AGPL-3.0 license. Third-party materials retain their own terms; the license does not grant rights over partner data or Indigenous knowledge.

The series provides retrospective screening and research design. It contains no burn prescriptions, active-fire predictions, Nation rankings, synthetic vegetation opportunity scores or claims that regional satellite records identify cultural burning.
