# -*- coding: utf-8 -*-
"""MyCyTax static generator. English, Russian and Greek.

    BASE=https://mycytax.com python3 source/build.py

The custom domain is mycytax.com. BASE is the origin with no trailing slash.
The path inside BASE becomes the link prefix. No trailing slash.
"""
import datetime, html, os, re, shutil
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
BASE = os.environ.get("BASE", "https://mycytax.com").rstrip("/")
OUT = os.environ.get("OUT", ROOT)
PREFIX = urlparse(BASE).path.rstrip("/")
TODAY = "2026-11-13"
SITE = "MyCyTax"
EMAIL = "cynews24@gmail.com"
PUBLISHER = "Anna"
CYNEWS = "https://cynews24.net/"
LANGS = ["en", "ru", "el"]

UI = {
 "en": dict(
    name=SITE, tagline="Cyprus property and tax calculators",
    calcs="Calculators", guides="Guides", about="About", contact="Contact",
    privacy="Privacy", cookies="Cookies", terms="Terms",
    home="Home", lang="Language", disclaimer="Not legal or tax advice",
    sources="Sources", faq="Questions", related="Related",
    cynews="Cyprus news on CyNews 24",
    lead="Need help buying or selling? Contact us",
    read="Read the guide", open="Open calculator",
    ad="Advertisement",
    home_h="Cyprus property and tax calculators",
    home_desc="Transfer fees, VAT, capital gains, rental income and a mortgage payment, plus practical guides.",
    home_intro="Work out the Land Registry fee, VAT, stamp duty, capital gains tax, rental tax and a mortgage payment. Every rate on MyCyTax is tied to a source. The publisher is Anna, in Cyprus.",
    list_calcs="Cyprus property calculators: transfer fees, stamp duty, VAT, capital gains, rental income and mortgage payments.",
    list_guides="Practical guides to buying, selling, tax residency, non-dom status, title deeds and renting property in Cyprus.",
    contact_t="Contact", contact_d="Write to MyCyTax about buying or selling. The form goes to cynews24@gmail.com.",
    contact_i="The publisher is Anna. Email cynews24@gmail.com, or use the form. The first time the form is used, FormSubmit sends Anna a confirmation email. Until that link is opened, the form will not deliver.",
    thanks_t="Thank you", thanks_d="Your message has been sent.",
    thanks_i="If FormSubmit has already been confirmed for this address, your message is on its way. If this was the first submission, Anna still needs to open the confirmation email before messages are delivered."),
 "ru": dict(
    name=SITE, tagline="Калькуляторы недвижимости и налогов Кипра",
    calcs="Калькуляторы", guides="Справочники", about="О сайте", contact="Контакты",
    privacy="Конфиденциальность", cookies="Файлы cookie", terms="Условия",
    home="Главная", lang="Язык", disclaimer="Это не юридическая и не налоговая консультация",
    sources="Источники", faq="Вопросы", related="Ещё по теме",
    cynews="Новости Кипра на CyNews 24",
    lead="Нужна помощь с покупкой или продажей? Напишите нам",
    read="Читать справочник", open="Открыть калькулятор",
    ad="Реклама",
    home_h="Калькуляторы недвижимости и налогов Кипра",
    home_desc="Сборы кадастра, НДС, прирост капитала, аренда и ипотечный платёж, плюс практические справочники.",
    home_intro="Посчитайте сбор Земельного кадастра, НДС, гербовый сбор, налог на прирост капитала, налог с аренды и ипотечный платёж. Каждая ставка на MyCyTax привязана к источнику. Издатель — Анна, Кипр.",
    list_calcs="Калькуляторы по недвижимости Кипра: сборы кадастра, гербовый сбор, НДС, прирост капитала, аренда и ипотека.",
    list_guides="Практические справочники о покупке, продаже, налоговом резидентстве, статусе non-dom, титулах и аренде на Кипре.",
    contact_t="Контакты", contact_d="Напишите MyCyTax о покупке или продаже. Форма уходит на cynews24@gmail.com.",
    contact_i="Издатель — Анна. Пишите на cynews24@gmail.com или через форму. При первом использовании FormSubmit отправит Анне письмо для подтверждения. Пока ссылка в нём не открыта, форма не доставляет сообщения.",
    thanks_t="Спасибо", thanks_d="Сообщение отправлено.",
    thanks_i="Если FormSubmit для этого адреса уже подтверждён, сообщение в пути. Если это была первая отправка, Анне ещё нужно открыть письмо подтверждения, прежде чем сообщения начнут доходить."),
 "el": dict(
    name=SITE, tagline="Υπολογιστές ακινήτων και φόρων Κύπρου",
    calcs="Υπολογιστές", guides="Οδηγοί", about="Σχετικά", contact="Επικοινωνία",
    privacy="Απόρρητο", cookies="Cookies", terms="Όροι",
    home="Αρχική", lang="Γλώσσα", disclaimer="Δεν είναι νομική ή φορολογική συμβουλή",
    sources="Πηγές", faq="Ερωτήσεις", related="Σχετικά",
    cynews="Ειδήσεις Κύπρου στο CyNews 24",
    lead="Χρειάζεστε βοήθεια για αγορά ή πώληση; Επικοινωνήστε",
    read="Διαβάστε τον οδηγό", open="Άνοιγμα υπολογιστή",
    ad="Διαφήμιση",
    home_h="Υπολογιστές ακινήτων και φόρων Κύπρου",
    home_desc="Τέλη μεταβίβασης, ΦΠΑ, κεφαλαιουχικά κέρδη, ενοίκιο και δόση δανείου, μαζί με πρακτικούς οδηγούς.",
    home_intro="Υπολογίστε το τέλος του Κτηματολογίου, τον ΦΠΑ, το χαρτόσημο, τον φόρο κεφαλαιουχικών κερδών, τον φόρο ενοικίου και τη δόση στεγαστικού. Κάθε συντελεστής στο MyCyTax δένεται με πηγή. Εκδότρια είναι η Άννα, στην Κύπρο.",
    list_calcs="Υπολογιστές ακινήτων Κύπρου: τέλη μεταβίβασης, χαρτόσημο, ΦΠΑ, κεφαλαιουχικά κέρδη, ενοίκιο και δόση δανείου.",
    list_guides="Πρακτικοί οδηγοί για αγορά, πώληση, φορολογική κατοικία, καθεστώς non-dom, τίτλους και ενοικίαση στην Κύπρο.",
    contact_t="Επικοινωνία", contact_d="Γράψτε στο MyCyTax για αγορά ή πώληση. Η φόρμα πηγαίνει στο cynews24@gmail.com.",
    contact_i="Εκδότρια είναι η Άννα. Στείλτε email στο cynews24@gmail.com ή χρησιμοποιήστε τη φόρμα. Την πρώτη φορά το FormSubmit στέλνει email επιβεβαίωσης στην Άννα. Μέχρι να ανοίξει ο σύνδεσμος, η φόρμα δεν παραδίδει μηνύματα.",
    thanks_t="Ευχαριστούμε", thanks_d="Το μήνυμά σας στάλθηκε.",
    thanks_i="Αν το FormSubmit έχει ήδη επιβεβαιωθεί για αυτή τη διεύθυνση, το μήνυμα είναι καθ’ οδόν. Αν αυτή ήταν η πρώτη υποβολή, η Άννα πρέπει ακόμη να ανοίξει το email επιβεβαίωσης."),
}

DISCLAIMER = {
 "en": "Figures on this site are taken from the official and primary sources linked on each page and describe the position as published for 2026. They are general information, not legal, tax or investment advice, and not a quote from the Land Registry or the Tax Department. Rules, reliefs and local fees change, and a transaction can fall outside the ordinary case. Check the linked source, and take advice on your own facts, before you rely on a result.",
 "ru": "Цифры на сайте взяты из официальных и первичных источников, на которые есть ссылки на каждой странице, и описывают правила в том виде, в каком они опубликованы на 2026 год. Это общая информация, а не юридическая, налоговая или инвестиционная консультация и не расчёт Земельного кадастра или Налогового департамента. Правила, льготы и местные сборы меняются, а сделка может не попадать в обычный случай. Прежде чем опираться на результат, сверьтесь с источником по ссылке и получите консультацию по своим фактам.",
 "el": "Τα ποσά σε αυτόν τον ιστότοπο προέρχονται από τις επίσημες και πρωτογενείς πηγές που συνδέονται σε κάθε σελίδα και περιγράφουν όσα έχουν δημοσιευτεί για το 2026. Είναι γενική πληροφόρηση, όχι νομική, φορολογική ή επενδυτική συμβουλή, ούτε βεβαίωση του Κτηματολογίου ή του Τμήματος Φορολογίας. Οι κανόνες, οι απαλλαγές και τα τοπικά τέλη αλλάζουν, και μια συναλλαγή μπορεί να ξεφεύγει από τη συνηθισμένη περίπτωση. Ελέγξτε τη συνδεδεμένη πηγή και ζητήστε συμβουλή για τα δικά σας γεγονότα πριν βασιστείτε σε αποτέλεσμα.",
}

CALC_ORDER = ["transfer-fees", "stamp-duty", "vat", "capital-gains", "rental-yield", "mortgage"]
CALCS = {
 "transfer-fees": {
    "en": ("Property transfer fees", "Land Registry transfer fees on a Cyprus purchase, including the 50% reduction when VAT is not charged and the exemption when it is."),
    "ru": ("Сборы за переоформление", "Сборы Земельного кадастра при покупке на Кипре, включая снижение на 50%, если НДС не взимается, и освобождение, если взимается."),
    "el": ("Τέλη μεταβίβασης ακινήτου", "Τέλη Κτηματολογίου σε αγορά στην Κύπρο, με μείωση 50% όταν δεν επιβάλλεται ΦΠΑ και απαλλαγή όταν επιβάλλεται."),
 },
 "stamp-duty": {
    "en": ("Stamp duty on a purchase contract", "Stamp duty is €0 on a contract signed from 1 January 2026. The old scale still applies if a party signed by 31 December 2025."),
    "ru": ("Гербовый сбор с договора купли", "С договора, подписанного с 1 января 2026 года, гербовый сбор — €0. Старая шкала действует, если сторона подписала до 31 декабря 2025 года."),
    "el": ("Χαρτόσημο συμβολαίου αγοράς", "Το χαρτόσημο είναι €0 σε συμβόλαιο που υπογράφεται από την 1η Ιανουαρίου 2026. Η παλιά κλίμακα ισχύει αν ένα μέρος υπέγραψε έως τις 31 Δεκεμβρίου 2025."),
 },
 "vat": {
    "en": ("VAT on a new property", "Standard VAT is 19%. The 5% rate covers only part of a qualifying primary residence, within the area and value limits."),
    "ru": ("НДС на новое жильё", "Обычная ставка НДС — 19%. Ставка 5% покрывает лишь часть основного жилья, в пределах площади и стоимости."),
    "el": ("ΦΠΑ σε νέα κατοικία", "Ο κανονικός ΦΠΑ είναι 19%. Ο συντελεστής 5% καλύπτει μόνο μέρος κύριας κατοικίας που πληροί τα όρια εμβαδού και αξίας."),
 },
 "capital-gains": {
    "en": ("Capital gains tax", "A 20% tax on the inflation-adjusted gain, with the lifetime exemptions in the Capital Gains Tax Law as amended for 2026."),
    "ru": ("Налог на прирост капитала", "Налог 20% с прироста после индексации и пожизненные вычеты по закону о налоге на прирост капитала в редакции 2026 года."),
    "el": ("Φόρος κεφαλαιουχικών κερδών", "Φόρος 20% στο κέρδος μετά την τιμαριθμική αναπροσαρμογή, με τις ισόβιες απαλλαγές του νόμου όπως ισχύουν για το 2026."),
 },
 "rental-yield": {
    "en": ("Rental yield and income tax", "Gross yield, the 20% statutory deduction, 2026 income-tax bands and GHS. Defence contribution on rent is nil in 2026."),
    "ru": ("Доходность аренды и подоходный налог", "Валовая доходность, уставные 20%, шкалы подоходного налога 2026 года и ГЕСИ. Сбор на оборону с аренды в 2026 году не взимается."),
    "el": ("Απόδοση ενοικίου και φόρος εισοδήματος", "Μικτή απόδοση, η νόμιμη έκπτωση 20%, οι κλίμακες φόρου εισοδήματος του 2026 και η ΓεΣΥ. Η έκτακτη εισφορά για την άμυνα στο ενοίκιο είναι μηδέν το 2026."),
 },
 "mortgage": {
    "en": ("Mortgage payment", "Monthly payment on a euro loan at a fixed rate. The rate is the one your bank offers. This page does not publish a market rate."),
    "ru": ("Платёж по ипотеке", "Ежемесячный платёж по кредиту в евро при фиксированной ставке. Ставку даёт банк. Рыночную ставку эта страница не публикует."),
    "el": ("Δόση στεγαστικού", "Μηνιαία δόση δανείου σε ευρώ με σταθερό επιτόκιο. Το επιτόκιο είναι αυτό που δίνει η τράπεζά σας. Η σελίδα δεν δημοσιεύει επιτόκιο αγοράς."),
 },
}

GUIDE_ORDER = [
 "buying-as-a-foreigner", "total-cost", "selling-and-taxes", "tax-residency", "non-dom",
 "residence-permit", "title-deeds", "renting-out", "off-plan", "taxes-overview",
]

def e(s):
    return html.escape(s if s is not None else "", quote=True)

def loc(lang, path):
    """English lives at the root. Russian and Greek live under /ru and /el."""
    if not path.startswith("/"):
        path = "/" + path
    if lang == "en":
        return path
    if path == "/":
        return f"/{lang}/"
    return f"/{lang}{path}"

def href(path):
    if not path.startswith("/"):
        path = "/" + path
    return f"{PREFIX}{path}" if PREFIX else path

def absu(path):
    return BASE + path

def load_md(lang, slug):
    path = os.path.join(HERE, "guides", lang, slug + ".md")
    raw = open(path, encoding="utf8").read().replace("\r\n", "\n")
    meta = {}
    if raw.startswith("---\n"):
        head, raw = raw.split("---\n", 2)[1:]
        for line in head.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, raw.strip()

def inline(text):
    text = e(text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    return text

def parse(md):
    """Return html body, faq pairs, source html, and plain word count of the article."""
    faq, sources = [], []
    mode = "body"
    blocks, buf = [], []
    words = []
    def flush():
        if buf:
            blocks.append(("p", " ".join(buf).strip()))
            buf.clear()
    for line in md.splitlines():
        s = line.strip()
        if s == "## FAQ":
            flush(); mode = "faq"; continue
        if s == "## Sources":
            flush(); mode = "sources"; continue
        if mode == "sources":
            m = re.match(r"-\s*\[([^\]]+)\]\((https?://[^)]+)\)", s)
            if m:
                sources.append((m.group(1), m.group(2)))
            continue
        if mode == "faq":
            if s.startswith("### "):
                faq.append([s[4:].strip(), []])
            elif s and faq:
                faq[-1][1].append(s)
            continue
        if not s:
            flush(); continue
        if s.startswith("## "):
            flush(); blocks.append(("h2", s[3:].strip())); continue
        if s.startswith("- "):
            flush(); blocks.append(("li", s[2:].strip())); words.append(s[2:].strip()); continue
        buf.append(s)
        words.append(s)
    flush()
    for q, a in faq:
        words.append(q)
        words.extend(a)
    html_parts = []
    for kind, text in blocks:
        if kind == "h2":
            html_parts.append(f"<h2>{inline(text)}</h2>")
            words.append(text)
        elif kind == "li":
            html_parts.append(f"<li>{inline(text)}</li>")
        else:
            html_parts.append(f"<p>{inline(text)}</p>")
    # wrap consecutive li
    body = "\n".join(html_parts)
    body = re.sub(r"(?:<li>.*?</li>\n?)+", lambda m: "<ul>" + m.group(0) + "</ul>", body)
    faqs = [(q, " ".join(a)) for q, a in faq]
    src = "".join(f'<li><a href="{e(u)}">{e(n)}</a></li>' for n, u in sources)
    count = len(re.findall(r"\w+", " ".join(words), flags=re.UNICODE))
    return body, faqs, src, count

def css():
    return r'''
:root{--ink:#1c2420;--muted:#5c675f;--line:#e2d9cc;--paper:#f7f3ec;--card:#fffdf9;--pine:#1e3d34;--pine2:#2f6f5e;--copper:#8c4a2f;--sand:#efe6d6}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;color:var(--ink);background:var(--paper);font:17px/1.6 "Segoe UI",system-ui,-apple-system,sans-serif}
a{color:var(--pine2);text-decoration-thickness:1px;text-underline-offset:2px}
a:hover{color:var(--copper)}
img{max-width:100%;height:auto}
.skip{position:absolute;left:-999px;top:0}.skip:focus{left:8px;background:#fff;padding:8px;z-index:9}
.wrap{width:min(1080px,calc(100% - 32px));margin:0 auto}
header.top{background:var(--pine);color:#f4efe6}
header.top a{color:#f4efe6;text-decoration:none}
.bar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 0}
.logo{font-family:Georgia,"Iowan Old Style",Palatino,serif;font-weight:700;font-size:22px;letter-spacing:-.3px;line-height:1.1}
.logo small{display:block;font-family:"Segoe UI",system-ui,sans-serif;font-weight:500;font-size:12px;letter-spacing:.04em;opacity:.8;margin-top:3px}
nav.main{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
nav.main a{font-size:15px;font-weight:650}
nav.main a[aria-current="page"]{box-shadow:inset 0 -2px 0 #e7c7a4}
.langs a{border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:2px 8px;font-size:13px}
.langs a[aria-current="true"]{background:#f4efe6;color:var(--pine)}
.hero{padding:42px 0 20px}
.hero h1{font-family:Georgia,"Iowan Old Style",Palatino,serif;font-size:clamp(32px,5vw,52px);line-height:1.08;letter-spacing:-.03em;margin:0 0 12px;font-weight:700}
.lede{font-size:19px;color:#2d3832;max-width:68ch}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 16px 14px;display:flex;flex-direction:column;gap:8px;box-shadow:0 1px 0 rgba(30,61,52,.04)}
.card h2,.card h3{font-family:Georgia,Palatino,serif;font-size:22px;line-height:1.2;margin:0}
.card p{margin:0;color:#314038;font-size:15.5px}
.card .more{margin-top:auto;font-weight:700;font-size:14px}
h2.sec{font-family:Georgia,Palatino,serif;font-size:30px;margin:34px 0 12px}
.page{padding:26px 0 10px}
.page h1{font-family:Georgia,Palatino,serif;font-size:clamp(30px,4vw,44px);line-height:1.12;margin:0 0 8px;letter-spacing:-.02em}
.meta{color:var(--muted);font-size:14px;margin:0 0 16px}
article .body h2{font-family:Georgia,Palatino,serif;font-size:26px;margin:28px 0 8px}
article .body p{margin:0 0 14px;max-width:72ch}
article .body ul{margin:0 0 14px;padding-left:1.2em;max-width:72ch}
article .body li{margin:4px 0}
.banner{background:#fff6ea;border:1px solid #ecd7bc;border-radius:12px;padding:12px 14px;color:#5a3b22;font-size:14.5px;margin:12px 0 18px}
.src{background:var(--card);border-left:4px solid var(--pine2);padding:12px 14px;margin:22px 0;border-radius:0 12px 12px 0}
.src h2{margin:0 0 6px;font-size:15px;letter-spacing:.04em;text-transform:uppercase}
.src ul{margin:0;padding-left:18px}
.faq details{border-top:1px solid var(--line);padding:10px 0}
.faq summary{cursor:pointer;font-weight:700}
.calcform{display:grid;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;max-width:720px}
.fld{display:grid;gap:4px;font-weight:650}
.fld input{font:inherit;padding:10px 12px;border:1px solid #d5cbbd;border-radius:10px;background:#fff;width:100%}
.chk{display:flex;gap:8px;align-items:flex-start;font-size:15.5px}
.chk input{width:18px;height:18px;margin-top:3px;flex:none}
fieldset.choices{border:1px solid var(--line);border-radius:12px;margin:0;padding:8px 12px}
button.go,button.send{background:var(--pine);color:#fff;border:0;border-radius:999px;padding:12px 18px;font:inherit;font-weight:700;cursor:pointer;justify-self:start}
button.go:hover,button.send:hover{background:var(--copper)}
table.out{width:100%;border-collapse:collapse;margin-top:8px}
table.out th{text-align:left;font-weight:600;padding:8px 8px 8px 0;vertical-align:top}
table.out td{text-align:right;font-variant-numeric:tabular-nums;padding:8px 0;white-space:nowrap}
table.out tr{border-bottom:1px solid var(--line)}
.result{margin-top:16px;background:#fff;border-radius:16px;padding:8px 16px 16px;border:1px solid var(--line);max-width:720px}
.fine{color:var(--muted);font-size:13px}
.adslot{border:1px dashed #c9bfb0;border-radius:12px;min-height:90px;margin:16px 0;display:flex;align-items:center;justify-content:center;color:#8a8174;font-size:12px;letter-spacing:.08em;text-transform:uppercase;background:transparent}
.adslot:empty{display:none}
form.lead{display:grid;gap:12px;max-width:640px}
.hp{position:absolute;left:-9999px}
footer{margin-top:48px;background:var(--pine);color:#e7e1d6;padding:28px 0;font-size:14.5px}
footer a{color:#fff}
footer .cols{display:flex;flex-wrap:wrap;gap:10px 18px}
footer p{max-width:78ch}
@media(max-width:800px){.grid{grid-template-columns:1fr}.bar{align-items:flex-start;flex-direction:column}}
'''

def head(lang, title, desc, path, alt_path, jsonld=None, extra=""):
    u = UI[lang]
    alts = []
    for l in LANGS:
        alts.append(f'<link rel="alternate" hreflang="{l}" href="{absu(alt_path(l))}">')
    alts.append(f'<link rel="alternate" hreflang="x-default" href="{absu(alt_path("en"))}">')
    ld = ""
    if jsonld:
        import json
        for obj in jsonld:
            ld += '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{absu(path)}">
{chr(10).join(alts)}
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:site_name" content="{e(u["name"])}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{absu(path)}"><meta property="og:type" content="website">
<meta name="theme-color" content="#1e3d34">
<link rel="stylesheet" href="{href("/assets/style.css")}">{ld}{extra}</head>'''

def header(lang, path_for):
    u = UI[lang]
    def item(key, path):
        cur = ' aria-current="page"' if path_for(lang) == path else ""
        return f'<a href="{href(path)}"{cur}>{u[key]}</a>'
    langs = " ".join(
        f'<a href="{href(path_for(l))}" hreflang="{l}" lang="{l}"{" aria-current=\"true\"" if l==lang else ""}>{l.upper()}</a>'
        for l in LANGS)
    return f'''<a class="skip" href="#main">{u["home"]}</a><header class="top"><div class="wrap bar">
<a class="logo" href="{href(loc(lang, "/"))}">{e(u["name"])}<small>{e(u["tagline"])}</small></a>
<nav class="main" aria-label="{e(u["lang"])}">{item("calcs", loc(lang, "/calculators/"))}{item("guides", loc(lang, "/guides/"))}{item("about", loc(lang, "/about/"))}{item("contact", loc(lang, "/contact/"))}
<span class="langs">{langs}</span></nav></div></header>'''

def footer(lang):
    u = UI[lang]
    links = [
        (loc(lang, "/about/"), u["about"]), (loc(lang, "/contact/"), u["contact"]),
        (loc(lang, "/privacy/"), u["privacy"]), (loc(lang, "/cookies/"), u["cookies"]),
        (loc(lang, "/terms/"), u["terms"]),
    ]
    nav = "".join(f'<a href="{href(path)}">{e(name)}</a>' for path, name in links)
    return f'''<footer><div class="wrap"><nav class="cols">{nav}<a href="{CYNEWS}">{e(u["cynews"])}</a></nav>
<p>{e(DISCLAIMER[lang])}</p><p>© 2026 {SITE}. {e(PUBLISHER)}, Cyprus. <a href="mailto:{EMAIL}">{EMAIL}</a></p></div></footer></body></html>'''

def ad(label):
    return f'<div class="adslot" data-ad="{e(label)}" aria-label="{e(UI["en"]["ad"])}"><!-- AdSense slot "{e(label)}": leave empty until a unit is approved. --></div>'

def org():
    return {"@type":"Organization","name":SITE,"url":absu("/"),"email":EMAIL,
            "address":{"@type":"PostalAddress","addressCountry":"CY"},
            "founder":{"@type":"Person","name":PUBLISHER},
            "sameAs":[CYNEWS]}

def page_shell(lang, title, desc, path, alt, body, jsonld=None, active_path=None):
    def path_for(l, alt=alt):
        return alt(l)
    return head(lang, title, desc, path, alt, jsonld) + header(lang, path_for) + body + footer(lang)

def form(lang, next_path):
    labels = {
     "en": dict(name="Name", email="Email", phone="Phone (optional)", intent="I am",
                buy="Buying", sell="Selling", both="Both / not sure",
                where="District or town", msg="Message",
                consent="I agree that MyCyTax may use these details only to reply to this message.",
                send="Send", honey="Leave blank"),
     "ru": dict(name="Имя", email="Эл. почта", phone="Телефон (необязательно)", intent="Я",
                buy="Покупаю", sell="Продаю", both="И то и другое / пока не решил",
                where="Район или город", msg="Сообщение",
                consent="Я согласен, что MyCyTax использует эти сведения только чтобы ответить на это сообщение.",
                send="Отправить", honey="Оставьте пустым"),
     "el": dict(name="Όνομα", email="Email", phone="Τηλέφωνο (προαιρετικό)", intent="Ενδιαφέρομαι για",
                buy="Αγορά", sell="Πώληση", both="Και τα δύο / δεν είμαι σίγουρος",
                where="Επαρχία ή πόλη", msg="Μήνυμα",
                consent="Συμφωνώ ότι το MyCyTax θα χρησιμοποιήσει αυτά τα στοιχεία μόνο για να απαντήσει σε αυτό το μήνυμα.",
                send="Αποστολή", honey="Αφήστε κενό"),
    }[lang]
    opts = "".join(f'<option value="{e(v)}">{e(lab)}</option>' for v, lab in (("buying", labels["buy"]), ("selling", labels["sell"]), ("both", labels["both"])))
    return f'''<form class="lead" action="https://formsubmit.co/{EMAIL}" method="POST">
<input type="hidden" name="_subject" value="MyCyTax enquiry">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="true">
<input type="hidden" name="_next" value="{e(absu(next_path))}">
<p class="hp"><label>{e(labels["honey"])}<input name="_honey" tabindex="-1" autocomplete="off"></label></p>
<label class="fld"><span>{e(labels["name"])}</span><input name="name" required autocomplete="name"></label>
<label class="fld"><span>{e(labels["email"])}</span><input type="email" name="email" required autocomplete="email"></label>
<label class="fld"><span>{e(labels["phone"])}</span><input name="phone" autocomplete="tel"></label>
<label class="fld"><span>{e(labels["intent"])}</span><select name="intent">{opts}</select></label>
<label class="fld"><span>{e(labels["where"])}</span><input name="place"></label>
<label class="fld"><span>{e(labels["msg"])}</span><textarea name="message" required style="min-height:140px;font:inherit;padding:10px;border:1px solid #d5cbbd;border-radius:10px"></textarea></label>
<label class="chk"><input type="checkbox" name="consent" value="yes" required><span>{e(labels["consent"])}</span></label>
<button class="send" type="submit">{e(labels["send"])}</button></form>'''

def home(lang):
    u = UI[lang]
    def alt(l):
        return loc(l, "/")
    title, desc, intro = u["home_h"], u["home_desc"], u["home_intro"]
    cards = []
    for slug in CALC_ORDER:
        t, d = CALCS[slug][lang]
        cards.append(f'<article class="card"><h2>{e(t)}</h2><p>{e(d)}</p><a class="more" href="{href(loc(lang, "/calculators/"+slug+"/"))}">{e(u["open"])}</a></article>')
    guides = []
    for slug in GUIDE_ORDER:
        meta, _ = load_md(lang, slug)
        guides.append(f'<article class="card"><h3>{e(meta["title"])}</h3><p>{e(meta["description"])}</p><a class="more" href="{href(loc(lang, "/guides/"+slug+"/"))}">{e(u["read"])}</a></article>')
    ld = [{"@context":"https://schema.org","@type":"WebSite","name":SITE,"url":absu(alt(lang)),"inLanguage":lang,"publisher":org()},
          {"@context":"https://schema.org",**org()}]
    body = f'''<main id="main"><div class="wrap hero"><h1>{e(title)}</h1><p class="lede">{e(intro)}</p>
<p class="banner">{e(DISCLAIMER[lang])}</p>{ad("home-top")}</div>
<div class="wrap"><h2 class="sec">{e(u["calcs"])}</h2><div class="grid">{"".join(cards)}</div>
<h2 class="sec">{e(u["guides"])}</h2><div class="grid">{"".join(guides)}</div>
<h2 class="sec">{e(u["lead"])}</h2>{form(lang, loc(lang, "/contact/thanks/"))}{ad("home-bottom")}</div></main>'''
    return page_shell(lang, f"{title} | {SITE}", desc, alt(lang), alt, body, ld)

def listing(lang, kind):
    u = UI[lang]
    if kind == "calculators":
        title, desc, items = u["calcs"], u["list_calcs"], CALC_ORDER
        def card(slug):
            t, d = CALCS[slug][lang]
            return f'<article class="card"><h2>{e(t)}</h2><p>{e(d)}</p><a class="more" href="{href(loc(lang, "/calculators/"+slug+"/"))}">{e(u["open"])}</a></article>'
        path = loc(lang, "/calculators/")
    else:
        title, desc, items = u["guides"], u["list_guides"], GUIDE_ORDER
        def card(slug):
            meta, _ = load_md(lang, slug)
            return f'<article class="card"><h2>{e(meta["title"])}</h2><p>{e(meta["description"])}</p><a class="more" href="{href(loc(lang, "/guides/"+slug+"/"))}">{e(u["read"])}</a></article>'
        path = loc(lang, "/guides/")
    def alt(l, kind=kind):
        return loc(l, "/calculators/" if kind == "calculators" else "/guides/")
    body = f'<main id="main" class="wrap page"><h1>{e(title)}</h1><p class="lede">{e(desc)}</p><div class="grid">{"".join(card(s) for s in items)}</div></main>'
    return page_shell(lang, f"{title} | {SITE}", desc, path if path.endswith("/") else path+"/", alt, body)

def calc_page(lang, slug):
    u = UI[lang]
    t, d = CALCS[slug][lang]
    path = loc(lang, f"/calculators/{slug}/")
    def alt(l, slug=slug):
        return loc(l, f"/calculators/{slug}/")
    notes = {
     "transfer-fees": {
        "en": "The scale is Chapter 17 of the Department of Lands and Surveys (Fees and Charges) Law, Cap. 219: 3% to €85,000, 5% from €85,001 to €170,000 and 8% above that, on the contract price or the market value if the Director does not accept the price. Gov.cy states a total exemption where the transfer is a transaction subject to VAT, and a 50% exemption where it is not. The DLS sale notes add two limits: the 50% reduction is not given where the seller acquired the property in a forced sale under Parts VI and VIA of the Transfer and Mortgage Law 9/1965, and a contract not deposited within six months can increase the fee by 10% when title is transferred. Fees are shown per equal share because the scale is applied to the value each buyer takes. Unequal shares should be entered as separate calculations.",
        "ru": "Шкала — глава 17 Закона о сборах и пошлинах Департамента земель и землеустройства, гл. 219: 3% до €85 000, 5% с €85 001 до €170 000 и 8% сверх этого, с цены договора или с рыночной стоимости, если директор её не принимает. На Gov.cy указано полное освобождение, если переход связан со сделкой, облагаемой НДС, и освобождение на 50%, если не связан. В примечаниях DLS к продаже есть два ограничения: скидка 50% не даётся, если продавец приобрёл объект на принудительной продаже по частям VI и VIA закона 9/1965 о переходе и ипотеке, а договор, не сданный в течение шести месяцев, может увеличить сбор на 10% при переоформлении. Сбор показан на равную долю, потому что шкала применяется к стоимости, которую получает каждый покупатель. Неравные доли считайте отдельными расчётами.",
        "el": "Η κλίμακα είναι το Κεφάλαιο 17 του περί Τελών και Δικαιωμάτων Νόμου του Τμήματος Κτηματολογίου, Κεφ. 219: 3% έως €85.000, 5% από €85.001 έως €170.000 και 8% πάνω από αυτό, στην τιμή του συμβολαίου ή στην αγοραία αξία αν ο Διευθυντής δεν δέχεται την τιμή. Το Gov.cy αναφέρει πλήρη απαλλαγή όταν η μεταβίβαση αφορά συναλλαγή που υπόκειται σε ΦΠΑ, και απαλλαγή 50% όταν δεν υπόκειται. Οι σημειώσεις του Κτηματολογίου προσθέτουν δύο όρια: η μείωση 50% δεν δίνεται αν ο πωλητής απέκτησε το ακίνητο σε αναγκαστική πώληση κατά τα Μέρη VI και VIA του Νόμου 9/1965, και συμβόλαιο που δεν κατατέθηκε μέσα σε έξι μήνες μπορεί να αυξήσει το τέλος κατά 10% κατά τη μεταβίβαση. Τα τέλη φαίνονται ανά ίσο μερίδιο, γιατί η κλίμακα εφαρμόζεται στην αξία που παίρνει κάθε αγοραστής. Άνισα μερίδια υπολογίζονται χωριστά.",
     },
     "stamp-duty": {
        "en": "Law 239(I)/2025 repealed the Stamp Duty Laws from 1 January 2026. The Tax Department's announcement, as reported by KPMG, is that a document drawn up and signed by at least one party on or after that date is not subject to stamp duty, while a document signed by at least one party on or before 31 December 2025 still is. The old scale for a fixed-sum contract was nil up to €5,000, €1.50 per €1,000 or part from €5,001 to €170,000, and €2 per €1,000 or part above €170,000, capped at €20,000. This calculator rounds each band up to the next €1,000, which is what “or part thereof” requires.",
        "ru": "Закон 239(I)/2025 отменил законы о гербовом сборе с 1 января 2026 года. По объявлению Налогового департамента, как его передаёт KPMG, документ, составленный и подписанный хотя бы одной стороной в эту дату или позже, гербовым сбором не облагается, а документ, подписанный хотя бы одной стороной не позднее 31 декабря 2025 года, облагается. Старая шкала для договора с твёрдой суммой: ноль до €5 000, €1,50 за €1 000 или часть с €5 001 до €170 000 и €2 за €1 000 или часть сверх €170 000, не более €20 000. Калькулятор округляет каждый диапазон до следующих €1 000 вверх — так и работает формулировка «или часть».",
        "el": "Ο Νόμος 239(I)/2025 κατάργησε τους περί Χαρτοσήμων Νόμους από την 1η Ιανουαρίου 2026. Σύμφωνα με την ανακοίνωση του Τμήματος Φορολογίας, όπως τη μεταφέρει η KPMG, έγγραφο που καταρτίστηκε και υπογράφηκε από τουλάχιστον ένα μέρος κατά ή μετά την ημερομηνία αυτή δεν υπόκειται σε χαρτόσημο, ενώ έγγραφο που υπέγραψε τουλάχιστον ένα μέρος έως τις 31 Δεκεμβρίου 2025 εξακολουθεί. Η παλιά κλίμακα για συμβόλαιο με σταθερό ποσό ήταν μηδέν έως €5.000, €1,50 ανά €1.000 ή μέρος από €5.001 έως €170.000 και €2 ανά €1.000 ή μέρος πάνω από €170.000, με ανώτατο €20.000. Ο υπολογιστής στρογγυλοποιεί κάθε κλιμάκιο στην επόμενη χιλιάδα, όπως απαιτεί το «ή μέρος».",
     },
     "vat": {
        "en": "The standard rate is 19%. From the amending law in force since 2023, the 5% rate applies to a house or apartment used as the buyer's primary and permanent residence: the first 130 m² and up to €350,000 of value, provided the total buildable area does not exceed 190 m² and the total value does not exceed €475,000. Between those inner and outer limits the 5% applies only to the qualifying portion, in proportion. Over 190 m² or over €475,000, the reduced rate is not available. Persons with disabilities may claim 5% on the first 190 m² irrespective of the total area; this calculator still applies the €350,000 / €475,000 value limits and says so. The Tax Department publishes its own tool. Use that tool before you file. A transitional route for some projects with a planning application by 31 October 2023 required the reduced-rate application by 15 June 2026. That date has passed. If you think the old 200 m² route still applies to a filed case, ask the Tax Department. This calculator does not apply it.",
        "ru": "Обычная ставка — 19%. По поправке, действующей с 2023 года, ставка 5% применяется к дому или квартире, которые служат покупателю основным и постоянным жильём: первые 130 м² и стоимость до €350 000, если общая площадь застройки не выше 190 м², а вся стоимость не выше €475 000. Между внутренним и внешним пределом 5% применяется только к подходящей доле, пропорционально. Свыше 190 м² или €475 000 сниженная ставка недоступна. Лица с инвалидностью могут заявить 5% на первые 190 м² независимо от общей площади; этот калькулятор всё равно применяет пределы €350 000 и €475 000 и так об этом и пишет. У Налогового департамента есть собственный инструмент. Перед подачей используйте его. Переходный путь для части проектов с заявлением на планировочное разрешение до 31 октября 2023 года требовал заявления на сниженную ставку до 15 июня 2026 года. Эта дата прошла. Если вам кажется, что старый порог 200 м² ещё действует по уже поданному делу, спросите Налоговый департамент. Этот калькулятор его не применяет.",
        "el": "Ο κανονικός συντελεστής είναι 19%. Με την τροποποίηση που ισχύει από το 2023, το 5% εφαρμόζεται σε οικία ή διαμέρισμα που χρησιμοποιείται ως κύρια και μόνιμη κατοικία του αγοραστή: τα πρώτα 130 τ.μ. και αξία έως €350.000, εφόσον το συνολικό εμβαδόν δομήσιμου δεν υπερβαίνει τα 190 τ.μ. και η συνολική αξία τα €475.000. Ανάμεσα στο εσωτερικό και το εξωτερικό όριο το 5% πιάνει μόνο το επιλέξιμο μέρος, αναλογικά. Πάνω από 190 τ.μ. ή €475.000 ο μειωμένος συντελεστής δεν είναι διαθέσιμος. Άτομα με αναπηρία μπορούν να ζητήσουν 5% στα πρώτα 190 τ.μ. ανεξάρτητα από το συνολικό εμβαδόν. Αυτός ο υπολογιστής εξακολουθεί να εφαρμόζει τα όρια αξίας €350.000 και €475.000 και το λέει. Το Τμήμα Φορολογίας δημοσιεύει δικό του εργαλείο. Χρησιμοποιήστε το πριν την αίτηση. Μεταβατική οδός για ορισμένα έργα με αίτηση πολεοδομικής άδειας έως τις 31 Οκτωβρίου 2023 απαιτούσε αίτηση μειωμένου συντελεστή έως τις 15 Ιουνίου 2026. Η ημερομηνία πέρασε. Αν νομίζετε ότι η παλιά οδός των 200 τ.μ. ισχύει ακόμη για κατατεθειμένη υπόθεση, ρωτήστε το Τμήμα Φορολογίας. Αυτός ο υπολογιστής δεν την εφαρμόζει.",
     },
     "capital-gains": {
        "en": "Capital gains tax is 20% of the gain on disposal of immovable property in Cyprus, and on some share disposals. The Tax Department says the gain is reduced for inflation using the official retail price index. This page does not store that index. Enter the ratio from the Department's inflation table (indexed cost ÷ original cost). Disposal costs are not indexed. For an individual, the Capital Gains Tax Law as consolidated on CyLaw now states a lifetime exemption of €30,000, €50,000 where a farmer sells agricultural land, and €150,000 on a qualifying main residence used by the owner for at least five years (ten years if it is not the first such disposal) on land of up to 1.5 decares. A person does not get both the general exemption and the residence exemption. Anything already used comes off the amount. Companies do not get these lifetime exemptions. Gifts, inheritances and several reorganisations are outside the tax on conditions set out by the Tax Department. This calculator taxes one sale and does not decide whether the sale qualifies.",
        "ru": "Налог на прирост капитала — 20% с прироста при отчуждении недвижимости на Кипре и при некоторых продажах акций. Налоговый департамент уменьшает прирост на инфляцию по официальному индексу розничных цен. Эта страница индекс не хранит. Введите коэффициент из таблицы инфляции департамента (проиндексированная стоимость ÷ исходная). Расходы на продажу не индексируются. Для физического лица закон о налоге на прирост капитала в сводке на CyLaw теперь указывает пожизненный вычет €30 000, €50 000, если фермер продаёт сельхозземлю, и €150 000 по основному жилью, которым владелец пользовался не меньше пяти лет (десять лет, если это не первое такое отчуждение), на участке до 1,5 декара. Общий вычет и вычет за жильё вместе не даются. Уже использованное вычитается. Компании этих пожизненных вычетов не имеют. Дарение, наследование и ряд реорганизаций вне налога на условиях, которые описал Налоговый департамент. Калькулятор считает одну продажу и не решает, подпадает ли она под льготу.",
        "el": "Ο φόρος κεφαλαιουχικών κερδών είναι 20% στο κέρδος από διάθεση ακίνητης ιδιοκτησίας στην Κύπρο και σε ορισμένες διαθέσεις μετοχών. Το Τμήμα Φορολογίας μειώνει το κέρδος για τον πληθωρισμό με τον επίσημο δείκτη τιμών λιανικής. Αυτή η σελίδα δεν αποθηκεύει τον δείκτη. Εισάγετε τον λόγο από τον πίνακα πληθωρισμού του Τμήματος (τιμαριθμική αξία διά αρχική). Τα έξοδα διάθεσης δεν τιμαριθμοποιούνται. Για φυσικό πρόσωπο, ο νόμος όπως είναι κωδικοποιημένος στο CyLaw αναφέρει ισόβια απαλλαγή €30.000, €50.000 όταν γεωργός πωλεί γεωργική γη, και €150.000 για κύρια κατοικία που χρησιμοποιήθηκε από τον ιδιοκτήτη τουλάχιστον πέντε έτη (δέκα αν δεν είναι η πρώτη τέτοια διάθεση) σε γη έως 1,5 δεκάρια. Δεν δικαιούται κανείς και τη γενική απαλλαγή και την απαλλαγή κατοικίας. Ό,τι έχει ήδη χρησιμοποιηθεί αφαιρείται. Οι εταιρείες δεν έχουν αυτές τις ισόβιες απαλλαγές. Δωρεές, κληρονομιές και ορισμένες αναδιοργανώσεις είναι εκτός φόρου υπό όρους που εκθέτει το Τμήμα. Ο υπολογιστής φορολογεί μία πώληση και δεν κρίνει αν η πώληση πληροί τις προϋποθέσεις.",
     },
     "rental-yield": {
        "en": "A 20% deduction from gross rent is the statutory income-tax deduction for rental income, as set out in PwC's Tax Facts & Figures 2026, which tracks the Income Tax Law. Interest on a loan used to buy the building, and wear and tear if it is not already exhausted, can be extra. Do not put the 20% in the extra box. From 1 January 2026 the income-tax bands for an individual are nil on the first €22,000, 20% to €32,000, 25% to €42,000, 30% to €72,000 and 35% above that. The Tax Department's older individuals page still shows the pre-2026 bands; the 2026 reform pages are the ones used here. Special Defence Contribution on rent was abolished from the 2026 tax year for domiciled residents as well. It is shown as zero. GHS on rental income is 2.65% of the gross rent on the Tax Department's rental page. An annual ceiling can apply under the GHS law and is not modelled, because this page does not reproduce a 2026 ceiling from that law. Short-stay income can be treated as business income on conditions in a 2023 Tax Department circular. That route is not modelled.",
        "ru": "Вычет 20% из валовой аренды — уставный вычет для подоходного налога с аренды, как он изложен в PwC Tax Facts & Figures 2026, который следует закону о подоходном налоге. Проценты по кредиту на покупку здания и амортизация, если она ещё не исчерпана, могут быть дополнительными. Не вписывайте эти 20% в поле дополнительных расходов. С 1 января 2026 года шкалы подоходного налога для физического лица: ноль на первые €22 000, 20% до €32 000, 25% до €42 000, 30% до €72 000 и 35% сверх этого. На старой странице Налогового департамента для физических лиц всё ещё видны шкалы до 2026 года; здесь использованы страницы реформы 2026 года. Специальный сбор на оборону с аренды с налогового 2026 года отменён и для домицилированных резидентов. Он показан нулём. Взнос ГЕСИ с аренды — 2,65% валовой аренды по странице Налогового департамента об аренде. Годовой потолок по закону о ГЕСИ возможен и здесь не смоделирован, потому что эта страница не воспроизводит потолок 2026 года из того закона. Доход от краткосрочной сдачи при условиях циркуляра 2023 года может считаться предпринимательским. Этот путь не смоделирован.",
        "el": "Η έκπτωση 20% από το ακαθάριστο ενοίκιο είναι η νόμιμη έκπτωση φόρου εισοδήματος για εισόδημα από ενοίκια, όπως εκτίθεται στο Tax Facts & Figures 2026 της PwC, που ακολουθεί τον περί Φορολογίας του Εισοδήματος Νόμο. Τόκοι δανείου για την αγορά του κτιρίου και φθορά, αν δεν έχει ήδη εξαντληθεί, μπορούν να είναι επιπλέον. Μην βάλετε το 20% στο πεδίο των επιπλέον εξόδων. Από την 1η Ιανουαρίου 2026 οι κλίμακες για φυσικό πρόσωπο είναι μηδέν στα πρώτα €22.000, 20% έως €32.000, 25% έως €42.000, 30% έως €72.000 και 35% πάνω από αυτό. Η παλαιότερη σελίδα του Τμήματος Φορολογίας για φυσικά πρόσωπα δείχνει ακόμη τις κλίμακες προ του 2026. Εδώ χρησιμοποιούνται οι σελίδες της μεταρρύθμισης του 2026. Η έκτακτη εισφορά για την άμυνα στο ενοίκιο καταργήθηκε από το φορολογικό έτος 2026 και για κατοίκους με κατοικία. Φαίνεται μηδέν. Η εισφορά ΓεΣΥ στο ενοίκιο είναι 2,65% του ακαθάριστου ενοικίου στη σελίδα του Τμήματος. Ετήσιο ανώτατο μπορεί να ισχύει κατά τον νόμο ΓεΣΥ και δεν μοντελοποιείται εδώ, γιατί η σελίδα δεν αναπαράγει ανώτατο του 2026 από εκείνον τον νόμο. Εισόδημα βραχυχρόνιας μίσθωσης μπορεί να αντιμετωπιστεί ως επιχειρηματικό υπό όρους εγκυκλίου του 2023. Αυτή η οδός δεν μοντελοποιείται.",
     },
     "mortgage": {
        "en": "The monthly payment is the standard annuity: the loan, the monthly interest rate and the number of months. It assumes the rate never changes and that you pay no bank fee, no life-policy premium and no early-repayment charge. Cyprus banks publish their own rates. This page deliberately does not state one.",
        "ru": "Ежемесячный платёж — обычный аннуитет: сумма кредита, месячная ставка и число месяцев. Расчёт предполагает, что ставка не меняется и что нет комиссии банка, страховой премии и штрафа за досрочное погашение. Ставки публикуют сами кипрские банки. Эта страница намеренно не называет ни одной.",
        "el": "Η μηνιαία δόση είναι η συνήθης τοκοχρεολυτική: το δάνειο, το μηνιαίο επιτόκιο και ο αριθμός των μηνών. Υποθέτει ότι το επιτόκιο δεν αλλάζει και ότι δεν πληρώνετε έξοδο τράπεζας, ασφάλιστρο ζωής ή ποινή πρόωρης εξόφλησης. Οι κυπριακές τράπεζες δημοσιεύουν τα δικά τους επιτόκια. Αυτή η σελίδα σκόπιμα δεν αναφέρει κανένα.",
     },
    }
    note = notes[slug][lang]
    ld = [{"@context":"https://schema.org","@type":"WebApplication","name":t,"applicationCategory":"FinanceApplication","operatingSystem":"Web","url":absu(path),
           "description":d,"inLanguage":lang,"offers":{"@type":"Offer","price":"0","priceCurrency":"EUR"},"publisher":org()},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
              {"@type":"Question","name":t,"acceptedAnswer":{"@type":"Answer","text":d}}]}]
    body = f'''<main id="main" class="wrap page"><p class="meta"><a href="{href(loc(lang, "/calculators/"))}">{e(u["calcs"])}</a></p>
<h1>{e(t)}</h1><p class="lede">{e(d)}</p><p class="banner">{e(DISCLAIMER[lang])}</p>{ad("calc-top")}
<div id="calc" data-calc="{e(slug.split("-")[0] if False else {"transfer-fees":"transfer","stamp-duty":"stamp","vat":"vat","capital-gains":"cgt","rental-yield":"rental","mortgage":"mortgage"}[slug])}"></div>
<div class="body"><h2>{e(u["sources"])}</h2><p>{note}</p></div>{ad("calc-bottom")}</main>
<script src="{href("/assets/calc.js")}" defer></script>'''
    return page_shell(lang, f"{t} | {SITE}", d, path, alt, body, ld)

def guide_page(lang, slug, words_out):
    u = UI[lang]
    meta, md = load_md(lang, slug)
    body_html, faqs, src, count = parse(md)
    words_out.append((lang, slug, count))
    path = loc(lang, f"/guides/{slug}/")
    def alt(l, slug=slug):
        return loc(l, f"/guides/{slug}/")
    faq_html = ""
    if faqs:
        faq_html = f'<section class="faq"><h2>{e(u["faq"])}</h2>' + "".join(
            f"<details><summary>{inline(q)}</summary><p>{inline(a)}</p></details>" for q, a in faqs) + "</section>"
    ld = [
        {"@context":"https://schema.org","@type":"Article","headline":meta["title"],"description":meta["description"],
         "inLanguage":lang,"datePublished":TODAY,"dateModified":TODAY,"mainEntityOfPage":absu(path),
         "author":{"@type":"Organization","name":SITE,"url":absu("/")},
         "publisher":{"@type":"Organization","name":SITE,"url":absu("/")}},
    ]
    if faqs:
        ld.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q, a in faqs]})
    body = f'''<main id="main" class="wrap page"><p class="meta"><a href="{href(loc(lang, "/guides/"))}">{e(u["guides"])}</a></p>
<article><h1>{e(meta["title"])}</h1><p class="lede">{e(meta["description"])}</p>
<p class="banner">{e(DISCLAIMER[lang])}</p>{ad("guide-top")}
<div class="body">{body_html}</div>
{faq_html}
<section class="src"><h2>{e(u["sources"])}</h2><ul>{src}</ul></section>
{ad("guide-bottom")}</article></main>'''
    return page_shell(lang, f'{meta["title"]} | {SITE}', meta["description"], path, alt, body, ld)

STATIC = {
 "about": {
   "en": ("About", "Who publishes MyCyTax, and how the calculators are produced.",
          ["MyCyTax is an independent site of property and tax calculators and practical guides in English, Russian and Greek. English is the primary language.",
           "The publisher is Anna. The site is based in Cyprus. Editorial and advertising contact is cynews24@gmail.com. No other person is named here, because this page does not invent a staff list.",
           "Calculators run in your browser. The rates are the ones stated by the Department of Lands and Surveys, the Tax Department, the Ministry of Interior, Gov.cy, the consolidated statutes on CyLaw, or a named professional summary where the statute is in Greek and the summary tracks it. If a figure is not settled, the page says so.",
           "The site is separate from CyNews 24, which publishes Cyprus news in Russian, English and Greek. A link to CyNews 24 is in the footer.",
           "Advertising spaces are empty on purpose. No advertising script runs. When an ad network is added, the privacy and cookie pages will be updated."]),
   "ru": ("О сайте", "Кто издаёт MyCyTax и как считаются калькуляторы.",
          ["MyCyTax — независимый сайт калькуляторов и практических справочников по недвижимости и налогам на английском, русском и греческом. Основной язык — английский.",
           "Издатель — Анна. Сайт базируется на Кипре. Контакт редакции и рекламы: cynews24@gmail.com. Других имён здесь нет: страница не придумывает список сотрудников.",
           "Калькуляторы работают в браузере. Ставки — те, что указали Департамент земель и землеустройства, Налоговый департамент, Министерство внутренних дел, Gov.cy, сводные тексты на CyLaw или названный профессиональный обзор, если закон по-гречески, а обзор ему следует. Если цифра не устоялась, страница так и пишет.",
           "Сайт отделён от CyNews 24, который публикует новости Кипра на русском, английском и греческом. Ссылка на CyNews 24 есть в подвале.",
           "Рекламные места нарочно пустые. Рекламный скрипт не выполняется. Когда появится рекламная сеть, страницы о конфиденциальности и cookie будут обновлены."]),
   "el": ("Σχετικά", "Ποιος εκδίδει το MyCyTax και πώς παράγονται οι υπολογιστές.",
          ["Το MyCyTax είναι ανεξάρτητος ιστότοπος υπολογιστών και πρακτικών οδηγών για ακίνητα και φόρους, στα αγγλικά, ρωσικά και ελληνικά. Η κύρια γλώσσα είναι η αγγλική.",
           "Εκδότρια είναι η Άννα. Ο ιστότοπος έχει έδρα την Κύπρο. Επικοινωνία σύνταξης και διαφήμισης: cynews24@gmail.com. Δεν κατονομάζεται άλλο πρόσωπο, γιατί η σελίδα δεν επινοεί κατάλογο συνεργατών.",
           "Οι υπολογιστές τρέχουν στον φυλλομετρητή σας. Οι συντελεστές είναι αυτοί που δηλώνουν το Τμήμα Κτηματολογίου και Χωρομετρίας, το Τμήμα Φορολογίας, το Υπουργείο Εσωτερικών, το Gov.cy, τα κωδικοποιημένα κείμενα στο CyLaw, ή επώνυμη επαγγελματική σύνοψη όπου ο νόμος είναι στα ελληνικά και η σύνοψη τον ακολουθεί. Αν ένα ποσό δεν είναι σταθερό, η σελίδα το λέει.",
           "Ο ιστότοπος είναι χωριστός από το CyNews 24, που δημοσιεύει ειδήσεις Κύπρου στα ρωσικά, αγγλικά και ελληνικά. Σύνδεσμος προς το CyNews 24 υπάρχει στο υποσέλιδο.",
           "Οι θέσεις διαφήμισης είναι σκόπιμα κενές. Δεν τρέχει διαφημιστικό σενάριο. Όταν προστεθεί δίκτυο διαφημίσεων, οι σελίδες απορρήτου και cookies θα ενημερωθούν."]),
 },
 "privacy": {
   "en": ("Privacy policy", "What MyCyTax does with the contact form, and what it does not collect.",
          ["The publisher is Anna, based in Cyprus. Email: cynews24@gmail.com.",
           "The contact form sends your name, email, phone if you give one, whether you are buying or selling, a place name and your message through FormSubmit (formsubmit.co) to cynews24@gmail.com. Those details are used only to reply. FormSubmit processes the submission in order to deliver the email. The details are not sold and are not added to a marketing list.",
           "The calculators run on your device. The numbers you type are not sent to this site.",
           "The site does not use Google Analytics or any other analytics tool. It does not embed advertising scripts. If advertising is added later, this page will say what data the ad provider receives.",
           "Email sent to cynews24@gmail.com is kept for as long as needed to answer it."]),
   "ru": ("Политика конфиденциальности", "Что MyCyTax делает с формой связи и чего не собирает.",
          ["Издатель — Анна, Кипр. Эл. почта: cynews24@gmail.com.",
           "Форма отправляет имя, эл. почту, телефон, если вы его указали, покупку или продажу, место и сообщение через FormSubmit (formsubmit.co) на cynews24@gmail.com. Эти сведения используются только для ответа. FormSubmit обрабатывает отправку, чтобы доставить письмо. Сведения не продаются и не попадают в маркетинговый список.",
           "Калькуляторы работают на вашем устройстве. Введённые цифры на этот сайт не отправляются.",
           "Сайт не использует Google Analytics и другие средства аналитики. Рекламные скрипты не подключаются. Если реклама появится позже, эта страница скажет, какие данные получает рекламная служба.",
           "Письма на cynews24@gmail.com хранятся, пока нужен ответ."]),
   "el": ("Πολιτική απορρήτου", "Τι κάνει το MyCyTax με τη φόρμα επικοινωνίας και τι δεν συλλέγει.",
          ["Εκδότρια είναι η Άννα, με έδρα την Κύπρο. Email: cynews24@gmail.com.",
           "Η φόρμα στέλνει το όνομα, το email, το τηλέφωνο αν το δώσετε, αν αγοράζετε ή πουλάτε, έναν τόπο και το μήνυμά σας μέσω FormSubmit (formsubmit.co) στο cynews24@gmail.com. Τα στοιχεία χρησιμοποιούνται μόνο για απάντηση. Το FormSubmit επεξεργάζεται την υποβολή για να παραδώσει το email. Τα στοιχεία δεν πωλούνται και δεν μπαίνουν σε λίστα μάρκετινγκ.",
           "Οι υπολογιστές τρέχουν στη συσκευή σας. Οι αριθμοί που πληκτρολογείτε δεν στέλνονται σε αυτόν τον ιστότοπο.",
           "Ο ιστότοπος δεν χρησιμοποιεί Google Analytics ούτε άλλο εργαλείο αναλυτικών. Δεν ενσωματώνει διαφημιστικά σενάρια. Αν προστεθεί διαφήμιση αργότερα, η σελίδα θα πει ποια δεδομένα λαμβάνει ο πάροχος.",
           "Το email προς cynews24@gmail.com κρατιέται για όσο χρειάζεται η απάντηση."]),
 },
 "cookies": {
   "en": ("Cookie notice", "Cookies on this site today, and what would change if advertising is added.",
          ["MyCyTax does not set its own cookies. The calculators and the language switcher do not store a cookie. The language switcher is an ordinary link.",
           "The contact form is a normal POST to FormSubmit. Any cookie that service sets is described in FormSubmit's own policy, not by this site.",
           "There is no advertising code, so there are no advertising cookies. If Google AdSense or another network is added, that provider may set cookies, including on visitors in the EEA, and a consent tool will be added before those tags run. The placeholder boxes on the pages are empty.",
           "You can refuse or delete cookies in your browser. Because this site does not rely on a cookie to show a page, the calculators and guides still work if cookies are blocked."]),
   "ru": ("Уведомление о файлах cookie", "Какие cookie есть на сайте сейчас и что изменится, если появится реклама.",
          ["MyCyTax не ставит собственные cookie. Калькуляторы и переключатель языка cookie не записывают. Переключатель языка — обычная ссылка.",
           "Форма — обычный POST в FormSubmit. Любые cookie этой службы описаны в её собственной политике, а не на этом сайте.",
           "Рекламного кода нет, поэтому нет и рекламных cookie. Если будут подключены Google AdSense или другая сеть, эта служба может ставить cookie, в том числе посетителям из ЕЭЗ, и до запуска меток появится инструмент согласия. Прямоугольники на страницах пустые.",
           "Отказаться от cookie или удалить их можно в браузере. Страницы не зависят от cookie, поэтому калькуляторы и справочники работают и при их блокировке."]),
   "el": ("Ειδοποίηση για cookies", "Ποια cookies υπάρχουν σήμερα και τι θα άλλαζε αν προστεθεί διαφήμιση.",
          ["Το MyCyTax δεν τοποθετεί δικά του cookies. Οι υπολογιστές και ο διακόπτης γλώσσας δεν αποθηκεύουν cookie. Ο διακόπτης γλώσσας είναι απλός σύνδεσμος.",
           "Η φόρμα είναι συνηθισμένο POST προς το FormSubmit. Όποιο cookie ορίζει εκείνη η υπηρεσία περιγράφεται στη δική της πολιτική, όχι από αυτόν τον ιστότοπο.",
           "Δεν υπάρχει κώδικας διαφήμισης, άρα δεν υπάρχουν διαφημιστικά cookies. Αν προστεθεί Google AdSense ή άλλο δίκτυο, ο πάροχος μπορεί να τοποθετεί cookies, και σε επισκέπτες του ΕΟΧ, και εργαλείο συγκατάθεσης θα προστεθεί πριν τρέξουν αυτές οι ετικέτες. Τα πλαίσια στις σελίδες είναι κενά.",
           "Μπορείτε να αρνηθείτε ή να διαγράψετε cookies στον φυλλομετρητή. Επειδή ο ιστότοπος δεν βασίζεται σε cookie για να δείξει σελίδα, οι υπολογιστές και οι οδηγοί λειτουργούν και με αποκλεισμένα cookies."]),
 },
 "terms": {
   "en": ("Terms and disclaimer", "The limits of what this site is offering.",
          ["Using the site does not create a client relationship with the publisher or with anyone else. Nothing on the site is legal advice, tax advice, immigration advice or a valuation.",
           "The calculators apply the rates described on each page to the numbers you type. They do not know your residence, your domicile, your other income, earlier exemptions you have used, or whether the Land Registry will accept the price in the contract. Two equal buyers are assumed only when you type that number.",
           "Official sources prevail. Where a professional firm's summary is cited because the statute is published in Greek, that is identified. Where this site is unsure, it says so.",
           "To the extent the law allows, the publisher is not liable for a decision you take because of a page or a calculator result. Local authority fees, utility deposits and bank charges are not included unless a page says they are.",
           "You may link to the pages. You may not copy the guides or the calculator code and present them as your own."]),
   "ru": ("Условия и оговорка", "Пределы того, что предлагает этот сайт.",
          ["Пользование сайтом не создаёт отношений клиента с издателем или с кем-либо ещё. Ничто на сайте не является юридической, налоговой или иммиграционной консультацией и не является оценкой.",
           "Калькуляторы применяют ставки, описанные на странице, к введённым числам. Им неизвестны ваше резидентство, домициль, другой доход, уже использованные вычеты и то, примет ли Земельный кадастр цену в договоре. Два равных покупателя предполагаются только если вы ввели это число.",
           "Приоритет у официальных источников. Если назван обзор фирмы, потому что закон опубликован по-гречески, это указано. Где сайт не уверен, он так и пишет.",
           "В пределах, допустимых законом, издатель не отвечает за решение, которое вы приняли из-за страницы или результата калькулятора. Местные сборы, залоги за коммуникации и банковские комиссии не включены, если страница прямо не говорит об обратном.",
           "На страницы можно ссылаться. Нельзя копировать справочники или код калькуляторов и выдавать их за свои."]),
   "el": ("Όροι και αποποίηση", "Τα όρια αυτού που προσφέρει ο ιστότοπος.",
          ["Η χρήση του ιστοτόπου δεν δημιουργεί σχέση εντολέα με την εκδότρια ή με οποιονδήποτε άλλον. Τίποτα στον ιστότοπο δεν είναι νομική, φορολογική ή μεταναστευτική συμβουλή, ούτε εκτίμηση.",
           "Οι υπολογιστές εφαρμόζουν τους συντελεστές που περιγράφει κάθε σελίδα στους αριθμούς που πληκτρολογείτε. Δεν γνωρίζουν την κατοικία σας, τον τόπο διαμονής, το άλλο εισόδημα, απαλλαγές που έχετε ήδη χρησιμοποιήσει, ούτε αν το Κτηματολόγιο θα δεχτεί την τιμή του συμβολαίου. Δύο ίσοι αγοραστές υποτίθενται μόνο όταν πληκτρολογήσετε αυτόν τον αριθμό.",
           "Οι επίσημες πηγές υπερισχύουν. Όπου αναφέρεται σύνοψη δικηγορικού γραφείου επειδή ο νόμος είναι δημοσιευμένος στα ελληνικά, αυτό δηλώνεται. Όπου ο ιστότοπος δεν είναι βέβαιος, το λέει.",
           "Στο μέτρο που επιτρέπει ο νόμος, η εκδότρια δεν ευθύνεται για απόφαση που παίρνετε λόγω σελίδας ή αποτελέσματος υπολογιστή. Τέλη τοπικής αρχής, εγγυήσεις υπηρεσιών κοινής ωφέλειας και τραπεζικές χρεώσεις δεν περιλαμβάνονται, εκτός αν μια σελίδα το λέει.",
           "Μπορείτε να συνδέεστε προς τις σελίδες. Δεν μπορείτε να αντιγράφετε τους οδηγούς ή τον κώδικα των υπολογιστών και να τους παρουσιάζετε ως δικούς σας."]),
 },
}

def static_page(lang, slug):
    title, desc, paras = STATIC[slug][lang]
    path = loc(lang, f"/{slug}/")
    def alt(l, slug=slug):
        return loc(l, f"/{slug}/")
    body_html = "".join(f"<p>{e(p)}</p>" for p in paras)
    extra = ""
    if slug == "contact":
        pass
    body = f'<main id="main" class="wrap page"><h1>{e(title)}</h1><p class="lede">{e(desc)}</p><div class="body">{body_html}</div>'
    if slug == "about":
        body += f'<p><a href="{href(loc(lang, "/contact/"))}">{e(UI[lang]["contact"])}</a></p>'
    body += "</main>"
    return page_shell(lang, f"{title} | {SITE}", desc, path, alt, body)

def contact(lang):
    u = UI[lang]
    path = loc(lang, "/contact/")
    def alt(l):
        return loc(l, "/contact/")
    title, desc, intro = u["contact_t"], u["contact_d"], u["contact_i"]
    body = f'<main id="main" class="wrap page"><h1>{e(title)}</h1><p class="lede">{e(desc)}</p><p>{e(intro)}</p><p class="banner">{e(DISCLAIMER[lang])}</p>{form(lang, loc(lang, "/contact/thanks/"))}</main>'
    return page_shell(lang, f"{title} | {SITE}", desc, path, alt, body)

def thanks(lang):
    u = UI[lang]
    path = loc(lang, "/contact/thanks/")
    def alt(l):
        return loc(l, "/contact/thanks/")
    title, desc, text = u["thanks_t"], u["thanks_d"], u["thanks_i"]
    body = f'<main id="main" class="wrap page"><h1>{e(title)}</h1><p>{e(text)}</p></main>'
    html_page = page_shell(lang, f"{title} | {SITE}", desc, path, alt, body)
    return html_page.replace('content="index,follow,max-image-preview:large"', 'content="noindex,follow"')

def w(rel, content):
    path = os.path.join(OUT, rel.lstrip("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        f.write(content)

def sitemap():
    paths = ["/"]
    for slug in ("about", "contact", "privacy", "cookies", "terms", "calculators", "guides"):
        paths.append(f"/{slug}/")
    for slug in CALC_ORDER:
        paths.append(f"/calculators/{slug}/")
    for slug in GUIDE_ORDER:
        paths.append(f"/guides/{slug}/")
    urls = [loc(lang, p) for lang in LANGS for p in paths]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"<url><loc>{e(absu(u))}</loc><lastmod>{TODAY}</lastmod></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"

def main():
    keep = {"source", ".git"}
    for name in os.listdir(OUT):
        if name in keep or name.startswith("."):
            continue
        path = os.path.join(OUT, name)
        if name == "README.md":
            continue
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif name not in ("README.md",):
            if name.endswith((".html", ".xml", ".txt", ".css", ".js")) or name == "CNAME":
                os.remove(path)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "static", "calc.js"), os.path.join(OUT, "assets", "calc.js"))
    w("/assets/style.css", css())
    words = []
    for lang in LANGS:
        w(loc(lang, "/") + "index.html", home(lang))
        w(loc(lang, "/calculators/") + "index.html", listing(lang, "calculators"))
        w(loc(lang, "/guides/") + "index.html", listing(lang, "guides"))
        for slug in CALC_ORDER:
            w(loc(lang, f"/calculators/{slug}/") + "index.html", calc_page(lang, slug))
        for slug in GUIDE_ORDER:
            w(loc(lang, f"/guides/{slug}/") + "index.html", guide_page(lang, slug, words))
        for slug in STATIC:
            w(loc(lang, f"/{slug}/") + "index.html", static_page(lang, slug))
        w(loc(lang, "/contact/") + "index.html", contact(lang))
        w(loc(lang, "/contact/thanks/") + "index.html", thanks(lang))
    w("/sitemap.xml", sitemap())
    w("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    # GitHub Pages custom domain. Rewritten on every build so a rebuild cannot drop it.
    w("/CNAME", "mycytax.com\n")
    # Google Search Console verification. Rewritten on every build so a rebuild cannot drop it.
    w("/google62249645dc64d12b.html", "google-site-verification: google62249645dc64d12b.html\n")
    short = [x for x in words if x[2] < 800]
    print("built", BASE)
    for lang, slug, n in words:
        flag = " SHORT" if n < 800 or n > 1600 else ""
        print(f"  {lang} {slug} {n}{flag}")
    if short:
        raise SystemExit("guides under 800 words: " + ", ".join(f"{a}/{b}={c}" for a, b, c in short))

if __name__ == "__main__":
    main()
