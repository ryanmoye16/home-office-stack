
/* Affiliate outbound-click instrumentation (GA4).
   Fires an `affiliate_click` event on clicks to Amazon product pages
   (/dp/ links and pick-card window.open handlers) and to Systeme.io
   affiliate links (sa= parameter). Pageviews alone cannot show which
   pages send revenue clicks; this closes that gap. Added 2026-10-25
   under the full-ownership plan, P0 item 2. */
(function () {
  if (window.__affiliateClickTracking) return;
  window.__affiliateClickTracking = true;

  function destinationFromOnclick(el) {
    var oc = el.getAttribute && el.getAttribute("onclick");
    if (!oc) return null;
    var match = oc.match(/https?:\/\/[^\s'")]+/);
    return match ? match[0] : null;
  }

  function affiliateDestination(url) {
    try {
      var parsed = new URL(url, window.location.href);
      if (parsed.hostname === "www.amazon.com" && parsed.pathname.indexOf("/dp/") === 0) return parsed;
      if (parsed.hostname === "systeme.io" && parsed.search.indexOf("sa=") !== -1) return parsed;
      return null;
    } catch (err) {
      return null;
    }
  }

  document.addEventListener("click", function (event) {
    var el = event.target;
    if (!el || typeof el.closest !== "function") return;
    var anchor = el.closest("a[href]");
    var url = anchor ? anchor.href : null;
    var sourceEl = anchor || el;
    if (!url) {
      var card = el.closest("[onclick]");
      if (card) {
        url = destinationFromOnclick(card);
        sourceEl = card;
      }
    }
    if (!url) return;
    var dest = affiliateDestination(url);
    if (!dest) return;
    if (typeof window.gtag !== "function") return;
    window.gtag("event", "affiliate_click", {
      destination_host: dest.hostname,
      destination_path: dest.pathname,
      page_path: window.location.pathname,
      link_text: (sourceEl.textContent || "").trim().replace(/\s+/g, " ").slice(0, 80),
      transport_type: "beacon"
    });
  }, true);
})();
