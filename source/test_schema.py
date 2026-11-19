# -*- coding: utf-8 -*-
"""schema.org JSON-LD parses and covers the page types. No network."""
import json
import re
import unittest

import build


def blocks(html):
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html):
        out.append(json.loads(raw.replace("<\\/", "</")))
    return out


def types(html):
    found = set()
    for obj in blocks(html):
        kind = obj.get("@type")
        if isinstance(kind, list):
            found.update(kind)
        elif kind:
            found.add(kind)
    return found


class SchemaTests(unittest.TestCase):
    def test_every_block_parses_and_the_main_types_are_present(self):
        pages = {
            "WebSite": build.home("en"),
            "ProfessionalService": build.services_page("ru"),
            "Article": build.guide_page("el", "taxes-overview", []),
            "FAQPage": build.guide_page("en", "non-dom", []),
            "HowTo": build.checklist_page("en"),
            "BreadcrumbList": build.calc_page("el", "vat"),
            "WebApplication": build.calc_page("ru", "stamp-duty"),
        }
        for kind, html in pages.items():
            self.assertTrue(blocks(html), kind)
            self.assertIn(kind, types(html), kind)
            self.assertIn("BreadcrumbList", types(html), kind)
        home_types = types(build.home("el"))
        for kind in ("WebSite", "Organization", "ProfessionalService", "AccountingService", "BreadcrumbList"):
            self.assertIn(kind, home_types)
        for lang in build.LANGS:
            for obj in blocks(build.home(lang)) + blocks(build.services_page(lang)):
                blob = json.dumps(obj)
                self.assertNotIn("streetAddress", blob)
                if obj.get("@type") in ("Organization", ["ProfessionalService", "AccountingService"]) or (
                    isinstance(obj.get("@type"), list) and "AccountingService" in obj["@type"]
                ):
                    self.assertEqual(obj.get("email"), build.LEADS_EMAIL)
                    self.assertEqual(obj["areaServed"]["name"], "Cyprus")
                    self.assertIn("https://t.me/mycytax", obj["sameAs"])
                    self.assertIn("https://www.instagram.com/mycytax/", obj["sameAs"])
        howto = next(obj for obj in blocks(build.checklist_page("en")) if obj["@type"] == "HowTo")
        self.assertGreaterEqual(len(howto["step"]), 6)
        crumbs = next(obj for obj in blocks(build.guide_page("ru", "resident-handbook/tic", [])) if obj["@type"] == "BreadcrumbList")
        self.assertGreaterEqual(len(crumbs["itemListElement"]), 3)
        self.assertEqual(crumbs["itemListElement"][0]["name"], build.UI["ru"]["home"])


if __name__ == "__main__":
    unittest.main()
