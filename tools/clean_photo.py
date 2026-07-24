#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUTPUT_PATH = Path("assets/photo-ready.png")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a portrait for ASCII conversion.")
    parser.add_argument("input_photo", help="Input portrait file path")
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Output cleaned image path (default: assets/photo-ready.png)",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=720,
        help="Output square image size in pixels (default: 720)",
    )
    return parser.parse_args()


def apply_clahe(rgb: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    merged = cv2.merge((l2, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_photo)
    output_path = Path(args.output)
    if not input_path.exists():
        raise FileNotFoundError(f"Input photo not found: {input_path}")

    source = input_path.read_bytes()
    no_bg = remove(source)

    # rembg returns PNG bytes with alpha; decode to ndarray.
    decoded = cv2.imdecode(np.frombuffer(no_bg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if decoded is None or decoded.shape[2] < 4:
        raise RuntimeError("Failed to decode transparent image from rembg output.")

    rgba = cv2.cvtColor(decoded, cv2.COLOR_BGRA2RGBA)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    enhanced = apply_clahe(rgb)
    white = np.full_like(enhanced, 255, dtype=np.uint8)
    alpha_f = (alpha.astype(np.float32) / 255.0)[..., None]
    composited = (enhanced * alpha_f + white * (1.0 - alpha_f)).astype(np.uint8)

    h, w = composited.shape[:2]
    side = max(h, w)
    canvas = np.full((side, side, 3), 255, dtype=np.uint8)
    y_off = (side - h) // 2
    x_off = (side - w) // 2
    canvas[y_off : y_off + h, x_off : x_off + w] = composited
    resized = cv2.resize(canvas, (args.size, args.size), interpolation=cv2.INTER_CUBIC)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(resized).save(output_path)


if __name__ == "__main__":
    main()
