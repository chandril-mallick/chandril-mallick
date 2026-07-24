#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

OUTPUT_PATH = Path("sysinfo.svg")
ROWS = [
    ("role", "Applied ML Engineer"),
    ("focus", "LLMs, RAG, Healthcare IoT"),
    ("stack", "Python · FastAPI · Flutter · Docker"),
    ("now", "Building Dabba AI + SmartSant IoT"),
    ("paper", "IEEE 2026 · NAPSO framework"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render terminal-style profile panel SVG.")
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Output SVG path (default: sysinfo.svg)",
    )
    return parser.parse_args()


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_svg() -> str:
    width = 900
    row_height = 45
    body_top = 70
    height = body_top + row_height * len(ROWS) + 34
    preview = os.getenv("PREVIEW", "").strip().lower() in {"1", "true", "yes"}

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Profile system info panel">',
        "<defs>",
        "<style>",
        ".bg{fill:#0b111d}.head{fill:#101a2b}.title{font:600 16px ui-monospace,monospace;fill:#dbeafe}",
        ".k{font:600 15px ui-monospace,monospace;fill:#7dd3fc}.v{font:15px ui-monospace,monospace;fill:#d1e4f7}",
        ".line{stroke:#1d2c45;stroke-width:1}",
        "</style>",
        "</defs>",
        f'<rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="12"/>',
        f'<rect class="head" x="0" y="0" width="{width}" height="44" rx="12"/>',
        '<circle cx="22" cy="22" r="6" fill="#ef4444"/>',
        '<circle cx="42" cy="22" r="6" fill="#f59e0b"/>',
        '<circle cx="62" cy="22" r="6" fill="#22c55e"/>',
        '<text class="title" x="86" y="28">$ whoami --verbose</text>',
    ]

    for idx, (key, value) in enumerate(ROWS):
        y = body_top + idx * row_height
        label_y = y + 24
        begin = round(0.18 + idx * 0.16, 2)
        key_x = 28
        val_x = 180

        lines.append(f'<line class="line" x1="20" x2="{width - 20}" y1="{y}" y2="{y}"/>')

        if preview:
            lines.append(f'<text class="k" x="{key_x}" y="{label_y}">{esc(key)}</text>')
            lines.append(f'<text class="v" x="{val_x}" y="{label_y}">{esc(value)}</text>')
            continue

        lines.append(f'<text class="k" x="{key_x}" y="{label_y}" opacity="0">{esc(key)}')
        lines.append(
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="0.18s" fill="freeze"/>'
        )
        lines.append("</text>")
        lines.append(f'<text class="v" x="{val_x}" y="{label_y}" opacity="0">{esc(value)}')
        lines.append(
            f'<animate attributeName="opacity" from="0" to="1" begin="{round(begin + 0.08, 2)}s" dur="0.22s" fill="freeze"/>'
        )
        lines.append("</text>")

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.write_text(render_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()
