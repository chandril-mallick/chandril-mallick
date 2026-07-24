#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

INPUT_PATH = Path("assets/photo-ready.png")
OUTPUT_PATH = Path("portrait.svg")
GLYPHS = " '.,:;~+*xXO#"
CELL_W = 10
CELL_H = 14
FONT_SIZE = 13
ACCENT = "#8dd4ff"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render animated ASCII portrait SVG.")
    parser.add_argument(
        "--input",
        default=str(INPUT_PATH),
        help="Prepared image path (default: assets/photo-ready.png)",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Output SVG path (default: portrait.svg)",
    )
    parser.add_argument("--cols", type=int, default=36, help="Character columns (default: 36)")
    return parser.parse_args()


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def to_ascii_rows(image_path: Path, cols: int) -> list[str]:
    if not image_path.exists():
        return [
            "            ....''''....            ",
            "        ..''            ''..        ",
            "      .'     load your photo   '.    ",
            "     /     assets/photo-ready    \\   ",
            "    ;        then rerender        ;  ",
            "    |    python tools/render_     |  ",
            "    |       portrait.py           |  ",
            "    ;                              ;  ",
            "     \\      preview placeholder   /   ",
            "      '.                      .'      ",
            "        ''..              ..''        ",
            "            ''''......''''            ",
        ]

    image = Image.open(image_path).convert("L")
    width, height = image.size
    aspect = height / max(width, 1)
    rows = max(20, int(cols * aspect * 0.52))
    scaled = image.resize((cols, rows), Image.Resampling.BICUBIC)
    arr = np.asarray(scaled)

    idx = np.clip((arr / 255.0 * (len(GLYPHS) - 1)).astype(int), 0, len(GLYPHS) - 1)
    lines: list[str] = []
    for row in idx:
        chars = "".join(GLYPHS[p] for p in row)
        if chars.strip():
            lines.append(chars)
        else:
            lines.append(" " * len(chars))
    return lines


def render_svg(ascii_rows: list[str]) -> str:
    cols = len(ascii_rows[0]) if ascii_rows else 0
    width = 30 + cols * CELL_W + 30
    height = 34 + len(ascii_rows) * CELL_H + 30

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="ASCII portrait">',
        "<defs>",
        "<style>",
        f".bg{{fill:#091220}} .txt{{font:{FONT_SIZE}px ui-monospace,monospace;fill:{ACCENT};dominant-baseline:hanging;white-space:pre}}",
        "</style>",
        "</defs>",
        f'<rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="12"/>',
    ]

    content_w = cols * CELL_W
    for row_idx, row in enumerate(ascii_rows):
        y = 18 + row_idx * CELL_H
        clip_id = f"row-{row_idx}"
        delay = round(row_idx * 0.04, 3)

        lines.append("<g>")
        lines.append(f'<clipPath id="{clip_id}">')
        lines.append(f'<rect x="20" y="{y}" width="0" height="{CELL_H + 2}">')
        lines.append(
            f'<animate attributeName="width" from="0" to="{content_w + 4}" begin="{delay}s" dur="0.26s" fill="freeze" />'
        )
        lines.append("</rect>")
        lines.append("</clipPath>")
        lines.append(f'<text class="txt" x="20" y="{y}" clip-path="url(#{clip_id})">{esc(row)}</text>')
        lines.append("</g>")

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    ascii_rows = to_ascii_rows(Path(args.input), args.cols)
    Path(args.output).write_text(render_svg(ascii_rows), encoding="utf-8")


if __name__ == "__main__":
    main()
