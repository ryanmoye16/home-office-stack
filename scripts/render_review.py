#!/usr/bin/env python3
"""
render_review.py — Generate a review page HTML from the Jinja2 template.

Usage:
    python3 render_review.py <slug> [data_key]

Examples:
    python3 render_review.py anker-7in1-hub
    python3 render_review.py my-new-product  # uses featured-products.json

The product data is read from data/featured-products.json by slug.
Output is written to reviews/<slug>.html
"""

import json
import sys
from pathlib import Path
from jinja2 import Template

REPO = Path(__file__).parent.parent
TEMPLATE_FILE = REPO / "templates" / "review-page.html"
DATA_FILE = REPO / "data" / "featured-products.json"
OUTPUT_DIR = REPO / "reviews"
AMAZON_TAG = "homeofficestack-20"


def load_product(slug: str):
    with open(DATA_FILE) as f:
        data = json.load(f)
    for p in data["desk_gear"]:
        if p["slug"] == slug:
            return p
    print(f"ERROR: Product '{slug}' not found in {DATA_FILE}", file=sys.stderr)
    print("Available slugs:", [p["slug"] for p in data["desk_gear"]], file=sys.stderr)
    sys.exit(1)


def render_review(product):
    template_text = TEMPLATE_FILE.read_text()
    template = Template(template_text)
    return template.render(product=product, amazon_tag=AMAZON_TAG)


def main():
    if len(sys.argv) < 2:
        print("Usage: render_review.py <slug>", file=sys.stderr)
        sys.exit(1)

    slug = sys.argv[1]
    product = load_product(slug)
    html = render_review(product)

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{slug}.html"
    # Strip leading/trailing whitespace to avoid double newlines
    output_path.write_text(html.strip())
    print(f"✅ Generated {output_path}")


if __name__ == "__main__":
    main()
