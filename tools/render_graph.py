import json
import os
import sys

LEVELS = ["#161b22", "#16537e", "#1c7ed6", "#4dabf7", "#a5d8ff"]

def render_graph(input_path="assets/contributions.json", output_path="graph.svg"):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run pull_contributions.py first.")
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    days = data.get("days", [])
    total_contribs = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    busiest_day = data.get("busiest_day", "N/A")
    
    # Structure days into 53 weeks (columns) x 7 days (rows)
    # Note: days array is ordered chronologically
    weeks = []
    current_week = []
    
    for d in days:
        current_week.append(d)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    if current_week:
        weeks.append(current_week)
        
    cell_size = 11
    cell_gap = 3
    pad_left = 32
    pad_top = 50
    
    width = 820
    grid_height = 7 * (cell_size + cell_gap)
    height = pad_top + grid_height + 55
    
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
      .stats { fill: #c9d1d9; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11.5px; font-weight: 500; }
      .legend-text { fill: #8b949e; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 10px; }
      .cell { rx: 2.5px; ry: 2.5px; }
    </style>''')
    
    # Window container
    svg_parts.append(f'<rect width="{width}" height="{height}" class="bg" stroke="#30363d" stroke-width="1"/>')
    # Header bar
    svg_parts.append(f'<path d="M 0 10 Q 0 0 10 0 L {width-10} 0 Q {width} 0 {width} 10 L {width} 32 L 0 32 Z" class="header-bar"/>')
    svg_parts.append('<circle cx="16" cy="16" r="5" class="btn-red"/>')
    svg_parts.append('<circle cx="32" cy="16" r="5" class="btn-yellow"/>')
    svg_parts.append('<circle cx="48" cy="16" r="5" class="btn-green"/>')
    svg_parts.append(f'<text x="{width//2}" y="20" text-anchor="middle" class="title">contributions.log — 52-week activity wave</text>')
    
    # Render week columns with staggered wave animation
    for w_idx, week in enumerate(weeks):
        x_pos = pad_left + w_idx * (cell_size + cell_gap)
        delay = round(w_idx * 0.03, 2)
        
        svg_parts.append(f'<g transform="translate({x_pos}, 0)" opacity="0">')
        svg_parts.append(f'  <animate attributeName="opacity" from="0" to="1" dur="0.25s" begin="{delay}s" fill="freeze" />')
        
        for d_idx, day in enumerate(week):
            y_pos = pad_top + d_idx * (cell_size + cell_gap)
            level = day.get("level", 0)
            color = LEVELS[min(level, len(LEVELS) - 1)]
            
            svg_parts.append(
                f'  <rect x="0" y="{y_pos}" width="{cell_size}" height="{cell_size}" fill="{color}" class="cell">'
                f'<title>{day.get("date")}: {day.get("count")} contributions</title></rect>'
            )
            
        svg_parts.append('</g>')
        
    # Render Stats summary & Legend footer
    footer_y = pad_top + grid_height + 30
    
    # Left stats line
    stats_str = f"&gt; Total: {total_contribs} commits  |  Current Streak: {current_streak} days  |  Longest: {longest_streak} days  |  Peak: {busiest_day}"
    svg_parts.append(f'<text x="{pad_left}" y="{footer_y}" class="stats">{stats_str}</text>')
    
    # Right legend
    legend_x = width - pad_left - 130
    svg_parts.append(f'<text x="{legend_x - 32}" y="{footer_y}" class="legend-text">Less</text>')
    for idx, col in enumerate(LEVELS):
        lx = legend_x + idx * (cell_size + 3)
        ly = footer_y - 9
        svg_parts.append(f'<rect x="{lx}" y="{ly}" width="{cell_size}" height="{cell_size}" fill="{col}" class="cell"/>')
    svg_parts.append(f'<text x="{legend_x + len(LEVELS) * (cell_size + 3) + 6}" y="{footer_y}" class="legend-text">More</text>')
    
    svg_parts.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
        
    print(f"Rendered contribution graph SVG to {output_path} ({width}x{height})")

if __name__ == "__main__":
    render_graph()
