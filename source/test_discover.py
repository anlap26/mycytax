# -*- coding: utf-8 -*-
"""Google Discover: large lead images and Article JSON-LD on every guide."""
import json
import os
import re
import struct
import unittest

import build


def article(html):
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html):
        obj = json.loads(raw.replace("<\\/", "</"))
        if obj.get("@type") == "Article":
            return obj
    raise AssertionError("no Article")


class DiscoverTests(unittest.TestCase):
    def test_every_guide_has_a_large_image_and_article_dates(self):
        for lang in build.LANGS:
            for slug in build.GUIDE_ORDER:
                html = build.guide_page(lang, slug, [])
                meta, _ = build.load_md(lang, slug)
                if lang in build.GUIDES[slug]["missing"]:
                    self.assertIn('<meta name="robots" content="noindex,follow">', html)
                else:
                    self.assertIn(
                        '<meta name="robots" content="index,follow,max-image-preview:large">',
                        html,
                    )
                self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
                lead = build.guide_lead(lang, slug, meta["title"])
                self.assertGreaterEqual(lead["width"], 1200)
                self.assertIn(f'<meta property="og:image" content="{lead["url"]}">', html)
                self.assertIn(f'<meta property="og:image:width" content="{lead["width"]}">', html)
                self.assertIn(f'<meta property="og:image:height" content="{lead["height"]}">', html)
                self.assertIn(f'<meta name="twitter:image" content="{lead["url"]}">', html)
                self.assertIn(f'<img src="{build.href(lead["path"])}"', html)
                block = article(html)
                self.assertEqual(block["headline"], meta["title"])
                self.assertRegex(block["datePublished"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertRegex(block["dateModified"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertEqual(block["author"]["@type"], "Organization")
                self.assertEqual(block["author"]["name"], build.SITE)
                self.assertEqual(block["publisher"]["name"], build.SITE)
                self.assertEqual(block["author"]["url"], block["publisher"]["url"])
                self.assertIn(build.TG_RU, block["author"]["sameAs"])
                self.assertIn(build.TG_EN, block["publisher"]["sameAs"])
                image = block["image"]
                self.assertEqual(image["@type"], "ImageObject")
                self.assertEqual(image["url"], lead["url"])
                self.assertGreaterEqual(image["width"], 1200)
                self.assertEqual(image["width"], lead["width"])
                self.assertEqual(image["height"], lead["height"])

    def test_a_wide_photo_is_used_and_other_guides_get_a_title_card(self):
        photo = build.guide_lead("en", "water-tariff-proposal", "unused")
        self.assertEqual(photo["kind"], "photo")
        self.assertEqual((photo["width"], photo["height"]), (1600, 1200))
        self.assertTrue(photo["url"].endswith("/assets/guides/kouris-dam.jpg"))
        self.assertEqual(build._image_size(os.path.join(
            build.HERE, "static", "guides", "kouris-dam.jpg")), (1600, 1200))
        card = build.guide_lead("ru", "taxes-overview", "Налоги")
        self.assertEqual(card["kind"], "card")
        self.assertEqual((card["width"], card["height"]), (1200, 675))
        self.assertTrue(card["url"].endswith("/assets/guides/cards/ru/taxes-overview.png"))
        nested = build.guide_lead("en", "resident-handbook/tic", "Tax number")
        self.assertTrue(nested["path"].endswith("/en/resident-handbook--tic.png"))

    def test_title_card_is_a_stable_1200_by_675_png(self):
        titles = [
            "Cyprus property taxes, an overview",
            "Налоги на недвижимость Кипра: обзор",
            "Φορολογική κατοικία στην Κύπρο: ο κανόνας των 60 ημερών και ο κανόνας των 183 ημερών",
        ]
        pngs = [build.render_title_card(title) for title in titles]
        self.assertEqual(pngs[0], build.render_title_card(titles[0]))
        self.assertEqual(len(set(pngs)), 3)
        for png in pngs:
            self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
            width, height = struct.unpack(">II", png[16:24])
            self.assertEqual((width, height), (1200, 675))


if __name__ == "__main__":
    unittest.main()
