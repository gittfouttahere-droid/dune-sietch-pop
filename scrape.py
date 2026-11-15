"""Append per-sietch online counts for one Dune: Awakening World to a CSV.

Source: dunestatus.com/worlds/<world> (third-party). Stdlib only.
"""
import csv, datetime as dt, os, re, sys, urllib.request

WORLD = os.environ.get("WORLD", "umma")
OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", f"{WORLD}.csv"))
URL = f"https://dunestatus.com/worlds/{WORLD}"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (sietch-pop logger)"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8").replace('\\"', '"')

rows = {}
for rec in re.findall(r'\{"ServerId":"[^"]+","DimensionIndex":\d+.*?\}', html):
    name = re.search(r'"DisplayName":"([^"]+)"', rec)
    cnt = re.search(r'"CurrentConcurrentPlayerCount":(\d+)', rec)
    cap = re.search(r'"MaxConcurrentPlayerCapacity":(\d+)', rec)
    seen = re.search(r'"LastSeen":(\d+)', rec)
    status = re.search(r'"ServerStatus":(\d+)', rec)
    if name and cnt:
        rows[name.group(1).strip()] = (
            int(cnt.group(1)),
            int(cap.group(1)) if cap else "",
            int(seen.group(1)) if seen else "",
            int(status.group(1)) if status else "",
        )

if not rows:
    sys.exit("no sietch records found - page format may have changed")

now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
new = not os.path.exists(OUT)
with open(OUT, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["fetched_utc", "sietch", "players", "capacity", "source_lastseen_epoch", "server_status"])
    for name in sorted(rows):
        w.writerow([now, name, *rows[name]])
print(f"{now}: wrote {len(rows)} sietches to {OUT}")
