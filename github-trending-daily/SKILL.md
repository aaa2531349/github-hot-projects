---
name: github-trending-daily
description: Fetch and summarize the top 10 currently popular GitHub repositories for daily pushes, trend reports, developer newsletters, or requests like "今天 GitHub 热门项目", "推送 10 个热门 GitHub 项目", "GitHub Trending daily", and recurring GitHub project discovery updates.
---

# GitHub Trending Daily

## Overview

Use this skill to produce a concise Chinese daily digest of 10 popular GitHub repositories. Prefer the bundled script so the data collection, 7-day dedupe, and final formatting are repeatable.

## Quick Start

Run:

```bash
python3 scripts/fetch_github_trending.py --limit 10 --format markdown --record-history
```

Useful options:

- `--language python`: limit Trending to one language.
- `--since daily|weekly|monthly`: choose GitHub Trending time window. Default: `daily`.
- `--format json`: return structured data for downstream formatting.
- `--fallback-days 30`: when Trending scraping fails, query recently created repositories from GitHub Search.
- `--dedupe-days 7`: prefer repositories not pushed in the last 7 days.
- `--record-history`: after a real push, record returned repositories in `history/pushed_repos.json`.
- Omit `--record-history` for previews and tests that should not affect future dedupe.

## Workflow

1. Run the script from this skill directory.
2. If the script returns Markdown, use it directly as the factual backbone.
3. Add a short Chinese intro with the date and source.
4. For each repository, keep the link, description, language, stars, today's trend, and history status when available.
5. Add one concise "为什么值得看" sentence based on the repository description, topic, and developer usefulness.
6. If live fetching fails, say the failure plainly and include the fallback source shown by the script.

## Output Style

Use a compact daily push format:

- Title: `GitHub 今日热门项目 Top 10`
- One line date/source note.
- Numbered list of 10 repositories.
- Each item: repo link, language, stars, daily stars if available, description, and a short recommendation.
- Include history labels such as `新上榜` or `7 天内已推过` when the script returns them.
- End with 1-2 trend observations, such as dominant languages or recurring themes.

Do not invent star counts or daily trend numbers. If a field is missing, omit that field instead of guessing.

## Resources

### scripts/

- `fetch_github_trending.py`: Fetches GitHub Trending with a GitHub Search fallback, prefers projects not pushed in the last 7 days, optionally records push history, and outputs Markdown or JSON.
