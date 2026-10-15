import copy
import json
import tempfile
import unittest
from pathlib import Path
from esiilfire.notebooks import clear_execution, check_clean_notebook

class NotebookSourceTests(unittest.TestCase):
    def fixture(self):
        return {"metadata": {"widgets": {"state": "test widget"}, "title": "Keep title"},
                "cells": [
                    {"cell_type": "markdown", "source": ["Keep prose"], "metadata": {}},
                    {"cell_type": "code", "source": ["print('keep code')"],
                     "metadata": {"execution": {"timing": "test"}, "tags": ["keep"]},
                     "outputs": [{"output_type": "stream", "name": "stdout", "text": ["test output"]}],
                     "execution_count": 1}]}

    def test_clear_preserves_code_prose_and_tags_and_is_idempotent(self):
        n = self.fixture()
        clear_execution(n)
        self.assertEqual(n["cells"][0]["source"], ["Keep prose"])
        self.assertEqual(n["cells"][1]["source"], ["print('keep code')"])
        self.assertEqual(n["cells"][1]["metadata"], {"tags": ["keep"]})
        self.assertEqual(n["metadata"], {"title": "Keep title"})
        self.assertEqual(n["cells"][1]["outputs"], [])
        self.assertIsNone(n["cells"][1]["execution_count"])
        once = copy.deepcopy(n)
        clear_execution(n)
        self.assertEqual(n, once)

    def test_named_error_and_clean_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "example.ipynb"
            n = self.fixture()
            p.write_text(json.dumps(n), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"example.ipynb.*code cells 2.*clear_notebook_outputs"):
                check_clean_notebook(p)
            clear_execution(n)
            p.write_text(json.dumps(n), encoding="utf-8")
            check_clean_notebook(p)

    def test_counter_without_outputs_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "counter.ipynb"
            n = clear_execution(self.fixture())
            n["cells"][1]["execution_count"] = 0
            p.write_text(json.dumps(n), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "counter.ipynb"):
                check_clean_notebook(p)
