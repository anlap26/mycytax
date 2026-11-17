# -*- coding: utf-8 -*-
"""English Instagram link-in-bio page."""
import os
import unittest

import build

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


class LinksPageTests(unittest.TestCase):
    def test_buttons_follow_the_existing_pages_and_carry_the_campaign(self):
        html = build.links_page()
        expected = list(build.LINKS_ITEMS) + [
            (build.LEAD["en"]["buy"], "/contact/?type=buy"),
        ]
        positions = []
        for label, path in expected:
            url = build.links_url(path)
            self.assertIn("utm_source=instagram", url)
            self.assertIn("utm_medium=social", url)
            self.assertIn("utm_content=links", url)
            self.assertIn(url.count("?"), (1,))
            needle = f'href="{build.e(url)}">{build.e(label)}</a>'
            self.assertIn(needle, html)
            positions.append(html.index(needle))
            target = path.split("?", 1)[0]
            on_disk = ROOT if target == "/" else os.path.join(ROOT, target.strip("/"))
            self.assertTrue(os.path.isdir(on_disk), target)
            self.assertTrue(os.path.isfile(os.path.join(on_disk, "index.html")), target)
        self.assertEqual(positions, sorted(positions))
        self.assertIn('class="bio-contact"', html)
        self.assertEqual(html.count("utm_source=instagram"), len(expected))

    def test_page_is_indexable_english_and_uses_the_shared_head_snippet(self):
        html = build.links_page()
        self.assertIn("<html lang=\"en\">", html)
        self.assertIn("Free Cyprus property tax calculators &amp; guides | MyCyTax", html)
        self.assertIn('name="description"', html)
        self.assertIn('rel="canonical" href="https://mycytax.com/links/"', html)
        self.assertIn('property="og:title"', html)
        self.assertIn('property="og:description"', html)
        self.assertIn('property="og:url" content="https://mycytax.com/links/"', html)
        self.assertIn('property="og:type" content="website"', html)
        self.assertIn('name="robots" content="index,follow,max-image-preview:large"', html)
        self.assertNotIn("noindex", html)
        self.assertIn(build.ADSENSE, html)
        self.assertIn('hreflang="en"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertNotIn('hreflang="ru"', html)
        self.assertNotIn('hreflang="el"', html)
        self.assertIn("info@mycytax.com", html)
        self.assertIn(">MyCyTax</a>", html)
        self.assertIn("Free Cyprus property tax calculators &amp; guides", html)

    def test_site_nav_does_not_list_the_page_and_the_sitemap_does(self):
        for lang in build.LANGS:
            header = build.header(lang, lambda l: "/")
            self.assertNotIn("/links/", header)
        xml = build.sitemap()
        self.assertEqual(xml.count("https://mycytax.com/links/"), 1)
        self.assertNotIn("https://mycytax.com/ru/links/", xml)
        self.assertNotIn("https://mycytax.com/el/links/", xml)

    def test_styles_use_the_site_colours(self):
        css = build.css()
        self.assertIn("main.bio", css)
        self.assertIn("min-height:56px", css)
        self.assertIn("#e7c7a4", css)
        self.assertIn("var(--pine)", css)
