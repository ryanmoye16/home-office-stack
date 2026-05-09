#!/usr/bin/env python3
"""
audit_images.py — Verify all Amazon image URLs in featured-products.json
before every push. Fail fast if any image returns non-200.

Usage:
    python3 scripts/audit_images.py
    python3 scripts/audit_images.py --fix  # attempt to auto-fix broken URLs

Exit codes:
    0 = all images valid
    1 = one or more images broken (will print which ones)
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO = Path(__file__).parent.parent
DATA_FILE = REPO / "data" / "featured-products.json"
AMAZON_IMAGE_RE = "https://m.media-amazon.com/images/I/"


def check_image(url: str, timeout: int = 5) -> tuple[bool, str]:
    """Return (success, status_line)."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, f"HTTP/{resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP/{e.code}"
    except Exception as e:
        return False, str(e)


def extract_code(url: str) -> str:
    """Pull the image code from a URL like .../71zuiK5poRL._SL500_.jpg"""
    # Remove base + extract code before ._SL500_
    code = url.replace(AMAZON_IMAGE_RE, "").split("._SL500_")[0]
    return code


def main():
    with open(DATA_FILE) as f:
        data = json.load(f)

    products = data.get("desk_gear", [])
    if not products:
        print(f"ERROR: No products found in {DATA_FILE}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Checking {len(products)} products...")
    print()

    broken = []
    checked = []

    for p in products:
        url = p.get("amazon_image", "")
        if not url:
            broken.append((p["slug"], "MISSING", "No amazon_image field"))
            continue

        if AMAZON_IMAGE_RE not in url:
            broken.append((p["slug"], "BAD FORMAT", f"URL doesn't match expected pattern: {url}"))
            continue

        code = extract_code(url)
        ok, status = check_image(url)
        checked.append((p["slug"], code, ok, status))

        if not ok:
            broken.append((p["slug"], code, status))

    # Print results
    for slug, code, ok, status in checked:
        icon = "✅" if ok else "❌"
        print(f"  {icon} {code} — {slug}: {status}")

    print()
    if broken:
        print(f"❌ {len(broken)} BROKEN IMAGE(S):")
        for slug, code, reason in broken:
            print(f"  • {slug} ({code}): {reason}")
        print()
        print("Fix: Verify correct image code from Amazon product page,")
        print("     then update data/featured-products.json")
        sys.exit(1)
    else:
        print(f"✅ All {len(checked)} image URLs return HTTP 200")
        sys.exit(0)


if __name__ == "__main__":
    main()