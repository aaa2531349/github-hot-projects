#!/usr/bin/env python3
"""Fetch GitHub Trending repositories and print a compact digest."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser


USER_AGENT = "Codex GitHub Trending Daily Skill"
DEFAULT_HISTORY_FILE = Path(__file__).resolve().parents[2] / "history" / "pushed_repos.json"


def fetch_url(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


class TrendingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.repos: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.tag_stack: list[str] = []
        self.capture: str | None = None
        self.buffer: list[str] = []
        self.anchor_href = ""
        self.in_repo_h2 = False
        self.in_language = False
        self.in_star_link = False
        self.star_links_seen = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        self.tag_stack.append(tag)

        if tag == "article" and "Box-row" in attr.get("class", ""):
            self.current = {}
            self.star_links_seen = 0

        if self.current is None:
            return

        if tag == "h2":
            self.in_repo_h2 = True
        elif self.in_repo_h2 and tag == "a":
            self.capture = "repo"
            self.buffer = []
            self.anchor_href = attr.get("href", "")
        elif tag == "p" and "col-9" in attr.get("class", ""):
            self.capture = "description"
            self.buffer = []
        elif tag == "span" and attr.get("itemprop") == "programmingLanguage":
            self.in_language = True
            self.capture = "language"
            self.buffer = []
        elif tag == "a" and attr.get("href", "").endswith("/stargazers"):
            self.in_star_link = True
            self.capture = "stars"
            self.buffer = []
        elif tag == "span" and "float-sm-right" in attr.get("class", ""):
            self.capture = "trend"
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is not None and self.capture:
            if (self.capture == "repo" and tag == "a") or (
                self.capture in {"description", "language", "stars", "trend"} and tag in {"p", "span", "a"}
            ):
                value = compact_text("".join(self.buffer))
                if value:
                    if self.capture == "repo":
                        repo = value.replace(" / ", "/").replace(" ", "")
                        self.current["repo"] = repo
                        self.current["url"] = "https://github.com" + self.anchor_href
                    elif self.capture == "stars":
                        self.star_links_seen += 1
                        if self.star_links_seen == 1:
                            self.current["stars"] = value
                    else:
                        self.current[self.capture] = value
                self.capture = None
                self.buffer = []

        if tag == "h2":
            self.in_repo_h2 = False
        elif tag == "span":
            self.in_language = False
        elif tag == "a":
            self.in_star_link = False
        elif tag == "article" and self.current is not None:
            if self.current.get("repo") and self.current.get("url"):
                self.current["source"] = "github-trending"
                self.repos.append(self.current)
            self.current = None

        if self.tag_stack:
            self.tag_stack.pop()


def fetch_trending(limit: int, language: str, since: str) -> list[dict[str, str]]:
    language_path = urllib.parse.quote(language.strip()) if language else ""
    url = f"https://github.com/trending/{language_path}?since={urllib.parse.quote(since)}"
    parser = TrendingParser()
    parser.feed(fetch_url(url))
    return parser.repos[:limit]


def fetch_search_fallback(limit: int, days: int) -> list[dict[str, str]]:
    created_after = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    query = f"created:>{created_after}"
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": str(limit),
        }
    )
    payload = json.loads(fetch_url(f"https://api.github.com/search/repositories?{params}"))
    repos = []
    for item in payload.get("items", [])[:limit]:
        repos.append(
            {
                "repo": item.get("full_name", ""),
                "url": item.get("html_url", ""),
                "description": item.get("description") or "",
                "language": item.get("language") or "",
                "stars": f"{item.get('stargazers_count', 0):,}",
                "trend": f"created after {created_after}",
                "source": "github-search-fallback",
            }
        )
    return repos


def load_history(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    repos = payload.get("repos", {})
    if not isinstance(repos, dict):
        return {}
    history: dict[str, list[str]] = {}
    for repo, dates in repos.items():
        if isinstance(repo, str) and isinstance(dates, list):
            history[repo] = [value for value in dates if isinstance(value, str)]
    return history


def recent_push_dates(dates: list[str], today: dt.date, days: int) -> list[dt.date]:
    cutoff = today - dt.timedelta(days=days)
    recent = []
    for value in dates:
        try:
            pushed_at = dt.date.fromisoformat(value)
        except ValueError:
            continue
        if cutoff <= pushed_at <= today:
            recent.append(pushed_at)
    return sorted(recent, reverse=True)


def annotate_and_select(
    repos: list[dict[str, str]],
    history: dict[str, list[str]],
    limit: int,
    dedupe_days: int,
) -> list[dict[str, str]]:
    today = dt.date.today()
    fresh: list[dict[str, str]] = []
    repeated: list[dict[str, str]] = []
    seen_in_candidates = set()

    for repo in repos:
        name = repo.get("repo")
        if not name or name in seen_in_candidates:
            continue
        seen_in_candidates.add(name)

        recent_dates = recent_push_dates(history.get(name, []), today, dedupe_days)
        annotated = dict(repo)
        if recent_dates:
            days_ago = (today - recent_dates[0]).days
            annotated["pushed_recently"] = "true"
            annotated["history_status"] = "7 天内已推过" if days_ago else "今天已推过"
            annotated["days_since_push"] = str(days_ago)
            repeated.append(annotated)
        else:
            annotated["pushed_recently"] = "false"
            annotated["history_status"] = "新上榜"
            fresh.append(annotated)

    return (fresh + repeated)[:limit]


def save_history(path: Path, history: dict[str, list[str]], repos: list[dict[str, str]]) -> None:
    today = dt.date.today().isoformat()
    for repo in repos:
        name = repo.get("repo")
        if not name:
            continue
        dates = history.setdefault(name, [])
        if today not in dates:
            dates.append(today)
        history[name] = sorted(set(dates))[-30:]

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "repos": dict(sorted(history.items())),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_markdown(repos: list[dict[str, str]]) -> str:
    today = dt.date.today().isoformat()
    lines = [f"# GitHub 今日热门项目 Top {len(repos)}", "", f"日期：{today}"]
    if repos:
        sources = ", ".join(sorted({repo.get("source", "unknown") for repo in repos}))
        lines.append(f"来源：{sources}")
    lines.append("")

    for index, repo in enumerate(repos, start=1):
        meta = []
        if repo.get("language"):
            meta.append(repo["language"])
        if repo.get("stars"):
            meta.append(f"{repo['stars']} stars")
        if repo.get("trend"):
            meta.append(repo["trend"])
        if repo.get("history_status"):
            meta.append(repo["history_status"])
        lines.append(f"{index}. [{repo['repo']}]({repo['url']})")
        if meta:
            lines.append(f"   - {' | '.join(meta)}")
        if repo.get("description"):
            lines.append(f"   - {repo['description']}")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch GitHub Trending repositories.")
    parser.add_argument("--limit", type=int, default=10, help="Number of repositories to return.")
    parser.add_argument("--candidate-limit", type=int, default=30, help="Number of candidate repositories to fetch before dedupe.")
    parser.add_argument("--language", default="", help="Optional GitHub Trending language filter.")
    parser.add_argument("--since", choices=["daily", "weekly", "monthly"], default="daily")
    parser.add_argument("--fallback-days", type=int, default=30)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--dedupe-days", type=int, default=7, help="Prefer repos not pushed in this many days.")
    parser.add_argument("--history-file", type=Path, default=DEFAULT_HISTORY_FILE)
    parser.add_argument("--record-history", action="store_true", help="Record returned repositories as pushed today.")
    args = parser.parse_args()
    candidate_limit = max(args.limit, args.candidate_limit)

    try:
        repos = fetch_trending(candidate_limit, args.language, args.since)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"Warning: GitHub Trending fetch failed: {exc}", file=sys.stderr)
        repos = []

    if len(repos) < candidate_limit:
        try:
            fallback = fetch_search_fallback(candidate_limit - len(repos), args.fallback_days)
            seen = {repo.get("repo") for repo in repos}
            repos.extend(repo for repo in fallback if repo.get("repo") not in seen)
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            print(f"Warning: GitHub Search fallback failed: {exc}", file=sys.stderr)

    try:
        history = load_history(args.history_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Warning: History file ignored: {exc}", file=sys.stderr)
        history = {}

    repos = annotate_and_select(repos, history, args.limit, args.dedupe_days)
    if args.record_history and repos:
        save_history(args.history_file, history, repos)

    if args.format == "json":
        print(json.dumps(repos, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(repos))
    return 0 if repos else 1


if __name__ == "__main__":
    raise SystemExit(main())
