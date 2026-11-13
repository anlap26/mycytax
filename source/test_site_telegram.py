# -*- coding: utf-8 -*-
"""Telegram subscribe links rendered by the static generator."""
import re
import unittest

import build


def telegram_anchors(html):
    return re.findall(r"<a\b[^>]*href=\"https://t\.me/[^\"]+\"[^>]*>", html)


class TelegramLinkTests(unittest.TestCase):
    def test_localized_call_to_action(self):
        self.assertEqual(build.UI["en"]["tg"], "Follow us on Telegram")
        self.assertEqual(build.UI["ru"]["tg"], "Подписывайтесь на наш Telegram-канал")
        self.assertEqual(build.UI["el"]["tg"], "Ακολουθήστε μας στο Telegram")

    def test_page_language_picks_the_channel(self):
        self.assertEqual(build.tg_primary("ru"), build.TG_RU)
        self.assertEqual(build.tg_primary("en"), build.TG_EN)
        self.assertEqual(build.tg_primary("el"), build.TG_EN)
        self.assertEqual(build.tg_secondary("ru"), build.TG_EN)
        self.assertEqual(build.tg_secondary("en"), build.TG_RU)
        self.assertEqual(build.tg_secondary("el"), build.TG_RU)

    def test_header_and_footer_link_the_page_language_only(self):
        for lang in build.LANGS:
            primary = build.tg_primary(lang)
            other = build.tg_secondary(lang)
            phrase = build.UI[lang]["tg"]
            for html in (build.header(lang, lambda l: "/"), build.footer(lang)):
                self.assertIn(f'href="{primary}"', html)
                self.assertNotIn(f'href="{other}"', html)
                self.assertIn(phrase, html)
                self.assertIn("<svg", html)
                self.assertNotIn("<img", html)
            self.assertIn('class="tg-nav"', build.header(lang, lambda l: "/"))
            self.assertIn('class="tg-foot"', build.footer(lang))

    def test_card_lists_the_page_language_channel_first(self):
        for lang in build.LANGS:
            card = build.telegram_card(lang)
            primary = f'href="{build.tg_primary(lang)}"'
            other = f'href="{build.tg_secondary(lang)}"'
            self.assertLess(card.index(primary), card.index(other))
            self.assertEqual(card.count(primary), 2)
            self.assertEqual(card.count(other), 1)
            self.assertIn(build.UI[lang]["tg"], card)
            self.assertIn(build.UI[lang]["tg_other"], card)
            self.assertIn("<svg", card)

    def test_every_telegram_anchor_opens_in_a_new_tab(self):
        pages = [
            build.home(lang) for lang in build.LANGS
        ]
        pages.append(build.listing("en", "calculators"))
        pages.append(build.listing("ru", "guides"))
        pages.append(build.static_page("el", "about"))
        pages.append(build.contact("en"))
        pages.append(build.thanks("ru"))
        pages.append(build.calc_page("el", "vat"))
        pages.append(build.guide_page("ru", "taxes-overview", []))
        pages.append(build.guide_page("en", "taxes-overview", []))
        for html in pages:
            anchors = telegram_anchors(html)
            self.assertGreaterEqual(len(anchors), 2)
            for tag in anchors:
                self.assertIn('rel="noopener"', tag)
                self.assertIn('target="_blank"', tag)
                self.assertNotIn("noreferrer", tag)

    def test_call_to_action_is_only_on_guides_and_calculators(self):
        self.assertNotIn('class="tg-cta"', build.home("en"))
        self.assertNotIn('class="tg-cta"', build.listing("ru", "guides"))
        self.assertNotIn('class="tg-cta"', build.listing("el", "calculators"))
        self.assertNotIn('class="tg-cta"', build.static_page("en", "privacy"))
        self.assertNotIn('class="tg-cta"', build.contact("el"))
        guide = build.guide_page("el", "taxes-overview", [])
        calc = build.calc_page("ru", "mortgage")
        self.assertIn('class="tg-cta"', guide)
        self.assertIn('class="tg-cta"', calc)
        self.assertIn("Ακολουθήστε μας στο Telegram", guide)
        self.assertIn("Подписывайтесь на наш Telegram-канал", calc)
        self.assertLess(
            guide.index('class="tg-cta"'),
            guide.index("</article>"),
        )

    def test_organization_same_as_includes_both_channels(self):
        same = build.org()["sameAs"]
        self.assertEqual(same[0], build.CYNEWS)
        self.assertEqual(same[1:], [build.TG_RU, build.TG_EN])
        home = build.home("en")
        self.assertIn('"sameAs": ["https://cynews24.net/", "https://t.me/mycytax", "https://t.me/mycytaxen"]', home)
        guide = build.guide_page("en", "off-plan", [])
        self.assertIn('"sameAs": ["https://t.me/mycytax", "https://t.me/mycytaxen"]', guide)
        calc = build.calc_page("en", "stamp-duty")
        self.assertIn('"sameAs": ["https://cynews24.net/", "https://t.me/mycytax", "https://t.me/mycytaxen"]', calc)


if __name__ == "__main__":
    unittest.main()
