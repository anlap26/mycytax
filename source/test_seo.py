# -*- coding: utf-8 -*-
"""Consent, search meta, sitemap dates and guide feeds."""
import re
import unittest

import build


class SeoTests(unittest.TestCase):
    def test_consent_default_is_before_adsense_and_gtag(self):
        pages = [build.home(lang) for lang in build.LANGS]
        pages.append(build.links_page("el"))
        for html in pages:
            consent = html.index("gtag('consent','default'")
            ads = html.index("pagead2.googlesyndication.com")
            self.assertLess(consent, ads)
            for signal in ("ad_storage", "analytics_storage", "ad_user_data", "ad_personalization"):
                self.assertIn(f"{signal}:'denied'", html[consent:ads])
            self.assertNotIn("googletagmanager.com/gtag/js", html)
            self.assertNotIn("msvalidate.01", html)
            self.assertIn("mycytax-consent", html)
            self.assertIn('data-cookie="granted"', html)
            self.assertIn('data-cookie="denied"', html)
            self.assertIn("data-cookie-settings", html)

    def test_ga4_and_bing_render_only_when_set(self):
        old_ga, old_bing = build.GA4_ID, build.BING_MSVALIDATE
        try:
            build.GA4_ID = "G-TEST1234"
            build.BING_MSVALIDATE = "deadbeef"
            html = build.home("en")
            consent = html.index("gtag('consent','default'")
            ga = html.index("googletagmanager.com/gtag/js?id=G-TEST1234")
            config = html.index('gtag("config","G-TEST1234")')
            ads = html.index("pagead2.googlesyndication.com")
            self.assertLess(consent, ga)
            self.assertLess(ga, config)
            self.assertLess(config, ads)
            self.assertIn('<meta name="msvalidate.01" content="deadbeef" />', html)
            build.BING_MSVALIDATE = "a<b>"
            self.assertIn("a&lt;b&gt;", build.links_page("ru"))
        finally:
            build.GA4_ID = old_ga
            build.BING_MSVALIDATE = old_bing

    def test_share_image_and_twitter_card_on_every_language(self):
        pages = [
            build.home("en"),
            build.links_page("ru"),
            build.guide_page("el", "taxes-overview", []),
            build.calc_page("en", "vat"),
        ]
        for html in pages:
            self.assertIn('<meta property="og:image" content="https://mycytax.com/assets/og.png">', html)
            self.assertIn('<meta property="og:image:width" content="1200">', html)
            self.assertIn('<meta property="og:image:height" content="630">', html)
            self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
            self.assertIn('<meta name="twitter:image" content="https://mycytax.com/assets/og.png">', html)
            self.assertIn('type="application/atom+xml"', html)

    def test_instagram_sits_next_to_telegram(self):
        for lang in build.LANGS:
            footer = build.footer(lang)
            header = build.header(lang, lambda l: "/")
            for html in (footer, header):
                ig = re.search(r'<a class="ig-(?:foot|nav)"[^>]*>', html)
                self.assertIsNotNone(ig, lang)
                tag = ig.group(0)
                self.assertIn('href="https://www.instagram.com/mycytax/"', tag)
                self.assertIn('rel="noopener"', tag)
                self.assertIn('target="_blank"', tag)
                self.assertIn("<svg", html)
            self.assertLess(footer.index("tg-foot"), footer.index("ig-foot"))
            self.assertNotIn("yt-foot", footer)
            self.assertNotIn("yt-nav", header)
            self.assertNotIn("youtube.com", footer)
            self.assertNotIn("youtube.com", header)
            self.assertIn(build.UI[lang]["cookie_settings"], footer)
            self.assertIn(build.UI[lang]["cookie_accept"], footer)
            self.assertIn(build.UI[lang]["cookie_reject"], footer)
            self.assertNotIn("/links/", header)

    def test_sitemap_dates_follow_the_source_and_include_links(self):
        xml = build.sitemap()
        for url in (
            "https://mycytax.com/links/",
            "https://mycytax.com/ru/links/",
            "https://mycytax.com/el/links/",
            "https://mycytax.com/feed.xml",
            "https://mycytax.com/ru/feed.xml",
            "https://mycytax.com/el/feed.xml",
        ):
            self.assertIn(f"<loc>{url}</loc>", xml)
        guide = build.page_lastmod("/guides/taxes-overview/")
        self.assertRegex(guide, r"^\d{4}-\d{2}-\d{2}$")
        self.assertIn(
            f"<loc>https://mycytax.com/guides/taxes-overview/</loc><lastmod>{guide}</lastmod>",
            xml,
        )
        self.assertIn(
            f"<loc>https://mycytax.com/el/guides/taxes-overview/</loc><lastmod>{guide}</lastmod>",
            xml,
        )
        self.assertEqual(guide, build.git_days("source/content/guides/taxes-overview.json")[1])
        self.assertEqual(build.page_lastmod("/links/"), build.page_lastmod("/el/links/"))
        home_src = build.git_days("source/build.py")[1]
        if home_src and home_src != guide:
            self.assertNotEqual(build.page_lastmod("/"), guide)

    def test_feed_lists_guides(self):
        feed = build.atom_feed("en")
        self.assertIn('<feed xmlns="http://www.w3.org/2005/Atom">', feed)
        self.assertIn("https://mycytax.com/guides/taxes-overview/", feed)
        self.assertIn("https://mycytax.com/ru/guides/taxes-overview/", build.atom_feed("ru"))

    def test_indexnow_key_is_configured_and_trackers_are_empty(self):
        self.assertRegex(build.INDEXNOW_KEY, r"^[0-9a-f]{32}$")
        self.assertEqual(build.BING_MSVALIDATE, "")
        self.assertEqual(build.GA4_ID, "")


if __name__ == "__main__":
    unittest.main()
