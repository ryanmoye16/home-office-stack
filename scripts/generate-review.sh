#!/bin/bash
# =============================================================================
# Generate Review - Creates a new review page from the template
# =============================================================================
# Hermes fills in the placeholders, then validation+publish ensure consistency.
# =============================================================================

set -euo pipefail

SITE_DIR="${SITE_DIR:-$HOME/budget-tech-picks}"
TEMPLATE="$SITE_DIR/templates/review-template.html"
REVIEWS_DIR="$SITE_DIR/reviews"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

usage() {
    echo "Generate a new review page from template."
    echo ""
    echo "Usage:"
    echo "  $0 <output-file.html> <field1=value> <field2=value> ..."
    echo ""
    echo "Required fields:"
    echo "  PRODUCT_NAME       - Full product name"
    echo "  ASIN               - Amazon ASIN (e.g., B0CQXMT3QC)"
    echo "  CATEGORY_SLUG      - Category URL slug (e.g., monitor-arms)"
    echo "  CATEGORY_NAME      - Display name (e.g., Monitor Arms)"
    echo ""
    echo "Optional fields:"
    echo "  BRAND_NAME         - Brand (default: extracted from PRODUCT_NAME)"
    echo "  PRICE              - Price string (e.g., \$35.99)"
    echo "  RATING             - Number 1-5 (default: 4.0)"
    echo "  RATING_STARS       - Unicode stars (default: ★★★)"
    echo "  META_DESCRIPTION   - Meta description (auto-generated if missing)"
    echo ""
    echo "Example:"
    echo "  $0 new-product.html PRODUCT_NAME=\"Ergotron LX\" ASIN=\"B00JQB4N8G\" CATEGORY_SLUG=\"monitor-arms\" CATEGORY_NAME=\"Monitor Arms\""
    exit 1
}

# Check args
if [[ $# -lt 2 ]]; then
    usage
fi

OUTPUT_FILE="$1"
shift

# Parse fields into individual variables using a simple function
while [[ $# -gt 0 ]]; do
    case "$1" in
        PRODUCT_NAME=*) PRODUCT_NAME="${1#*=}" ;;
        ASIN=*) ASIN="${1#*=}" ;;
        CATEGORY_SLUG=*) CATEGORY_SLUG="${1#*=}" ;;
        CATEGORY_NAME=*) CATEGORY_NAME="${1#*=}" ;;
        BRAND_NAME=*) BRAND_NAME="${1#*=}" ;;
        PRICE=*) PRICE="${1#*=}" ;;
        RATING=*) RATING="${1#*=}" ;;
        RATING_STARS=*) RATING_STARS="${1#*=}" ;;
        META_DESCRIPTION=*) META_DESCRIPTION="${1#*=}" ;;
        AMAZON_IMAGE_URL=*) AMAZON_IMAGE_URL="${1#*=}" ;;
        *) ;;
    esac
    shift
done

# Validate required fields
if [[ -z "$PRODUCT_NAME" ]]; then
    echo -e "${RED}✗ PRODUCT_NAME is required${NC}"
    exit 1
fi

if [[ -z "$ASIN" ]]; then
    echo -e "${RED}✗ ASIN is required${NC}"
    exit 1
fi

if [[ -z "$CATEGORY_SLUG" ]]; then
    echo -e "${RED}✗ CATEGORY_SLUG is required${NC}"
    exit 1
fi

if [[ -z "$CATEGORY_NAME" ]]; then
    echo -e "${RED}✗ CATEGORY_NAME is required${NC}"
    exit 1
fi

# Resolve output path
if [[ ! "$OUTPUT_FILE" = /* ]]; then
    OUTPUT_FILE="$REVIEWS_DIR/$OUTPUT_FILE"
fi

# Set defaults
RATING="${RATING:-4.0}"
RATING_STARS="${RATING_STARS:-★★★★☆}"

# Auto-generate some fields
BRAND_NAME="${BRAND_NAME:-$(echo "$PRODUCT_NAME" | awk '{print $1}')}"
META_DESCRIPTION="${META_DESCRIPTION:-Review of $PRODUCT_NAME. $BRAND_NAME product for home office. Honest testing, pros and cons, and our recommendation.}"
REVIEW_SUBTITLE="A closer look at $PRODUCT_NAME for your home office setup."
AMAZON_IMAGE_URL="${AMAZON_IMAGE_URL:-https://m.media-amazon.com/images/I/placeholder._SL500_.jpg}"

# Generate date and filename
DATE_PUBLISHED=$(date +%Y-%m-%d)
FILENAME=$(basename "$OUTPUT_FILE" .html)

# Verdicts based on rating
if command -v bc &>/dev/null; then
    if (( $(echo "$RATING >= 4.5" | bc -l) )); then
        VERDICT_LABEL="out of 5 — Excellent"
    elif (( $(echo "$RATING >= 4.0" | bc -l) )); then
        VERDICT_LABEL="out of 5 — Good Value"
    elif (( $(echo "$RATING >= 3.0" | bc -l) )); then
        VERDICT_LABEL="out of 5 — Decent"
    else
        VERDICT_LABEL="out of 5 — Skip It"
    fi
else
    # Fallback without bc
    if [[ $(echo "$RATING >= 4.5" | awk '{print ($1 >= 4.5)?"1":"0"}') == "1" ]]; then
        VERDICT_LABEL="out of 5 — Excellent"
    elif [[ $(echo "$RATING >= 4.0" | awk '{print ($1 >= 4.0)?"1":"0"}') == "1" ]]; then
        VERDICT_LABEL="out of 5 — Good Value"
    elif [[ $(echo "$RATING >= 3.0" | awk '{print ($1 >= 3.0)?"1":"0"}') == "1" ]]; then
        VERDICT_LABEL="out of 5 — Decent"
    else
        VERDICT_LABEL="out of 5 — Skip It"
    fi
fi

# =============================================================================
# Build the review file
# =============================================================================

echo "Generating review: $OUTPUT_FILE"

cp "$TEMPLATE" "$OUTPUT_FILE"

# Replace all placeholders using sed
# The sed substitutions below handle all the template variables

sed -i '' "s/{{PRODUCT_NAME}}/$PRODUCT_NAME/g" "$OUTPUT_FILE"
sed -i '' "s/{{ASIN}}/$ASIN/g" "$OUTPUT_FILE"
sed -i '' "s/{{CATEGORY_SLUG}}/$CATEGORY_SLUG/g" "$OUTPUT_FILE"
sed -i '' "s/{{CATEGORY_NAME}}/$CATEGORY_NAME/g" "$OUTPUT_FILE"
sed -i '' "s/{{BRAND_NAME}}/$BRAND_NAME/g" "$OUTPUT_FILE"
sed -i '' "s/{{PRICE}}/$PRICE/g" "$OUTPUT_FILE"
sed -i '' "s/{{RATING}}/$RATING/g" "$OUTPUT_FILE"
sed -i '' "s/{{RATING_STARS}}/$RATING_STARS/g" "$OUTPUT_FILE"
sed -i '' "s/{{META_DESCRIPTION}}/$META_DESCRIPTION/g" "$OUTPUT_FILE"
sed -i '' "s/{{OG_DESCRIPTION}}/$META_DESCRIPTION/g" "$OUTPUT_FILE"
sed -i '' "s/{{REVIEW_SUBTITLE}}/$REVIEW_SUBTITLE/g" "$OUTPUT_FILE"
sed -i '' "s|{{AMAZON_IMAGE_URL}}|$AMAZON_IMAGE_URL|g" "$OUTPUT_FILE"
sed -i '' "s/{{DATE_PUBLISHED}}/$DATE_PUBLISHED/g" "$OUTPUT_FILE"
sed -i '' "s/{{FILE_NAME}}/$FILENAME/g" "$OUTPUT_FILE"
sed -i '' "s|{{SITE_URL}}|https://homeofficestack.com|g" "$OUTPUT_FILE"
sed -i '' "s/{{VERDICT_LABEL}}/$VERDICT_LABEL/g" "$OUTPUT_FILE"

# Category nav placeholders
sed -i '' "s/{{CATEGORY_SLUG_1}}/$CATEGORY_SLUG/g" "$OUTPUT_FILE"
sed -i '' "s/{{CATEGORY_NAME_1}}/$CATEGORY_NAME/g" "$OUTPUT_FILE"

# Placeholder content (Hermes should replace these)
sed -i '' 's|{{VERDICT_PARAGRAPH}}|[Hermes: Write 2-3 sentences summarizing your verdict here.]|g' "$OUTPUT_FILE"
sed -i '' 's|{{SPECS_TABLE}}|[Hermes: Add specifications in table format]|g' "$OUTPUT_FILE"
sed -i '' 's|{{LIKED_CONTENT}}|[Hermes: Write about what you liked]|g' "$OUTPUT_FILE"
sed -i '' 's|{{IMPROVEMENTS_CONTENT}}|[Hermes: Write about what could be better]|g' "$OUTPUT_FILE"
sed -i '' 's|{{PERFORMANCE_CONTENT}}|[Hermes: Write about real-world performance]|g' "$OUTPUT_FILE"
sed -i '' 's|{{BOTTOM_LINE}}|<p>[Hermes: Write your bottom line recommendation]</p>|g' "$OUTPUT_FILE"
sed -i '' 's|{{QUICK_FACTS}}|<li>[Hermes: Add pros and cons]</li>|g' "$OUTPUT_FILE"
sed -i '' 's/{{BADGE_TEXT}}/Recommended/g' "$OUTPUT_FILE"
sed -i '' 's/{{CARD_SUBTITLE}}/[Product type]/g' "$OUTPUT_FILE"
sed -i '' 's/{{REVIEW_SUMMARY}}/[Hermes: Write 1-2 sentences for JSON-LD schema]/g' "$OUTPUT_FILE"

# Clear any remaining placeholders
sed -i '' 's/{{[A-Z_]*}}/[FILL IN]/g' "$OUTPUT_FILE"

echo ""
echo -e "${GREEN}✓ Review generated: $OUTPUT_FILE${NC}"
echo ""
echo "Next steps:"
echo "  1. Fill in the [FILL IN] placeholders with your content"
echo "  2. Get the actual Amazon image URL"
echo "  3. Run: ./scripts/validate-review.sh $OUTPUT_FILE"
echo "  4. If validation passes, run: ./scripts/publish-review.sh $OUTPUT_FILE"
echo ""

exit 0