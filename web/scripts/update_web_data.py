#!/usr/bin/env python3
"""Export the daily GitHub Trending push data for the website."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FETCH_SCRIPT = PROJECT_ROOT / "github-trending-daily" / "scripts" / "fetch_github_trending.py"
OUTPUT_FILE = PROJECT_ROOT / "web" / "data" / "latest.json"
ARCHIVE_DIR = PROJECT_ROOT / "web" / "data" / "archive"
DATES_FILE = PROJECT_ROOT / "web" / "data" / "dates.json"


def load_existing_translations() -> dict[str, str]:
    payloads = []
    if OUTPUT_FILE.exists():
        payloads.append(json.loads(OUTPUT_FILE.read_text(encoding="utf-8")))
    for path in sorted(ARCHIVE_DIR.glob("*.json")):
        payloads.append(json.loads(path.read_text(encoding="utf-8")))

    translations = {}
    for payload in payloads:
        for repo in payload.get("repositories", []):
            name = repo.get("repo")
            description_zh = repo.get("description_zh")
            if name and description_zh:
                translations[name] = description_zh
    return translations


def update_dates_manifest(date: str) -> None:
    dates = set()
    if DATES_FILE.exists():
        payload = json.loads(DATES_FILE.read_text(encoding="utf-8"))
        dates.update(value for value in payload.get("dates", []) if isinstance(value, str))
    dates.add(date)
    payload = {
        "latest": date,
        "dates": sorted(dates),
    }
    DATES_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update website data from the GitHub Trending skill.")
    parser.add_argument("--record-history", action="store_true", help="Record selected repositories as pushed today.")
    args = parser.parse_args()

    command = [
        str(FETCH_SCRIPT),
        "--limit",
        "10",
        "--candidate-limit",
        "30",
        "--dedupe-days",
        "7",
        "--format",
        "json",
    ]
    if args.record_history:
        command.append("--record-history")

    result = subprocess.run(command, check=True, capture_output=True, text=True)
    repositories = json.loads(result.stdout)
    translations = load_existing_translations()
    for repo in repositories:
        description_zh = translations.get(repo.get("repo"))
        if description_zh:
            repo["description_zh"] = description_zh
    sources = sorted({repo.get("source", "unknown") for repo in repositories})
    today = dt.date.today().isoformat()
    payload = {
        "date": today,
        "source": ", ".join(sources),
        "repositories": repositories,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ARCHIVE_DIR / f"{today}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_dates_manifest(today)
    print(f"Updated {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        raise
