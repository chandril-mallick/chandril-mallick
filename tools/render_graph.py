#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

INPUT_PATH = Path("assets/contributions.json")
OUTPUT_PATH = Path("graph.svg")
LEVEL_COLORS = ["#121826", "#12446a", "#1867a3", "#2f8fd5", "#90caf9"]

CELL_SIZE = 12
GAP = 3
LEFT_PAD = 48
TOP_PAD = 32
BOTTOM_PAD = 72
RIGHT_PAD = 22
WEEKDAY_LABELS = ["Mon", "Wed", "Fri"]
WEEKDAY_ROWS = [0, 2, 4]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render animated contribution graph SVG.")
    parser.add_argument(
        "--input",
        default=str(INPUT_PATH),
        help="Input JSON path from pull_contributions.py (default: assets/contributions.json)",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Output SVG path (default: graph.svg)",
    )
    return parser.parse_args()


def load_data(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing contribution data file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def chunk_weeks(days: list[dict]) -> list[list[dict]]:
    if not days:
        return []

    ordered = sorted(days, key=lambda d: d["date"])
    first_date = datetime.strptime(ordered[0]["date"], "%Y-%m-%d")
    prefix = first_date.weekday()  # Monday=0

    padded = [{"date": "", "count": 0, "level": 0}] * prefix + ordered
    while len(padded) % 7:
        padded.append({"date": "", "count": 0, "level": 0})

    return [padded[i : i + 7] for i in range(0, len(padded), 7)]


def graph_dimensions(week_count: int) -> tuple[int, int]:
    width = LEFT_PAD + RIGHT_PAD + week_count * CELL_SIZE + (week_count - 1) * GAP
    height = TOP_PAD + BOTTOM_PAD + 7 * CELL_SIZE + 6 * GAP
    return width, height


def render_svg(payload: dict) -> str:
    weeks = chunk_weeks(payload["days"])
    week_count = len(weeks)
    width, height = graph_dimensions(week_count)

    stats = payload.get("stats", {})
    footer = (
        f"total={stats.get('total_contributions', 0)}  "
        f"streak={stats.get('current_streak_days', 0)}d  "
        f"best={stats.get('busiest_weekday', 'N/A')}"
    )
    username = payload.get("username", "unknown")
    stamp = payload.get("updated_at_utc", "")
    preview = os.getenv("PREVIEW", "").strip().lower() in {"1", "true", "yes"}

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Contribution graph for {username}">',
        "<defs>",
        "<style>",
        ".bg{fill:#070b14}.label{font:12px ui-monospace,monospace;fill:#9fb3c8}",
        ".title{font:600 14px ui-monospace,monospace;fill:#d8e7f5}",
        ".footer{font:11px ui-monospace,monospace;fill:#7f9bb5}",
        "</style>",
        "</defs>",
        f'<rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="12"/>',
        f'<text class="title" x="{LEFT_PAD}" y="20">$ contributions --user {username}</text>',
    ]

    for label, row in zip(WEEKDAY_LABELS, WEEKDAY_ROWS):
        y = TOP_PAD + row * (CELL_SIZE + GAP) + CELL_SIZE - 1
        lines.append(f'<text class="label" x="10" y="{y}">{label}</text>')

    for col, week in enumerate(weeks):
        x = LEFT_PAD + col * (CELL_SIZE + GAP)
        clip_id = f"col-{col}"
        reveal_delay = round(col * 0.04, 3)

        lines.append("<g>")
        lines.append(f'<clipPath id="{clip_id}">')
        if preview:
            lines.append(
                f'<rect x="{x - 1}" y="{TOP_PAD - 1}" width="{CELL_SIZE + 2}" '
                f'height="{7 * CELL_SIZE + 6 * GAP + 2}" />'
            )
        else:
            lines.append(
                f'<rect x="{x - 1}" y="{TOP_PAD - 1}" width="0" '
                f'height="{7 * CELL_SIZE + 6 * GAP + 2}">'
            )
            lines.append(
                f'<animate attributeName="width" from="0" to="{CELL_SIZE + 2}" '
                f'begin="{reveal_delay}s" dur="0.22s" fill="freeze" />'
            )
            lines.append("</rect>")
        lines.append("</clipPath>")
        lines.append(f'<g clip-path="url(#{clip_id})">')

        for row, day in enumerate(week):
            y = TOP_PAD + row * (CELL_SIZE + GAP)
            color = LEVEL_COLORS[max(0, min(4, int(day["level"])))]
            if day["date"]:
                if day.get("count") is None:
                    tooltip = f'{day["date"]}: activity level {day["level"]}'
                else:
                    tooltip = f'{day["date"]}: {day["count"]} contributions'
            else:
                tooltip = "padding"
            lines.append(
                f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'rx="2" fill="{color}" opacity="0.98"><title>{tooltip}</title></rect>'
            )

        lines.append("</g>")
        lines.append("</g>")

    legend_y = height - 45
    legend_x = LEFT_PAD
    lines.append(f'<text class="footer" x="{legend_x}" y="{legend_y}">less</text>')
    for idx, color in enumerate(LEVEL_COLORS):
        lx = legend_x + 34 + idx * (CELL_SIZE + 4)
        lines.append(
            f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" fill="{color}" />'
        )
    lines.append(
        f'<text class="footer" x="{legend_x + 34 + len(LEVEL_COLORS) * (CELL_SIZE + 4) + 8}" y="{legend_y}">more</text>'
    )
    lines.append(f'<text class="footer" x="{LEFT_PAD}" y="{height - 20}">{footer}</text>')
    lines.append(
        f'<text class="footer" x="{width - RIGHT_PAD - 210}" y="{height - 20}">updated {stamp}</text>'
    )
    lines.append("</svg>")

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    payload = load_data(input_path)
    output_path.write_text(render_svg(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
