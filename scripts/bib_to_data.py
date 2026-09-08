#!/usr/bin/env python3
"""Regenerate docs/_data/publications.yml and docs/_data/commentary.yml
from references.bib. Stdlib only — no pip install needed.

Usage:
    python3 scripts/bib_to_data.py

See the comment block at the top of references.bib for the field
conventions this script expects. One easy-to-miss one: compound surnames
("Di Terlizzi", "van der Berg") must use "Last, First" comma form in the
.bib, or the last whitespace-separated word gets treated as the whole
surname and everything before it as middle initials.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BIB_PATH = REPO_ROOT / "references.bib"
PUBLICATIONS_YML = REPO_ROOT / "docs" / "_data" / "publications.yml"
COMMENTARY_YML = REPO_ROOT / "docs" / "_data" / "commentary.yml"

# Last name matched (case-insensitively) to auto-bold the site owner in
# author lists. Change this if the site ever changes hands.
SELF_LASTNAME = "treado"


# --------------------------------------------------------------------------
# .bib parsing — a small hand-rolled parser, not a full BibTeX implementation.
# Handles braced/quoted field values with nested braces, but not LaTeX
# escapes or comment (%) lines inside field values.
# --------------------------------------------------------------------------

def strip_comments(text):
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("%")
    )


def split_top_level(body, sep=","):
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch == "{":
            depth += 1
            cur.append(ch)
        elif ch == "}":
            depth -= 1
            cur.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        parts.append("".join(cur))
    return parts


def parse_bib(text):
    text = strip_comments(text)
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{", text):
        etype = m.group(1).lower()
        j, depth = m.end(), 1
        start = j
        while depth > 0 and j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[start : j - 1]
        parts = split_top_level(body, ",")
        if not parts:
            continue
        key = parts[0].strip()
        fields = {"type": etype, "key": key}
        for part in parts[1:]:
            if "=" not in part:
                continue
            name, _, value = part.partition("=")
            name = name.strip().lower()
            value = value.strip()
            if value.startswith("{") and value.endswith("}"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            fields[name] = value.strip()
        entries.append(fields)
    return entries


# --------------------------------------------------------------------------
# Author formatting
# --------------------------------------------------------------------------

def format_name(raw):
    raw = raw.strip()
    starred = raw.endswith("*")
    if starred:
        raw = raw[:-1].strip()

    if "," in raw:
        last, first = (s.strip() for s in raw.split(",", 1))
    else:
        tokens = raw.split()
        last, first = tokens[-1], " ".join(tokens[:-1])

    initials = []
    for tok in first.split():
        if len(tok) <= 2 and tok.endswith("."):
            initials.append(tok)  # already an initial, e.g. "D."
        else:
            initials.append(tok[0].upper() + ".")

    name = " ".join(initials + [last]) if initials else last
    if last.lower() == SELF_LASTNAME:
        name = f"<b>{name}</b>"
    if starred:
        name += "*"
    return name


def format_authors(raw):
    names = [format_name(n) for n in re.split(r"\s+and\s+", raw.strip())]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


# --------------------------------------------------------------------------
# YAML output — hand-emitted for this fixed schema, no PyYAML dependency.
# --------------------------------------------------------------------------

def yq(value):
    return "'" + str(value).replace("'", "''") + "'"


GENERATED_HEADER = (
    "# GENERATED FILE — do not hand-edit.\n"
    "# Source of truth is /references.bib at the repo root.\n"
    "# Regenerate with: python3 scripts/bib_to_data.py\n\n"
)


def resolve_url(entry):
    if entry.get("url"):
        return entry["url"]
    if entry.get("doi"):
        return f"https://doi.org/{entry['doi']}"
    return ""


def gen_publications_yaml(entries):
    lines = [GENERATED_HEADER.rstrip("\n")]
    for e in entries:
        lines.append(f"- year: {e['year']}")
        lines.append(f"  authors: {yq(format_authors(e['author']))}")
        lines.append(f"  title: {yq(e['title'])}")
        lines.append(f"  journal: {yq(e['journal'])}")
        url = resolve_url(e)
        if url:
            lines.append(f"  url: {yq(url)}")
        if e.get("volume"):
            lines.append(f"  volume: {yq(e['volume'])}")
        if e.get("pages"):
            lines.append(f"  pages: {yq(e['pages'])}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def gen_commentary_yaml(entries):
    lines = [GENERATED_HEADER.rstrip("\n")]
    for e in entries:
        lines.append(f"- authors: {yq(format_authors(e['author']))}")
        lines.append(f"  title: {yq(e['title'])}")
        lines.append(f"  journal: {yq(e['journal'])}")
        url = resolve_url(e)
        if url:
            lines.append(f"  url: {yq(url)}")
        date = e.get("date") or e.get("year", "")
        if date:
            lines.append(f"  date: {yq(date)}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main():
    if not BIB_PATH.exists():
        sys.exit(f"error: {BIB_PATH} not found")

    entries = parse_bib(BIB_PATH.read_text(encoding="utf-8"))
    if not entries:
        sys.exit(f"error: no @entries found in {BIB_PATH}")

    for e in entries:
        missing = [f for f in ("author", "title", "journal") if not e.get(f)]
        if missing:
            sys.exit(f"error: entry '{e['key']}' is missing field(s): {', '.join(missing)}")

    publications = [e for e in entries if e["type"] != "misc"]
    commentary = [e for e in entries if e["type"] == "misc"]

    for e in publications:
        if not e.get("year"):
            sys.exit(f"error: publication entry '{e['key']}' is missing 'year'")

    PUBLICATIONS_YML.write_text(gen_publications_yaml(publications), encoding="utf-8")
    COMMENTARY_YML.write_text(gen_commentary_yaml(commentary), encoding="utf-8")

    print(f"wrote {len(publications)} publication(s) to {PUBLICATIONS_YML.relative_to(REPO_ROOT)}")
    print(f"wrote {len(commentary)} commentary entr(y/ies) to {COMMENTARY_YML.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
