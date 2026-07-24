#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx
from lxml import html

DEFAULT_USERNAME = "chandril-mallick"
OUTPUT_PATH = Path("assets/contributions.json")
ENDPOINT_TEMPLATE = "https://github.com/users/{username}/contributions"

WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


@dataclass(frozen=True)
class ContributionDay:
    date: str
    count: int | None
    level: int
    weekday: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pull GitHub public contribution cells.")
    parser.add_argument(
        "--username",
        default=os.getenv("GITHUB_USERNAME", DEFAULT_USERNAME),
        help="GitHub username (default: env GITHUB_USERNAME or chandril-mallick)",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Output JSON path (default: assets/contributions.json)",
    )
    return parser.parse_args()


def fetch_markup(username: str) -> str:
    url = ENDPOINT_TEMPLATE.format(username=username)
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def parse_days(markup: str) -> list[ContributionDay]:
    tree = html.fromstring(markup)
    cells = tree.xpath('//td[@data-date and @data-level]')
    days: list[ContributionDay] = []

    for cell in cells:
        date_value = cell.attrib["data-date"]
        date_obj = datetime.strptime(date_value, "%Y-%m-%d")
        days.append(
            ContributionDay(
                date=date_value,
                count=None,
                level=int(cell.attrib["data-level"]),
                weekday=date_obj.weekday(),
            )
        )

    return sorted(days, key=lambda day: day.date)


def compute_streaks(days: list[ContributionDay]) -> tuple[int, int]:
    longest = 0
    current = 0
    active = 0
    today = datetime.now(timezone.utc).date()

    for day in days:
        if day.level > 0:
            active += 1
            longest = max(longest, active)
        else:
            active = 0

    for day in reversed(days):
        date_obj = datetime.strptime(day.date, "%Y-%m-%d").date()
        if date_obj > today:
            continue
        if day.level > 0:
            current += 1
        else:
            break

    return current, longest


def busiest_weekday(days: list[ContributionDay]) -> str:
    counter: Counter[int] = Counter()
    for day in days:
        if day.level > 0:
            counter[day.weekday] += 1

    if not counter:
        return "N/A"

    weekday_index, _ = counter.most_common(1)[0]
    return WEEKDAY_NAMES[weekday_index]


def parse_total_contributions(markup: str) -> int:
    tree = html.fromstring(markup)
    heading = tree.xpath('normalize-space(//h2[@id="js-contribution-activity-description"])')
    if not heading:
        return 0
    match = re.search(r"([0-9][0-9,]*)\s+contributions?", heading)
    if not match:
        return 0
    return int(match.group(1).replace(",", ""))


def write_output(path: Path, username: str, days: list[ContributionDay], total: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    current_streak, longest_streak = compute_streaks(days)
    max_level = max((day.level for day in days), default=0)

    payload = {
        "username": username,
        "updated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "stats": {
            "total_contributions": total,
            "active_days": sum(1 for day in days if day.level > 0),
            "current_streak_days": current_streak,
            "longest_streak_days": longest_streak,
            "busiest_weekday": busiest_weekday(days),
            "max_daily_level": max_level,
            "count_source": "github_heatmap_levels",
        },
        "days": [
            {"date": day.date, "count": day.count, "level": day.level} for day in days
        ],
    }

    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    markup = fetch_markup(args.username)
    days = parse_days(markup)
    if not days:
        raise RuntimeError("No contribution cells parsed from GitHub markup.")
    total = parse_total_contributions(markup)
    write_output(output_path, args.username, days, total)


if __name__ == "__main__":
    main()
