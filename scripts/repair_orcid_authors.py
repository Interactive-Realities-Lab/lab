"""Repair legacy single-author imports using matching ORCID BibTeX citations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from validate_orcid_publications import (
    bibtex_details,
    front_matter,
    get_json,
    normalize,
    unreliable_author,
    year_date,
)


def replace_authors(path: Path, authors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if line == "authors:\n"), None)
    if start is None:
        raise ValueError(f"Missing authors block: {path}")
    end = start + 1
    while end < len(lines) and (lines[end].startswith("  ") or not lines[end].strip()):
        end += 1
    replacement = ["authors:\n"] + [
        f"  - {json.dumps(author, ensure_ascii=False)}\n" for author in authors
    ]
    updated_index = "".join(lines[:start] + replacement + lines[end:])

    cite_path = path.with_name("cite.bib")
    updated_cite = None
    if cite_path.exists():
        cite = cite_path.read_text(encoding="utf-8")
        new_author = "  author = {" + " and ".join(authors) + "},"
        cite, count = re.subn(r"(?m)^  author = \{[^\n]*\},?$", lambda _: new_author, cite)
        if count != 1:
            raise ValueError(f"Expected one BibTeX author line: {cite_path}")
        updated_cite = cite
    path.write_text(updated_index, encoding="utf-8")
    if updated_cite is not None:
        cite_path.write_text(updated_cite, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--orcid-id", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    repairable = 0
    for path in sorted(args.root.glob("*/index.md")):
        data, _ = front_matter(path)
        current = data.get("authors") or []
        work_id = ((data.get("hugoblox") or {}).get("ids") or {}).get("orcid", "")
        if data.get("draft") or len(current) != 1 or not work_id.startswith(args.orcid_id + ":"):
            continue
        put_code = work_id.rsplit(":", 1)[1]
        if not put_code.isdigit():
            continue
        work = get_json(f"https://pub.orcid.org/v3.0/{args.orcid_id}/work/{put_code}")
        try:
            bib_year, authors, bib_title, _ = bibtex_details(work)
        except ValueError:
            continue
        local_year = str(data.get("date", ""))[:4]
        orcid_year = year_date(work.get("publication-date"))
        source_years = [year for year in (bib_year, orcid_year[:4] if orcid_year else None) if year]
        if not source_years or any(year != local_year for year in source_years):
            continue
        orcid_title = ((work.get("title") or {}).get("title") or {}).get("value") or ""
        if normalize(data.get("title", "")) != normalize(orcid_title):
            continue
        if bib_title and normalize(bib_title) != normalize(orcid_title):
            continue
        if (
            len(authors) < 2
            or any(unreliable_author(author) for author in authors)
            or not any(normalize(author.split()[-1]) == normalize(current[0].split()[-1]) for author in authors)
        ):
            continue
        print(f"{'REPAIR' if args.apply else 'WOULD REPAIR'} {path.parent.name}: {len(authors)} authors")
        if args.apply:
            replace_authors(path, authors)
        repairable += 1
    print(f"{'Repaired' if args.apply else 'Repairable'}: {repairable}")


if __name__ == "__main__":
    main()
