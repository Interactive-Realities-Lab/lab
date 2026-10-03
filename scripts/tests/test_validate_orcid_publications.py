"""Checks for the metadata mistakes observed in the ORCID import."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import yaml
from pybtex.database import parse_string

from scripts.validate_orcid_publications import admit, main


TITLE = "Designing High-Precision 3D Interaction Techniques for Large Displays"


def work(*, year: str | None, bibtex: str) -> dict:
    return {
        "title": {"title": {"value": TITLE}},
        "publication-date": {"year": {"value": year}} if year else None,
        "contributors": {"contributor": []},
        "citation": {"citation-type": "bibtex", "citation-value": bibtex},
    }


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.imported = {
            "title": TITLE,
            "date": "2026-10-03",
            "authors": ["Regis Kopper"],
            "hugoblox": {"ids": {"orcid": "0000-0003-2081-7061:53337519"}},
        }

    def test_bibtex_supplies_missing_year_and_authors(self) -> None:
        record = work(
            year=None,
            bibtex=r"@misc{x, title={Designing High-Precision 3D Interaction Techniques for Large Displays}, year={2007}, author={Ryan P. McMahan and Regis Kopper and Mara Guimar{\~a}es da Silva and Will McConnell and Doug A. Bowman}}",
        )
        corrected, reason = admit(self.imported, record, {})
        self.assertEqual(reason, "")
        self.assertEqual(corrected["date"], "2007-01-01")
        self.assertEqual(
            corrected["authors"],
            [
                "Ryan P. McMahan",
                "Regis Kopper",
                "Mara Guimarães da Silva",
                "Will McConnell",
                "Doug A. Bowman",
            ],
        )

    def test_missing_publication_year_is_rejected(self) -> None:
        record = work(
            year=None,
            bibtex=f"@misc{{x, title={{{TITLE}}}, author={{Regis Kopper}}}}",
        )
        corrected, reason = admit(self.imported, record, {})
        self.assertIsNone(corrected)
        self.assertEqual(reason, "no supported publication year")

    def test_missing_authors_are_rejected(self) -> None:
        record = work(
            year="2007",
            bibtex=f"@misc{{x, title={{{TITLE}}}, year={{2007}}}}",
        )
        corrected, reason = admit(self.imported, record, {})
        self.assertIsNone(corrected)
        self.assertEqual(reason, "no supported author list")

    def test_single_bibtex_author_needs_confirmation(self) -> None:
        record = work(
            year="2007",
            bibtex=f"@misc{{x, title={{{TITLE}}}, year={{2007}}, author={{Regis Kopper}}}}",
        )
        corrected, reason = admit(self.imported, record, {})
        self.assertIsNone(corrected)
        self.assertEqual(reason, "single BibTeX author lacks independent confirmation")

    def test_single_author_thesis_uses_bibtex(self) -> None:
        title = "Understanding and improving distal pointing interaction"
        imported = {**self.imported, "title": title}
        record = {
            "title": {"title": {"value": title}},
            "type": "dissertation-thesis",
            "publication-date": {"year": {"value": "2011"}},
            "contributors": {"contributor": []},
            "citation": {
                "citation-type": "bibtex",
                "citation-value": r"@phdthesis{x,author={Kopper, R{\'e}gis Augusto Poli},school={Virginia Tech},title={Understanding and improving distal pointing interaction},year={2011}}",
            },
        }
        corrected, reason = admit(imported, record, {})
        self.assertEqual(reason, "")
        self.assertEqual(corrected["authors"], ["Régis Augusto Poli Kopper"])
        self.assertEqual(corrected["publication_types"], ["thesis"])

    def test_conflicting_years_are_rejected(self) -> None:
        record = work(
            year="2007",
            bibtex=f"@misc{{x, title={{{TITLE}}}, year={{2008}}, author={{Regis Kopper}}}}",
        )
        corrected, reason = admit(self.imported, record, {})
        self.assertIsNone(corrected)
        self.assertIn("conflicting publication years", reason)

    def test_placeholder_author_is_rejected(self) -> None:
        record = work(
            year="2007",
            bibtex=f"@misc{{x, title={{{TITLE}}}, author={{Regis Kopper and others}}}}",
        )
        corrected, reason = admit(self.imported, record, {})
        self.assertIsNone(corrected)
        self.assertEqual(reason, "unreadable author name")

    def test_import_moves_bundle_to_bibtex_year_and_rewrites_citation(self) -> None:
        record = work(
            year=None,
            bibtex=f"@misc{{x, title={{{TITLE}}}, year={{2007}}, author={{Ryan P. McMahan and Regis Kopper and Will McConnell}}}}",
        )
        with TemporaryDirectory() as temp:
            root = Path(temp)
            imported = root / "imported"
            bundle = imported / "2026-designing-high-precision-3d"
            bundle.mkdir(parents=True)
            (bundle / "index.md").write_text(
                "---\n" + yaml.safe_dump(self.imported, sort_keys=False) + "---\n",
                encoding="utf-8",
            )
            (bundle / "cite.bib").write_text(
                f"@article{{x, author = {{Regis Kopper}}, title = {{{TITLE}}}, year = {{2026}}}}\n",
                encoding="utf-8",
            )
            existing = root / "existing"
            existing.mkdir()
            output = root / "output"
            args = [
                "validate_orcid_publications.py",
                "--imported", str(imported),
                "--existing", str(existing),
                "--output", str(output),
                "--orcid-id", "0000-0003-2081-7061",
            ]
            with patch("sys.argv", args), patch(
                "scripts.validate_orcid_publications.get_json", return_value=record
            ):
                main()
            corrected = output / "2007-designing-high-precision-3d"
            self.assertTrue(corrected.exists())
            self.assertEqual(
                yaml.safe_load((corrected / "index.md").read_text().split("---", 2)[1])["authors"],
                ["Ryan P. McMahan", "Regis Kopper", "Will McConnell"],
            )
            citation = (corrected / "cite.bib").read_text()
            entry = next(iter(parse_string(citation, "bibtex").entries.values()))
            self.assertEqual(len(entry.persons["author"]), 3)
            self.assertEqual(entry.persons["author"][2].last_names, ["McConnell"])
            self.assertEqual(entry.fields["year"], "2007")

    def test_existing_title_prevents_duplicate_import(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            imported = root / "imported" / "2026-designing-high-precision-3d"
            existing = root / "existing" / "2007-designing-high-precision-3d"
            imported.mkdir(parents=True)
            existing.mkdir(parents=True)
            for directory in (imported, existing):
                (directory / "index.md").write_text(
                    "---\n" + yaml.safe_dump(self.imported, sort_keys=False) + "---\n",
                    encoding="utf-8",
                )
            output = root / "output"
            args = [
                "validate_orcid_publications.py",
                "--imported", str(imported.parent),
                "--existing", str(existing.parent),
                "--output", str(output),
                "--orcid-id", "0000-0003-2081-7061",
            ]
            with patch("sys.argv", args), patch(
                "scripts.validate_orcid_publications.get_json"
            ) as fetch:
                main()
            fetch.assert_not_called()
            self.assertEqual(list(output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
