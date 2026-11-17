# -*- coding: utf-8 -*-
"""IndexNow URL selection. No network."""
import unittest

import indexnow_submit as indexnow


SITEMAP = [
    "https://mycytax.com/",
    "https://mycytax.com/guides/taxes-overview/",
    "https://mycytax.com/ru/guides/taxes-overview/",
    "https://mycytax.com/el/links/",
    "https://mycytax.com/feed.xml",
]


class IndexNowPlanTests(unittest.TestCase):
    def test_key_shape_and_payload(self):
        key = indexnow.load_config()
        self.assertRegex(key, r"^[0-9a-f]{32}$")
        body = indexnow.payload(key, SITEMAP[:1])
        self.assertEqual(body["host"], "mycytax.com")
        self.assertEqual(body["key"], key)
        self.assertEqual(body["keyLocation"], f"https://mycytax.com/{key}.txt")
        self.assertEqual(body["urlList"], SITEMAP[:1])

    def test_build_and_unknown_diff_submit_the_whole_sitemap(self):
        self.assertEqual(indexnow.plan(None, SITEMAP, from_build=True), ("submit", SITEMAP))
        self.assertEqual(indexnow.plan(None, SITEMAP, from_build=False), ("submit", SITEMAP))

    def test_source_change_is_left_to_the_build_workflow(self):
        files = ["source/build.py", "README.md"]
        self.assertEqual(indexnow.plan(files, SITEMAP), ("skip", []))
        self.assertTrue(indexnow.triggers_rebuild("source/content/pages/links.json"))
        self.assertFalse(indexnow.triggers_rebuild("source/content/telegram-posted.json"))

    def test_changed_pages_only_when_the_diff_maps_onto_the_sitemap(self):
        files = [
            "guides/taxes-overview/index.html",
            "ru/guides/taxes-overview/index.html",
            "contact/thanks/index.html",
        ]
        action, urls = indexnow.plan(files, SITEMAP)
        self.assertEqual(action, "submit")
        self.assertEqual(urls, [
            "https://mycytax.com/guides/taxes-overview/",
            "https://mycytax.com/ru/guides/taxes-overview/",
        ])

    def test_sitemap_or_key_file_submits_every_url(self):
        self.assertEqual(indexnow.plan(["sitemap.xml"], SITEMAP)[1], SITEMAP)
        self.assertEqual(indexnow.plan(["12694a866f68bcfc40fb090ffc489ae7.txt"], SITEMAP)[1], SITEMAP)

    def test_readme_only_submits_nothing(self):
        self.assertEqual(indexnow.plan(["README.md"], SITEMAP), ("submit", []))

    def test_sitemap_parser_and_key_check(self):
        text = "<url><loc>https://mycytax.com/ru/links/</loc><lastmod>2026-11-17</lastmod></url>"
        self.assertEqual(indexnow.parse_sitemap(text), ["https://mycytax.com/ru/links/"])
        self.assertTrue(indexnow.key_is_live("abc", lambda url: "abc\n"))
        self.assertFalse(indexnow.key_is_live("abc", lambda url: "nope"))
        self.assertFalse(indexnow.key_is_live("abc", lambda url: (_ for _ in ()).throw(OSError("down"))))


if __name__ == "__main__":
    unittest.main()
