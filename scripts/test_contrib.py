import urllib.request
import re
from datetime import datetime, date

def fetch_actual_contributions(login="Harsh33t"):
    url = f"https://github.com/users/{login}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode("utf-8")

    # Map id -> date
    td_matches = re.findall(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-[^"]+)"', html)
    id_to_date = {c_id: d_str for d_str, c_id in td_matches}

    # Map id -> count from tool-tip
    id_to_count = {}
    tooltips = re.findall(r'<tool-tip[^>]*for="(contribution-day-component-[^"]+)"[^>]*>([^<]+)</tool-tip>', html)
    for c_id, text in tooltips:
        match = re.search(r'(\d+|No)\s+contribution', text)
        if match:
            cnt_str = match.group(1)
            id_to_count[c_id] = 0 if cnt_str == "No" else int(cnt_str)

    # Build sorted days list
    days_dict = {}
    for c_id, d_str in id_to_date.items():
        cnt = id_to_count.get(c_id, 0)
        days_dict[d_str] = cnt

    sorted_dates = sorted(days_dict.keys())
    days = [{"date": d_str, "contributionCount": days_dict[d_str]} for d_str in sorted_dates]
    return days

def calculate_streaks(days):
    best = {"length": 0, "start": None, "end": None}
    run, run_start = 0, None
    for d in days:
        if d["contributionCount"] > 0:
            run += 1
            run_start = run_start or d["date"]
            if run > best["length"]:
                best = {"length": run, "start": run_start, "end": d["date"]}
        else:
            run, run_start = 0, None

    cur = {"length": 0, "start": None, "end": None}
    tail = days[:-1] if days and days[-1]["contributionCount"] == 0 else days
    for d in reversed(tail):
        if d["contributionCount"] == 0:
            break
        cur["length"] += 1
        cur["start"] = d["date"]
        cur["end"] = cur["end"] or d["date"]
    return cur, best

if __name__ == "__main__":
    days = fetch_actual_contributions("Harsh33t")
    print(f"Total parsed days: {len(days)}")
    total = sum(d["contributionCount"] for d in days)
    print(f"Total contributions: {total}")
    active = sum(1 for d in days if d["contributionCount"] > 0)
    print(f"Active days: {active}")
    cur, best = calculate_streaks(days)
    print(f"Current Streak: {cur['length']} days ({cur['start']} to {cur['end']})")
    print(f"Longest Streak: {best['length']} days ({best['start']} to {best['end']})")
    print("\nNon-zero contribution sample:", [d for d in days if d["contributionCount"] > 0][:15])
