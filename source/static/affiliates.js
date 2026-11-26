/* MyCyTax partner links.

   This is the only file that holds partner URLs. Every partner button on the
   site reads this object (the build writes the same address into the HTML, and
   the page script applies it again from here).

   Replace a placeholder with the real https:// link when you have it.
   Keep the key. A value must be either #AFFILIATE_NAME or an https:// URL
   with no spaces. Do not paste links into the HTML.

   genki and semrush are reserved. No page shows them until a
   guide or calculator names that key. */
window.MYCYTAX_AFFILIATES = {
  "nordvpn": "#AFFILIATE_NORDVPN",
  "surfshark": "#AFFILIATE_SURFSHARK",
  "proton": "#AFFILIATE_PROTON",
  "ledger": "#AFFILIATE_LEDGER",
  "trezor": "https://affil.trezor.io/aff_c?offer_id=352&aff_id=847056",
  "binance": "#AFFILIATE_BINANCE",
  "bybit": "#AFFILIATE_BYBIT",
  "interactivebrokers": "#AFFILIATE_INTERACTIVEBROKERS",
  "genki": "#AFFILIATE_GENKI",
  "semrush": "#AFFILIATE_SEMRUSH",
  "amazon": "https://www.amazon.de/?tag=cynews24-21"
};

/* Search link for a type of product. No ASINs. The tag comes from the amazon entry. */
window.MYCYTAX_AMAZON_SEARCH = function (query) {
  var base = (window.MYCYTAX_AFFILIATES && window.MYCYTAX_AFFILIATES.amazon) || "";
  var tag = "cynews24-21";
  var origin = "https://www.amazon.de";
  var match = /[?&]tag=([^&#]+)/.exec(base);
  if (match) tag = decodeURIComponent(match[1]);
  try {
    if (base.indexOf("https://") === 0) origin = new URL(base).origin;
  } catch (err) {}
  var q = encodeURIComponent(String(query == null ? "" : query).replace(/^\s+|\s+$/g, ""));
  return origin + "/s?k=" + q + "&tag=" + encodeURIComponent(tag);
};
