import json
import os
import re
import sys
from datetime import datetime, timezone
import httpx
from lxml import html

USERNAME = "chandril-mallick"
OUTPUT_FILE = "assets/contributions.json"

DAYS_OF_WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def pull_contributions(username=USERNAME, output_path=OUTPUT_FILE):
    url = f"https://github.com/users/{username}/contributions"
    print(f"Fetching contribution calendar from {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    resp = httpx.get(url, headers=headers, follow_redirects=True)
    if resp.status_code != 200:
        print(f"Error fetching contributions: HTTP {resp.status_code}")
        sys.exit(1)
        
    tree = html.fromstring(resp.text)
    
    tds = tree.xpath('//td[contains(@class, "ContributionCalendar-day")]')
    tooltips = {t.attrib.get("for"): t.text for t in tree.xpath('//tool-tip') if t.text}
    
    calendar_days = []
    
    for td in tds:
        td_id = td.attrib.get("id", "")
        date_str = td.attrib.get("data-date", "")
        level = int(td.attrib.get("data-level", 0))
        
        if not date_str:
            continue
            
        tip = tooltips.get(td_id, "")
        count = 0
        if tip:
            match = re.search(r'(\d+)\s+contribution', tip)
            if match:
                count = int(match.group(1))
                
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = dt.strftime("%A")
        
        calendar_days.append({
            "date": date_str,
            "count": count,
            "level": level,
            "weekday": weekday
        })
        
    # Sort chronologically
    calendar_days.sort(key=lambda x: x["date"])
    
    # Calculate statistics
    total_contributions = sum(d["count"] for d in calendar_days)
    
    # Calculate streaks
    longest_streak = 0
    current_temp = 0
    for d in calendar_days:
        if d["count"] > 0:
            current_temp += 1
            if current_temp > longest_streak:
                longest_streak = current_temp
        else:
            current_temp = 0
            
    # Calculate current streak
    current_streak = 0
    # Search backwards from the end
    for d in reversed(calendar_days):
        if d["count"] > 0:
            current_streak += 1
        elif current_streak == 0:
            # If latest day has 0, check if previous day had commits
            continue
        else:
            break
            
    # Calculate busiest day of week
    weekday_counts = {w: 0 for w in DAYS_OF_WEEK}
    for d in calendar_days:
        weekday_counts[d["weekday"]] += d["count"]
        
    busiest_day = max(weekday_counts.items(), key=lambda x: x[1])[0] if total_contributions > 0 else "N/A"
    
    data = {
        "username": username,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "busiest_day": busiest_day,
        "days": calendar_days
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully saved contribution data to {output_path}")
    print(f"Stats: Total={total_contributions}, Current Streak={current_streak}, Longest Streak={longest_streak}, Busiest={busiest_day}")

if __name__ == "__main__":
    pull_contributions()
