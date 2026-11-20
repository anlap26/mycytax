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
            self.assertNotIn("example-limassol-apartment", page)
            self.assertIn("/real-estate/bellissimo/", page)
            self.assertIn("/real-estate/olivia/", page)
            self.assertIn("/real-estate/the-city-home-2/", page)
            self.assertIn("water-tariff-proposal", page)
            self.assertIn(build.href(build.loc(lang, "/calculators/vat/")), page)
            self.assertIn(build.href(build.loc(lang, "/calculators/transfer-fees/")), page)

    def test_sample_listing_is_hidden_and_a_published_one_links_the_price(self):
        published = [row["id"] for row in build.published_listings()]
        self.assertEqual(published, ["bellissimo", "olivia", "the-city-home-2"])
        xml = build.sitemap()
        self.assertIn("https://mycytax.com/real-estate/", xml)
        self.assertIn("https://mycytax.com/ru/real-estate/", xml)
        self.assertIn("https://mycytax.com/el/real-estate/", xml)
        self.assertNotIn("example-limassol-apartment", xml)
        for ident in published:
            self.assertIn(f"https://mycytax.com/real-estate/{ident}/", xml)
            self.assertIn(f"https://mycytax.com/ru/real-estate/{ident}/", xml)
            self.assertIn(f"https://mycytax.com/el/real-estate/{ident}/", xml)
        olivia = build.listing_detail("en", next(row for row in build.PROPERTIES if row["id"] == "olivia"))
        self.assertIn("Price on request", olivia)
        self.assertNotIn("?value=", olivia)
        self.assertNotIn("?price=", olivia)
        self.assertNotIn("?principal=", olivia)
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

    def test_listing_pages_post_a_request_to_the_contact_form_address(self):
        labels = {"en": "Request info", "ru": "Оставить заявку", "el": "Ζητήστε πληροφορίες"}
        interests = {
            "en": "I'm interested in ",
            "ru": "Меня интересует ",
            "el": "Ενδιαφέρομαι για ",
        }
        xml = build.sitemap()
        self.assertNotIn("/real-estate/thanks/", xml)
        self.assertNotIn("wa.me", build.real_estate_page("en"))
        for lang, label in labels.items():
            section = build.real_estate_page(lang)
            thanks = build.listing_thanks(lang)
            self.assertIn('name="robots" content="noindex,follow"', thanks)
            self.assertIn(build.LISTING_LEAD[lang]["thanks_d"], thanks)
            self.assertNotIn("/real-estate/thanks/", section)
            for item in build.published_listings():
                page = build.listing_detail(lang, item)
                title = item["title"][lang]
                detail = build.href(build.loc(lang, f"/real-estate/{item['id']}/"))
                form_at = page.index('id="listing-lead"')
                top = page.index('class="listing-request"')
                self.assertLess(page.index("<h1>"), top)
                self.assertLess(top, page.index('class="gallery"') if 'class="gallery"' in page else form_at)
                self.assertIn(f'<a class="request" href="#listing-lead">{label}</a>', page)
                self.assertIn(f'<a class="request" href="{detail}#listing-lead">{label}</a>', section)
                self.assertLess(
                    section.index(f'href="{detail}#listing-lead"'),
                    section.index(item["description"][lang][:80]),
                )
                form = page[form_at:page.index("</form>", form_at)]
                self.assertIn(f'action="https://formsubmit.co/{build.LEADS_EMAIL}"', form)
                self.assertIn('method="POST"', form)
                self.assertIn(f'name="_subject" value="MyCyTax lead: {build.e(title)}"', form)
                self.assertIn('name="_template" value="table"', form)
                self.assertIn('name="_captcha" value="false"', form)
                self.assertIn('name="_honey"', form)
                self.assertIn(
                    f'name="_next" value="{build.absu(build.loc(lang, "/real-estate/thanks/"))}"',
                    form,
                )
                self.assertIn(f'name="listing" value="{build.e(title)}"', form)
                self.assertIn(
                    f'name="page url" value="{build.absu(build.loc(lang, f"/real-estate/{item["id"]}/"))}"',
                    form,
                )
                self.assertIn('<input name="name" required', form)
                self.assertIn('<input name="phone" required', form)
                email = form[form.index('type="email"'):form.index('type="email"') + 80]
                self.assertNotIn("required", email)
                self.assertIn(
                    "<textarea name=\"message\">" + build.e(interests[lang] + title) + "</textarea>",
                    form,
                )
                self.assertIn('name="consent" value="yes" required', form)
                self.assertNotIn("<script", form)
                self.assertNotIn("wa.me", page)
                self.assertNotIn("youtube.com", page)


if __name__ == "__main__":
    unittest.main()
