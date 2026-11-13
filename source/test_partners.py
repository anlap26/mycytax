# -*- coding: utf-8 -*-
"""Partner recommendation boxes. No network."""
import json
import os
import re
import unittest

import build


HERE = os.path.dirname(os.path.abspath(__file__))


def partner_anchors(html):
    start = html.find('class="partners"')
    if start < 0:
        return []
    end = html.find("</aside>", start)
    return re.findall(r"<a\b[^>]*>", html[start:end])


class PartnerTests(unittest.TestCase):
    def test_config_uses_public_homepages_until_affiliate_links_exist(self):
        with open(os.path.join(HERE, "partners.json"), encoding="utf-8") as handle:
            raw = json.load(handle)
        self.assertEqual(raw["heading"]["en"], "Useful services")
        self.assertEqual(raw["heading"]["ru"], "Полезные сервисы")
        self.assertEqual(raw["heading"]["el"], "Χρήσιμες υπηρεσίες")
        self.assertIn("does not change the price for you", raw["disclosure"]["en"])
        self.assertIn("партнёрскими", raw["disclosure"]["ru"])
        self.assertIn("συνεργατών", raw["disclosure"]["el"])
        by_id = {item["id"]: item for item in raw["partners"]}
        self.assertEqual(set(by_id), {"wise", "currencies-direct"})
        self.assertEqual(by_id["wise"]["url"], "https://wise.com/")
        self.assertEqual(by_id["currencies-direct"]["url"], "https://www.currenciesdirect.com/")
        for item in raw["partners"]:
            self.assertEqual(item["affiliate_url"].strip(), "")
            self.assertTrue(item["description"]["en"])
            self.assertTrue(item["description"]["ru"])
            self.assertTrue(item["description"]["el"])
            self.assertTrue(item["applies_to"])

    def test_affiliate_url_replaces_the_homepage_when_it_is_https(self):
        wise = {"name": "Wise", "url": "https://wise.com/", "affiliate_url": ""}
        self.assertEqual(build.partner_href(wise), "https://wise.com/")
        wise["affiliate_url"] = "  "
        self.assertEqual(build.partner_href(wise), "https://wise.com/")
        wise["affiliate_url"] = "https://wise.com/invite/EXAMPLE"
        self.assertEqual(build.partner_href(wise), "https://wise.com/invite/EXAMPLE")
        wise["affiliate_url"] = "javascript:alert(1)"
        self.assertEqual(build.partner_href(wise), "https://wise.com/")
        wise["url"] = "http://wise.com/"
        wise["affiliate_url"] = "not a url"
        self.assertEqual(build.partner_href(wise), "")

    def test_block_uses_the_affiliate_link_and_escapes_text(self):
        data = {
            "heading": {"en": "Useful services"},
            "disclosure": {"en": "Some links may be partner links; this does not change the price for you."},
            "partners": [
                {
                    "name": "Wise & Co <x>",
                    "url": "https://wise.com/",
                    "affiliate_url": "https://wise.com/invite/EXAMPLE?id=1&ref=a",
                    "description": {"en": 'Fees <shown> & "quoted"'},
                    "applies_to": ["guides/total-cost"],
                },
                {
                    "name": "Currencies Direct",
                    "url": "https://www.currenciesdirect.com/",
                    "affiliate_url": "",
                    "description": {"en": "Larger payments."},
                    "applies_to": ["calculators/mortgage"],
                },
            ],
        }
        guide = build.partners_block("en", "guides", "total-cost", data)
        self.assertIn('href="https://wise.com/invite/EXAMPLE?id=1&amp;ref=a"', guide)
        self.assertNotIn('href="https://wise.com/"', guide)
        self.assertIn("Wise &amp; Co &lt;x&gt;", guide)
        self.assertIn("Fees &lt;shown&gt; &amp; &quot;quoted&quot;", guide)
        self.assertNotIn("Currencies Direct", guide)
        calc = build.partners_block("en", "calculators", "mortgage", data)
        self.assertIn('href="https://www.currenciesdirect.com/"', calc)
        self.assertNotIn("wise.com", calc)
        self.assertEqual(build.partners_block("en", "guides", "non-dom", data), "")
        for tag in partner_anchors(guide):
            self.assertIn('rel="sponsored noopener"', tag)
            self.assertIn('target="_blank"', tag)
            self.assertNotIn("noreferrer", tag)

    def test_relevant_pages_show_the_box_before_telegram(self):
        pages = set()
        for partner in build.PARTNERS["partners"]:
            pages.update(partner["applies_to"])
        self.assertIn("guides/buying-as-a-foreigner", pages)
        self.assertIn("guides/off-plan", pages)
        self.assertIn("guides/total-cost", pages)
        self.assertIn("guides/renting-out", pages)
        self.assertIn("guides/residence-permit", pages)
        self.assertIn("guides/tax-residency", pages)
        self.assertIn("calculators/transfer-fees", pages)
        self.assertIn("calculators/stamp-duty", pages)
        self.assertIn("calculators/vat", pages)
        self.assertIn("calculators/rental-yield", pages)
        self.assertIn("calculators/mortgage", pages)
        self.assertNotIn("guides/selling-and-taxes", pages)
        self.assertNotIn("guides/non-dom", pages)
        self.assertNotIn("guides/title-deeds", pages)
        self.assertNotIn("guides/taxes-overview", pages)
        self.assertNotIn("calculators/capital-gains", pages)

        for lang in build.LANGS:
            heading = build.PARTNERS["heading"][lang]
            disclosure = build.PARTNERS["disclosure"][lang]
            for slug in build.GUIDE_ORDER:
                html = build.guide_page(lang, slug, [])
                if f"guides/{slug}" in pages:
                    self.assertIn('class="partners"', html)
                    self.assertIn(heading, html)
                    self.assertIn(disclosure, html)
                    self.assertIn('href="https://wise.com/"', html)
                    self.assertIn('href="https://www.currenciesdirect.com/"', html)
                    self.assertLess(html.index('class="partners"'), html.index('class="tg-cta"'))
                    self.assertLess(html.index('class="tg-cta"'), html.index('class="cy-news"'))
                    self.assertLess(html.index('class="cy-news"'), html.index("</article>"))
                    for tag in partner_anchors(html):
                        self.assertIn('rel="sponsored noopener"', tag)
                        self.assertIn('target="_blank"', tag)
                    wise = next(item for item in build.PARTNERS["partners"] if item["id"] == "wise")
                    self.assertIn(wise["description"][lang], html)
                else:
                    self.assertNotIn('class="partners"', html)
                    self.assertNotIn("wise.com", html)
                    self.assertNotIn("currenciesdirect.com", html)
            for slug in build.CALC_ORDER:
                html = build.calc_page(lang, slug)
                if f"calculators/{slug}" in pages:
                    self.assertIn('class="partners"', html)
                    self.assertIn(heading, html)
                    self.assertIn(disclosure, html)
                    self.assertLess(html.index('class="partners"'), html.index('class="tg-cta"'))
                    self.assertNotIn('class="cy-news"', html)
                    for tag in partner_anchors(html):
                        self.assertIn('rel="sponsored noopener"', tag)
                        self.assertIn('target="_blank"', tag)
                else:
                    self.assertNotIn('class="partners"', html)
                    self.assertNotIn("wise.com", html)
                    self.assertNotIn("currenciesdirect.com", html)
            for html in (
                build.home(lang),
                build.listing(lang, "guides"),
                build.listing(lang, "calculators"),
                build.static_page(lang, "privacy"),
                build.contact(lang),
                build.thanks(lang),
            ):
                self.assertNotIn('class="partners"', html)
                self.assertNotIn("wise.com", html)
                self.assertNotIn("currenciesdirect.com", html)

    def test_missing_translation_falls_back_without_dropping_the_box(self):
        data = {
            "heading": {"en": "Useful services"},
            "disclosure": {"ru": "Некоторые ссылки могут быть партнёрскими; для вас цена от этого не меняется."},
            "partners": [{
                "name": "Wise",
                "url": "https://wise.com/",
                "affiliate_url": "",
                "description": {"en": "Send euros to Cyprus."},
                "applies_to": ["guides/renting-out"],
            }],
        }
        html = build.partners_block("el", "guides", "renting-out", data)
        self.assertIn("Useful services", html)
        self.assertIn("Send euros to Cyprus.", html)
        self.assertIn(build.PARTNER_DISCLOSURE["el"], html)
        self.assertNotIn("партнёрскими", html)


if __name__ == "__main__":
    unittest.main()
