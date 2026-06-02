#!/usr/bin/env python3
"""Update publication metadata from an ADS public library."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path


API_ROOT = "https://api.adsabs.harvard.edu/v1"
LIBRARY_ID = "Ehu1oU_ISIairGeqwhMJWw"
OUTPUT_PATH = Path("data/publications.json")
FIELDS = "bibcode,title,author,year,pubdate,pub,volume,page,doi"


def ads_request(path: str, token: str, params: dict[str, str] | None = None) -> dict:
    url = f"{API_ROOT}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ADS request failed with HTTP {exc.code}: {detail}") from exc


def get_library_bibcodes(token: str) -> list[str]:
    payload = ads_request(f"/biblib/libraries/{LIBRARY_ID}", token)
    documents = payload.get("documents", [])
    if not isinstance(documents, list) or not documents:
        raise RuntimeError("ADS library response did not include any documents.")
    return [str(bibcode) for bibcode in documents]


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def get_records(token: str, bibcodes: list[str]) -> list[dict]:
    records: list[dict] = []
    for bibcode_chunk in chunks(bibcodes, 25):
        query = " OR ".join(f'bibcode:"{bibcode}"' for bibcode in bibcode_chunk)
        payload = ads_request(
            "/search/query",
            token,
            {
                "q": query,
                "fl": FIELDS,
                "rows": str(len(bibcode_chunk)),
                "sort": "date desc,bibcode desc",
            },
        )
        records.extend(payload.get("response", {}).get("docs", []))
        time.sleep(0.2)
    return records


def initials(given_names: list[str]) -> str:
    return " ".join(f"{name[0]}." for name in given_names if name)


def format_author(author: str) -> str:
    parts = [part.strip() for part in author.split(",")]
    if len(parts) == 1:
        return parts[0]
    family = parts[0]
    given = " ".join(parts[1:]).replace(".", " ").split()
    return f"{family} {initials(given)}".strip()


def format_authors(authors: list[str]) -> str:
    visible_authors = [format_author(author) for author in authors[:5]]
    if len(authors) > 5:
        visible_authors.append("et al.")
    return ", ".join(visible_authors)


def format_publication(record: dict) -> str:
    pub = record.get("pub")
    volume = record.get("volume")
    pages = record.get("page") or []
    page = pages[0] if pages else None
    if pub and volume and page:
        return f"{pub}, {volume}, {page}."
    if pub:
        return f"{pub}."
    return "Publication details pending."


def clean_title(title: str) -> str:
    title = unescape(title)
    title = re.sub(r"</?sub>", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\$(.*?)\$", r"\1", title)
    title = title.replace("─", "-")
    return " ".join(title.split())


def is_first_author(record: dict) -> bool:
    authors = record.get("author") or []
    if not authors:
        return False
    first_author = authors[0].lower()
    return first_author.startswith("lu,")


def normalize_record(record: dict) -> dict:
    title = record.get("title") or ["Untitled publication"]
    authors = record.get("author") or []
    doi = record.get("doi") or []
    return {
        "bibcode": record["bibcode"],
        "title": clean_title(title[0]),
        "year": str(record.get("year", "")),
        "authors": format_authors(authors),
        "publication": format_publication(record),
        "adsUrl": f"https://ui.adsabs.harvard.edu/abs/{record['bibcode']}/abstract",
        "doiUrl": f"https://doi.org/{doi[0]}" if doi else "",
        "category": "first-author" if is_first_author(record) else "co-author",
    }


def main() -> int:
    token = os.environ.get("ADS_TOKEN")
    if not token:
        print("ADS_TOKEN is required.", file=sys.stderr)
        return 1

    bibcodes = get_library_bibcodes(token)
    records_by_bibcode = {record["bibcode"]: record for record in get_records(token, bibcodes)}
    missing = [bibcode for bibcode in bibcodes if bibcode not in records_by_bibcode]
    if missing:
        print(f"Missing metadata for {len(missing)} bibcode(s): {', '.join(missing)}", file=sys.stderr)

    publications = [normalize_record(records_by_bibcode[bibcode]) for bibcode in bibcodes if bibcode in records_by_bibcode]
    publications.sort(key=lambda item: (item["year"], item["bibcode"]), reverse=True)

    payload = {
        "source": "https://ui.adsabs.harvard.edu/public-libraries/Ehu1oU_ISIairGeqwhMJWw",
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "publications": publications,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT_PATH} with {len(publications)} publication(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
