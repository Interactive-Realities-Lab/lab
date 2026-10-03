"""Admit new ORCID publications only when their bibliographic data is supported.

The upstream importer substitutes today's date and the ORCID owner's name when
publication dates or contributors are missing. This script checks the original
work and its embedded BibTeX before copying an imported bundle into the site.
"""

from __future__ import annotations

import argparse
import codecs
import collections
import datetime as dt
import http.client
import json
import re
import shutil
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import latexcodec  # Registers the ulatex codec used for BibTeX names.
import yaml
from pybtex.database import Person, parse_string


ORCID_API = "https://pub.orcid.org/v3.0"
CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "IRLab-publication-sync/1.0 (public metadata validation)"
TYPE_MAP = {
    "journal-article": "article-journal",
    "article-journal": "article-journal",
    "conference-paper": "paper-conference",
    "proceedings-article": "paper-conference",
    "book-chapter": "chapter",
    "book": "book",
    "report": "report",
    "thesis": "thesis",
    "dissertation": "thesis",
    "dissertation-thesis": "thesis",
    "preprint": "manuscript",
}
BIB_TYPE_MAP = {
    "article": "article-journal",
    "inproceedings": "paper-conference",
    "conference": "paper-conference",
    "incollection": "chapter",
    "book": "book",
    "techreport": "report",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
    "unpublished": "manuscript",
}
BIB_OUTPUT_TYPES = {
    "article-journal": "article",
    "paper-conference": "inproceedings",
    "chapter": "incollection",
    "book": "book",
    "report": "techreport",
    "thesis": "phdthesis",
    "manuscript": "unpublished",
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError, http.client.RemoteDisconnected):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise AssertionError("unreachable")


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(char for char in value if not unicodedata.combining(char))
    return "".join(char for char in value if char.isalnum())


def front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Missing YAML front matter: {path}")
    end = next((index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError(f"Missing closing YAML delimiter: {path}")
    header = "".join(lines[1:end])
    body = "".join(lines[end + 1 :])
    data = yaml.safe_load(header)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML front matter: {path}")
    return data, body


def year_date(node: dict | None) -> str | None:
    if not isinstance(node, dict):
        return None
    year = (node.get("year") or {}).get("value")
    month = (node.get("month") or {}).get("value") or "1"
    day = (node.get("day") or {}).get("value") or "1"
    if not year:
        return None
    try:
        return dt.date(int(year), int(month), int(day)).isoformat()
    except (TypeError, ValueError):
        return None


def crossref_date(record: dict) -> str | None:
    for field in ("published", "published-print", "published-online", "issued"):
        parts = (record.get(field) or {}).get("date-parts") or []
        if parts and parts[0]:
            numbers = parts[0]
            try:
                return dt.date(
                    int(numbers[0]),
                    int(numbers[1]) if len(numbers) > 1 else 1,
                    int(numbers[2]) if len(numbers) > 2 else 1,
                ).isoformat()
            except (TypeError, ValueError):
                continue
    return None


def latex_text(value: str) -> str:
    decoded = codecs.decode(value, "ulatex")
    return decoded.replace("{", "").replace("}", "").strip()


def bibtex_details(work: dict) -> tuple[str | None, list[str], str | None, dict]:
    citation = work.get("citation") or {}
    if citation.get("citation-type", "").lower() != "bibtex":
        return None, [], None, {}
    raw = citation.get("citation-value") or ""
    try:
        entries = parse_string(raw, "bibtex").entries
    except Exception as error:
        raise ValueError(f"Cannot parse ORCID BibTeX: {error}") from error
    if len(entries) != 1:
        raise ValueError("ORCID BibTeX must contain exactly one entry")
    entry = next(iter(entries.values()))
    year = entry.fields.get("year")
    year = year.strip() if year and re.fullmatch(r"\d{4}", year.strip()) else None
    authors = []
    for person in entry.persons.get("author", []):
        given = " ".join(person.first_names + person.middle_names)
        family = " ".join(person.prelast_names + person.last_names)
        name = latex_text(" ".join(part for part in (given, family) if part))
        if person.lineage_names:
            name += ", " + latex_text(" ".join(person.lineage_names))
        if name:
            authors.append(name)
    title = entry.fields.get("title")
    fields = {key.lower(): latex_text(value) for key, value in entry.fields.items()}
    fields["_entry_type"] = entry.type.lower()
    return year, authors, latex_text(title) if title else None, fields


def contributor_authors(work: dict) -> list[str]:
    result = []
    for contributor in (work.get("contributors") or {}).get("contributor") or []:
        for field in ("credit-name", "contributor-name"):
            name = (contributor.get(field) or {}).get("value")
            if name:
                result.append(name.strip())
                break
    return result


def crossref_authors(record: dict) -> list[str]:
    return [
        " ".join(part for part in (author.get("given"), author.get("family")) if part)
        or author.get("name", "")
        for author in record.get("author") or []
    ]


def author_keys(authors: list[str]) -> list[str]:
    # Initials and accents vary between sources; family names and order must agree.
    return [normalize(author.split()[-1]) for author in authors]


def unreliable_author(name: str) -> bool:
    return (
        not normalize(name)
        or normalize(name) in {"others", "etal", "etalia"}
        or "\\" in name
        or len(name.split()) < 2
    )


def doi_from_work(work: dict) -> str | None:
    for item in (work.get("external-ids") or {}).get("external-id") or []:
        if item.get("external-id-type", "").casefold() == "doi":
            return item.get("external-id-value", "").strip().lower() or None
    return None


def clean_doi(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)", "", value.strip(), flags=re.I)
    return value.casefold() or None


def admit(data: dict, work: dict, crossref: dict) -> tuple[dict | None, str]:
    orcid_title = ((work.get("title") or {}).get("title") or {}).get("value") or ""
    if normalize(data.get("title", "")) != normalize(orcid_title):
        return None, "imported title differs from ORCID"

    try:
        bib_year, bib_authors, bib_title, bib_fields = bibtex_details(work)
    except ValueError as error:
        return None, str(error)
    if bib_title and normalize(bib_title) != normalize(orcid_title):
        return None, "BibTeX title differs from ORCID"
    crossref_titles = crossref.get("title") or []
    crossref_title = (
        crossref_titles[0]
        if isinstance(crossref_titles, list) and crossref_titles
        else crossref_titles if isinstance(crossref_titles, str) else None
    )
    if crossref_title and normalize(crossref_title) != normalize(orcid_title):
        return None, "Crossref title differs from ORCID"

    dates = {
        "ORCID": year_date(work.get("publication-date")),
        "Crossref": crossref_date(crossref),
        "BibTeX": f"{bib_year}-01-01" if bib_year else None,
    }
    available_dates = {source: value for source, value in dates.items() if value}
    if not available_dates:
        return None, "no supported publication year"
    if len({value[:4] for value in available_dates.values()}) != 1:
        return None, f"conflicting publication years: {available_dates}"
    date = dates["ORCID"] or dates["Crossref"] or dates["BibTeX"]

    source_authors = {
        "Crossref": crossref_authors(crossref),
        "ORCID": contributor_authors(work),
        "BibTeX": bib_authors,
    }
    available_authors = {key: value for key, value in source_authors.items() if value}
    if not available_authors:
        return None, "no supported author list"
    if (
        list(available_authors) == ["BibTeX"]
        and len(bib_authors) == 1
        and bib_fields.get("_entry_type") not in {"phdthesis", "mastersthesis"}
    ):
        return None, "single BibTeX author lacks independent confirmation"
    if any(unreliable_author(author) for names in available_authors.values() for author in names):
        return None, "unreadable author name"
    if len({tuple(author_keys(value)) for value in available_authors.values()}) != 1:
        return None, f"conflicting author lists: {list(available_authors)}"
    authors = next(iter(available_authors.values()))

    result = dict(data)
    result["date"] = date
    result["authors"] = authors
    source_type = TYPE_MAP.get(
        (crossref.get("type") or work.get("type") or "").lower()
    )
    bib_type = BIB_TYPE_MAP.get(bib_fields.get("_entry_type", ""))
    if source_type and bib_type and source_type != bib_type:
        return None, "publication type differs between metadata and BibTeX"
    result["publication_types"] = [source_type or bib_type] if source_type or bib_type else []
    raw_publication = result.get("publication")
    publication = dict(raw_publication) if isinstance(raw_publication, dict) else {}
    if isinstance(raw_publication, str) and raw_publication:
        publication["name"] = raw_publication
    venue = (
        publication.get("name")
        or next(iter(crossref.get("container-title") or []), None)
        or (work.get("journal-title") or {}).get("value")
        or bib_fields.get("journal")
        or bib_fields.get("booktitle")
        or bib_fields.get("school")
    )
    if venue:
        publication["name"] = venue
        publication.setdefault("short_name", venue)
    for key, bib_key in (("volume", "volume"), ("issue", "number"), ("pages", "pages"), ("publisher", "publisher")):
        if bib_fields.get(bib_key):
            publication.setdefault(key, bib_fields[bib_key])
    if publication:
        result["publication"] = publication
    if not result.get("abstract") and bib_fields.get("abstract"):
        result["abstract"] = bib_fields["abstract"]
    link = bib_fields.get("url")
    if link and urllib.parse.urlparse(link).scheme in ("http", "https") and not result.get("links"):
        result["links"] = [{"type": "source", "url": link}]
    return result, ""


def existing_keys(root: Path) -> tuple[set[str], set[str], set[str]]:
    titles, work_ids, dois = set(), set(), set()
    for path in root.glob("*/index.md"):
        data, _ = front_matter(path)
        titles.add(normalize(data.get("title", "")))
        ids = (data.get("hugoblox") or {}).get("ids") or {}
        if ids.get("orcid"):
            work_ids.add(ids["orcid"])
        if ids.get("doi"):
            dois.add(ids["doi"].casefold())
    return titles, work_ids, dois


def write_bundle(source: Path, target: Path, data: dict, body: str) -> None:
    shutil.copytree(source, target)
    header = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
    (target / "index.md").write_text(f"---\n{header}---\n{body}", encoding="utf-8")
    cite_path = target / "cite.bib"
    if cite_path.exists():
        entries = parse_string(cite_path.read_text(encoding="utf-8"), "bibtex").entries
        if len(entries) != 1:
            raise ValueError(f"Expected one citation in {cite_path}")
        entry = next(iter(entries.values()))
        entry.type = BIB_OUTPUT_TYPES.get((data.get("publication_types") or [None])[0], "misc")
        entry.persons["author"] = [Person(author) for author in data["authors"]]
        entry.fields["year"] = data["date"][:4]
        venue = (data.get("publication") or {}).get("name")
        if venue:
            field = {
                "inproceedings": "booktitle",
                "incollection": "booktitle",
                "article": "journal",
                "phdthesis": "school",
                "techreport": "institution",
                "book": "publisher",
                "misc": "howpublished",
            }[entry.type]
            entry.fields[field] = venue
        cite_path.write_text(next(iter(entries.values())).to_string("bibtex"), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imported", type=Path, required=True)
    parser.add_argument("--existing", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--orcid-id", required=True)
    args = parser.parse_args()

    titles, work_ids, dois = existing_keys(args.existing)
    candidates = []
    for path in sorted(args.imported.glob("*/index.md")):
        data, body = front_matter(path)
        candidates.append((path.parent, data, body))
    title_counts = collections.Counter(normalize(data.get("title", "")) for _, data, _ in candidates)

    accepted = skipped = 0
    args.output.mkdir(parents=True, exist_ok=True)
    for folder, data, body in candidates:
        title_key = normalize(data.get("title", ""))
        ids = (data.get("hugoblox") or {}).get("ids") or {}
        work_id = ids.get("orcid", "")
        doi = ids.get("doi", "").casefold()
        reason = None
        if not title_key or not work_id.startswith(args.orcid_id + ":"):
            reason = "missing title or ORCID work ID"
        elif title_key in titles or work_id in work_ids or (doi and doi in dois):
            reason = "already represented in the site"
        elif title_counts[title_key] > 1:
            reason = "multiple imported records have the same title"
        if reason:
            print(f"SKIP {folder.name}: {reason}")
            skipped += 1
            continue

        put_code = work_id.rsplit(":", 1)[1]
        if not put_code.isdigit():
            print(f"SKIP {folder.name}: invalid ORCID work ID")
            skipped += 1
            continue
        work = get_json(f"{ORCID_API}/{args.orcid_id}/work/{put_code}")
        orcid_doi = clean_doi(doi_from_work(work))
        try:
            bib_doi = clean_doi(bibtex_details(work)[3].get("doi"))
        except ValueError:
            bib_doi = None
        if orcid_doi and bib_doi and orcid_doi != bib_doi:
            print(f"SKIP {folder.name}: DOI differs between ORCID and BibTeX")
            skipped += 1
            continue
        source_doi = orcid_doi or bib_doi
        if source_doi and source_doi in dois:
            print(f"SKIP {folder.name}: DOI already represented in the site")
            skipped += 1
            continue
        crossref = {}
        if source_doi:
            url = f"{CROSSREF_API}/{urllib.parse.quote(source_doi, safe='')}"
            try:
                crossref = get_json(url).get("message") or {}
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
        if crossref.get("DOI") and crossref["DOI"].casefold() != source_doi:
            print(f"SKIP {folder.name}: Crossref DOI differs from ORCID")
            skipped += 1
            continue
        corrected, reason = admit(data, work, crossref)
        if corrected is None:
            print(f"SKIP {folder.name}: {reason}")
            skipped += 1
            continue
        corrected_doi = ((corrected.get("hugoblox") or {}).get("ids") or {}).get("doi")
        if source_doi and corrected_doi and source_doi != clean_doi(corrected_doi):
            print(f"SKIP {folder.name}: imported DOI differs from ORCID")
            skipped += 1
            continue
        if source_doi:
            corrected["hugoblox"]["ids"]["doi"] = source_doi
        year = corrected["date"][:4]
        suffix = folder.name.split("-", 1)[1]
        destination = args.output / f"{year}-{suffix}"
        if destination.exists() or (args.existing / destination.name).exists():
            print(f"SKIP {folder.name}: destination already exists")
            skipped += 1
            continue
        write_bundle(folder, destination, corrected, body)
        titles.add(title_key)
        work_ids.add(work_id)
        if doi:
            dois.add(doi)
        accepted += 1
        print(f"ADD {destination.name}: {len(corrected['authors'])} authors, {corrected['date']}")
    print(f"Accepted {accepted}; skipped {skipped}")


if __name__ == "__main__":
    main()
