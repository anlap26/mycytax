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
  "trezor": "#AFFILIATE_TREZOR",
  "binance": "#AFFILIATE_BINANCE",
  "bybit": "#AFFILIATE_BYBIT",
  "interactivebrokers": "#AFFILIATE_INTERACTIVEBROKERS",
  "wise": "#AFFILIATE_WISE",
  "genki": "#AFFILIATE_GENKI",
  "semrush": "#AFFILIATE_SEMRUSH"
};
