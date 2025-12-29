#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

ROOT_PMMS_JSON = "pmms.json"

# Prefer your Worker endpoint (avoid FreddieMac 403)
DEFAULT_SOURCE = "https://michiganmortgagecalculator.org/api/pmms"

def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (GitHub Actions) MichiganMortgageCalculator/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)

def read_existing(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

def main():
    source = os.environ.get("PMMS_SOURCE", DEFAULT_SOURCE)
    print(f"[update_pmms] Source: {source}")

    existing = read_existing(ROOT_PMMS_JSON)

    try:
        incoming = fetch_json(source)
    except Exception as e:
        print(f"[update_pmms] ERROR fetching source: {e}", file=sys.stderr)
        # Do NOT fail the workflow if the endpoint is down; keep last known rates
        # If you WANT it to fail hard, change exit code to 1.
        print("[update_pmms] Keeping existing pmms.json (no update).")
        return 0

    # Accept several possible key formats
    # Your current format:
    # { "pmms30yr": 6.23, "pmms15yr": 5.51, ... }
    pmms30 = incoming.get("pmms30yr", incoming.get("30-year"))
    pmms15 = incoming.get("pmms15yr", incoming.get("15-year"))

    if pmms30 is None or pmms15 is None:
        print("[update_pmms] ERROR: Source JSON missing pmms30yr/pmms15yr (or 30-year/15-year).", file=sys.stderr)
        print(f"[update_pmms] Got keys: {list(incoming.keys())}", file=sys.stderr)
        return 1

    out = {
        "pmms30yr": float(pmms30),
        "pmms15yr": float(pmms15),
        "source": incoming.get("source", source),
        "lastUpdatedUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if existing == out:
        print("[update_pmms] No change.")
        return 0

    write_json(ROOT_PMMS_JSON, out)
    print("[update_pmms] Wrote pmms.json:", out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
