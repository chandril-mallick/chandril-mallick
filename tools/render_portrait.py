import os
import sys
from PIL import Image
import numpy as np

GLYPHS = " '.,:;~+*xXO#"

def render_portrait(input_path="assets/photo-ready.png", output_path="portrait.svg", cols=64):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} does not exist. Run clean_photo.py first.")
        sys.exit(1)
        
    img = Image.open(input_path).convert("L")
    w, h = img.size
    
    # Character aspect ratio roughly 0.5 (width / height)
    aspect_ratio = h / w
    rows = int(cols * aspect_ratio * 0.52)
    
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    img_np = np.array(img_resized)
    
    # Map pixel brightness (0-255) to GLYPHS index
    # Note: 255 is white (light/empty), 0 is black (dense/dark)
    num_glyphs = len(GLYPHS)
    
    lines = []
    for r in range(rows):
        line_chars = []
        for c in range(cols):
            val = img_np[r, c]
            # 255 -> index 0 (lightest/space), 0 -> index num_glyphs-1 (darkest)
            idx = int((255 - val) / 255.0 * (num_glyphs - 1))
            idx = max(0, min(num_glyphs - 1, idx))
            char = GLYPHS[idx]
            # Escape XML special chars
            if char == "&": char = "&amp;"
            elif char == "<": char = "&lt;"
            elif char == ">": char = "&gt;"
            elif char == '"': char = "&quot;"
            elif char == "'": char = "&apos;"
            line_chars.append(char)
        lines.append("".join(line_chars))
        
    # Build SVG
    font_size = 9.5
    line_height = 11.5
    pad_x = 18
    pad_top = 45
    pad_bottom = 20
    
    svg_width = int(cols * (font_size * 0.58) + pad_x * 2)
    svg_height = int(rows * line_height + pad_top + pad_bottom)
    
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    svg_parts.append('<defs>')
    
    # Define clip paths per row with staggered SMIL animation
    for i in range(rows):
        begin_delay = round(i * 0.04, 2)
        y_pos = pad_top + i * line_height - font_size + 2
        clip_def = (
            f'  <clipPath id="clip-row-{i}">\n'
            f'    <rect x="{pad_x}" y="{y_pos}" width="0" height="{line_height + 4}">\n'
            f'      <animate attributeName="width" from="0" to="{svg_width - pad_x*2}" dur="0.35s" begin="{begin_delay}s" fill="freeze" />\n'
            f'    </rect>\n'
            f'  </clipPath>'
        )
        svg_parts.append(clip_def)
        
    svg_parts.append('</defs>')
    
    # Styles
    svg_parts.append('''<style>
      .bg { fill: #0d1117; rx: 10px; }
      .header-bar { fill: #161b22; }
      .btn-red { fill: #ff5f56; }
      .btn-yellow { fill: #ffbd2e; }
      .btn-green { fill: #27c93f; }
      .title { fill: #8b949e; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11px; font-weight: 600; }
      .ascii-text { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 9.5px; fill: #38bdf8; xml:space: preserve; white-space: pre; }
    </style>''')
    
    # Window container
    svg_parts.append(f'<rect width="{svg_width}" height="{svg_height}" class="bg" stroke="#30363d" stroke-width="1"/>')
    # Header bar
    svg_parts.append(f'<path d="M 0 10 Q 0 0 10 0 L {svg_width-10} 0 Q {svg_width} 0 {svg_width} 10 L {svg_width} 32 L 0 32 Z" class="header-bar"/>')
    svg_parts.append('<circle cx="16" cy="16" r="5" class="btn-red"/>')
    svg_parts.append('<circle cx="32" cy="16" r="5" class="btn-yellow"/>')
    svg_parts.append('<circle cx="48" cy="16" r="5" class="btn-green"/>')
    svg_parts.append(f'<text x="{svg_width//2}" y="20" text-anchor="middle" class="title">portrait.asc — 80×{rows}</text>')
    
    # Render ASCII text rows
    for i, line in enumerate(lines):
        y_pos = pad_top + i * line_height
        svg_parts.append(
            f'<text x="{pad_x}" y="{y_pos}" class="ascii-text" clip-path="url(#clip-row-{i})">{line}</text>'
        )
        
    svg_parts.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
        
    print(f"Rendered ASCII portrait SVG to {output_path} ({svg_width}x{svg_height})")

if __name__ == "__main__":
    render_portrait()
