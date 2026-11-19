# -*- coding: utf-8 -*-
"""Services menu and the gated buying checklist. No network."""
import unittest

import build


class ServiceTests(unittest.TestCase):
    def test_menu_quotes_and_checklist_gate(self):
        forbidden = "cs1." + "atex@gmail.com"
        for lang in build.LANGS:
            header = build.header(lang, lambda l: "/")
            self.assertIn(build.href(build.loc(lang, "/services/")), header)
            page = build.services_page(lang)
            self.assertEqual(page.count(build.QUOTE[lang]), 4)
            self.assertNotIn("€", page)
            self.assertNotIn(forbidden, page)
            for value, _copy in build.SERVICE_LIST:
                self.assertIn(build.consult_href(lang, value), page)
            gate = build.checklist_gate_page(lang)
            self.assertIn(f'action="https://formsubmit.co/{build.LEADS_EMAIL}"', gate)
            self.assertIn('name="_subject" value="mycytax lead"', gate)
            self.assertIn('name="_captcha" value="true"', gate)
            self.assertIn('name="name"', gate)
            self.assertIn('name="email"', gate)
            self.assertIn('name="consent"', gate)
            self.assertIn("/buying-checklist/2026/", gate)
            guide = build.checklist_page(lang)
            self.assertIn("noindex,follow", guide)
            self.assertIn("window.print()", guide)
            self.assertIn("€85,000" if lang == "en" else "85", guide)
            self.assertIn("20%", guide)
            self.assertTrue("2.65%" in guide or "2,65%" in guide)
            self.assertNotIn(forbidden, guide)
        self.assertIn("@media print", build.css())
        self.assertIn("https://mycytax.com/services/", build.sitemap())
        self.assertIn("https://mycytax.com/buying-checklist/", build.sitemap())
        self.assertNotIn("/buying-checklist/2026/", build.sitemap())


if __name__ == "__main__":
    unittest.main()
