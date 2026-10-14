# Release checks

The public-source prototype may be shared as a discussion resource with its status and limitations intact. This does not authorize future partner-specific outputs.

For the public build, run `python scripts/check_public.py`, `python -m unittest discover -s tests -v`, `python scripts/execute_notebooks.py`, and `quarto render`. Source notebook outputs must be empty. Executed copies belong in ignored `work/` and are not automatically published.

For partner-specific work, record the appropriate authority, permitted purpose, data stewardship, interpretation review, release decision and conditions. Review images, captions, metadata, downloadable notebooks and small-cell tables for unintended disclosure. Do not publish field locations or knowledge merely because the data file is technically accessible. A typed approval record is documentation, not an authentication system or a substitute for the authority it names.

Before creating a public repository, inspect `git ls-files` and confirm it contains no `data/private`, raw data, credentials, executed notebooks, or unapproved results. The AGPL software license does not license partner knowledge or observations. Review current source descriptions and event availability before relying on them for a new invitation.
