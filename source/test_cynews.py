# -*- coding: utf-8 -*-
"""CyNews24 cross-links. The fallback test does not use the network."""
import unittest

import build


SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  <url><loc>https://cynews24.net/ru/older/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-01T09:00:00+02:00</news:publication_date><news:title>Старая новость</news:title></news:news></url>
  <url><loc>https://cynews24.net/ru/sixth/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-10T09:00:00+02:00</news:publication_date><news:title>Шестая</news:title></news:news></url>
  <url><loc>https://cynews24.net/en/english-one/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>en</news:language></news:publication><news:publication_date>2026-11-13T12:00:00+02:00</news:publication_date><news:title>English &amp; one</news:title></news:news></url>
  <url><loc>https://cynews24.net/ru/tie-second/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-12T09:00:00+02:00</news:publication_date><news:title>Вторая при равенстве</news:title></news:news></url>
  <url><loc>https://example.com/ru/offsite/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-20T09:00:00+02:00</news:publication_date><news:title>Чужой сайт</news:title></news:news></url>
  <url><loc>https://cynews24.net/ru/newest/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-13T09:00:00+02:00</news:publication_date><news:title>Самая свежая &lt;новость&gt;</news:title></news:news></url>
  <url><loc>https://cynews24.net/ru/tie-first/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-12T09:00:00+02:00</news:publication_date><news:title>Первая при равенстве</news:title></news:news></url>
  <url><loc>https://cynews24.net/ru/mid/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-11T09:00:00+02:00</news:publication_date><news:title>Средняя</news:title></news:news></url>
  <url><loc>https://cynews24.net/el/greek/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>el</news:language></news:publication><news:publication_date>2026-11-13T09:00:00+02:00</news:publication_date><news:title>Ελληνικός τίτλος</news:title></news:news></url>
  <url><loc>https://cynews24.net/ru/blank/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-13T10:00:00+02:00</news:publication_date><news:title>  </news:title></news:news></url>
  <url><loc>https://cynews24.net/en/mismatch/</loc><news:news><news:publication><news:name>CyNews 24</news:name><news:language>ru</news:language></news:publication><news:publication_date>2026-11-13T11:00:00+02:00</news:publication_date><news:title>Язык не совпал</news:title></news:news></url>
</urlset>
"""


class CyNewsTests(unittest.TestCase):
    def tearDown(self):
        for lang in build.LANGS:
            build.CYNEWS_HEADLINES[lang] = None

    def test_language_homes_match_the_live_paths(self):
        self.assertEqual(build.cynews_home("ru"), "https://cynews24.net/ru/")
        self.assertEqual(build.cynews_home("en"), "https://cynews24.net/en/")
        self.assertEqual(build.cynews_home("el"), "https://cynews24.net/el/")
        self.assertEqual(build.CYNEWS, "https://cynews24.net/")

    def test_footer_projects_line_on_every_language(self):
        expected = {
            "ru": ("Наши проекты", "CyNews24 — новости Кипра", "https://cynews24.net/ru/"),
            "en": ("Our projects", "CyNews24 — Cyprus news", "https://cynews24.net/en/"),
            "el": ("Τα έργα μας", "CyNews24 — ειδήσεις Κύπρου", "https://cynews24.net/el/"),
        }
        for lang, (label, name, url) in expected.items():
            html = build.footer(lang)
            self.assertIn(f'class="projects"', html)
            self.assertIn(label, html)
            self.assertIn(f'<a href="{url}">{name}</a>', html)
            self.assertNotIn("nofollow", html)
            line = html[html.index('class="projects"'):html.index("</p>", html.index('class="projects"'))]
            self.assertNotIn("target=", line)
            self.assertNotIn(f'href="{build.CYNEWS}"', line)

    def test_latest_five_per_language_keep_sitemap_order_on_a_tie(self):
        loaded = build.load_latest_news(fetch=lambda url, timeout: SITEMAP)
        self.assertEqual(
            [item["url"] for item in loaded["ru"]],
            [
                "https://cynews24.net/ru/newest/",
                "https://cynews24.net/ru/tie-second/",
                "https://cynews24.net/ru/tie-first/",
                "https://cynews24.net/ru/mid/",
                "https://cynews24.net/ru/sixth/",
            ],
        )
        self.assertNotIn("https://cynews24.net/ru/older/", [item["url"] for item in loaded["ru"]])
        self.assertEqual(loaded["en"][0]["title"], "English & one")
        self.assertEqual(loaded["el"][0]["title"], "Ελληνικός τίτλος")
        self.assertEqual(len(loaded["en"]), 1)
        block = build.news_block("ru", loaded["ru"])
        self.assertIn("Свежие новости Кипра", block)
        self.assertIn("Самая свежая &lt;новость&gt;", block)
        self.assertNotIn("<новость>", block)
        self.assertNotIn("nofollow", block)
        self.assertNotIn("target=", block)
        self.assertLess(block.index("/ru/tie-second/"), block.index("/ru/tie-first/"))

    def test_fetch_failure_falls_back_to_a_static_link(self):
        def boom(url, timeout):
            self.assertEqual(url, build.CYNEWS_SITEMAP)
            self.assertLessEqual(timeout, 5)
            raise TimeoutError("timed out")

        loaded = build.load_latest_news(fetch=boom)
        self.assertIsNone(loaded)
        build.refresh_cynews(fetch=boom)
        for lang in build.LANGS:
            self.assertIsNone(build.CYNEWS_HEADLINES[lang])
            block = build.news_block(lang)
            self.assertIn(build.UI[lang]["news_h"], block)
            self.assertIn(f'href="{build.cynews_home(lang)}"', block)
            self.assertIn("cynews24.net", block)
            self.assertNotIn("<ul>", block)
            self.assertNotIn("nofollow", block)
            self.assertNotIn('target="_blank"', block)
            self.assertNotIn("noopener", block)

    def test_empty_and_broken_sitemap_also_fall_back(self):
        self.assertIsNone(build.load_latest_news(fetch=lambda url, timeout: b""))
        self.assertIsNone(build.load_latest_news(fetch=lambda url, timeout: b"<not-xml"))
        self.assertIsNone(build.load_latest_news(fetch=lambda url, timeout: b"<urlset></urlset>"))
        block = build.news_block("en", None)
        self.assertIn('href="https://cynews24.net/en/"', block)
        self.assertIn("Latest Cyprus news", block)

    def test_home_and_guides_show_the_block_and_other_pages_do_not(self):
        build.CYNEWS_HEADLINES["ru"] = [{
            "url": "https://cynews24.net/ru/newest/",
            "title": "Самая свежая",
        }]
        home = build.home("ru")
        guide = build.guide_page("ru", "taxes-overview", [])
        calc = build.calc_page("ru", "vat")
        listing = build.listing("en", "guides")
        about = build.static_page("el", "about")
        for html in (home, guide):
            self.assertIn('class="cy-news"', html)
            self.assertIn("https://cynews24.net/ru/newest/", html)
            self.assertIn("Самая свежая", html)
            self.assertIn("Наши проекты", html)
            self.assertIn('href="https://cynews24.net/ru/"', html)
        self.assertLess(guide.index('class="tg-cta"'), guide.index('class="cy-news"'))
        self.assertLess(guide.index('class="cy-news"'), guide.index("</article>"))
        for html in (calc, listing, about):
            self.assertNotIn('class="cy-news"', html)
        self.assertIn("Our projects", listing)
        self.assertIn("Τα έργα μας", about)
        self.assertIn('href="https://cynews24.net/en/"', listing)
        self.assertIn('href="https://cynews24.net/el/"', about)

    def test_organization_same_as_is_unchanged(self):
        self.assertEqual(build.org()["sameAs"][0], "https://cynews24.net/")
        self.assertEqual(build.org()["sameAs"][1:], [build.TG_RU, build.TG_EN])


if __name__ == "__main__":
    unittest.main()
