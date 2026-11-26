# -*- coding: utf-8 -*-
"""Embeddable calculators: lightweight frames, a dofollow backlink, and /embed/."""
import re
import unittest

import build


class EmbedTests(unittest.TestCase):
    def test_every_calculator_has_an_id(self):
        self.assertEqual(set(build.CALC_IDS), set(build.CALC_ORDER))

    def test_snippet_puts_the_backlink_outside_the_frame(self):
        snippet = build.embed_snippet("en", "vat", "680", "1280")
        self.assertIn(
            '<iframe src="https://mycytax.com/embed/vat/" width="680" height="1280" '
            'style="border:0;max-width:100%" title="VAT on a new property"></iframe>',
            snippet,
        )
        self.assertTrue(snippet.endswith(
            '<p><a href="https://mycytax.com/calculators/vat/">Calculator by MyCyTax</a></p>'
        ))
        self.assertNotIn("nofollow", snippet)
        self.assertNotIn("sponsored", snippet)
        self.assertNotIn("ugc", snippet)
        self.assertNotIn('rel="', snippet)
        ru = build.embed_snippet("ru", "compare-countries", "400", "1100")
        self.assertIn('src="https://mycytax.com/ru/embed/compare-countries/"', ru)
        self.assertIn('href="https://mycytax.com/ru/calculators/compare-countries/"', ru)
        self.assertIn(">Калькулятор от MyCyTax</a>", ru)
        el = build.embed_snippet("el", "purchase-costs", "100%", "1480")
        self.assertIn('src="https://mycytax.com/el/embed/purchase-costs/"', el)
        self.assertIn('width="100%"', el)
        self.assertIn(">Υπολογιστής από τη MyCyTax</a>", el)

    def test_embed_page_is_a_frame_without_chrome(self):
        for lang in build.LANGS:
            for slug in build.CALC_ORDER:
                page = build.embed_page(lang, slug)
                embed, full = build.embed_paths(lang, slug)
                title = build.CALCS[slug][lang][0]
                self.assertIn(f'<html lang="{lang}">', page)
                self.assertIn('name="viewport"', page)
                self.assertIn('name="robots" content="noindex,follow"', page)
                self.assertNotIn("max-image-preview", page)
                self.assertIn(
                    '<meta http-equiv="Content-Security-Policy" content="frame-ancestors *;">',
                    page,
                )
                self.assertNotIn("<header", page)
                self.assertNotIn("<footer", page)
                self.assertNotIn("cookie-banner", page)
                self.assertNotIn("pagead2.googlesyndication.com", page)
                self.assertNotIn("data-affiliate", page)
                self.assertNotIn('class="tg-cta"', page)
                self.assertIn(f'data-calc="{build.CALC_IDS[slug]}"', page)
                self.assertIn('src="/assets/calc.js"', page) if lang == "en" else self.assertIn("assets/calc.js", page)
                self.assertIn('class="embed-credit"', page)
                credit = re.search(r'<p class="embed-credit"><a ([^>]*)>', page)
                self.assertIsNotNone(credit, slug)
                attrs = credit.group(1)
                self.assertIn(f'href="{build.absu(full)}"', attrs)
                self.assertIn('target="_top"', attrs)
                self.assertNotIn("rel=", attrs)
                self.assertIn(f">{build.e(build.EMBED[lang]['powered'])}</a>", page)
                self.assertIn(build.UI[lang]["disclaimer"], page)
                self.assertIn(f"<h1>{build.e(title)}</h1>", page)
                self.assertIn(f'rel="canonical" href="{build.absu(embed)}"', page)
                self.assertNotIn("frame-ancestors 'none'", page)
                self.assertNotIn("frame-ancestors 'self'", page)

    def test_full_pages_do_not_opt_in_to_framing(self):
        pages = [
            build.home("en"),
            build.calc_page("ru", "vat"),
            build.embed_landing("el"),
            build.listing("en", "calculators"),
        ]
        for html in pages:
            self.assertNotIn("frame-ancestors", html)
            self.assertNotIn("X-Frame-Options", html)

    def test_each_calculator_offers_the_snippet_and_presets(self):
        for lang in build.LANGS:
            label = build.EMBED[lang]
            for slug in build.CALC_ORDER:
                html = build.calc_page(lang, slug)
                self.assertLess(html.index('id="calc"'), html.index('class="embed-box"'))
                if 'class="aff-offer' in html:
                    self.assertLess(html.index('class="embed-box"'), html.index('class="aff-offer'))
                self.assertIn(label["box_h"], html)
                self.assertIn('class="go embed-copy"', html)
                self.assertIn(label["copy"], html)
                self.assertEqual(html.count('class="go embed-copy"'), 1)
                for width, height, key in build.EMBED_PRESETS:
                    self.assertIn(f'data-width="{width}" data-height="{height}"', html)
                    self.assertIn(label[key], html)
                self.assertIn('aria-pressed="true"', html)
                snippet = build.embed_snippet(lang, slug, "680", "1280")
                self.assertIn(build.e(snippet), html)
                self.assertIn("</iframe><p><a href=", snippet)
                self.assertNotIn("nofollow", snippet)

    def test_landing_is_indexable_in_three_languages(self):
        for lang, home in (("en", "/embed/"), ("ru", "/ru/embed/"), ("el", "/el/embed/")):
            html = build.embed_landing(lang)
            copy = build.EMBED[lang]
            self.assertIn(f"<html lang=\"{lang}\">", html)
            self.assertIn(f"{copy['h']} | MyCyTax", html)
            self.assertIn(f'name="description" content="{build.e(copy["desc"])}"', html)
            self.assertIn(f'rel="canonical" href="https://mycytax.com{home}"', html)
            self.assertIn('name="robots" content="index,follow,max-image-preview:large"', html)
            self.assertNotIn("noindex", html)
            self.assertIn('property="og:title"', html)
            self.assertIn('property="og:description"', html)
            self.assertIn(f'property="og:url" content="https://mycytax.com{home}"', html)
            self.assertIn('hreflang="en"', html)
            self.assertIn('hreflang="ru" href="https://mycytax.com/ru/embed/"', html)
            self.assertIn('hreflang="el" href="https://mycytax.com/el/embed/"', html)
            self.assertIn('hreflang="x-default"', html)
            self.assertIn("<header", html)
            self.assertIn("<footer", html)
            self.assertEqual(html.count('class="go embed-copy"'), len(build.CALC_ORDER))
            self.assertEqual(html.count("function snippet(box,w,h)"), 1)
            for slug in build.CALC_ORDER:
                embed, full = build.embed_paths(lang, slug)
                self.assertIn(build.href(embed), html)
                self.assertIn(build.href(full), html)
                self.assertIn(build.CALCS[slug][lang][0], html)
            self.assertIn("CollectionPage", html)
            self.assertIn(copy["footer"], build.footer(lang))
            self.assertIn(build.href(home), build.footer(lang))
            self.assertNotIn("/embed/", build.header(lang, lambda l: "/"))

    def test_sitemap_lists_the_landing_page_and_not_the_frames(self):
        xml = build.sitemap()
        for lang in build.LANGS:
            landing = build.absu(build.loc(lang, "/embed/"))
            self.assertIn(f"<loc>{landing}</loc>", xml)
            for slug in build.CALC_ORDER:
                frame = build.absu(build.loc(lang, f"/embed/{slug}/"))
                self.assertNotIn(frame, xml)
                self.assertIn(build.absu(build.loc(lang, f"/calculators/{slug}/")), xml)

    def test_headers_allow_framing_only_on_calculator_embeds(self):
        text = build.embed_headers()
        self.assertIn("frame-ancestors 'self'", text)
        self.assertIn("X-Frame-Options: SAMEORIGIN", text)
        allowed = []
        current = None
        for line in text.splitlines():
            if line.startswith("/"):
                current = line.strip()
            elif "frame-ancestors *" in line and current:
                allowed.append(current)
                current = None
        self.assertGreaterEqual(len(allowed), len(build.CALC_ORDER) * len(build.LANGS) * 3)
        for path in allowed:
            self.assertIn("/embed/", path)
            self.assertTrue(any(f"/{slug}" in path for slug in build.CALC_ORDER), path)
            self.assertFalse(path.rstrip("/").endswith("embed"), path)
            self.assertNotIn("/calculators/", path)
        self.assertIn("/embed/vat/", allowed)
        self.assertIn("/embed/vat", allowed)
        self.assertIn("/embed/vat/index.html", allowed)
        self.assertIn("/ru/embed/mortgage/", allowed)
        self.assertIn("/el/embed/compare-countries/", allowed)
        self.assertNotIn("/embed/", allowed)
        self.assertNotIn("/embed/index.html", allowed)
        # The noindex header is on the frames, not on the whole site.
        self.assertIn("X-Robots-Tag: noindex, follow", text)
        head, _rest = text.split("/embed/transfer-fees", 1)
        self.assertNotIn("noindex", head)


if __name__ == "__main__":
    unittest.main()
