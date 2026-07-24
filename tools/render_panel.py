import os
import sys

ROWS = [
    ("user", "chandril-mallick"),
    ("role", "Applied ML Engineer"),
    ("focus", "LLMs, RAG, Healthcare IoT"),
    ("stack", "Python · FastAPI · Flutter · Docker"),
    ("now", "Building Dabba AI + SmartSant IoT"),
    ("paper", "IEEE 2026 · NAPSO framework"),
]

def render_panel(output_path="sysinfo.svg"):
    is_preview = os.environ.get("PREVIEW", "0") == "1"
    
    width = 460
    header_height = 32
    row_height = 28
    pad_top = 48
    pad_bottom = 24
    pad_left = 20
    
    height = pad_top + len(ROWS) * row_height + pad_bottom + 20
    
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    
    # Styles
    svg_parts.append('''<style>
      .bg { fill: #0d1117; rx: 10px; }
      .header-bar { fill: #161b22; }
      .btn-red { fill: #ff5f56; }
      .btn-yellow { fill: #ffbd2e; }
      .btn-green { fill: #27c93f; }
      .title { fill: #8b949e; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11px; font-weight: 600; }
      .label { fill: #38bdf8; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12.5px; font-weight: 600; }
      .val { fill: #c9d1d9; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12.5px; }
      .prompt { fill: #7ee787; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12.5px; font-weight: 600; }
      .cursor { fill: #58a6ff; }
    </style>''')
    
    # Window container
    svg_parts.append(f'<rect width="{width}" height="{height}" class="bg" stroke="#30363d" stroke-width="1"/>')
    # Header bar
    svg_parts.append(f'<path d="M 0 10 Q 0 0 10 0 L {width-10} 0 Q {width} 0 {width} 10 L {width} 32 L 0 32 Z" class="header-bar"/>')
    svg_parts.append('<circle cx="16" cy="16" r="5" class="btn-red"/>')
    svg_parts.append('<circle cx="32" cy="16" r="5" class="btn-yellow"/>')
    svg_parts.append('<circle cx="48" cy="16" r="5" class="btn-green"/>')
    svg_parts.append(f'<text x="{width//2}" y="20" text-anchor="middle" class="title">sysinfo.sh — zsh</text>')
    
    # Render rows
    for i, (key, val) in enumerate(ROWS):
        y_pos = pad_top + i * row_height
        delay = round(0.1 + i * 0.35, 2)
        
        row_g_attrs = ''
        if not is_preview:
            # Staggered fade and slight horizontal slide
            anim_html = (
                f'<g opacity="0" transform="translate(0, 0)">\n'
                f'  <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay}s" fill="freeze" />\n'
            )
        else:
            anim_html = '<g opacity="1">'
            
        svg_parts.append(anim_html)
        
        # Label (Key) formatted like terminal flag / field
        formatted_key = f"{key:<8}"
        svg_parts.append(f'  <text x="{pad_left}" y="{y_pos}" class="label">{key}:</text>')
        # Value
        svg_parts.append(f'  <text x="{pad_left + 80}" y="{y_pos}" class="val">{val}</text>')
        svg_parts.append('</g>')
        
    # Terminal command prompt at bottom
    prompt_y = pad_top + len(ROWS) * row_height + 15
    prompt_delay = round(0.1 + len(ROWS) * 0.35, 2)
    
    if not is_preview:
        svg_parts.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{prompt_delay}s" fill="freeze"/>')
    else:
        svg_parts.append('<g opacity="1">')
        
    svg_parts.append(f'<text x="{pad_left}" y="{prompt_y}" class="prompt">chandril@terminal ~ % </text>')
    svg_parts.append(f'<rect x="{pad_left + 175}" y="{prompt_y - 10}" width="8" height="13" class="cursor">')
    svg_parts.append('  <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />')
    svg_parts.append('</rect>')
    svg_parts.append('</g>')
    
    svg_parts.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
        
    print(f"Rendered sysinfo panel SVG to {output_path} (preview={is_preview})")

if __name__ == "__main__":
    render_panel()
