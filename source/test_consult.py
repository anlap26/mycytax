# -*- coding: utf-8 -*-
"""Property consultation lead. No network."""
import os
import unittest

import build


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


class ConsultTests(unittest.TestCase):
    def test_address_is_the_leads_inbox_and_not_the_forbidden_one(self):
        self.assertEqual(build.LEADS_EMAIL, "2877novosti@gmail.com")
        self.assertNotIn("cs1.atex", build.LEADS_EMAIL)
        for dirpath, _dirs, names in os.walk(ROOT):
            if "/.git" in dirpath:
                continue
            for name in names:
                if not name.endswith((".py", ".html", ".json", ".js", ".md", ".yml")):
                    continue
                with open(os.path.join(dirpath, name), encoding="utf8", errors="replace") as handle:
                    text = handle.read()
                forbidden = "cs1." + "atex@gmail.com"
                self.assertNotIn(forbidden, text, os.path.join(dirpath, name))

    def test_page_form_and_block_on_guides_and_calculators(self):
        for lang in build.LANGS:
            page = build.consultation_page(lang)
            self.assertIn(build.CONSULT["en"]["h"] if lang == "en" else build.CONSULT[lang]["h"], page)
            self.assertIn(f'action="https://formsubmit.co/{build.LEADS_EMAIL}"', page)
            self.assertIn(f'action="https://formsubmit.co/{build.LEADS_EMAIL}"', build.contact(lang))
            self.assertIn('name="_subject" value="mycytax lead"', page)
            self.assertIn('name="_captcha" value="true"', page)
            self.assertIn("/property-consultation/thanks/", page)
            self.assertIn('name="consent"', page)
            self.assertIn(build.href(build.loc(lang, "/privacy/")), page)
            for value, _label in build.CONSULT[lang]["options"]:
                self.assertIn(f'value="{value}"', page)
            self.assertIn("consult-cta", build.guide_page(lang, "taxes-overview", []))
            self.assertIn("consult-cta", build.calc_page(lang, "vat"))
            self.assertIn("interest=Capital%20gains%20tax", build.calc_page(lang, "capital-gains"))
            self.assertIn("interest=Rental%20income%20tax", build.calc_page(lang, "rental-yield"))
            thanks = build.consultation_thanks(lang)
            self.assertIn("noindex,follow", thanks)
            self.assertNotIn("formsubmit.co", thanks)
        self.assertIn("https://mycytax.com/property-consultation/", build.sitemap())
        self.assertIn("https://mycytax.com/ru/property-consultation/", build.sitemap())
        self.assertIn("https://mycytax.com/el/property-consultation/", build.sitemap())
        self.assertNotIn("/property-consultation/thanks/", build.sitemap())


if __name__ == "__main__":
    unittest.main()
