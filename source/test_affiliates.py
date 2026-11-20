# -*- coding: utf-8 -*-
"""Partner buttons read one config. No network."""
import json
import os
import re
import unittest

import build


HERE = os.path.dirname(os.path.abspath(__file__))
NEW_GUIDES = ("store-savings-and-crypto", "international-brokers", "vpn-abroad")
CALC_KEYS = {
    "capital-gains": "ledger",
    "rental-yield": "interactivebrokers",
}
NO_OFFER = ("transfer-fees", "stamp-duty", "vat", "mortgage")


def ld_objects(html):
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html):
        out.append(json.loads(raw.replace("<\\/", "</")))
    return out


class AffiliateTests(unittest.TestCase):
    def test_config_is_the_only_list_of_partner_keys(self):
        data = build.load_affiliates()
        self.assertEqual(set(build.AFFILIATE_KEYS), set(data))
        for key in build.AFFILIATE_KEYS:
            if key == "amazon":
                self.assertEqual(data[key], "https://www.amazon.de/?tag=cynews24-21")
            else:
                self.assertEqual(data[key], "#AFFILIATE_" + key.upper())
            self.assertTrue(build._affiliate_url_ok(data[key]))
        self.assertEqual(
            build.amazon_search_url("Belegscanner"),
            "https://www.amazon.de/s?k=Belegscanner&tag=cynews24-21",
        )
        self.assertEqual(
            build.amazon_search_url("Buchhaltung Buch"),
            "https://www.amazon.de/s?k=Buchhaltung%20Buch&tag=cynews24-21",
        )
        self.assertNotIn("/dp/", build.amazon_search_url("Smart Lock"))
        self.assertFalse(build._affiliate_url_ok("javascript:alert(1)"))
        self.assertFalse(build._affiliate_url_ok("http://example.com"))
        self.assertFalse(build._affiliate_url_ok("https://ok.example/a b"))
        self.assertTrue(build._affiliate_url_ok("https://example.com/path?a=1&b=2"))

    def test_bad_config_is_rejected(self):
        path = os.path.join(HERE, "static", "affiliates.js")
        with open(path, encoding="utf8") as handle:
            raw = handle.read()
        broken = raw.replace("#AFFILIATE_LEDGER", "javascript:alert(1)")
        tmp = os.path.join(HERE, "_affiliates_bad.js")
        try:
            with open(tmp, "w", encoding="utf8") as handle:
                handle.write(broken)
            with self.assertRaises(SystemExit):
                build.load_affiliates(tmp)
        finally:
            if os.path.isfile(tmp):
                os.remove(tmp)

    def test_guides_have_buttons_disclosure_and_schema(self):
        expected = {
            "store-savings-and-crypto": ["ledger", "trezor", "binance", "bybit"],
            "international-brokers": ["interactivebrokers"],
            "vpn-abroad": ["nordvpn", "surfshark", "proton"],
        }
        for lang in build.LANGS:
            for slug, keys in expected.items():
                html = build.guide_page(lang, slug, [])
                self.assertIn(f'<html lang="{lang}">', html)
                self.assertIn(f'rel="canonical" href="https://mycytax.com{build.loc(lang, "/guides/"+slug+"/")}"', html)
                for l in build.LANGS:
                    self.assertIn(f'hreflang="{l}"', html)
                self.assertIn('hreflang="x-default"', html)
                self.assertIn('class="faq"', html)
                self.assertIn('class="aff-disclosure"', html)
                self.assertIn(build.UI[lang]["aff_note"], html)
                self.assertIn(build.href(build.loc(lang, "/affiliate-disclosure/")), html)
                self.assertIn("assets/js/affiliates.js", html)
                self.assertNotIn("currenciesdirect.com", html)
                self.assertNotIn('class="partners"', html)
                for key in keys:
                    self.assertIn(f'data-affiliate="{key}"', html)
                    self.assertIn(f'href="{build.affiliate_href(key)}"', html)
                for tag in re.findall(r'<a class="aff-btn"[^>]*>', html):
                    self.assertIn('rel="nofollow sponsored noopener"', tag)
                    self.assertIn('target="_blank"', tag)
                    self.assertNotIn("noreferrer", tag)
                types = {obj.get("@type") for obj in ld_objects(html)}
                self.assertIn("Article", types)
                self.assertIn("FAQPage", types)
                article = next(obj for obj in ld_objects(html) if obj.get("@type") == "Article")
                meta, _ = build.load_md(lang, slug)
                self.assertEqual(article["headline"], meta["title"])
                self.assertEqual(article["description"], meta["description"])
                self.assertTrue(article["datePublished"])
                faq = next(obj for obj in ld_objects(html) if obj.get("@type") == "FAQPage")
                self.assertGreaterEqual(len(faq["mainEntity"]), 4)
                for q in faq["mainEntity"]:
                    self.assertTrue(q["name"])
                    self.assertTrue(q["acceptedAnswer"]["text"])

    def test_each_calculator_has_one_matching_widget(self):
        for lang in build.LANGS:
            for slug, key in CALC_KEYS.items():
                html = build.calc_page(lang, slug)
                self.assertEqual(html.count('class="aff-offer aff-calc"'), 1)
                self.assertIn(f'data-affiliate-widget="{key}"', html)
                self.assertIn(f'data-affiliate="{key}"', html)
                self.assertIn(f'href="{build.affiliate_href(key)}"', html)
                self.assertIn('rel="nofollow sponsored noopener"', html)
                self.assertIn(build.UI[lang]["aff_note"], html)
                self.assertLess(html.index('id="calc"'), html.index("aff-calc"))
                self.assertLess(html.index("aff-calc"), html.index('class="cta"'))
                self.assertIn("assets/js/affiliates.js", html)
                self.assertIn(build.href(build.loc(lang, "/guides/" + build.CALC_OFFERS[slug]["guide"] + "/")), html)
            for slug in NO_OFFER:
                html = build.calc_page(lang, slug)
                self.assertEqual(html.count('class="aff-offer aff-calc"'), 0)
                self.assertNotIn("data-affiliate-widget=", html)

    def test_disclosure_page_is_in_the_footer_sitemap_and_index(self):
        for lang in build.LANGS:
            footer = build.footer(lang)
            path = build.loc(lang, "/affiliate-disclosure/")
            self.assertIn(build.href(path), footer)
            page = build.static_page(lang, "affiliate-disclosure")
            self.assertIn(f'rel="canonical" href="https://mycytax.com{path}"', page)
            self.assertNotIn("data-affiliate=", page)
            self.assertNotIn("assets/js/affiliates.js", page)
            listing = build.listing(lang, "guides")
            for slug in NEW_GUIDES:
                self.assertIn(build.href(build.loc(lang, "/guides/" + slug + "/")), listing)
        xml = build.sitemap()
        for lang in build.LANGS:
            for slug in NEW_GUIDES:
                self.assertIn(f"<loc>https://mycytax.com{build.loc(lang, '/guides/' + slug + '/')}</loc>", xml)
            self.assertIn(f"<loc>https://mycytax.com{build.loc(lang, '/affiliate-disclosure/')}</loc>", xml)
        feed = build.atom_feed("en")
        self.assertIn("https://mycytax.com/guides/vpn-abroad/", feed)

    def test_existing_partner_box_is_unchanged(self):
        html = build.calc_page("en", "transfer-fees")
        self.assertIn('class="partners"', html)
        self.assertIn('href="https://www.currenciesdirect.com/"', html)
        self.assertIn('rel="sponsored noopener"', html)
        self.assertEqual(html.count("data-affiliate="), 0)


if __name__ == "__main__":
    unittest.main()
