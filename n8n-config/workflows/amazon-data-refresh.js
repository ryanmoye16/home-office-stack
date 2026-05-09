// n8n Workflow: Weekly Amazon Data Refresh
// Run every Monday at 8am
// Scrapes live Amazon prices/ratings/reviews for all products
// Updates HTML files, pushes to GitHub, notifies Telegram if anything changed

const path = require('path');
const fs = require('fs');

// Load ASIN data
const configPath = '/Users/ryanmoye/budget-tech-picks/n8n-config/asin-data.json';
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Results accumulator
const results = {
  updated: [],
  unchanged: [],
  errors: []
};

for (const product of config.products) {
  try {
    // Fetch Amazon product page
    const url = `https://www.amazon.com/dp/${product.asin}`;
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
    });

    if (!response.ok) {
      results.errors.push({ product: product.name, error: `HTTP ${response.status}` });
      continue;
    }

    const html = await response.text();

    // Extract price
    let price = null;
    const priceMatch = html.match(/"priceAmount":\s*([0-9.]+)/);
    if (priceMatch) {
      price = parseFloat(priceMatch[1]);
    } else {
      // Fallback: look for whole dollar amount
      const altPriceMatch = html.match(/class="a-price-whole">([0-9,]+)/);
      if (altPriceMatch) {
        price = parseFloat(altPriceMatch[1].replace(',', ''));
      }
    }

    // Extract rating
    let rating = null;
    const ratingMatch = html.match(/"ratingValue":\s*"([0-9.]+)"/);
    if (ratingMatch) {
      rating = parseFloat(ratingMatch[1]);
    }

    // Extract review count
    let reviews = null;
    const reviewsMatch = html.match(/"reviewCount":\s*"([0-9,]+)"/);
    if (reviewsMatch) {
      reviews = parseInt(reviewsMatch[1].replace(/,/g, ''));
    } else {
      const altRevMatch = html.match(/id="acrCustomerReviewText"[^>]*>.*?([0-9,]+)\s+review/i);
      if (altRevMatch) {
        reviews = parseInt(altRevMatch[1].replace(/,/g, ''));
      }
    }

    // Check if anything changed
    const priceChanged = price && Math.abs(price - product.currentPrice) > 0.01;
    const ratingChanged = rating && rating !== product.currentRating;
    const reviewsChanged = reviews && reviews !== product.currentReviews;

    if (priceChanged || ratingChanged || reviewsChanged) {
      results.updated.push({
        name: product.name,
        slug: product.slug,
        changes: {
          price: priceChanged ? { from: product.currentPrice, to: price } : null,
          rating: ratingChanged ? { from: product.currentRating, to: rating } : null,
          reviews: reviewsChanged ? { from: product.currentReviews, to: reviews } : null
        }
      });

      // Update local config
      if (price) product.currentPrice = price;
      if (rating) product.currentRating = rating;
      if (reviews) product.currentReviews = reviews;
      product.lastChecked = new Date().toISOString().split('T')[0];
    } else {
      results.unchanged.push(product.name);
      product.lastChecked = new Date().toISOString().split('T')[0];
    }

  } catch (err) {
    results.errors.push({ product: product.name, error: err.message });
  }
}

// Save updated config
fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

// Return results for downstream nodes
return {
  updated: results.updated,
  unchanged: results.unchanged,
  errors: results.errors,
  hasChanges: results.updated.length > 0
};
