# -*- coding: utf-8 -*-
"""Real Estate section and the unpublished sample listing."""
import unittest

import build


class RealEstateTests(unittest.TestCase):
    def test_navigation_and_section_list_the_property_guides(self):
        for lang, name in (("en", "Real Estate"), ("ru", "Недвижимость"), ("el", "Ακίνητα")):
            header = build.header(lang, lambda l: "/")
            self.assertIn(f'href="{build.href(build.loc(lang, "/real-estate/"))}"', header)
            self.assertIn(name, header)
            page = build.real_estate_page(lang)
            self.assertIn(name, page)
            self.assertIn(build.PROPERTY_LABELS[lang]["empty"], page)
            self.assertNotIn("example-limassol-apartment", page)
            self.assertIn("water-tariff-proposal", page)
            self.assertIn(build.href(build.loc(lang, "/calculators/vat/")), page)
            self.assertIn(build.href(build.loc(lang, "/calculators/transfer-fees/")), page)

    def test_sample_listing_is_hidden_and_a_published_one_links_the_price(self):
        self.assertEqual(build.published_listings(), [])
        xml = build.sitemap()
        self.assertIn("https://mycytax.com/real-estate/", xml)
        self.assertIn("https://mycytax.com/ru/real-estate/", xml)
        self.assertIn("https://mycytax.com/el/real-estate/", xml)
        self.assertNotIn("example-limassol-apartment", xml)
        sample = dict(build.PROPERTIES[0])
        sample["published"] = True
        sample["photos"] = []
        page = build.listing_detail("en", sample)
        self.assertIn("EXAMPLE", page)
        self.assertIn("/calculators/transfer-fees/?value=350000", page)
        self.assertIn("/calculators/vat/?price=350000&amp;area=85", page)
        self.assertIn("/calculators/stamp-duty/?value=350000", page)
        self.assertIn("/calculators/mortgage/?principal=350000", page)
        self.assertIn('class="cta"', page)
        block = build.listings_block("ru", [sample])
        self.assertIn("ПРИМЕР", block)
        self.assertNotIn(build.PROPERTY_LABELS["ru"]["empty"], block)
        self.assertIn(build.PROPERTY_LABELS["en"]["empty"], build.listings_block("en", []))

    def test_water_guide_uses_the_dam_photograph_and_its_sources(self):
        page = build.guide_page("en", "water-tariff-proposal", [])
        self.assertIn("/assets/guides/kouris-dam.jpg", page)
        self.assertIn("Kouris Dam", page)
        self.assertIn("https://commons.wikimedia.org/wiki/File:Kouris_Dam,_Cyprus.jpg", page)
        self.assertIn("https://en.philenews.com/insider/cyprus-uniform-water-charges-cabinet/", page)
        self.assertIn("1.2 per cent", page)
        self.assertLess(page.index('class="guide-fig"'), page.index('class="cta"'))
        self.assertIn("€10", build.guide_page("el", "water-tariff-proposal", []))
        self.assertIn("17 ноября 2026", build.guide_page("ru", "water-tariff-proposal", []))


if __name__ == "__main__":
    unittest.main()
