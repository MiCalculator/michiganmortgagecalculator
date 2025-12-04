import json
import re
import urllib.request
import datetime

PMMS_URL = "https://www.freddiemac.com/pmms"

def fetch_html(url):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def main():
    html = fetch_html(PMMS_URL)

    # Look for:
    # "The 30-year fixed-rate mortgage averaged 6.23% ..."
    # "The 15-year fixed-rate mortgage averaged 5.51% ..."
    m30 = re.search(r"30-year fixed-rate mortgage averaged\s+([\d.]+)%", html, re.IGNORECASE)
    m15 = re.search(r"15-year fixed-rate mortgage averaged\s+([\d.]+)%", html, re.IGNORECASE)

    pmms30 = 6.23  # fallback
    pmms15 = 5.51  # fallback

    if m30:
        pmms30 = float(m30.group(1))
    if m15:
        pmms15 = float(m15.group(1))

    data = {
        "pmms30yr": pmms30,
        "pmms15yr": pmms15,
        "source": PMMS_URL,
        "lastUpdatedUtc": datetime.datetime.utcnow().isoformat() + "Z"
    }

    with open("pmms.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print("Updated pmms.json with:", data)

if __name__ == "__main__":
    main()
