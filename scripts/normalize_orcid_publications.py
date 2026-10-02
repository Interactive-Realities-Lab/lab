"""Normalize hugobloxorcid metadata for current HugoBlox publication pages."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FIELDS = (
    ("publication", "name"),
    ("publication_short", "short_name"),
    ("volume", "volume"),
    ("issue", "issue"),
    ("pages", "pages"),
    ("publisher", "publisher"),
)


def normalize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    if len(lines) < 3 or lines[0].strip() != "---":
        return False

    try:
        frontmatter_end = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration:
        return False

    values: dict[str, str] = {}
    matched_indexes: list[int] = []
    for index in range(1, frontmatter_end):
        for source_name, target_name in FIELDS:
            match = re.fullmatch(rf"{re.escape(source_name)}:\s+(.+?)\s*", lines[index].rstrip("\r\n"))
            if match:
                values[target_name] = match.group(1)
                matched_indexes.append(index)
                break

    if "name" not in values:
        return False

    newline = "\r\n" if lines[0].endswith("\r\n") else "\n"
    first_index = min(matched_indexes)
    nested = [f"publication:{newline}"]
    for _, target_name in FIELDS:
        if target_name in values:
            nested.append(f"  {target_name}: {values[target_name]}{newline}")

    matched = set(matched_indexes)
    output: list[str] = []
    for index, line in enumerate(lines):
        if index == first_index:
            output.extend(nested)
        if index not in matched:
            output.append(line)

    path.write_text("".join(output), encoding="utf-8", newline="")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    changed = sum(normalize(path) for path in args.root.rglob("index.md"))
    print(f"Normalized {changed} publication file(s).")


if __name__ == "__main__":
    main()
