# -*- coding: utf-8 -*-
"""MyCyTax static generator. English, Russian and Greek.

    BASE=https://mycytax.com python3 source/build.py

The custom domain is mycytax.com. BASE is the origin with no trailing slash.
The path inside BASE becomes the link prefix. No trailing slash.
"""
import datetime, html, json, os, re, shutil, subprocess, urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
BASE = os.environ.get("BASE", "https://mycytax.com").rstrip("/")
OUT = os.environ.get("OUT", ROOT)
PREFIX = urlparse(BASE).path.rstrip("/")
TODAY = "2026-11-13"
SITE = "MyCyTax"
ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1547877294743851" crossorigin="anonymous"></script>'
ADS_TXT = "google.com, pub-1547877294743851, DIRECT, f08c47fec0942fa0\n"
EMAIL = "info@mycytax.com"
# Every lead, contact and listing form posts here. The public contact address stays EMAIL.
LEADS_EMAIL = "2877novosti@gmail.com"
PUBLISHER = "Anna"
CYNEWS = "https://cynews24.net/"
CYNEWS_SITEMAP = "https://cynews24.net/news-sitemap.xml"
CYNEWS_TIMEOUT = 5
_CYNEWS_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
}
# None for a language means the build-time fetch failed or returned nothing.
# The page then links to that language's CyNews24 home instead of headlines.
CYNEWS_HEADLINES = {lang: None for lang in ("en", "ru", "el")}
_MISSING = object()
TG_RU = "https://t.me/mycytax"
TG_EN = "https://t.me/mycytaxen"
IG = "https://www.instagram.com/mycytax/"
LANGS = ["en", "ru", "el"]
# Empty strings stay empty. The meta tag and the gtag snippet are omitted until a real value is set.
# indexnow_key is the public IndexNow key: the build writes /<key>.txt containing the key.
def _load_site_config():
    path = os.path.join(HERE, "site.json")
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected an object")
    def pick(key):
        value = data.get(key, "")
        if value is None:
            return ""
        return str(value).strip()
    key = pick("indexnow_key").lower()
    if not re.fullmatch(r"[0-9a-f]{32}", key):
        raise SystemExit(f"{path}: indexnow_key must be 32 hex characters")
    ga = pick("ga4_measurement_id")
    if ga and not re.fullmatch(r"G-[A-Z0-9]+", ga):
        raise SystemExit(f"{path}: ga4_measurement_id must be empty or look like G-XXXX")
    return {"bing_msvalidate": pick("bing_msvalidate"), "ga4_measurement_id": ga, "indexnow_key": key}

SITE_CONFIG = _load_site_config()
BING_MSVALIDATE = SITE_CONFIG["bing_msvalidate"]
GA4_ID = SITE_CONFIG["ga4_measurement_id"]
INDEXNOW_KEY = SITE_CONFIG["indexnow_key"]
# Editable copy lives in source/content/ (one JSON file per guide or page) and is
# loaded below. Calculator logic and the chrome around it stay in this file.
CONTENT = os.path.join(HERE, "content")
GUIDE_DIR = os.path.join(CONTENT, "guides")
PAGE_DIR = os.path.join(CONTENT, "pages")
PAGE_ORDER = ("about", "privacy", "cookies", "terms", "affiliate-disclosure")

UI = {
 "en": dict(
    name=SITE, tagline="Cyprus property and tax calculators",
    calcs="Calculators", guides="Guides", services="Services", about="About", contact="Contact",
    privacy="Privacy", cookies="Cookies", terms="Terms",
    affiliates="Affiliate links",
    consult="Tax paperwork",
    aff_note="Some buttons on this page are partner links. If you use one and buy, the publisher may earn a commission. Prices on the provider site can change. Nothing here is a recommendation for your own money.",
    home="Home", lang="Language", disclaimer="Not legal or tax advice",
    sources="Sources", faq="Questions", related="Related",
    projects="Our projects",
    project_cynews="CyNews24 — Cyprus news",
    news_h="Latest Cyprus news",
    lead="Need help buying or selling? Contact us",
    read="Read the guide", open="Open calculator",
    ad="Advertisement",
    tg="Follow us on Telegram",
    tg_other="Russian channel",
    tg_short="Telegram",
    ig="MyCyTax on Instagram",
    ig_short="Instagram",
    feed="MyCyTax guides",
    cookie_settings="Cookie settings",
    cookie_accept="Accept",
    cookie_reject="Reject",
    cookie_banner="Advertising and analytics cookies stay off until you accept. You can change this later.",
    real_estate="Real Estate",
    real_estate_desc="Property guides and tax calculators, and any home or project that is listed for sale.",
    home_h="Cyprus property and tax calculators",
    home_desc="Transfer fees, VAT, capital gains, rental income and a mortgage payment, plus practical guides.",
    home_intro="Work out the Land Registry fee, VAT, stamp duty, capital gains tax, rental tax and a mortgage payment. Every rate on MyCyTax is tied to a source. The publisher is Anna, in Cyprus.",
    list_calcs="Cyprus property calculators: transfer fees, stamp duty, VAT, capital gains, rental income and mortgage payments.",
    list_guides="Practical guides to buying, selling, tax residency, non-dom status, title deeds, renting, settling in, comparing a mortgage, storing savings, brokers and a VPN.",
    contact_t="Contact", contact_d="Write to MyCyTax about buying or selling. The form goes to 2877novosti@gmail.com.",
    contact_i="The publisher is Anna. Email info@mycytax.com, or use the form. The first message through the form asks FormSubmit to send a confirmation email to 2877novosti@gmail.com. Until that link is opened, the form will not deliver. We reply within 24 hours.",
    thanks_t="Thank you", thanks_d="Your message has been sent.",
    thanks_i="Thank you. If this address is already confirmed with FormSubmit, we will reply within 24 hours. If this was the first message, Anna still needs to open the confirmation email before it is delivered."),
 "ru": dict(
    name=SITE, tagline="Калькуляторы недвижимости и налогов Кипра",
    calcs="Калькуляторы", guides="Справочники", services="Услуги", about="О сайте", contact="Контакты",
    privacy="Конфиденциальность", cookies="Файлы cookie", terms="Условия",
    affiliates="Партнёрские ссылки",
    consult="Налоги и документы",
    aff_note="Некоторые кнопки на этой странице — партнёрские ссылки. Если вы по ним оформите услугу, издатель может получить комиссию. Цена провайдера меняется. Это не рекомендация для ваших денег.",
    home="Главная", lang="Язык", disclaimer="Это не юридическая и не налоговая консультация",
    sources="Источники", faq="Вопросы", related="Ещё по теме",
    projects="Наши проекты",
    project_cynews="CyNews24 — новости Кипра",
    news_h="Свежие новости Кипра",
    lead="Нужна помощь с покупкой или продажей? Напишите нам",
    read="Читать справочник", open="Открыть калькулятор",
    ad="Реклама",
    tg="Подписывайтесь на наш Telegram-канал",
    tg_other="Английский канал",
    tg_short="Telegram",
    ig="MyCyTax в Instagram",
    ig_short="Instagram",
    feed="Справочники MyCyTax",
    cookie_settings="Настройки cookie",
    cookie_accept="Принять",
    cookie_reject="Отклонить",
    cookie_banner="Рекламные и аналитические cookie выключены, пока вы их не примете. Выбор можно изменить позже.",
    real_estate="Недвижимость",
    real_estate_desc="Справочники по недвижимости и налоговые калькуляторы, а также объявления о продаже, если они опубликованы.",
    home_h="Калькуляторы недвижимости и налогов Кипра",
    home_desc="Сборы кадастра, НДС, прирост капитала, аренда и ипотечный платёж, плюс практические справочники.",
    home_intro="Посчитайте сбор Земельного кадастра, НДС, гербовый сбор, налог на прирост капитала, налог с аренды и ипотечный платёж. Каждая ставка на MyCyTax привязана к источнику. Издатель — Анна, Кипр.",
    list_calcs="Калькуляторы по недвижимости Кипра: сборы кадастра, гербовый сбор, НДС, прирост капитала, аренда и ипотека.",
    list_guides="Практические справочники о покупке, продаже, налоговом резидентстве, статусе non-dom, титулах, аренде, переезде, сравнении ипотеки, хранении сбережений, брокерах и VPN.",
    contact_t="Контакты", contact_d="Напишите MyCyTax о покупке или продаже. Форма уходит на 2877novosti@gmail.com.",
    contact_i="Издатель — Анна. Пишите на info@mycytax.com или через форму. Первое сообщение через форму FormSubmit подтверждает письмом на 2877novosti@gmail.com. Пока ссылка не открыта, форма не доставляет заявки. Ответим в течение 24 часов.",
    thanks_t="Спасибо", thanks_d="Сообщение отправлено.",
    thanks_i="Спасибо. Если адрес уже подтверждён в FormSubmit, ответим в течение 24 часов. Если это первое сообщение, Анне ещё нужно открыть письмо подтверждения, прежде чем оно будет доставлено."),
 "el": dict(
    name=SITE, tagline="Υπολογιστές ακινήτων και φόρων Κύπρου",
    calcs="Υπολογιστές", guides="Οδηγοί", services="Υπηρεσίες", about="Σχετικά", contact="Επικοινωνία",
    privacy="Απόρρητο", cookies="Cookies", terms="Όροι",
    affiliates="Σύνδεσμοι συνεργατών",
    consult="Φόροι και έγγραφα",
    aff_note="Ορισμένα κουμπιά σε αυτή τη σελίδα είναι σύνδεσμοι συνεργατών. Αν αγοράσετε μέσω αυτών, η εκδότρια μπορεί να λάβει προμήθεια. Η τιμή του παρόχου αλλάζει. Δεν είναι σύσταση για τα δικά σας χρήματα.",
    home="Αρχική", lang="Γλώσσα", disclaimer="Δεν είναι νομική ή φορολογική συμβουλή",
    sources="Πηγές", faq="Ερωτήσεις", related="Σχετικά",
    projects="Τα έργα μας",
    project_cynews="CyNews24 — ειδήσεις Κύπρου",
    news_h="Τελευταία νέα Κύπρου",
    lead="Χρειάζεστε βοήθεια για αγορά ή πώληση; Επικοινωνήστε",
    read="Διαβάστε τον οδηγό", open="Άνοιγμα υπολογιστή",
    ad="Διαφήμιση",
    tg="Ακολουθήστε μας στο Telegram",
    tg_other="Ρωσικό κανάλι",
    tg_short="Telegram",
    ig="Το MyCyTax στο Instagram",
    ig_short="Instagram",
    feed="Οδηγοί MyCyTax",
    cookie_settings="Ρυθμίσεις cookies",
    cookie_accept="Αποδοχή",
    cookie_reject="Απόρριψη",
    cookie_banner="Τα cookies διαφήμισης και ανάλυσης μένουν κλειστά μέχρι να τα αποδεχτείτε. Μπορείτε να το αλλάξετε αργότερα.",
    real_estate="Ακίνητα",
    real_estate_desc="Οδηγοί για ακίνητα και φορολογικοί υπολογιστές, και όσες κατοικίες ή έργα έχουν δημοσιευτεί προς πώληση.",
    home_h="Υπολογιστές ακινήτων και φόρων Κύπρου",
    home_desc="Τέλη μεταβίβασης, ΦΠΑ, κεφαλαιουχικά κέρδη, ενοίκιο και δόση δανείου, μαζί με πρακτικούς οδηγούς.",
    home_intro="Υπολογίστε το τέλος του Κτηματολογίου, τον ΦΠΑ, το χαρτόσημο, τον φόρο κεφαλαιουχικών κερδών, τον φόρο ενοικίου και τη δόση στεγαστικού. Κάθε συντελεστής στο MyCyTax δένεται με πηγή. Εκδότρια είναι η Άννα, στην Κύπρο.",
    list_calcs="Υπολογιστές ακινήτων Κύπρου: τέλη μεταβίβασης, χαρτόσημο, ΦΠΑ, κεφαλαιουχικά κέρδη, ενοίκιο και δόση δανείου.",
    list_guides="Πρακτικοί οδηγοί για αγορά, πώληση, φορολογική κατοικία, καθεστώς non-dom, τίτλους, ενοικίαση, εγκατάσταση, σύγκριση στεγαστικού, φύλαξη αποταμιεύσεων, χρηματιστές και VPN.",
    contact_t="Επικοινωνία", contact_d="Γράψτε στο MyCyTax για αγορά ή πώληση. Η φόρμα πηγαίνει στο 2877novosti@gmail.com.",
    contact_i="Εκδότρια είναι η Άννα. Στείλτε email στο info@mycytax.com ή χρησιμοποιήστε τη φόρμα. Το πρώτο μήνυμα μέσω της φόρμας το επιβεβαιώνει το FormSubmit με email στο 2877novosti@gmail.com. Μέχρι να ανοίξει ο σύνδεσμος, η φόρμα δεν παραδίδει αιτήματα. Απαντάμε μέσα σε 24 ώρες.",
    thanks_t="Ευχαριστούμε", thanks_d="Το μήνυμά σας στάλθηκε.",
    thanks_i="Ευχαριστούμε. Αν η διεύθυνση έχει ήδη επιβεβαιωθεί στο FormSubmit, θα απαντήσουμε μέσα σε 24 ώρες. Αν αυτό ήταν το πρώτο μήνυμα, η Άννα πρέπει ακόμη να ανοίξει το email επιβεβαίωσης πριν παραδοθεί."),
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

# Russian is required. English and Greek are optional: a missing translation falls
# back to the Russian text, and that language version is marked noindex.
_TR = dict(zip("абвгдеёзийклмнопрстуфхыэ", "abvgdeezijklmnoprstufhye")) | {"ж":"zh","ц":"ts","ч":"ch","ш":"sh","щ":"sch","ю":"yu","я":"ya","ъ":"","ь":""}

def _clean(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v.replace("\r\n", "\n").replace("\r", "\n").strip()
    return v

def _seq(v):
    if isinstance(v, bool) or v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None

def slugify(v):
    """Latin page address. Used when a new guide leaves the address field empty."""
    v = "".join(_TR.get(ch, ch) for ch in str(v).lower())
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", v)).strip("-")[:70].strip("-")

# A published address may be one segment or a hub plus one child, so a handbook
# can live at /guides/resident-handbook/tic/ without a second generator.
GUIDE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)?$")

def guide_address(raw, stem, title):
    """Keep a valid slug, including one slash. Otherwise derive one."""
    raw = _clean(raw)
    if raw and GUIDE_SLUG_RE.fullmatch(raw):
        return raw
    return slugify(raw or stem) or slugify(title)

def _guide_ok(block):
    return bool(_clean(block.get("title")) and _clean(block.get("description")) and _clean(block.get("body")))

def guide_markdown(block):
    """Rebuild the markdown the existing parser expects, from CMS fields."""
    parts = [_clean(block.get("body"))]
    faqs = []
    for item in block.get("faq") or []:
        if not isinstance(item, dict):
            continue
        q = _clean(item.get("q"))
        a = _clean(item.get("a"))
        if q or a:
            faqs.append((q, a))
    if faqs:
        chunk = ["## FAQ"]
        for q, a in faqs:
            chunk.append(f"### {q}")
            if a:
                chunk.append(a)
        parts.append("\n\n".join(chunk))
    src_lines = []
    for item in block.get("sources") or []:
        if not isinstance(item, dict):
            continue
        url = _clean(item.get("url"))
        name = _clean(item.get("name")) or url
        if url:
            src_lines.append(f"- [{name}]({url})")
    if src_lines:
        parts.append("## Sources\n\n" + "\n".join(src_lines))
    return "\n\n".join(p for p in parts if p)

def load_guides():
    if not os.path.isdir(GUIDE_DIR):
        raise SystemExit(f"missing {GUIDE_DIR}")
    out = []
    for fn in sorted(os.listdir(GUIDE_DIR)):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(GUIDE_DIR, fn)
        with open(path, encoding="utf8") as f:
            d = json.load(f)
        stem = os.path.splitext(fn)[0]
        ru = d.get("ru") if isinstance(d.get("ru"), dict) else {}
        # Page address: the slug field, else the file name, else the Russian title.
        slug = guide_address(d.get("slug"), stem, ru.get("title", ""))
        if not slug:
            raise SystemExit(f"{path}: cannot make a page address (slug)")
        if not _guide_ok(ru):
            raise SystemExit(f"{path}: Russian title, description and text are required")
        g = {"slug": slug, "seq": _seq(d.get("seq")), "missing": set(), "text": {},
             "image": d.get("image") if isinstance(d.get("image"), dict) else None}
        for lang in LANGS:
            src = d.get(lang) if isinstance(d.get(lang), dict) else {}
            if lang != "ru" and not _guide_ok(src):
                g["missing"].add(lang)
                src = ru
            g["text"][lang] = {
                "title": _clean(src.get("title")),
                "description": _clean(src.get("description")),
                "md": guide_markdown(src),
            }
        out.append(g)
    slugs = [g["slug"] for g in out]
    dup = sorted({s for s in slugs if slugs.count(s) > 1})
    if dup:
        raise SystemExit(f"Duplicate guide slugs: {dup}")
    # Guides migrated from the old files keep their original order (seq). New ones follow.
    out.sort(key=lambda g: (g["seq"] is None, g["seq"] if g["seq"] is not None else 0, g["slug"]))
    return out

GUIDES = {g["slug"]: g for g in load_guides()}
GUIDE_ORDER = [g["slug"] for g in sorted(GUIDES.values(), key=lambda g: (g["seq"] is None, g["seq"] if g["seq"] is not None else 0, g["slug"]))]

def load_md(lang, slug):
    t = GUIDES[slug]["text"][lang]
    return {"title": t["title"], "description": t["description"]}, t["md"]

def _paras(v):
    """Paragraphs from a list, or from text with a blank line between paragraphs."""
    if isinstance(v, list):
        out = []
        for item in v:
            if isinstance(item, dict):
                item = item.get("text") or item.get("paragraph") or ""
            s = _clean(item)
            if s:
                out.append(s)
        return out
    text = _clean(v)
    return [" ".join(x.strip() for x in p.split("\n")).strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

def _page_fields(block):
    if not isinstance(block, dict):
        return "", "", []
    title = _clean(block.get("title"))
    desc = _clean(block.get("description"))
    raw = block.get("body") if block.get("body") is not None else block.get("paragraphs")
    return title, desc, _paras(raw)

def load_pages():
    pages = {}
    for slug in PAGE_ORDER:
        path = os.path.join(PAGE_DIR, slug + ".json")
        if not os.path.isfile(path):
            raise SystemExit(f"missing {path}")
        with open(path, encoding="utf8") as f:
            d = json.load(f)
        ru = d.get("ru") if isinstance(d.get("ru"), dict) else {}
        title, desc, paras = _page_fields(ru)
        if not (title and desc and paras):
            raise SystemExit(f"{path}: Russian title, description and text are required")
        page = {"missing": set(), "text": {}}
        for lang in LANGS:
            src = d.get(lang) if isinstance(d.get(lang), dict) else {}
            t, ds, ps = _page_fields(src)
            if lang != "ru" and not (t and ds and ps):
                page["missing"].add(lang)
                t, ds, ps = title, desc, paras
            page["text"][lang] = (t, ds, ps)
        pages[slug] = page
    return pages

PAGES = load_pages()
PARTNERS_PATH = os.path.join(HERE, "partners.json")
PARTNER_HEADING = {
    "en": "Useful services",
    "ru": "Полезные сервисы",
    "el": "Χρήσιμες υπηρεσίες",
}
PARTNER_DISCLOSURE = {
    "en": "Some links may be partner links; this does not change the price for you.",
    "ru": "Некоторые ссылки могут быть партнёрскими; для вас цена от этого не меняется.",
    "el": "Ορισμένοι σύνδεσμοι μπορεί να είναι σύνδεσμοι συνεργατών· αυτό δεν αλλάζει την τιμή για εσάς.",
}

def _https(url):
    url = _clean(url)
    if url.startswith("https://") and not any(ch.isspace() for ch in url):
        return url
    return ""

def load_partners(path=None):
    path = path or PARTNERS_PATH
    if not os.path.isfile(path):
        raise SystemExit(f"missing {path}")
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("partners"), list):
        raise SystemExit(f"{path}: expected an object with a partners list")
    return data

def partner_href(partner):
    """Use affiliate_url when it is a non-empty https link. Otherwise use url.

    A non-empty affiliate_url that is not https is ignored, so a bad paste
    cannot replace the public homepage and is never written into the page.
    """
    if not isinstance(partner, dict):
        return ""
    affiliate = _clean(partner.get("affiliate_url"))
    if affiliate:
        safe = _https(affiliate)
        if safe:
            return safe
    return _https(partner.get("url"))

def _partner_text(data, key, lang, fallback):
    block = data.get(key) if isinstance(data, dict) and isinstance(data.get(key), dict) else {}
    return _clean(block.get(lang)) or _clean(block.get("en")) or fallback.get(lang, "")

def _partner_description(partner, lang):
    desc = partner.get("description") if isinstance(partner.get("description"), dict) else {}
    return _clean(desc.get(lang)) or _clean(desc.get("en")) or _clean(desc.get("ru"))

PARTNERS = load_partners()

# Partner buttons on the new guides and under calculators. One file holds every URL.
# Placeholders (#AFFILIATE_…) stay until the owner pastes an https link.
AFFILIATES_PATH = os.path.join(HERE, "static", "affiliates.js")
AFFILIATE_KEYS = (
    "nordvpn", "surfshark", "proton", "ledger", "trezor", "binance", "bybit",
    "interactivebrokers", "genki", "semrush", "amazon",
)
_AFFILIATE_PLACEHOLDER = re.compile(r"^#AFFILIATE_[A-Z0-9]+$")
AFF_REL = "nofollow sponsored noopener"

def _affiliate_url_ok(url):
    if not isinstance(url, str) or any(ch.isspace() for ch in url):
        return False
    if _AFFILIATE_PLACEHOLDER.fullmatch(url):
        return True
    return url.startswith("https://")

def load_affiliates(path=None):
    path = path or AFFILIATES_PATH
    if not os.path.isfile(path):
        raise SystemExit(f"missing {path}")
    with open(path, encoding="utf8") as f:
        text = f.read()
    m = re.search(r"MYCYTAX_AFFILIATES\s*=\s*(\{.*?\})\s*;", text, re.S)
    if not m:
        raise SystemExit(f"{path}: expected window.MYCYTAX_AFFILIATES = {{...}};")
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected an object of partner links")
    missing = [key for key in AFFILIATE_KEYS if key not in data]
    if missing:
        raise SystemExit(f"{path}: missing keys: {', '.join(missing)}")
    for key, url in data.items():
        if not re.fullmatch(r"[a-z0-9]+", str(key)) or not _affiliate_url_ok(url):
            raise SystemExit(
                f"{path}: {key} must be an https:// link or a #AFFILIATE_ placeholder"
            )
    return data

AFFILIATES = load_affiliates()

def affiliate_href(key, data=None):
    data = AFFILIATES if data is None else data
    url = data.get(key) if isinstance(data, dict) else ""
    return url if _affiliate_url_ok(url) else ""

def amazon_search_url(query, data=None):
    """Amazon.de search URL. The tag is read from the amazon entry. No product codes."""
    from urllib.parse import parse_qs, quote, urlparse
    query = _clean(query)
    base = affiliate_href("amazon", data)
    if not query or not base:
        return ""
    parsed = urlparse(base)
    tags = parse_qs(parsed.query).get("tag") or []
    tag = tags[0] if tags else ""
    if not tag or parsed.scheme != "https" or not parsed.netloc:
        return ""
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return origin + "/s?k=" + quote(query, safe="") + "&tag=" + quote(tag, safe="")

def amazon_links(items):
    """One box of Amazon search buttons. items are (label, query) pairs."""
    buttons = []
    for label, query in items:
        label = _clean(label)
        url = amazon_search_url(query)
        if not label or not url:
            continue
        buttons.append(
            f'<a class="aff-btn" data-amazon-search="{e(query)}" href="{e(url)}" '
            f'rel="sponsored nofollow noopener" target="_blank">{e(label)}</a>'
        )
    if not buttons:
        return ""
    return '<aside class="aff-offer aff-amazon">' + "".join(buttons) + "</aside>\n"

def affiliate_offer(key, label, note="", data=None):
    """Highlighted partner button. Empty when the key has no safe URL."""
    url = affiliate_href(key, data)
    label = _clean(label)
    if not url or not label:
        return ""
    note = _clean(note)
    note_html = f"<p>{inline(note)}</p>" if note else ""
    return (
        f'<aside class="aff-offer">{note_html}'
        f'<a class="aff-btn" data-affiliate="{e(key)}" href="{e(url)}" '
        f'rel="{AFF_REL}" target="_blank">{e(label)}</a></aside>\n'
    )

def affiliate_disclosure(lang):
    u = UI[lang]
    return (
        f'<p class="aff-disclosure">{e(u["aff_note"])} '
        f'<a href="{href(loc(lang, "/affiliate-disclosure/"))}">{e(u["affiliates"])}</a>.</p>\n'
    )

def affiliate_runtime():
    """Re-read the one config file in the browser, so a replaced link wins."""
    return (
        f'<script src="{href("/assets/js/affiliates.js")}"></script>'
        "<script>(function(){"
        "var map=window.MYCYTAX_AFFILIATES||{};"
        'document.querySelectorAll("[data-affiliate]").forEach(function(a){'
        'var url=map[a.getAttribute("data-affiliate")];'
        'if(typeof url!=="string")return;'
        'if(url.indexOf("https://")===0||url.indexOf("#AFFILIATE_")===0){a.href=url;}'
        "});"
        'if(typeof window.MYCYTAX_AMAZON_SEARCH==="function"){'
        'document.querySelectorAll("[data-amazon-search]").forEach(function(a){'
        'a.href=window.MYCYTAX_AMAZON_SEARCH(a.getAttribute("data-amazon-search"));'
        "});}"
        "})();</script>\n"
    )

def partners_block(lang, kind, slug, data=None):
    """Small partner box. Empty when no partner lists this guide or calculator."""
    data = PARTNERS if data is None else data
    if not isinstance(data, dict):
        return ""
    page = f"{kind}/{slug}"
    items = []
    for partner in data.get("partners") or []:
        if not isinstance(partner, dict):
            continue
        pages = partner.get("applies_to") or []
        if page not in pages:
            continue
        url = partner_href(partner)
        name = _clean(partner.get("name"))
        if not url or not name:
            continue
        desc = _partner_description(partner, lang)
        blurb = f"<p>{e(desc)}</p>" if desc else ""
        items.append(
            f'<li><a href="{e(url)}" rel="sponsored noopener" target="_blank">{e(name)}</a>{blurb}</li>'
        )
    if not items:
        return ""
    heading = _partner_text(data, "heading", lang, PARTNER_HEADING)
    note = _partner_text(data, "disclosure", lang, PARTNER_DISCLOSURE)
    return (
        f'<aside class="partners"><h2>{e(heading)}</h2><ul>{"".join(items)}</ul>'
        f'<p class="partner-note">{e(note)}</p></aside>\n'
    )

def inline(text):
    text = e(text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^\s)]+)\)",
                  lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    return text

def parse(md):
    """Return html body, faq pairs, source html, and plain word count of the article."""
    faq, sources = [], []
    mode = "body"
    blocks, buf = [], []
    words = []
    table = None
    def flush():
        if buf:
            blocks.append(("p", " ".join(buf).strip()))
            buf.clear()
    def flush_table():
        nonlocal table
        if table:
            blocks.append(("table", table))
            table = None
    for line in md.splitlines():
        s = line.strip()
        if s == "## FAQ":
            flush(); flush_table(); mode = "faq"; continue
        if s == "## Sources":
            flush(); flush_table(); mode = "sources"; continue
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
        offer = re.fullmatch(r"!!([a-z0-9]+)\|([^|]+?)(?:\|(.*))?$", s)
        if offer:
            flush(); flush_table()
            label = offer.group(2).strip()
            note = (offer.group(3) or "").strip()
            blocks.append(("offer", (offer.group(1), label, note)))
            words.append(label)
            if note:
                words.append(note)
            continue
        if s.startswith("|"):
            flush()
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-{3,}:?", c or "-") for c in cells):
                continue
            if table is None:
                table = []
            table.append(cells)
            words.append(" ".join(cells))
            continue
        flush_table()
        if not s:
            flush(); continue
        if s.startswith("## "):
            flush(); blocks.append(("h2", s[3:].strip())); continue
        if s.startswith("- "):
            flush(); blocks.append(("li", s[2:].strip())); words.append(s[2:].strip()); continue
        numbered = re.match(r"\d+\.\s+(.*)", s)
        if numbered:
            flush(); blocks.append(("oli", numbered.group(1).strip())); words.append(numbered.group(1).strip()); continue
        buf.append(s)
        words.append(s)
    flush()
    flush_table()
    for q, a in faq:
        words.append(q)
        words.extend(a)
    html_parts = []
    list_tag = None
    def close_list():
        nonlocal list_tag
        if list_tag:
            html_parts.append(f"</{list_tag}>")
            list_tag = None
    i = 0
    nblocks = len(blocks)
    while i < nblocks:
        kind, text = blocks[i]
        if kind == "offer" and text[0] == "amazon":
            close_list()
            group = []
            while i < nblocks and blocks[i][0] == "offer" and blocks[i][1][0] == "amazon":
                _key, label, query = blocks[i][1]
                group.append((label, query or label))
                i += 1
            html_parts.append(amazon_links(group))
            continue
        if kind == "offer":
            close_list()
            html_parts.append(affiliate_offer(text[0], text[1], text[2]))
            i += 1
            continue
        if kind in ("li", "oli"):
            tag = "ul" if kind == "li" else "ol"
            if list_tag != tag:
                close_list()
                html_parts.append(f"<{tag}>")
                list_tag = tag
            html_parts.append(f"<li>{inline(text)}</li>")
            i += 1
            continue
        close_list()
        if kind == "h2":
            html_parts.append(f"<h2>{inline(text)}</h2>")
            words.append(text)
        elif kind == "table":
            rows = text
            head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            body_rows = []
            for row in rows[1:]:
                body_rows.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            html_parts.append(
                f'<div class="table-wrap"><table class="compare"><thead><tr>{head}</tr></thead><tbody>{"".join(body_rows)}</tbody></table></div>'
            )
        else:
            html_parts.append(f"<p>{inline(text)}</p>")
        i += 1
    close_list()
    body = "\n".join(html_parts)
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
article .body ul,article .body ol{margin:0 0 14px;padding-left:1.2em;max-width:72ch}
article .body li{margin:4px 0}
.table-wrap{overflow-x:auto;max-width:72ch;margin:0 0 16px}
table.compare{width:100%;border-collapse:collapse;font-size:15px}
table.compare th,table.compare td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line);white-space:normal}
table.compare th{font-weight:700}
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
form.lead{display:grid;gap:12px;max-width:720px}
.choices{border:1px solid var(--line);border-radius:10px;padding:10px 12px;display:flex;flex-wrap:wrap;gap:8px 16px}
.choices legend{font-weight:700;padding:0 6px}
.cta{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--copper);border-radius:16px;padding:18px 18px 16px;margin:22px 0;max-width:720px}
.cta h2{font-family:Georgia,Palatino,serif;font-size:26px;line-height:1.2;margin:0 0 8px}
.cta p{margin:0 0 14px}
.cta-btns{display:flex;flex-wrap:wrap;gap:10px}
a.go{display:inline-flex;align-items:center;justify-content:center;text-align:center;text-decoration:none;line-height:1.3}
.cta-btns a{flex:1 1 240px}
.consult-cta{border-top-color:var(--pine2)}
.consult-cta h2{font-size:22px}
.fld select{font:inherit;padding:10px 12px;border:1px solid #d5cbbd;border-radius:10px;background:#fff;width:100%}
a.go.alt{background:#fff;color:var(--pine);border:2px solid var(--pine)}
a.go.alt:hover{background:var(--pine);color:#fff}
p.consult{margin:14px 0 0;font-weight:700}
@media(max-width:600px){.cta-btns{flex-direction:column}.cta-btns a{flex-basis:auto}}
@media print {
  header.top, footer, .cookie-banner, .skip, .no-print, .adslot { display:none !important }
  body { background:#fff; color:#000 }
  a { color:inherit; text-decoration:none }
  .print-doc { padding-top:0 }
  .print-doc h1 { font-size:22pt }
}
a.tg-nav{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:999px;background:#229ED9;color:#fff;flex:none}
a.tg-nav:hover{background:#1b86b8;color:#fff}
.tg-mark{width:18px;height:18px;display:block;flex:none}
footer a.tg-foot{display:inline-flex;align-items:center;gap:6px}
footer a.tg-foot .tg-mark{width:16px;height:16px}
a.ig-nav{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:999px;background:#c13584;color:#fff;flex:none}
a.ig-nav:hover{background:#a02b6e;color:#fff}
.ig-mark{width:18px;height:18px;display:block;flex:none}
footer a.ig-foot{display:inline-flex;align-items:center;gap:6px}
footer a.ig-foot .ig-mark{width:16px;height:16px}
.cookie-banner{position:fixed;z-index:20;left:16px;right:16px;bottom:16px;margin:0 auto;max-width:1080px;background:var(--card);color:var(--ink);border:1px solid var(--line);border-top:4px solid var(--copper);border-radius:16px;box-shadow:0 12px 32px rgba(30,61,52,.18);padding:14px 16px;display:flex;flex-wrap:wrap;gap:12px 16px;align-items:center}
.cookie-banner[hidden]{display:none}
.cookie-banner p{margin:0;flex:1 1 280px;font-size:15px}
.cookie-actions{display:flex;gap:8px;flex-wrap:wrap}
.cookie-banner button{font:inherit;font-weight:700;border-radius:999px;padding:8px 16px;cursor:pointer}
.cookie-banner button.accept{background:var(--pine);color:#fff;border:0}
.cookie-banner button.reject{background:#fff;color:var(--pine);border:2px solid var(--pine)}
.cookie-banner button.accept:hover{background:var(--copper)}
.cookie-banner button.reject:hover{background:var(--pine);color:#fff}
.guide-fig{margin:0 0 18px}
.guide-fig img{width:100%;border-radius:16px;display:block}
.guide-fig figcaption{color:var(--muted);font-size:13px;margin-top:6px}
.prop-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.prop-card{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}
.prop-card img{width:100%;height:180px;object-fit:cover;display:block;background:var(--sand)}
.prop-card .pad{padding:14px 14px 16px;display:flex;flex-direction:column;gap:6px;flex:1}
.prop-card h2{font-family:Georgia,Palatino,serif;font-size:22px;line-height:1.2;margin:0}
.prop-card p{margin:0;color:#314038;font-size:15px}
.prop-meta{color:var(--muted);font-size:14px}
.badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:12px;font-weight:700;background:var(--sand);color:var(--pine)}
.badge.sold{background:#f3e4e4;color:#6d2e2e}
.empty{background:var(--card);border:1px dashed #c9bfb0;border-radius:16px;padding:16px;color:var(--muted)}
.listing-facts{display:flex;flex-wrap:wrap;gap:8px 16px;margin:8px 0 16px;color:#314038}
.gallery{display:grid;gap:10px;margin:0 0 16px}
.gallery img{width:100%;border-radius:16px}
a.request{display:flex;align-items:center;justify-content:center;box-sizing:border-box;width:100%;max-width:720px;text-align:center;text-decoration:none;background:var(--pine);color:#fff;border-radius:999px;padding:12px 18px;font-weight:700;line-height:1.3}
a.request:hover,a.request:focus-visible{background:var(--copper);color:#fff}
.listing-request{margin:0 0 16px}
.listing-lead{scroll-margin-top:16px}
.prop-card .more{margin-top:auto}
.prop-card a.request{max-width:none;margin-top:4px}
.fld textarea{font:inherit;padding:10px 12px;border:1px solid #d5cbbd;border-radius:10px;background:#fff;width:100%;min-height:140px}
form.listing-form button.send{width:100%}
@media(min-width:601px){form.listing-form button.send{width:auto}}
.tg-cta{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--pine2);border-radius:16px;padding:18px 18px 16px;margin:22px 0;max-width:720px}
.tg-cta h2{font-family:Georgia,Palatino,serif;font-size:26px;line-height:1.2;margin:0 0 12px}
.tg-cta h2 a{display:inline-flex;align-items:center;gap:10px;color:var(--ink);text-decoration:none}
.tg-cta h2 a:hover{color:var(--copper)}
.tg-cta h2 .tg-mark{width:28px;height:28px;color:#229ED9}
.tg-cta .cta-btns a{gap:8px}
.tg-cta a.go{background:var(--pine);color:#fff;border:0;border-radius:999px;padding:12px 18px;font-weight:700}
.tg-cta a.go:hover{background:var(--copper);color:#fff}
.tg-cta a.go.alt{background:#fff;color:var(--pine);border:2px solid var(--pine);font-weight:650}
.tg-cta a.go.alt:hover{background:var(--pine);color:#fff}
.hp{position:absolute;left:-9999px}
footer{margin-top:48px;background:var(--pine);color:#e7e1d6;padding:28px 0;font-size:14.5px}
footer a{color:#fff}
footer .cols{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
footer p{max-width:78ch}
footer p.projects{margin:14px 0 0}
.cy-news{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 16px 12px;margin:22px 0;max-width:720px}
.cy-news h2{font-family:Georgia,Palatino,serif;font-size:22px;line-height:1.25;margin:0 0 8px}
.cy-news p{margin:0}
.cy-news ul{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.cy-news li{margin:0}
.cy-news a{font-weight:650}
.partners{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 16px 12px;margin:22px 0;max-width:720px}
.partners h2{font-family:Georgia,Palatino,serif;font-size:22px;line-height:1.25;margin:0 0 10px}
.partners ul{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.partners li{margin:0}
.partners a{font-weight:650;overflow-wrap:anywhere}
.partners p{margin:2px 0 0;color:#314038;font-size:15.5px}
.partners .partner-note{margin:12px 0 0;color:var(--muted);font-size:13px;line-height:1.45}
.aff-offer{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--copper);border-radius:12px;padding:12px 14px;margin:14px 0;max-width:720px}
.aff-offer h2{font-family:Georgia,Palatino,serif;font-size:20px;line-height:1.25;margin:0 0 6px}
.aff-offer p{margin:0 0 10px;font-size:15.5px;max-width:68ch}
.aff-btn{display:inline-flex;align-items:center;justify-content:center;text-align:center;background:var(--pine);color:#fff;text-decoration:none;border-radius:999px;padding:10px 16px;font-weight:700;line-height:1.3}
.aff-btn:hover,.aff-btn:focus-visible{background:var(--copper);color:#fff}
.aff-offer .aff-more{margin:10px 0 0;font-size:15px}
.aff-amazon{display:flex;flex-direction:column;align-items:flex-start;gap:10px}
.aff-amazon .aff-btn{margin:0}
.aff-disclosure{color:var(--muted);font-size:13px;line-height:1.45;margin:12px 0 16px;max-width:72ch}
.aff-offer .aff-disclosure{margin:10px 0 0}
@media(max-width:600px){.aff-btn{display:flex;width:100%;box-sizing:border-box}.aff-offer{padding:12px}}
@media(max-width:800px){.grid,.prop-grid{grid-template-columns:1fr}.bar{align-items:flex-start;flex-direction:column}.partners{padding:14px 14px 12px}}
main.bio{width:min(440px,calc(100% - 32px));margin:0 auto;padding:36px 0 12px}
.bio-brand{text-align:center;margin:0 0 22px}
.bio-brand .logo{display:inline-block;color:var(--pine);font-size:clamp(36px,9vw,48px);text-decoration:none}
.bio-brand .logo:hover{color:var(--copper)}
.bio-tag{margin:10px 0 0;color:#2d3832;font-size:17px;line-height:1.35;text-wrap:balance}
.bio-links{display:grid;gap:12px}
.bio-links a{display:flex;align-items:center;justify-content:center;box-sizing:border-box;width:100%;min-height:56px;padding:14px 16px;border:2px solid #e7c7a4;border-radius:14px;background:var(--pine);color:#f7f3ec;font-size:17px;font-weight:700;line-height:1.25;text-align:center;text-decoration:none}
.bio-links a:hover,.bio-links a:focus-visible{background:var(--pine2);color:#fff}
.bio-links a.bio-contact{background:#e7c7a4;color:var(--pine)}
.bio-links a.bio-contact:hover,.bio-links a.bio-contact:focus-visible{background:#f4efe6;color:var(--pine)}
'''

def bing_meta():
    """Bing Webmaster meta. Omitted while source/site.json leaves bing_msvalidate empty."""
    if not BING_MSVALIDATE:
        return ""
    return f'<meta name="msvalidate.01" content="{e(BING_MSVALIDATE)}" />'

def consent_bootstrap():
    """Consent Mode v2 default, then a stored Accept. Must run before AdSense and gtag.js."""
    return (
        "<script>"
        "window.dataLayer=window.dataLayer||[];"
        "function gtag(){dataLayer.push(arguments);}"
        "gtag('consent','default',{"
        "ad_storage:'denied',"
        "analytics_storage:'denied',"
        "ad_user_data:'denied',"
        "ad_personalization:'denied',"
        "wait_for_update:500"
        "});"
        "(function(){try{if(localStorage.getItem('mycytax-consent')==='granted'){"
        "gtag('consent','update',{"
        "ad_storage:'granted',"
        "analytics_storage:'granted',"
        "ad_user_data:'granted',"
        "ad_personalization:'granted'"
        "});}}catch(e){}})();"
        "</script>"
    )

def ga4_snippet():
    """Load gtag only when a GA4 measurement id is configured. Consent default is already set."""
    if not GA4_ID:
        return ""
    return (
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={e(GA4_ID)}"></script>'
        f'<script>gtag("js",new Date());gtag("config","{e(GA4_ID)}");</script>'
    )

def head(lang, title, desc, path, alt_path, jsonld=None, extra="", robots="index,follow,max-image-preview:large"):
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
    image = absu("/assets/og.png")
    social = (
        f'<meta property="og:site_name" content="{e(u["name"])}">'
        f'<meta property="og:title" content="{e(title)}">'
        f'<meta property="og:description" content="{e(desc)}">'
        f'<meta property="og:url" content="{absu(path)}">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:image" content="{image}">'
        f'<meta property="og:image:width" content="1200">'
        f'<meta property="og:image:height" content="630">'
        f'<meta property="og:image:alt" content="{e(u["tagline"])}">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{e(title)}">'
        f'<meta name="twitter:description" content="{e(desc)}">'
        f'<meta name="twitter:image" content="{image}">'
    )
    feed = (
        f'<link rel="alternate" type="application/atom+xml" title="{e(u["feed"])}" '
        f'href="{absu(loc(lang, "/feed.xml"))}">'
    )
    verify = bing_meta()
    verify_line = f"\n{verify}" if verify else ""
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="yandex-verification" content="8dc437c1055c8e9b" />
<meta name="impact-site-verification" value="04c75eec-b177-4aab-a06b-a7dc4db45d6b">
<meta name="impact-site-verification" value="91556748-8f38-47b9-874f-f6a1bf0cbe4e">{verify_line}
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{absu(path)}">
{chr(10).join(alts)}
<meta name="robots" content="{robots}">
{social}
{feed}
<meta name="theme-color" content="#1e3d34">
<link rel="icon" href="{href("/favicon.ico")}" sizes="16x16 32x32 48x48">
<link rel="icon" href="{href("/favicon-48x48.png")}" type="image/png" sizes="48x48">
<link rel="icon" href="{href("/icon-192.png")}" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{href("/apple-touch-icon.png")}" sizes="180x180">
<link rel="stylesheet" href="{href("/assets/style.css")}">{ld}{extra}{consent_bootstrap()}{ga4_snippet()}{ADSENSE}</head>'''

def header(lang, path_for):
    u = UI[lang]
    def item(key, path):
        here = path_for(lang)
        current = here == path or (path.rstrip("/") != "" and here.startswith(path))
        cur = ' aria-current="page"' if current else ""
        return f'<a href="{href(path)}"{cur}>{u[key]}</a>'
    langs = " ".join(
        f'<a href="{href(path_for(l))}" hreflang="{l}" lang="{l}"{" aria-current=\"true\"" if l==lang else ""}>{l.upper()}</a>'
        for l in LANGS)
    return f'''<a class="skip" href="#main">{u["home"]}</a><header class="top"><div class="wrap bar">
<a class="logo" href="{href(loc(lang, "/"))}">{e(u["name"])}<small>{e(u["tagline"])}</small></a>
<nav class="main" aria-label="{e(u["lang"])}">{item("calcs", loc(lang, "/calculators/"))}{item("guides", loc(lang, "/guides/"))}{item("services", loc(lang, "/services/"))}{item("real_estate", loc(lang, "/real-estate/"))}{item("about", loc(lang, "/about/"))}{item("contact", loc(lang, "/contact/"))}
{tg_icon_link(lang)}{ig_icon_link(lang)}<span class="langs">{langs}</span></nav></div></header>'''

def footer(lang):
    u = UI[lang]
    links = [
        (loc(lang, "/about/"), u["about"]), (loc(lang, "/contact/"), u["contact"]),
        (loc(lang, "/privacy/"), u["privacy"]), (loc(lang, "/cookies/"), u["cookies"]),
        (loc(lang, "/terms/"), u["terms"]),
        (loc(lang, "/property-consultation/"), u["consult"]),
        (loc(lang, "/affiliate-disclosure/"), u["affiliates"]),
    ]
    nav = "".join(f'<a href="{href(path)}">{e(name)}</a>' for path, name in links)
    settings = (
        f'<a class="cookie-settings" href="{href(loc(lang, "/cookies/"))}" data-cookie-settings>'
        f'{e(u["cookie_settings"])}</a>'
    )
    return f'''<footer><div class="wrap"><nav class="cols">{nav}{tg_footer_link(lang)}{ig_footer_link(lang)}{settings}</nav>
{projects_line(lang)}
<p>{e(DISCLAIMER[lang])}</p><p>© 2026 {SITE}. {e(PUBLISHER)}, Cyprus. <a href="mailto:{EMAIL}">{EMAIL}</a></p></div></footer>
{cookie_banner(lang)}</body></html>'''

def cookie_banner(lang):
    """Accept / Reject banner. The choice is localStorage, and it updates Consent Mode."""
    u = UI[lang]
    return (
        f'<div id="cookie-banner" class="cookie-banner" hidden><p>{e(u["cookie_banner"])} '
        f'<a href="{href(loc(lang, "/cookies/"))}">{e(u["cookies"])}</a> · '
        f'<a href="{href(loc(lang, "/privacy/"))}">{e(u["privacy"])}</a></p>'
        f'<div class="cookie-actions">'
        f'<button type="button" class="accept" data-cookie="granted">{e(u["cookie_accept"])}</button>'
        f'<button type="button" class="reject" data-cookie="denied">{e(u["cookie_reject"])}</button>'
        f'</div></div>'
        '<script>(function(){'
        'var KEY="mycytax-consent";'
        'var banner=document.getElementById("cookie-banner");'
        'function show(){if(banner)banner.hidden=false;}'
        'function hide(){if(banner)banner.hidden=true;}'
        'function apply(value){'
        'var state=value==="granted"?"granted":"denied";'
        'try{localStorage.setItem(KEY,state);}catch(e){}'
        'if(typeof gtag==="function"){gtag("consent","update",{'
        'ad_storage:state,analytics_storage:state,ad_user_data:state,ad_personalization:state'
        '});}'
        'hide();}'
        'document.querySelectorAll("[data-cookie]").forEach(function(btn){'
        'btn.addEventListener("click",function(){apply(btn.getAttribute("data-cookie"));});'
        '});'
        'document.querySelectorAll("[data-cookie-settings]").forEach(function(el){'
        'el.addEventListener("click",function(ev){ev.preventDefault();show();});'
        '});'
        'var saved=null;try{saved=localStorage.getItem(KEY);}catch(e){}'
        'if(saved!=="granted"&&saved!=="denied")show();'
        '})();</script>'
    )

def cynews_home(lang):
    """Language home on CyNews24. English is /en/, not the site root."""
    code = lang if lang in LANGS else "en"
    return f"{CYNEWS}{code}/"

def projects_line(lang):
    """Footer cross-link. Dofollow, same tab."""
    u = UI[lang]
    return (f'<p class="projects">{e(u["projects"])}: '
            f'<a href="{e(cynews_home(lang))}">{e(u["project_cynews"])}</a></p>')

def _cynews_stamp(value):
    text = (value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.datetime.fromisoformat(text)
    except ValueError:
        return 0.0
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=datetime.timezone.utc)
    return moment.timestamp()

def _cynews_article_lang(url):
    parsed = urlparse(url or "")
    if parsed.scheme != "https" or parsed.netloc != "cynews24.net":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0] not in LANGS:
        return None
    return parts[0]

def parse_news_sitemap(raw):
    """Return article dicts from a Google news sitemap. Empty when nothing matches."""
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    text = raw.strip()
    if not text:
        return []
    root = ET.fromstring(text)
    found = []
    for order, node in enumerate(root.findall("sm:url", _CYNEWS_NS)):
        loc = (node.findtext("sm:loc", default="", namespaces=_CYNEWS_NS) or "").strip()
        path_lang = _cynews_article_lang(loc)
        if path_lang is None:
            continue
        title = (node.findtext("news:news/news:title", default="", namespaces=_CYNEWS_NS) or "").strip()
        title = " ".join(title.split())
        if not title:
            continue
        declared = (node.findtext(
            "news:news/news:publication/news:language", default="", namespaces=_CYNEWS_NS,
        ) or "").strip().lower()
        if declared and declared != path_lang:
            continue
        when = node.findtext("news:news/news:publication_date", default="", namespaces=_CYNEWS_NS)
        found.append({
            "lang": path_lang,
            "title": title,
            "url": loc,
            "stamp": _cynews_stamp(when),
            "order": order,
        })
    return found

def _http_get(url, timeout):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "mycytax-build", "Accept": "application/xml,text/xml,*/*"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(2_000_000)

def load_latest_news(fetch=None, timeout=CYNEWS_TIMEOUT):
    """Five newest headlines per language, or None when the fetch cannot be used.

    `fetch` is `fn(url, timeout) -> bytes`. Any error, timeout or empty sitemap
    returns None so the caller can render a static link and the build continues.
    """
    getter = fetch or _http_get
    try:
        raw = getter(CYNEWS_SITEMAP, timeout)
        items = parse_news_sitemap(raw)
    except Exception as exc:
        print(f"cynews: fetch failed ({type(exc).__name__}); linking to CyNews24 without headlines")
        return None
    if not items:
        print("cynews: sitemap had no headlines; linking to CyNews24 without headlines")
        return None
    grouped = {}
    for lang in LANGS:
        rows = [item for item in items if item["lang"] == lang]
        rows.sort(key=lambda item: (-item["stamp"], item["order"]))
        grouped[lang] = rows[:5]
    return grouped

def refresh_cynews(fetch=None):
    """Fill CYNEWS_HEADLINES once per build. A failed fetch leaves every language empty."""
    loaded = load_latest_news(fetch=fetch)
    for lang in LANGS:
        rows = (loaded or {}).get(lang) or []
        CYNEWS_HEADLINES[lang] = rows or None
    if loaded:
        print("cynews", {lang: len(CYNEWS_HEADLINES[lang] or []) for lang in LANGS})
    return loaded

def news_block(lang, headlines=_MISSING):
    """Small headline list. With no headlines, one dofollow link to the language home."""
    rows = CYNEWS_HEADLINES.get(lang) if headlines is _MISSING else headlines
    u = UI[lang]
    heading = e(u["news_h"])
    if not rows:
        return (f'<aside class="cy-news"><h2>{heading}</h2>'
                f'<p><a href="{e(cynews_home(lang))}">{e(u["project_cynews"])}</a></p></aside>')
    items = "".join(
        f'<li><a href="{e(row["url"])}">{e(row["title"])}</a></li>' for row in rows[:5]
    )
    return f'<aside class="cy-news"><h2>{heading}</h2><ul>{items}</ul></aside>'

def ad(label):
    return f'<div class="adslot" data-ad="{e(label)}" aria-label="{e(UI["en"]["ad"])}"><!-- AdSense slot "{e(label)}": leave empty until a unit is approved. --></div>'

def org():
    return {"@type":"Organization","name":SITE,"url":absu("/"),"logo":absu("/icon-512.png"),"email":EMAIL,
            "address":{"@type":"PostalAddress","addressCountry":"CY"},
            "founder":{"@type":"Person","name":PUBLISHER},
            "sameAs":[CYNEWS, TG_RU, TG_EN, IG]}

# Official Telegram mark (paper plane), drawn with currentColor so it follows the link.
TG_ICON = (
    '<svg class="tg-mark" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>'
    "</svg>"
)

def tg_primary(lang):
    """Russian pages use @mycytax. English and Greek pages use @mycytaxen."""
    return TG_RU if lang == "ru" else TG_EN

def tg_secondary(lang):
    return TG_EN if lang == "ru" else TG_RU

def tg_handle(url):
    return "@mycytaxen" if url == TG_EN else "@mycytax"

def tg_icon_link(lang):
    u = UI[lang]
    return (f'<a class="tg-nav" href="{e(tg_primary(lang))}" rel="noopener" target="_blank" '
            f'aria-label="{e(u["tg"])}">{TG_ICON}</a>')

def tg_footer_link(lang):
    u = UI[lang]
    return (f'<a class="tg-foot" href="{e(tg_primary(lang))}" rel="noopener" target="_blank" '
            f'aria-label="{e(u["tg"])}">{TG_ICON}<span>{e(u["tg_short"])}</span></a>')

IG_ICON = (
    '<svg class="ig-mark" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M12 2.2c3.2 0 3.6 0 4.9.1 3.2.1 4.8 1.7 4.9 4.9.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-3.2-.1-4.8-1.7-4.9-4.9C2.1 15.6 2 15.2 2 12s.1-3.6.2-4.8c.1-3.2 1.7-4.8 4.9-4.9C8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7 .1 2.7.3.3 2.7.1 7 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.3.1 1.7.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9C23.7 2.7 21.3.3 17 .1 15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 1 0 .1 12.4A6.2 6.2 0 0 0 12 5.8zm0 10.2a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.8a1.4 1.4 0 1 0 0 2.8 1.4 1.4 0 0 0 0-2.8z"/>'
    "</svg>"
)

def ig_icon_link(lang):
    u = UI[lang]
    return (f'<a class="ig-nav" href="{e(IG)}" rel="noopener" target="_blank" '
            f'aria-label="{e(u["ig"])}">{IG_ICON}</a>')

def ig_footer_link(lang):
    u = UI[lang]
    return (f'<a class="ig-foot" href="{e(IG)}" rel="noopener" target="_blank" '
            f'aria-label="{e(u["ig"])}">{IG_ICON}<span>{e(u["ig_short"])}</span></a>')

def telegram_card(lang):
    """Subscribe block. The page-language channel is the heading and the first button."""
    u = UI[lang]
    primary, other = tg_primary(lang), tg_secondary(lang)
    other_label = f'{u["tg_other"]} · {tg_handle(other)}'
    return (
        f'<aside class="tg-cta"><h2><a href="{e(primary)}" rel="noopener" target="_blank">'
        f'{TG_ICON}<span>{e(u["tg"])}</span></a></h2><div class="cta-btns">'
        f'<a class="go" href="{e(primary)}" rel="noopener" target="_blank">{TG_ICON}<span>{e(tg_handle(primary))}</span></a>'
        f'<a class="go alt" href="{e(other)}" rel="noopener" target="_blank">{TG_ICON}<span>{e(other_label)}</span></a>'
        f"</div></aside>"
    )

def service_nodes():
    """Accounting practice markup for the home and services pages. No street address."""
    same = [CYNEWS, TG_RU, TG_EN, IG]
    area = {"@type": "Country", "name": "Cyprus"}
    org_id = absu("/") + "#organization"
    organization = {
        "@type": "Organization",
        "@id": org_id,
        "name": SITE,
        "url": absu("/"),
        "logo": absu("/icon-512.png"),
        "email": LEADS_EMAIL,
        "areaServed": area,
        "sameAs": same,
    }
    service = {
        "@type": ["ProfessionalService", "AccountingService"],
        "@id": absu("/") + "#service",
        "name": SITE,
        "url": absu("/"),
        "email": LEADS_EMAIL,
        "areaServed": area,
        "sameAs": same,
        "provider": {"@id": org_id},
    }
    return [
        {"@context": "https://schema.org", **organization},
        {"@context": "https://schema.org", **service},
    ]

def _crumb_title(title):
    if title and " | " in title:
        return title.split(" | ", 1)[0]
    return title or ""

def _crumb_name(lang, parts, current_title):
    u = UI[lang]
    known = {
        "about": u["about"], "contact": u["contact"], "privacy": u["privacy"],
        "cookies": u["cookies"], "terms": u["terms"],
        "affiliate-disclosure": u["affiliates"], "property-consultation": u["consult"],
        "services": u["services"], "calculators": u["calcs"], "guides": u["guides"],
        "real-estate": u["real_estate"], "buying-checklist": CHECKLIST[lang]["gate_h"],
    }
    if len(parts) == 1 and parts[0] in known:
        return known[parts[0]]
    if parts[0] == "calculators" and len(parts) == 2 and parts[1] in CALCS:
        return CALCS[parts[1]][lang][0]
    if parts[0] == "guides" and len(parts) >= 2:
        slug = "/".join(parts[1:])
        if slug in GUIDES:
            return load_md(lang, slug)[0]["title"]
    if parts[0] == "real-estate" and len(parts) == 2:
        for item in published_listings():
            if item["id"] == parts[1]:
                return item["title"][lang]
    if parts == ["buying-checklist", "2026"]:
        return CHECKLIST[lang]["h"]
    if parts == ["contact", "thanks"]:
        return u["thanks_t"]
    if parts == ["property-consultation", "thanks"]:
        return CONSULT[lang]["thanks_t"]
    return _crumb_title(current_title) or parts[-1]

def breadcrumbs(lang, path, current_title):
    """One BreadcrumbList for the page. New pages get this from page_shell."""
    bare = bare_path(path).split("?")[0]
    parts = [part for part in bare.strip("/").split("/") if part]
    items = [{
        "@type": "ListItem",
        "position": 1,
        "name": UI[lang]["home"],
        "item": absu(loc(lang, "/")),
    }]
    acc = ""
    for index, _part in enumerate(parts):
        acc += "/" + parts[index]
        items.append({
            "@type": "ListItem",
            "position": index + 2,
            "name": _crumb_name(lang, parts[:index + 1], current_title if index == len(parts) - 1 else ""),
            "item": absu(loc(lang, acc + "/")),
        })
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}

def with_breadcrumbs(lang, path, title, jsonld):
    blocks = list(jsonld or [])
    blocks.append(breadcrumbs(lang, path, title))
    return blocks

def page_shell(lang, title, desc, path, alt, body, jsonld=None, active_path=None, robots="index,follow,max-image-preview:large"):
    def path_for(l, alt=alt):
        return alt(l)
    runtime = affiliate_runtime() if ('data-affiliate="' in (body or "") or 'data-amazon-search="' in (body or "")) else ""
    return head(lang, title, desc, path, alt, with_breadcrumbs(lang, path, title, jsonld), robots=robots) + header(lang, path_for) + body + runtime + footer(lang)

LEAD = {
 "en": dict(h="Local help with your Cyprus property",
            p="Licensed local real estate help in Limassol and across Cyprus. We reply within 24 hours.",
            buy="Get a free property purchase consultation",
            sell="Sell or rent out your property in Cyprus",
            type="Request type", buyv="Buy consultation", sellv="Sell", rentv="Rent out",
            buyl="Buy consultation", selll="Sell", rentl="Rent out",
            prop="Property type", area="Area or city", budget="Budget or expected price (EUR)",
            phone="Phone or WhatsApp", msg="Message",
            props=[("Apartment","Apartment"),("House","House"),("Land","Land"),("Commercial","Commercial"),("Not sure","Not sure")],
            consent="I agree that MyCyTax may use these details only to reply to this request.",
            send="Send request", honey="Leave blank", name="Name", email="Email"),
 "ru": dict(h="Местная помощь с недвижимостью на Кипре",
            p="Лицензированная помощь с недвижимостью в Лимассоле и по всему Кипру. Ответим в течение 24 часов.",
            buy="Получить бесплатную консультацию по покупке",
            sell="Продать или сдать недвижимость на Кипре",
            type="Тип запроса", buyv="Buy consultation", sellv="Sell", rentv="Rent out",
            buyl="Консультация по покупке", selll="Продажа", rentl="Сдача в аренду",
            prop="Тип объекта", area="Район или город", budget="Бюджет или ожидаемая цена (EUR)",
            phone="Телефон или WhatsApp", msg="Сообщение",
            props=[("Apartment","Квартира"),("House","Дом"),("Land","Участок"),("Commercial","Коммерция"),("Not sure","Пока не знаю")],
            consent="Я согласен, что MyCyTax использует эти сведения только чтобы ответить на этот запрос.",
            send="Отправить запрос", honey="Оставьте пустым", name="Имя", email="Эл. почта"),
 "el": dict(h="Τοπική βοήθεια για το ακίνητό σας στην Κύπρο",
            p="Αδειοδοτημένη τοπική βοήθεια για ακίνητα στη Λεμεσό και σε όλη την Κύπρο. Απαντάμε μέσα σε 24 ώρες.",
            buy="Δωρεάν συμβουλή για αγορά ακινήτου",
            sell="Πουλήστε ή ενοικιάστε το ακίνητό σας στην Κύπρο",
            type="Τύπος αιτήματος", buyv="Buy consultation", sellv="Sell", rentv="Rent out",
            buyl="Συμβουλή αγοράς", selll="Πώληση", rentl="Ενοικίαση",
            prop="Τύπος ακινήτου", area="Περιοχή ή πόλη", budget="Προϋπολογισμός ή αναμενόμενη τιμή (EUR)",
            phone="Τηλέφωνο ή WhatsApp", msg="Μήνυμα",
            props=[("Apartment","Διαμέρισμα"),("House","Οικία"),("Land","Οικόπεδο"),("Commercial","Επαγγελματικό"),("Not sure","Δεν είμαι σίγουρος")],
            consent="Συμφωνώ ότι το MyCyTax θα χρησιμοποιήσει αυτά τα στοιχεία μόνο για να απαντήσει σε αυτό το αίτημα.",
            send="Αποστολή αιτήματος", honey="Αφήστε κενό", name="Όνομα", email="Email"),
}
CONSULT = {
 "en": dict(
    h="Selling or buying property in Cyprus? Get help with taxes and paperwork",
    p="Tell us what you are doing and where the property is. This is not a tax assessment.",
    go="Get help",
    d="A short form about a sale, a purchase, capital gains, rental income, or a developer’s trading-criteria form.",
    interest="What you need",
    area="Area or city",
    msg="Message",
    consent="I agree that these details are used only to reply to this request.",
    send="Send",
    thanks_t="Thank you",
    thanks_d="Your consultation request has been sent.",
    thanks_i="Thank you. If this address is already confirmed with FormSubmit, we will reply about the taxes and paperwork.",
    options=[
        ("30-minute property tax consultation", "30-minute property tax consultation"),
        ("Capital gains tax return", "Capital gains tax return"),
        ("Rental income tax filing", "Rental income tax filing"),
        ("Buying property checklist", "Buying property checklist"),
        ("Selling property", "Selling property"),
        ("Buying", "Buying"),
        ("Capital gains tax", "Capital gains tax"),
        ("Trading-criteria form for developers", "Trading-criteria form for developers"),
        ("Rental income tax", "Rental income tax"),
        ("Other", "Other"),
    ],
 ),
 "ru": dict(
    h="Продаёте или покупаете недвижимость на Кипре? Поможем с налогами и документами",
    p="Напишите, что вы делаете и где объект. Это не расчёт налога.",
    go="Получить помощь",
    d="Короткая форма о продаже, покупке, приросте капитала, аренде или форме критериев трейдинга для застройщика.",
    interest="Что нужно",
    area="Район или город",
    msg="Сообщение",
    consent="Я согласен, что эти сведения используются только чтобы ответить на этот запрос.",
    send="Отправить",
    thanks_t="Спасибо",
    thanks_d="Запрос на консультацию отправлен.",
    thanks_i="Спасибо. Если адрес уже подтверждён в FormSubmit, ответим по налогам и документам.",
    options=[
        ("30-minute property tax consultation", "Консультация по налогам на недвижимость, 30 минут"),
        ("Capital gains tax return", "Декларация по налогу на прирост капитала"),
        ("Rental income tax filing", "Подача налога на доход от аренды"),
        ("Buying property checklist", "Перечень налогов и сборов при покупке"),
        ("Selling property", "Продажа недвижимости"),
        ("Buying", "Покупка"),
        ("Capital gains tax", "Налог на прирост капитала"),
        ("Trading-criteria form for developers", "Форма критериев трейдинга для застройщиков"),
        ("Rental income tax", "Налог на доход от аренды"),
        ("Other", "Другое"),
    ],
 ),
 "el": dict(
    h="Πουλάτε ή αγοράζετε ακίνητο στην Κύπρο; Βοήθεια με φόρους και έγγραφα",
    p="Γράψτε τι κάνετε και πού είναι το ακίνητο. Δεν είναι φορολογικός υπολογισμός.",
    go="Ζητήστε βοήθεια",
    d="Σύντομη φόρμα για πώληση, αγορά, κεφαλαιουχικά κέρδη, ενοίκιο ή το έντυπο κριτηρίων εμπορίας για αναπτύκτη.",
    interest="Τι χρειάζεστε",
    area="Περιοχή ή πόλη",
    msg="Μήνυμα",
    consent="Συμφωνώ ότι αυτά τα στοιχεία χρησιμοποιούνται μόνο για απάντηση σε αυτό το αίτημα.",
    send="Αποστολή",
    thanks_t="Ευχαριστούμε",
    thanks_d="Το αίτημα συμβουλής στάλθηκε.",
    thanks_i="Ευχαριστούμε. Αν η διεύθυνση έχει ήδη επιβεβαιωθεί στο FormSubmit, θα απαντήσουμε για τους φόρους και τα έγγραφα.",
    options=[
        ("30-minute property tax consultation", "Συμβουλή για φόρους ακινήτου, 30 λεπτά"),
        ("Capital gains tax return", "Δήλωση φόρου κεφαλαιουχικών κερδών"),
        ("Rental income tax filing", "Υποβολή φόρου εισοδήματος από ενοίκια"),
        ("Buying property checklist", "Λίστα φόρων και τελών αγοράς"),
        ("Selling property", "Πώληση ακινήτου"),
        ("Buying", "Αγορά"),
        ("Capital gains tax", "Φόρος κεφαλαιουχικών κερδών"),
        ("Trading-criteria form for developers", "Έντυπο κριτηρίων εμπορίας για αναπτύκτες"),
        ("Rental income tax", "Φόρος εισοδήματος από ενοίκια"),
        ("Other", "Άλλο"),
    ],
 ),
}
def consult_href(lang, interest=""):
    from urllib.parse import quote
    path = href(loc(lang, "/property-consultation/"))
    return path + "?interest=" + quote(interest) if interest else path
def consult_card(lang, interest=""):
    """Compact invitation. The form itself is on the consultation page."""
    a = CONSULT[lang]
    return (f'<aside class="cta consult-cta"><h2>{e(a["h"])}</h2><p>{e(a["p"])}</p>'
            f'<div class="cta-btns"><a class="go" href="{consult_href(lang, interest)}">{e(a["go"])}</a></div></aside>')
def consult_form(lang, next_path):
    a = CONSULT[lang]
    base = LEAD[lang]
    options = "".join(f'<option value="{e(value)}">{e(label)}</option>' for value, label in a["options"])
    privacy = href(loc(lang, "/privacy/"))
    return f'''<form class="lead" id="consultform" action="https://formsubmit.co/{LEADS_EMAIL}" method="POST">
<input type="hidden" name="_subject" value="mycytax lead">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="true">
<input type="hidden" name="_next" value="{e(absu(next_path))}">
<p class="hp"><label>{e(base["honey"])}<input name="_honey" tabindex="-1" autocomplete="off"></label></p>
<label class="fld"><span>{e(base["name"])}</span><input name="name" required autocomplete="name"></label>
<label class="fld"><span>{e(base["email"])}</span><input type="email" name="email" required autocomplete="email"></label>
<label class="fld"><span>{e(base["phone"])}</span><input name="phone" required autocomplete="tel"></label>
<label class="fld"><span>{e(a["interest"])}</span><select name="interest" required>{options}</select></label>
<label class="fld"><span>{e(a["area"])}</span><input name="area" required></label>
<label class="fld"><span>{e(a["msg"])}</span><textarea name="message" required></textarea></label>
<label class="chk"><input type="checkbox" name="consent" value="yes" required><span>{e(a["consent"])} <a href="{privacy}">{e(UI[lang]["privacy"])}</a>.</span></label>
<button class="send" type="submit">{e(a["send"])}</button></form>
<script>
(function(){{
  var q=new URLSearchParams(location.search).get("interest")||"";
  var sel=document.querySelector("#consultform select[name=interest]");
  if(!sel||!q) return;
  Array.prototype.forEach.call(sel.options, function(opt){{ if(opt.value===q) sel.value=q; }});
}})();
</script>'''
def consultation_page(lang):
    u = UI[lang]
    a = CONSULT[lang]
    path = loc(lang, "/property-consultation/")
    def alt(l):
        return loc(l, "/property-consultation/")
    body = (f'<main id="main" class="wrap page"><h1>{e(a["h"])}</h1><p class="lede">{e(a["d"])}</p>'
            f'<p class="banner">{e(DISCLAIMER[lang])}</p>'
            f'{consult_form(lang, loc(lang, "/property-consultation/thanks/"))}</main>')
    return page_shell(lang, f'{u["consult"]} | {SITE}', a["d"], path, alt, body)
def consultation_thanks(lang):
    a = CONSULT[lang]
    path = loc(lang, "/property-consultation/thanks/")
    def alt(l):
        return loc(l, "/property-consultation/thanks/")
    body = f'<main id="main" class="wrap page"><h1>{e(a["thanks_t"])}</h1><p>{e(a["thanks_i"])}</p></main>'
    return page_shell(lang, f'{a["thanks_t"]} | {SITE}', a["thanks_d"], path, alt, body, robots="noindex,follow")

# Paid work. No prices: each button opens the consultation form with that service selected.
SERVICE_LIST = (
    ("30-minute property tax consultation", {
        "en": ("30-minute Cyprus property tax consultation",
               "Half an hour on the taxes that apply to a purchase, a sale or a letting you already have in mind. You receive a quote before any time is booked."),
        "ru": ("Консультация по налогам на недвижимость Кипра, 30 минут",
               "Полчаса о налогах на покупку, продажу или аренду, которая у вас уже на примете. Стоимость называют до того, как время будет назначено."),
        "el": ("Συμβουλή 30 λεπτών για φόρους ακινήτου στην Κύπρο",
               "Μισή ώρα για τους φόρους μιας αγοράς, πώλησης ή ενοικίασης που ήδη έχετε στο μυαλό σας. Η τιμή δίνεται πριν κλειστεί χρόνος."),
    }),
    ("Capital gains tax return", {
        "en": ("Capital gains tax return on a property sale",
               "Help preparing the computation on a disposal of immovable property in Cyprus: indexation from the Tax Department table, disposal costs, and any lifetime exemption. The Department still makes the assessment."),
        "ru": ("Декларация по налогу на прирост капитала при продаже",
               "Помощь с расчётом при отчуждении недвижимости на Кипре: индексация по таблице Налогового департамента, расходы на продажу и возможный пожизненный вычет. Оценку всё равно делает департамент."),
        "el": ("Δήλωση φόρου κεφαλαιουχικών κερδών σε πώληση ακινήτου",
               "Βοήθεια στον υπολογισμό διάθεσης ακίνητης ιδιοκτησίας στην Κύπρο: τιμαριθμική αναπροσαρμογή από τον πίνακα του Τμήματος Φορολογίας, έξοδα διάθεσης και τυχόν ισόβια απαλλαγή. Τη βεβαίωση την κάνει το Τμήμα."),
    }),
    ("Trading-criteria form for developers", {
        "en": ("Trading-criteria form for a developer",
               "Preparation of the trading-criteria form where a developer’s sale may be trading income rather than a capital gain. You supply the facts. This is not the Tax Department’s decision."),
        "ru": ("Форма критериев трейдинга для застройщика",
               "Подготовка формы критериев трейдинга, когда продажа застройщика может быть торговым доходом, а не приростом капитала. Факты даёте вы. Это не решение Налогового департамента."),
        "el": ("Έντυπο κριτηρίων εμπορίας για αναπτύκτη",
               "Ετοιμασία του εντύπου κριτηρίων εμπορίας, όπου μια πώληση αναπτύκτη μπορεί να είναι εμπορικό εισόδημα και όχι κεφαλαιουχικό κέρδος. Τα γεγονότα τα δίνετε εσείς. Δεν είναι απόφαση του Τμήματος Φορολογίας."),
    }),
    ("Rental income tax filing", {
        "en": ("Rental income tax filing",
               "Help with the income-tax side of a year’s rent: the statutory 20% deduction, the 2026 bands, and GHS at 2.65% of gross rent. Special Defence Contribution on rent is nil for 2026 on the published rule. A quote comes before the work."),
        "ru": ("Подача налога на доход от аренды",
               "Помощь с подоходным налогом на аренду за год: уставные 20%, шкалы 2026 года и ГЕСИ 2,65% валовой аренды. Сбор на оборону с аренды в 2026 году по опубликованному правилу равен нулю. Стоимость называют до начала работы."),
        "el": ("Υποβολή φόρου εισοδήματος από ενοίκια",
               "Βοήθεια με τον φόρο εισοδήματος ενός έτους ενοικίου: η νόμιμη έκπτωση 20%, οι κλίμακες του 2026 και η ΓεΣΥ στο 2,65% του ακαθάριστου ενοικίου. Η έκτακτη εισφορά για την άμυνα στο ενοίκιο είναι μηδέν για το 2026 κατά τον δημοσιευμένο κανόνα. Η τιμή δίνεται πριν από τη δουλειά."),
    }),
)
QUOTE = {"en": "Request a quote", "ru": "Запросить стоимость", "el": "Ζητήστε προσφορά"}
CHECKLIST = {
 "en": dict(
    h="Buying property in Cyprus: taxes and fees checklist 2026",
    lede="The published taxes on a purchase, and the ones that appear later if you let or sell. Not a fee for this site, and not an assessment of your contract.",
    print="Print or save as PDF",
    fork_h="Transfer fees or VAT, not usually both",
    fork="Gov.cy states that transfer fees are not charged when the transfer is a transaction subject to VAT, if you produce the VAT Department certificate. Where VAT is not charged, the legislation provides a 50% exemption from transfer fees. The 50% is refused where the seller acquired the property in a forced sale under Parts VI and VIA of the Transfer and Mortgage Law 9/1965. The Department of Lands and Surveys scale, before that 50%, is 3% from €0.01 to €85,000, 5% from €85,001 to €170,000, and 8% above €170,000. The bands are slices. On an accepted value of €200,000 with one buyer and no VAT, the full scale is €9,200 and half is €4,600. A contract not deposited within six months can increase the transfer fee by 10% when title is transferred, according to the Department’s leaflet.",
    vat_h="VAT at 19%, or 5% on part of a primary home",
    vat="The standard rate is 19% of the price before VAT. The 5% rate is for a primary and permanent residence, on the first 130 square metres and up to €350,000, and only if the whole buildable area is not over 190 square metres and the whole value is not over €475,000. Between those inner and outer limits only the qualifying portion is at 5%. Over either outer limit the reduced rate is not available. A holiday home, or a flat you will let from the start, is budgeted at 19%. The window for the transitional reduced-rate application ran to 15 June 2026. This checklist does not treat that route as still open.",
    stamp_h="Stamp duty",
    stamp="Law 239(I)/2025 repealed the stamp duty laws from 1 January 2026. A contract drawn up and signed by at least one party on or after that date is not stamped: the duty is €0. A contract that a party signed on or before 31 December 2025 is still on the old scale, capped at €20,000 on one document. The Ministry of Interior checklist has not always been rewritten for the repeal. Say so when you file.",
    cgt_h="If you later sell: capital gains tax at 20%",
    cgt="Capital gains tax is 20% of the gain on disposal of immovable property in Cyprus. The Tax Department reduces the gain for inflation using the official retail price index. This checklist does not store that index: take the ratio from the Department’s table. For an individual, the consolidated Capital Gains Tax Law states a lifetime exemption of €30,000, €50,000 where a farmer sells agricultural land, and €150,000 on a qualifying main residence used by the owner for at least five years (ten years if it is not the first such disposal) on land of up to 1.5 decares. A person does not get both the general exemption and the residence exemption. Companies do not get these lifetime exemptions.",
    rent_h="If you let",
    rent="A 20% deduction from gross rent is the statutory income-tax deduction. From 1 January 2026 the bands for an individual are nil on the first €22,000, 20% to €32,000, 25% to €42,000, 30% to €72,000 and 35% above that. Special Defence Contribution on rent is nil for the 2026 tax year, including for domiciled residents. GHS on rental income is 2.65% of the gross rent. An annual ceiling can apply and is not reproduced here.",
    other_h="Costs that are not a tax rate",
    other="Legal fees, the Land Registry search, the fee to deposit the contract, utility deposits and municipal charges are not on a single published percentage. Ask for them in writing. Do not add a national annual property tax: that state tax is not charged for tax years from 2017.",
    gate_h="Get the checklist",
    gate_p="Send your name and email. The checklist then opens in this browser, and you can print it or save it as a PDF. The details are used only to send you the page.",
    send="Send and open the checklist",
 ),
 "ru": dict(
    h="Покупка недвижимости на Кипре: перечень налогов и сборов 2026",
    lede="Опубликованные налоги при покупке и те, что возникают позже, если сдавать или продавать. Это не гонорар сайта и не расчёт по вашему договору.",
    print="Печать или сохранить как PDF",
    fork_h="Сбор за переход или НДС, обычно не оба",
    fork="На Gov.cy указано, что сбор за переход не берут, если переход относится к сделке с НДС и вы приносите справку Департамента НДС. Если НДС нет, закон даёт освобождение на 50% сбора. Эти 50% не дают, если продавец приобрёл объект на принудительной продаже по частям VI и VIA закона 9/1965. Шкала Департамента земель до этих 50%: 3% с €0,01 до €85 000, 5% с €85 001 до €170 000 и 8% сверх €170 000. Диапазоны — это слои. При принятой стоимости €200 000, одном покупателе и без НДС полная шкала — €9 200, половина — €4 600. Договор, не сданный в течение шести месяцев, по буклету департамента может увеличить сбор на 10% при переоформлении.",
    vat_h="НДС 19% или 5% с части основного жилья",
    vat="Обычная ставка — 19% цены без НДС. Ставка 5% — для основного и постоянного жилья, на первые 130 квадратных метров и до €350 000, и только если вся площадь застройки не выше 190 квадратных метров, а вся стоимость не выше €475 000. Между пределами 5% только на подходящую долю. За любым внешним пределом сниженной ставки нет. Жильё для отпуска или квартира, которую сразу сдают, закладывается по 19%. Окно заявления на сниженную ставку по переходному пути закрылось 15 июня 2026 года. Этот перечень не считает тот путь открытым.",
    stamp_h="Гербовый сбор",
    stamp="Закон 239(I)/2025 отменил гербовый сбор с 1 января 2026 года. Договор, составленный и подписанный хотя бы одной стороной в эту дату или позже, не штампуют: сбор €0. Договор, который сторона подписала не позднее 31 декабря 2025 года, всё ещё на старой шкале, не больше €20 000 с одного документа. Перечень Министерства внутренних дел не всегда переписан под отмену. Скажите об этом при подаче.",
    cgt_h="Если потом продадите: налог на прирост капитала 20%",
    cgt="Налог на прирост капитала — 20% с прироста при отчуждении недвижимости на Кипре. Налоговый департамент уменьшает прирост на инфляцию по официальному индексу розничных цен. Этот перечень индекс не хранит: коэффициент берите из таблицы департамента. Для физического лица сводка закона указывает пожизненный вычет €30 000, €50 000, если фермер продаёт сельхозземлю, и €150 000 по основному жилью, которым владелец пользовался не меньше пяти лет (десять лет, если это не первое такое отчуждение), на участке до 1,5 декара. Общий вычет и вычет за жильё вместе не даются. Компании этих пожизненных вычетов не имеют.",
    rent_h="Если будете сдавать",
    rent="Вычет 20% из валовой аренды — уставный вычет для подоходного налога. С 1 января 2026 года шкалы для физического лица: ноль на первые €22 000, 20% до €32 000, 25% до €42 000, 30% до €72 000 и 35% сверх этого. Специальный сбор на оборону с аренды в налоговом 2026 году равен нулю, в том числе для домицилированных резидентов. Взнос ГЕСИ с аренды — 2,65% валовой аренды. Годовой потолок возможен и здесь не воспроизводится.",
    other_h="Расходы, у которых нет налоговой ставки",
    other="Гонорар юриста, поиск в кадастре, пошлина за сдачу договора, залоги коммунальных компаний и муниципальные сборы не сводятся к одному опубликованному проценту. Просите их письменно. Не прибавляйте ежегодный государственный налог на недвижимость: за налоговые годы с 2017-го он не взимается.",
    gate_h="Получить перечень",
    gate_p="Отправьте имя и эл. почту. Перечень откроется в этом браузере, и его можно напечатать или сохранить как PDF. Сведения нужны только чтобы открыть страницу.",
    send="Отправить и открыть перечень",
 ),
 "el": dict(
    h="Αγορά ακινήτου στην Κύπρο: λίστα φόρων και τελών 2026",
    lede="Οι δημοσιευμένοι φόροι σε μια αγορά, και όσοι εμφανίζονται αργότερα αν ενοικιάσετε ή πουλήσετε. Δεν είναι αμοιβή αυτού του ιστοτόπου, ούτε βεβαίωση του συμβολαίου σας.",
    print="Εκτύπωση ή αποθήκευση PDF",
    fork_h="Τέλη μεταβίβασης ή ΦΠΑ, συνήθως όχι και τα δύο",
    fork="Το Gov.cy αναφέρει ότι τα τέλη μεταβίβασης δεν επιβάλλονται όταν η μεταβίβαση αφορά συναλλαγή που υπόκειται σε ΦΠΑ, αν προσκομίσετε το πιστοποιητικό του Τμήματος ΦΠΑ. Όπου δεν επιβάλλεται ΦΠΑ, η νομοθεσία παρέχει απαλλαγή 50% των τελών. Η απαλλαγή 50% δεν δίνεται αν ο πωλητής απέκτησε το ακίνητο σε αναγκαστική πώληση κατά τα Μέρη VI και VIA του Νόμου 9/1965. Η κλίμακα του Κτηματολογίου, πριν από το 50%, είναι 3% από €0,01 έως €85.000, 5% από €85.001 έως €170.000 και 8% πάνω από €170.000. Τα κλιμάκια είναι στρώσεις. Σε αποδεκτή αξία €200.000, με έναν αγοραστή και χωρίς ΦΠΑ, η πλήρης κλίμακα είναι €9.200 και το μισό €4.600. Συμβόλαιο που δεν κατατέθηκε μέσα σε έξι μήνες μπορεί, κατά το φυλλάδιο του Τμήματος, να αυξήσει το τέλος κατά 10% στη μεταβίβαση.",
    vat_h="ΦΠΑ 19% ή 5% σε μέρος κύριας κατοικίας",
    vat="Ο κανονικός συντελεστής είναι 19% της τιμής πριν τον ΦΠΑ. Το 5% είναι για κύρια και μόνιμη κατοικία, στα πρώτα 130 τετραγωνικά μέτρα και έως €350.000, και μόνο αν το συνολικό δομήσιμο δεν υπερβαίνει τα 190 τετραγωνικά μέτρα και η συνολική αξία τα €475.000. Ανάμεσα στα όρια το 5% πιάνει μόνο το επιλέξιμο μέρος. Πάνω από οποιοδήποτε εξωτερικό όριο ο μειωμένος συντελεστής δεν είναι διαθέσιμος. Κατοικία διακοπών, ή διαμέρισμα που θα ενοικιαστεί από την αρχή, υπολογίζεται με 19%. Το παράθυρο για τη μεταβατική αίτηση μειωμένου συντελεστή έτρεξε έως τις 15 Ιουνίου 2026. Αυτή η λίστα δεν θεωρεί την οδό ακόμη ανοιχτή.",
    stamp_h="Χαρτόσημο",
    stamp="Ο Νόμος 239(I)/2025 κατάργησε το χαρτόσημο από την 1η Ιανουαρίου 2026. Συμβόλαιο που καταρτίστηκε και υπογράφηκε από τουλάχιστον ένα μέρος κατά ή μετά την ημερομηνία αυτή δεν χαρτοσημαίνεται: το τέλος είναι €0. Συμβόλαιο που υπέγραψε ένα μέρος έως τις 31 Δεκεμβρίου 2025 παραμένει στην παλιά κλίμακα, με ανώτατο €20.000 σε ένα έγγραφο. Ο κατάλογος του Υπουργείου Εσωτερικών δεν έχει πάντα ξαναγραφεί για την κατάργηση. Πείτε το κατά την κατάθεση.",
    cgt_h="Αν πουλήσετε αργότερα: φόρος κεφαλαιουχικών κερδών 20%",
    cgt="Ο φόρος κεφαλαιουχικών κερδών είναι 20% στο κέρδος από διάθεση ακίνητης ιδιοκτησίας στην Κύπρο. Το Τμήμα Φορολογίας μειώνει το κέρδος για τον πληθωρισμό με τον επίσημο δείκτη τιμών λιανικής. Αυτή η λίστα δεν αποθηκεύει τον δείκτη: πάρτε τον λόγο από τον πίνακα του Τμήματος. Για φυσικό πρόσωπο, ο κωδικοποιημένος νόμος αναφέρει ισόβια απαλλαγή €30.000, €50.000 όταν γεωργός πωλεί γεωργική γη, και €150.000 για κύρια κατοικία που χρησιμοποιήθηκε τουλάχιστον πέντε έτη (δέκα αν δεν είναι η πρώτη τέτοια διάθεση) σε γη έως 1,5 δεκάρια. Δεν δικαιούται κανείς και τη γενική απαλλαγή και την απαλλαγή κατοικίας. Οι εταιρείες δεν έχουν αυτές τις ισόβιες απαλλαγές.",
    rent_h="Αν ενοικιάσετε",
    rent="Η έκπτωση 20% από το ακαθάριστο ενοίκιο είναι η νόμιμη έκπτωση φόρου εισοδήματος. Από την 1η Ιανουαρίου 2026 οι κλίμακες για φυσικό πρόσωπο είναι μηδέν στα πρώτα €22.000, 20% έως €32.000, 25% έως €42.000, 30% έως €72.000 και 35% πάνω από αυτό. Η έκτακτη εισφορά για την άμυνα στο ενοίκιο είναι μηδέν για το φορολογικό έτος 2026, και για κατοίκους με κατοικία. Η εισφορά ΓεΣΥ στο ενοίκιο είναι 2,65% του ακαθάριστου ενοικίου. Ετήσιο ανώτατο μπορεί να ισχύει και δεν αναπαράγεται εδώ.",
    other_h="Έξοδα που δεν είναι φορολογικός συντελεστής",
    other="Η αμοιβή δικηγόρου, η έρευνα στο Κτηματολόγιο, το τέλος κατάθεσης συμβολαίου, οι εγγυήσεις υπηρεσιών και τα δημοτικά τέλη δεν ανάγονται σε ένα δημοσιευμένο ποσοστό. Ζητήστε τα γραπτώς. Μην προσθέτετε ετήσιο κρατικό φόρο ακίνητης ιδιοκτησίας: δεν επιβάλλεται για φορολογικά έτη από το 2017.",
    gate_h="Πάρτε τη λίστα",
    gate_p="Στείλτε όνομα και email. Η λίστα ανοίγει σε αυτόν τον browser και μπορείτε να την εκτυπώσετε ή να την αποθηκεύσετε ως PDF. Τα στοιχεία χρησιμοποιούνται μόνο για να ανοίξει η σελίδα.",
    send="Αποστολή και άνοιγμα της λίστας",
 ),
}

def services_page(lang):
    u = UI[lang]
    intro = {
        "en": "Paid help with Cyprus property tax. Each item is quoted before any work starts. This page does not publish a fee.",
        "ru": "Платная помощь с налогами на недвижимость Кипра. По каждой услуге стоимость называют до начала работы. Эта страница цену не публикует.",
        "el": "Αμειβόμενη βοήθεια με φόρους ακινήτου στην Κύπρο. Κάθε υπηρεσία κοστολογείται πριν αρχίσει η δουλειά. Αυτή η σελίδα δεν δημοσιεύει τιμή.",
    }[lang]
    cards = []
    for value, copy in SERVICE_LIST:
        title, text = copy[lang]
        cards.append(
            f'<article class="card"><h2>{e(title)}</h2><p>{e(text)}</p>'
            f'<a class="more" href="{consult_href(lang, value)}">{e(QUOTE[lang])}</a></article>'
        )
    free_h = {"en": "Free checklist", "ru": "Бесплатный перечень", "el": "Δωρεάν λίστα"}[lang]
    free_p = CHECKLIST[lang]["h"]
    path = loc(lang, "/services/")
    def alt(l):
        return loc(l, "/services/")
    body = (f'<main id="main" class="wrap page"><h1>{e(u["services"])}</h1><p class="lede">{e(intro)}</p>'
            f'<div class="grid">{"".join(cards)}</div>'
            f'<h2 class="sec">{e(free_h)}</h2><p>{e(free_p)}</p>'
            f'<p><a class="go" href="{href(loc(lang, "/buying-checklist/"))}">{e(CHECKLIST[lang]["gate_h"])}</a></p>'
            f'</main>')
    return page_shell(lang, f'{u["services"]} | {SITE}', intro, path, alt, body, service_nodes())

def checklist_gate(lang):
    base = LEAD[lang]
    c = CHECKLIST[lang]
    a = CONSULT[lang]
    privacy = href(loc(lang, "/privacy/"))
    nxt = loc(lang, "/buying-checklist/2026/")
    return f'''<form class="lead" action="https://formsubmit.co/{LEADS_EMAIL}" method="POST">
<input type="hidden" name="_subject" value="mycytax lead">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="true">
<input type="hidden" name="_next" value="{e(absu(nxt))}">
<input type="hidden" name="interest" value="Buying property checklist">
<p class="hp"><label>{e(base["honey"])}<input name="_honey" tabindex="-1" autocomplete="off"></label></p>
<label class="fld"><span>{e(base["name"])}</span><input name="name" required autocomplete="name"></label>
<label class="fld"><span>{e(base["email"])}</span><input type="email" name="email" required autocomplete="email"></label>
<label class="chk"><input type="checkbox" name="consent" value="yes" required><span>{e(a["consent"])} <a href="{privacy}">{e(UI[lang]["privacy"])}</a>.</span></label>
<button class="send" type="submit">{e(c["send"])}</button></form>'''

def checklist_gate_page(lang):
    c = CHECKLIST[lang]
    path = loc(lang, "/buying-checklist/")
    def alt(l):
        return loc(l, "/buying-checklist/")
    body = (f'<main id="main" class="wrap page"><h1>{e(c["gate_h"])}</h1>'
            f'<p class="lede">{e(c["h"])}</p><p>{e(c["gate_p"])}</p>'
            f'{checklist_gate(lang)}</main>')
    return page_shell(lang, f'{c["h"]} | {SITE}', c["gate_p"], path, alt, body)

def _checklist_links(lang):
    labels = {
        "en": ("Transfer fees", "VAT", "Stamp duty", "Capital gains", "Rental income", "Total cost of buying"),
        "ru": ("Сборы за переход", "НДС", "Гербовый сбор", "Прирост капитала", "Аренда", "Полная стоимость покупки"),
        "el": ("Τέλη μεταβίβασης", "ΦΠΑ", "Χαρτόσημο", "Κεφαλαιουχικά κέρδη", "Ενοίκιο", "Συνολικό κόστος αγοράς"),
    }[lang]
    slugs = (
        ("/calculators/transfer-fees/", labels[0]),
        ("/calculators/vat/", labels[1]),
        ("/calculators/stamp-duty/", labels[2]),
        ("/calculators/capital-gains/", labels[3]),
        ("/calculators/rental-yield/", labels[4]),
        ("/guides/total-cost/", labels[5]),
    )
    return " ".join(f'<a href="{href(loc(lang, path))}">{e(label)}</a>' for path, label in slugs)

def checklist_page(lang):
    c = CHECKLIST[lang]
    u = UI[lang]
    path = loc(lang, "/buying-checklist/2026/")
    def alt(l):
        return loc(l, "/buying-checklist/2026/")
    sources = (
        ("Calculation of transfer fees, Gov.cy", "https://www.gov.cy/en/service/calculation-of-real-estates-transfer-fees/"),
        ("Sale and exchange fees, Department of Lands and Surveys", "https://portal.dls.moi.gov.cy/en/application_forms/polisi-antallagi/"),
        ("VAT 5% tool, Gov.cy", "https://www.gov.cy/mof-tfa/en/documents/vat-5-calculation-tool-for-the-purchase-building-of-a-house/"),
        ("Repeal of stamp duty, KPMG note on the Tax Department announcement", "https://kpmg.com/us/en/taxnewsflash/news/2026/01/tnf-cyprus-repeal-of-stamp-duty-laws.html"),
        ("Capital Gains Tax Law section 5, CyLaw", "https://cylaw.org/nomoi/enop/ind/1980_1_52/section-sca7e654bc-d0c0-9dd6-06d7-c735c009387b.html"),
        ("Rental income, Tax Department", "https://www.mof.gov.cy/mof/TAX/taxdep.nsf/All/04BF7957A056E21DC225873D0038367D"),
        ("Tax residency and defence contribution on rent, Gov.cy", "https://www.gov.cy/mof-tax/en/documents/tax-residency-domicility/"),
        ("Tax Facts and Figures 2026, PwC Cyprus", "https://www.pwc.com.cy/en/publications/assets/tff-eng-2026.pdf"),
    )
    src = "".join(f'<li><a href="{e(url)}">{e(name)}</a></li>' for name, url in sources)
    body = f'''<main id="main" class="wrap page print-doc">
<p class="no-print"><button type="button" class="go" onclick="window.print()">{e(c["print"])}</button></p>
<h1>{e(c["h"])}</h1><p class="lede">{e(c["lede"])}</p>
<p class="banner">{e(DISCLAIMER[lang])}</p>
<div class="body">
<h2 id="step-1">{e(c["fork_h"])}</h2><p>{e(c["fork"])}</p>
<h2 id="step-2">{e(c["vat_h"])}</h2><p>{e(c["vat"])}</p>
<h2 id="step-3">{e(c["stamp_h"])}</h2><p>{e(c["stamp"])}</p>
<h2 id="step-4">{e(c["cgt_h"])}</h2><p>{e(c["cgt"])}</p>
<h2 id="step-5">{e(c["rent_h"])}</h2><p>{e(c["rent"])}</p>
<h2 id="step-6">{e(c["other_h"])}</h2><p>{e(c["other"])}</p>
<p>{_checklist_links(lang)}</p>
</div>
<section class="src"><h2>{e(u["sources"])}</h2><ul>{src}</ul></section>
</main>'''
    steps = []
    for position, key_h, key_t in (
        (1, "fork_h", "fork"), (2, "vat_h", "vat"), (3, "stamp_h", "stamp"),
        (4, "cgt_h", "cgt"), (5, "rent_h", "rent"), (6, "other_h", "other"),
    ):
        steps.append({
            "@type": "HowToStep",
            "position": position,
            "name": c[key_h],
            "text": c[key_t],
            "url": absu(path) + "#step-" + str(position),
        })
    howto = {"@context":"https://schema.org","@type":"HowTo","name":c["h"],"description":c["lede"],
             "inLanguage":lang,"step":steps}
    return page_shell(lang, f'{c["h"]} | {SITE}', c["lede"], path, alt, body, [howto], robots="noindex,follow")

def contact_href(lang, kind):
    return href(loc(lang, "/contact/")) + "?type=" + kind
def lead_card(lang):
    a = LEAD[lang]
    return (f'<aside class="cta"><h2>{e(a["h"])}</h2><p>{e(a["p"])}</p><div class="cta-btns">'
            f'<a class="go" href="{contact_href(lang,"buy")}">{e(a["buy"])}</a>'
            f'<a class="go alt" href="{contact_href(lang,"sell")}">{e(a["sell"])}</a></div></aside>')
def form(lang, next_path):
    a = LEAD[lang]
    types = [("buy", a["buyv"], a["buyl"]), ("sell", a["sellv"], a["selll"]), ("rent", a["rentv"], a["rentl"])]
    radios = "".join(
        f'<label class="chk"><input type="radio" name="request_choice" data-rtype="{k}" value="{e(v)}"><span>{e(lab)}</span></label>'
        for k, v, lab in types)
    props = "".join(f'<option value="{e(v)}">{e(lab)}</option>' for v, lab in a["props"])
    return f'''<form class="lead" id="leadform" action="https://formsubmit.co/{LEADS_EMAIL}" method="POST">
<input type="hidden" name="_subject" id="leadsubject" value="MyCyTax lead: Buy consultation">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="true">
<input type="hidden" name="_next" value="{e(absu(next_path))}">
<input type="hidden" name="request type" id="requesttype" value="Buy consultation">
<p class="hp"><label>{e(a["honey"])}<input name="_honey" tabindex="-1" autocomplete="off"></label></p>
<fieldset class="choices"><legend>{e(a["type"])}</legend>{radios}</fieldset>
<label class="fld"><span>{e(a["name"])}</span><input name="name" required autocomplete="name"></label>
<label class="fld"><span>{e(a["email"])}</span><input type="email" name="email" required autocomplete="email"></label>
<label class="fld"><span>{e(a["phone"])}</span><input name="phone" required autocomplete="tel"></label>
<label class="fld"><span>{e(a["prop"])}</span><select name="property type">{props}</select></label>
<label class="fld"><span>{e(a["area"])}</span><input name="area or city" required></label>
<label class="fld"><span>{e(a["budget"])}</span><input name="budget or expected price" inputmode="decimal"></label>
<label class="fld"><span>{e(a["msg"])}</span><textarea name="message" required style="min-height:140px;font:inherit;padding:10px;border:1px solid #d5cbbd;border-radius:10px"></textarea></label>
<label class="chk"><input type="checkbox" name="consent" value="yes" required><span>{e(a["consent"])}</span></label>
<button class="send" type="submit">{e(a["send"])}</button></form>
<script>
(function(){{
  var map={{buy:"Buy consultation",sell:"Sell",rent:"Rent out"}};
  var q=new URLSearchParams(location.search).get("type")||"buy";
  if(!map[q]) q="buy";
  function setType(key){{
    var label=map[key]||map.buy;
    document.getElementById("requesttype").value=label;
    document.getElementById("leadsubject").value="MyCyTax lead: "+label;
    document.querySelectorAll("[data-rtype]").forEach(function(el){{el.checked=el.getAttribute("data-rtype")===(map[key]?key:"buy");}});
  }}
  setType(q);
  document.querySelectorAll("[data-rtype]").forEach(function(el){{
    el.addEventListener("change", function(){{ if(el.checked) setType(el.getAttribute("data-rtype")); }});
  }});
}})();
</script>'''

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
    ld = [{"@context":"https://schema.org","@type":"WebSite","name":SITE,"url":absu(alt(lang)),"inLanguage":lang,
           "publisher":{"@id":absu("/") + "#organization"}}] + service_nodes()
    body = f'''<main id="main"><div class="wrap hero"><h1>{e(title)}</h1><p class="lede">{e(intro)}</p>
<p class="banner">{e(DISCLAIMER[lang])}</p>{ad("home-top")}</div>
<div class="wrap"><h2 class="sec">{e(u["calcs"])}</h2><div class="grid">{"".join(cards)}</div>
<h2 class="sec">{e(u["guides"])}</h2><div class="grid">{"".join(guides)}</div>
{lead_card(lang)}{ad("home-bottom")}
{news_block(lang)}</div></main>'''
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

# One unobtrusive offer under a calculator that names a partner. The button URL comes from affiliates.js.
# guide is an internal article, not a partner.
CALC_OFFERS = {
 "capital-gains": {
    "key": "ledger",
    "guide": "store-savings-and-crypto",
    "en": {
        "h": "Where anything you still hold should sit",
        "p": "The result is the tax on one sale, not a plan for the rest. Cash from a property sale usually belongs in a bank while you decide. If part of what you already hold is crypto, a hardware wallet such as a Ledger keeps the keys offline instead of on an exchange. Crypto prices can fall sharply. This is not a suggestion to turn the proceeds into crypto.",
        "btn": "See Ledger",
        "more": "How to store savings and crypto",
    },
    "ru": {
        "h": "Где держать то, что у вас остаётся",
        "p": "Результат — налог с одной продажи, а не план для остального. Деньги от продажи недвижимости обычно лежат в банке, пока вы решаете. Если часть того, что у вас уже есть, — это криптовалюта, аппаратный кошелёк вроде Ledger держит ключи офлайн, а не на бирже. Цены на криптовалюту могут сильно упасть. Это не предложение перевести выручку в криптовалюту.",
        "btn": "Открыть Ledger",
        "more": "Как хранить сбережения и криптовалюту",
    },
    "el": {
        "h": "Πού να κάθεται ό,τι σας μένει",
        "p": "Το αποτέλεσμα είναι ο φόρος μίας πώλησης, όχι σχέδιο για τα υπόλοιπα. Μετρητά από πώληση ακινήτου συνήθως ανήκουν σε τράπεζα όσο αποφασίζετε. Αν μέρος όσων ήδη κρατάτε είναι κρυπτοστοιχείο, ένα hardware πορτοφόλι όπως το Ledger κρατά τα κλειδιά εκτός σύνδεσης, όχι σε ανταλλακτήριο. Οι τιμές μπορούν να πέσουν απότομα. Δεν είναι πρόταση να μετατρέψετε το προϊόν σε κρυπτοστοιχείο.",
        "btn": "Δείτε το Ledger",
        "more": "Πώς να φυλάξετε αποταμιεύσεις και κρυπτοστοιχεία",
    },
 },
 "rental-yield": {
    "key": "interactivebrokers",
    "guide": "international-brokers",
    "en": {
        "h": "Rent you do not spend",
        "p": "The yield after tax is an illustration of one year, not a forecast. Money left after tax can stay in the bank that receives the rent. Some owners move a surplus they can leave untouched to a broker such as Interactive Brokers. A broker account can fall in value. Tax on the rent is separate from any later gain or loss. This is not advice to invest the rent.",
        "btn": "See Interactive Brokers",
        "more": "How to think about a broker account",
    },
    "ru": {
        "h": "Аренда, которую вы не тратите",
        "p": "Доходность после налога — иллюстрация одного года, не прогноз. Деньги после налога могут остаться в банке, куда приходит аренда. Кто-то переводит остаток, который можно не трогать, брокеру вроде Interactive Brokers. Брокерский счёт может подешеветь. Налог с аренды отдельно от последующей прибыли или убытка. Это не совет вкладывать аренду.",
        "btn": "Открыть Interactive Brokers",
        "more": "Как думать о брокерском счёте",
    },
    "el": {
        "h": "Ενοίκιο που δεν ξοδεύετε",
        "p": "Η απόδοση μετά τον φόρο είναι εικόνα μίας χρονιάς, όχι πρόβλεψη. Τα χρήματα μετά τον φόρο μπορούν να μείνουν στην τράπεζα που εισπράττει το ενοίκιο. Κάποιοι μεταφέρουν πλεόνασμα που μπορούν να αφήσουν άθικτο σε χρηματιστή όπως η Interactive Brokers. Ένας λογαριασμός χρηματιστή μπορεί να χάσει αξία. Ο φόρος του ενοικίου είναι χωριστά από οποιοδήποτε μεταγενέστερο κέρδος ή ζημία. Δεν είναι συμβουλή να επενδύσετε το ενοίκιο.",
        "btn": "Δείτε την Interactive Brokers",
        "more": "Πώς να σκέφτεστε έναν λογαριασμό χρηματιστή",
    },
 },
}

def calc_offer(lang, slug):
    """Small box under a calculator. Empty when this calculator has no offer."""
    spec = CALC_OFFERS.get(slug)
    if not isinstance(spec, dict):
        return ""
    text = spec.get(lang) if isinstance(spec.get(lang), dict) else None
    url = affiliate_href(spec.get("key"))
    if not text or not url or not text.get("h") or not text.get("p") or not text.get("btn"):
        return ""
    guide = spec.get("guide") or ""
    more = ""
    if guide and text.get("more"):
        more = (
            f'<p class="aff-more"><a href="{href(loc(lang, "/guides/" + guide + "/"))}">'
            f'{e(text["more"])}</a></p>'
        )
    u = UI[lang]
    return (
        f'<aside class="aff-offer aff-calc" data-affiliate-widget="{e(spec["key"])}">'
        f'<h2>{e(text["h"])}</h2><p>{e(text["p"])}</p>'
        f'<a class="aff-btn" data-affiliate="{e(spec["key"])}" href="{e(url)}" '
        f'rel="{AFF_REL}" target="_blank">{e(text["btn"])}</a>'
        f"{more}"
        f'<p class="aff-disclosure">{e(u["aff_note"])} '
        f'<a href="{href(loc(lang, "/affiliate-disclosure/"))}">{e(u["affiliates"])}</a>.</p>'
        f"</aside>\n"
    )

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
    offer = calc_offer(lang, slug)
    ld = [{"@context":"https://schema.org","@type":"WebApplication","name":t,"applicationCategory":"FinanceApplication","operatingSystem":"Web","url":absu(path),
           "description":d,"inLanguage":lang,"offers":{"@type":"Offer","price":"0","priceCurrency":"EUR"},"publisher":org()},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
              {"@type":"Question","name":t,"acceptedAnswer":{"@type":"Answer","text":d}}]}]
    body = f'''<main id="main" class="wrap page"><p class="meta"><a href="{href(loc(lang, "/calculators/"))}">{e(u["calcs"])}</a></p>
<h1>{e(t)}</h1><p class="lede">{e(d)}</p><p class="banner">{e(DISCLAIMER[lang])}</p>{ad("calc-top")}
<div id="calc" data-consult="{contact_href(lang,"buy")}" data-calc="{e({"transfer-fees":"transfer","stamp-duty":"stamp","vat":"vat","capital-gains":"cgt","rental-yield":"rental","mortgage":"mortgage"}[slug])}"></div>
{offer}
{lead_card(lang)}
{consult_card(lang, {"capital-gains":"Capital gains tax","rental-yield":"Rental income tax"}.get(slug, ""))}
<div class="body"><h2>{e(u["sources"])}</h2><p>{note}</p></div>{ad("calc-bottom")}
{partners_block(lang, "calculators", slug)}{telegram_card(lang)}</main>
<script src="{href("/assets/calc.js")}" defer></script>'''
    return page_shell(lang, f"{t} | {SITE}", d, path, alt, body, ld)

def guide_figure(lang, slug):
    """Optional photograph stored beside the guide. Empty when the guide has none."""
    img = GUIDES[slug].get("image") or {}
    src = _clean(img.get("src"))
    if not src or "/" in src or src.startswith("."):
        return ""
    altmap = img.get("alt") if isinstance(img.get("alt"), dict) else {}
    credmap = img.get("credit") if isinstance(img.get("credit"), dict) else {}
    alt = _clean(altmap.get(lang)) or _clean(altmap.get("en"))
    credit = _clean(credmap.get(lang)) or _clean(credmap.get("en"))
    url = _https(img.get("credit_url"))
    cap = f'<a href="{e(url)}" rel="noopener">{e(credit or url)}</a>' if url else e(credit)
    wh = ""
    if img.get("width") and img.get("height"):
        wh = f' width="{int(img["width"])}" height="{int(img["height"])}"'
    return (f'<figure class="guide-fig"><img src="{href("/assets/guides/" + src)}" alt="{e(alt)}"{wh}>'
            f"<figcaption>{cap}</figcaption></figure>")

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
         "inLanguage":lang,"datePublished":guide_published(slug),"dateModified":guide_modified(slug),"mainEntityOfPage":absu(path),
         "author":{"@type":"Organization","name":SITE,"url":absu("/"),"sameAs":[TG_RU, TG_EN]},
         "publisher":{"@type":"Organization","name":SITE,"url":absu("/"),"sameAs":[TG_RU, TG_EN]}},
    ]
    if faqs:
        ld.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q, a in faqs]})
    crumb = f'<a href="{href(loc(lang, "/guides/"))}">{e(u["guides"])}</a>'
    if "/" in slug:
        parent = slug.split("/", 1)[0]
        if parent in GUIDES:
            parent_meta, _ = load_md(lang, parent)
            crumb += f' · <a href="{href(loc(lang, "/guides/"+parent+"/"))}">{e(parent_meta["title"])}</a>'
    figure = guide_figure(lang, slug)
    if figure:
        ld[0]["image"] = absu("/assets/guides/" + GUIDES[slug]["image"]["src"])
    disclosure = affiliate_disclosure(lang) if ('data-affiliate="' in body_html or 'data-amazon-search="' in body_html) else ""
    body = f'''<main id="main" class="wrap page"><p class="meta">{crumb}</p>
<article><h1>{e(meta["title"])}</h1><p class="lede">{e(meta["description"])}</p>
{figure}
<p class="banner">{e(DISCLAIMER[lang])}</p>{ad("guide-top")}
<div class="body">{body_html}</div>
{disclosure}
{faq_html}
<section class="src"><h2>{e(u["sources"])}</h2><ul>{src}</ul></section>
{lead_card(lang)}
{consult_card(lang)}
{ad("guide-bottom")}
{partners_block(lang, "guides", slug)}{telegram_card(lang)}
{news_block(lang)}</article></main>'''
    robots = "noindex,follow" if lang in GUIDES[slug]["missing"] else "index,follow,max-image-preview:large"
    return page_shell(lang, f'{meta["title"]} | {SITE}', meta["description"], path, alt, body, ld, robots=robots)

def static_page(lang, slug):
    title, desc, paras = PAGES[slug]["text"][lang]
    path = loc(lang, f"/{slug}/")
    def alt(l, slug=slug):
        return loc(l, f"/{slug}/")
    body_html = "".join(f"<p>{e(p)}</p>" for p in paras)
    body = f'<main id="main" class="wrap page"><h1>{e(title)}</h1><p class="lede">{e(desc)}</p><div class="body">{body_html}</div>'
    if slug == "about":
        body += f'<p><a href="{href(loc(lang, "/contact/"))}">{e(UI[lang]["contact"])}</a></p>'
    body += "</main>"
    robots = "noindex,follow" if lang in PAGES[slug]["missing"] else "index,follow,max-image-preview:large"
    return page_shell(lang, f"{title} | {SITE}", desc, path, alt, body, robots=robots)

def contact(lang):
    u = UI[lang]
    path = loc(lang, "/contact/")
    def alt(l):
        return loc(l, "/contact/")
    title, desc, intro = u["contact_t"], u["contact_d"], u["contact_i"]
    body = f'<main id="main" class="wrap page"><h1>{e(title)}</h1><p class="lede">{e(desc)}</p><p>{e(intro)}</p><p class="banner">{e(DISCLAIMER[lang])}</p>{form(lang, loc(lang, "/contact/thanks/"))}</main>'
    return page_shell(lang, f"{title} | {SITE}", desc, path, alt, body)

# Instagram link-in-bio. Not linked from the site nav. One page per language.
# Generated here because main() deletes directories it does not rewrite.
LINKS_UTM = "utm_source=instagram&utm_medium=social&utm_content=links"
LINKS_TAGLINE = {
    "en": "Free Cyprus property tax calculators & guides",
    "ru": "Бесплатные калькуляторы и справочники по налогам Кипра",
    "el": "Δωρεάν υπολογιστές και οδηγοί για φόρους ακινήτων στην Κύπρο",
}
LINKS_DESC = {
    "en": (
        "Free Cyprus property tax calculators and guides: transfer fees, stamp duty, "
        "VAT, capital gains, rental income, tax residency, non-dom status and a residence permit."
    ),
    "ru": (
        "Бесплатные калькуляторы и справочники по налогам Кипра: сборы кадастра, гербовый сбор, "
        "НДС, прирост капитала, аренда, налоговое резидентство, non-dom и ВНЖ."
    ),
    "el": (
        "Δωρεάν υπολογιστές και οδηγοί για φόρους ακινήτων στην Κύπρο: τέλη μεταβίβασης, χαρτόσημο, "
        "ΦΠΑ, κεφαλαιουχικά κέρδη, ενοίκιο, φορολογική κατοικία, non-dom και άδεια διαμονής."
    ),
}
LINKS_ITEMS = [
    ("Transfer fees calculator", "/calculators/transfer-fees/"),
    ("Stamp duty", "/calculators/stamp-duty/"),
    ("VAT on new property 5% or 19%", "/calculators/vat/"),
    ("Capital gains tax", "/calculators/capital-gains/"),
    ("Rental income tax & yield", "/calculators/rental-yield/"),
    ("Tax residency 60/183-day guide", "/guides/tax-residency/"),
    ("Non-dom guide", "/guides/non-dom/"),
    ("Residence permit via property", "/guides/residence-permit/"),
    ("All calculators", "/"),
]
LINKS_LABELS = {
    "ru": [
        "Калькулятор сборов за переоформление",
        "Гербовый сбор",
        "НДС на новое жильё: 5% или 19%",
        "Налог на прирост капитала",
        "Налог на аренду и доходность",
        "Налоговое резидентство: 60 и 183 дня",
        "Справочник по non-dom",
        "ВНЖ через покупку недвижимости",
        "Все калькуляторы",
    ],
    "el": [
        "Υπολογιστής τελών μεταβίβασης",
        "Χαρτόσημο",
        "ΦΠΑ σε νέα κατοικία: 5% ή 19%",
        "Φόρος κεφαλαιουχικών κερδών",
        "Φόρος ενοικίου και απόδοση",
        "Φορολογική κατοικία: 60 και 183 ημέρες",
        "Οδηγός non-dom",
        "Άδεια διαμονής μέσω ακινήτου",
        "Όλοι οι υπολογιστές",
    ],
}

def links_labels(lang):
    if lang == "en":
        return [label for label, _dest in LINKS_ITEMS]
    return LINKS_LABELS[lang]

def links_dest(lang, path):
    """Same path in the page language. A query on the path is kept."""
    base, _, query = path.partition("?")
    localized = loc(lang, base)
    return localized + (("?" + query) if query else "")

def links_url(path):
    """Add the Instagram campaign query. Keep a query the path already has."""
    base, _, query = path.partition("?")
    params = LINKS_UTM if not query else query + "&" + LINKS_UTM
    return href(base) + "?" + params

def links_page(lang="en"):
    tagline = LINKS_TAGLINE[lang]
    title = f"{tagline} | {SITE}"
    desc = LINKS_DESC[lang]
    path = loc(lang, "/links/")
    def alt(l):
        return loc(l, "/links/")
    labels = links_labels(lang)
    if len(labels) != len(LINKS_ITEMS):
        raise SystemExit(f"links labels for {lang} do not match LINKS_ITEMS")
    items = [(label, links_dest(lang, dest)) for label, (_en, dest) in zip(labels, LINKS_ITEMS)]
    items.append((LEAD[lang]["buy"], links_dest(lang, "/contact/?type=buy")))
    anchors = []
    for index, (label, dest) in enumerate(items):
        kind = ' class="bio-contact"' if index == len(items) - 1 else ""
        anchors.append(f'<a{kind} href="{e(links_url(dest))}">{e(label)}</a>')
    ld = {
        "@context": "https://schema.org", "@type": "WebPage",
        "name": title, "description": desc, "url": absu(path), "inLanguage": lang,
        "isPartOf": {"@type": "WebSite", "name": SITE, "url": absu("/")},
    }
    body = f'''<a class="skip" href="#main">{e(UI[lang]["home"])}</a><main id="main" class="bio"><div class="bio-brand">
<a class="logo" href="{href(loc(lang, "/"))}">{e(SITE)}</a>
<p class="bio-tag">{e(tagline)}</p></div>
<nav class="bio-links" aria-label="{e(SITE)}">{"".join(anchors)}</nav></main>'''
    return head(lang, title, desc, path, alt, with_breadcrumbs(lang, path, title, [ld])) + body + footer(lang)

def thanks(lang):
    u = UI[lang]
    path = loc(lang, "/contact/thanks/")
    def alt(l):
        return loc(l, "/contact/thanks/")
    title, desc, text = u["thanks_t"], u["thanks_d"], u["thanks_i"]
    body = f'<main id="main" class="wrap page"><h1>{e(title)}</h1><p>{e(text)}</p></main>'
    return page_shell(lang, f"{title} | {SITE}", desc, path, alt, body, robots="noindex,follow")

def w(rel, content):
    path = os.path.join(OUT, rel.lstrip("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        f.write(content)

_GIT_DAYS = {}

def git_days(path):
    """(first commit day, last commit day) for a repo path, or (None, None)."""
    if path in _GIT_DAYS:
        return _GIT_DAYS[path]
    try:
        proc = subprocess.run(
            ["git", "-C", ROOT, "log", "--follow", "--format=%cs", "--", path],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        _GIT_DAYS[path] = (None, None)
        return _GIT_DAYS[path]
    days = [
        line.strip() for line in (proc.stdout or "").splitlines()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line.strip())
    ]
    _GIT_DAYS[path] = (days[-1], days[0]) if days else (None, None)
    return _GIT_DAYS[path]

def guide_published(slug):
    first, last = git_days(f"source/content/guides/{slug}.json")
    return first or last or TODAY

def guide_modified(slug):
    first, last = git_days(f"source/content/guides/{slug}.json")
    return last or first or TODAY

def bare_path(path):
    """Drop the /ru or /el prefix so a translation shares its source with English."""
    if not path.startswith("/"):
        path = "/" + path
    for lang in ("ru", "el"):
        if path == f"/{lang}" or path == f"/{lang}/":
            return "/"
        prefix = f"/{lang}/"
        if path.startswith(prefix):
            return "/" + path[len(prefix):]
    return path

def sources_for(path):
    """Files whose last commit is the page's modification date."""
    bare = bare_path(path).split("?")[0]
    if bare.endswith("feed.xml"):
        return [f"source/content/guides/{slug}.json" for slug in GUIDE_ORDER]
    parts = [part for part in bare.strip("/").split("/") if part]
    if not parts:
        return ["source/build.py"]
    if len(parts) == 1 and parts[0] in PAGE_ORDER:
        return [f"source/content/pages/{parts[0]}.json"]
    if len(parts) == 2 and parts[0] == "guides":
        return [f"source/content/guides/{parts[1]}.json"]
    if parts[0] == "real-estate":
        return ["source/build.py", "data/properties.json"]
    if parts[0] == "calculators" and len(parts) == 2:
        return ["source/build.py", "source/static/calc.js"]
    return ["source/build.py"]

def page_lastmod(path):
    """Git last-commit day of the page source, or the build day when git has none."""
    found = []
    for src in sources_for(path):
        _first, last = git_days(src)
        if last:
            found.append(last)
    if found:
        return max(found)
    return datetime.date.today().isoformat()

PROPERTIES_PATH = os.path.join(ROOT, "data", "properties.json")
LISTING_TYPES = ("project", "apartment", "villa", "house", "land", "commercial")
LISTING_STATUSES = ("available", "sold", "under-construction")
REAL_ESTATE_GUIDES = (
    "taxes-overview", "buying-as-a-foreigner", "total-cost", "off-plan", "title-deeds",
    "selling-and-taxes", "renting-out", "residence-permit", "mortgage-comparison",
    "relocation/cost-and-tax", "resident-handbook/utilities", "water-tariff-proposal",
)
PROPERTY_LABELS = {
 "en": {
    "listings": "Listings", "guides": "Guides", "calcs": "Calculators",
    "empty": "No properties are listed at the moment.",
    "calc_h": "Calculators for this price",
    "type": {"project": "Project", "apartment": "Apartment", "villa": "Villa", "house": "House", "land": "Land", "commercial": "Commercial"},
    "status": {"available": "Available", "sold": "Sold", "under-construction": "Under construction"},
 },
 "ru": {
    "listings": "Объявления", "guides": "Справочники", "calcs": "Калькуляторы",
    "empty": "Сейчас нет опубликованных объявлений.",
    "calc_h": "Калькуляторы с этой ценой",
    "type": {"project": "Проект", "apartment": "Квартира", "villa": "Вилла", "house": "Дом", "land": "Участок", "commercial": "Коммерция"},
    "status": {"available": "Свободно", "sold": "Продано", "under-construction": "Строится"},
 },
 "el": {
    "listings": "Αγγελίες", "guides": "Οδηγοί", "calcs": "Υπολογιστές",
    "empty": "Δεν υπάρχουν δημοσιευμένες αγγελίες αυτή τη στιγμή.",
    "calc_h": "Υπολογιστές με αυτή την τιμή",
    "type": {"project": "Έργο", "apartment": "Διαμέρισμα", "villa": "Βίλα", "house": "Οικία", "land": "Οικόπεδο", "commercial": "Επαγγελματικό"},
    "status": {"available": "Διαθέσιμο", "sold": "Πωλήθηκε", "under-construction": "Υπό κατασκευή"},
 },
}

def _listing_number(value, ident, field):
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SystemExit(f"data/properties.json: {ident}: {field} must be a number or null")
    if value < 0:
        raise SystemExit(f"data/properties.json: {ident}: {field} cannot be negative")
    return value

def load_properties(path=None):
    path = path or PROPERTIES_PATH
    if not os.path.isfile(path):
        raise SystemExit(f"missing {path}")
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    rows = data.get("listings") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise SystemExit(f"{path}: expected an object with a listings list")
    out, seen = [], set()
    for index, raw in enumerate(rows, 1):
        if not isinstance(raw, dict):
            raise SystemExit(f"{path}: listing {index} is not an object")
        ident = _clean(raw.get("id"))
        where = f"{path}: {ident or index}"
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident or ""):
            raise SystemExit(f"{where}: id must be lower-case letters, digits and hyphens")
        if ident in seen:
            raise SystemExit(f"{where}: duplicate id")
        seen.add(ident)
        if not isinstance(raw.get("published"), bool):
            raise SystemExit(f"{where}: published must be true or false")
        if not isinstance(raw.get("price_from"), bool):
            raise SystemExit(f"{where}: price_from must be true or false")
        title = raw.get("title") if isinstance(raw.get("title"), dict) else {}
        desc = raw.get("description") if isinstance(raw.get("description"), dict) else {}
        for lang in LANGS:
            if not _clean(title.get(lang)) or not _clean(desc.get(lang)):
                raise SystemExit(f"{where}: {lang} title and description are required")
        kind, status = _clean(raw.get("type")), _clean(raw.get("status"))
        if kind not in LISTING_TYPES:
            raise SystemExit(f"{where}: type must be one of {', '.join(LISTING_TYPES)}")
        if status not in LISTING_STATUSES:
            raise SystemExit(f"{where}: status must be one of {', '.join(LISTING_STATUSES)}")
        price = _listing_number(raw.get("price_eur"), ident, "price_eur")
        area = _listing_number(raw.get("area_m2"), ident, "area_m2")
        beds = raw.get("bedrooms")
        if beds is not None and beds != "":
            if isinstance(beds, bool) or not isinstance(beds, int):
                raise SystemExit(f"{where}: bedrooms must be a whole number or null")
            if beds < 0:
                raise SystemExit(f"{where}: bedrooms cannot be negative")
        else:
            beds = None
        photos = raw.get("photos") if raw.get("photos") is not None else []
        if not isinstance(photos, list):
            raise SystemExit(f"{where}: photos must be a list")
        prefix = f"images/properties/{ident}/"
        clean_photos = []
        for photo in photos:
            photo = _clean(photo)
            if not photo.startswith(prefix) or ".." in photo:
                raise SystemExit(f"{where}: each photo must start with {prefix}")
            if raw["published"] and not os.path.isfile(os.path.join(ROOT, photo)):
                raise SystemExit(f"{where}: missing {photo}")
            clean_photos.append(photo)
        out.append({
            "id": ident, "published": raw["published"], "title": {l: _clean(title[l]) for l in LANGS},
            "description": {l: _clean(desc[l]) for l in LANGS}, "type": kind, "status": status,
            "city": _clean(raw.get("city")), "area": _clean(raw.get("area")),
            "price_eur": price, "price_from": raw["price_from"], "bedrooms": beds, "area_m2": area,
            "photos": clean_photos,
        })
    return out

PROPERTIES = load_properties()

def published_listings(rows=None):
    rows = PROPERTIES if rows is None else rows
    return [row for row in rows if row["published"]]

def euro_text(lang, amount, price_from=False):
    number = int(amount) if float(amount).is_integer() else amount
    if isinstance(number, int):
        grouped = f"{number:,}"
        if lang == "ru":
            grouped = grouped.replace(",", " ")
        elif lang == "el":
            grouped = grouped.replace(",", ".")
        text = "€" + grouped
    else:
        text = f"€{number}"
    if price_from:
        return {"en": "From ", "ru": "От ", "el": "Από "}[lang] + text
    return text

# Same wording CyNews24 puts on a price that the source states as excluding VAT.
_VAT_NOTE = {"en": "+ VAT", "ru": "без НДС", "el": "πλέον ΦΠΑ"}
_PRICE_ON_REQUEST = {
    "en": "Price on request",
    "ru": "Цена по запросу",
    "el": "Τιμή κατόπιν αιτήματος",
}
_AREA_UNIT = {"en": "m²", "ru": "м²", "el": "τ.μ."}

def price_vat_note(lang, description):
    """VAT status for the catalogue price, only when this language's text says the price excludes VAT."""
    text = description or ""
    if lang == "en" and re.search(
        r"\+\s*VAT|\bplus VAT\b|\bexcluding VAT\b|\bexcludes VAT\b|\bexclude VAT\b", text, re.I,
    ):
        return _VAT_NOTE["en"]
    if lang == "ru":
        if "без НДС" in text:
            return _VAT_NOTE["ru"]
        if re.search(r"\+\s*НДС", text):
            return "+ НДС"
    if lang == "el" and ("πλέον ΦΠΑ" in text or "χωρίς ΦΠΑ" in text):
        return _VAT_NOTE["el"]
    return ""

def beds_text(lang, count):
    if lang == "en":
        return "1 bedroom" if count == 1 else f"{count} bedrooms"
    if lang == "el":
        return "1 υπνοδωμάτιο" if count == 1 else f"{count} υπνοδωμάτια"
    if count % 10 == 1 and count % 100 != 11:
        word = "спальня"
    elif count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        word = "спальни"
    else:
        word = "спален"
    return f"{count} {word}"

def area_text(lang, value):
    number = int(value) if float(value).is_integer() else value
    return f"{number} {_AREA_UNIT[lang]}"

def listing_place(item):
    return ", ".join(part for part in (item["area"], item["city"]) if part)

def listing_facts(lang, item):
    labels = PROPERTY_LABELS[lang]
    bits = [labels["type"][item["type"]]]
    place = listing_place(item)
    if place:
        bits.append(place)
    if item["price_eur"] is not None:
        price = euro_text(lang, item["price_eur"], item["price_from"])
        note = price_vat_note(lang, (item.get("description") or {}).get(lang, ""))
        if note:
            price = f"{price} {note}"
        bits.append(price)
    else:
        bits.append(_PRICE_ON_REQUEST[lang])
    if item["bedrooms"] is not None:
        bits.append(beds_text(lang, item["bedrooms"]))
    if item["area_m2"] is not None:
        bits.append(area_text(lang, item["area_m2"]))
    bits.append(labels["status"][item["status"]])
    return bits

def listing_calc_links(lang, item):
    """Open the four purchase calculators on this price, when a price is set."""
    price = item["price_eur"]
    if price is None:
        return ""
    number = int(price) if float(price).is_integer() else price
    area = item["area_m2"]
    area_q = ""
    if area is not None:
        area_q = "&area=" + (str(int(area)) if float(area).is_integer() else str(area))
    specs = (
        ("transfer-fees", f"value={number}"),
        ("vat", f"price={number}{area_q}"),
        ("stamp-duty", f"value={number}"),
        ("mortgage", f"principal={number}"),
    )
    items = []
    for slug, query in specs:
        name = CALCS[slug][lang][0]
        url = href(loc(lang, f"/calculators/{slug}/")) + "?" + query
        items.append(f'<li><a href="{e(url)}">{e(name)}</a></li>')
    heading = PROPERTY_LABELS[lang]["calc_h"]
    return f'<section class="src"><h2>{e(heading)}</h2><ul>{"".join(items)}</ul></section>'

LISTING_LEAD = {
 "en": dict(
    request="Request info",
    p="Send your name and a phone or WhatsApp number. We reply within 24 hours.",
    email="Email (optional)",
    interest="I'm interested in {title}",
    thanks_d="Your request about this listing has been sent.",
 ),
 "ru": dict(
    request="Оставить заявку",
    p="Оставьте имя и телефон или WhatsApp. Ответим в течение 24 часов.",
    email="Эл. почта (необязательно)",
    interest="Меня интересует {title}",
    thanks_d="Заявка по этому объявлению отправлена.",
 ),
 "el": dict(
    request="Ζητήστε πληροφορίες",
    p="Στείλτε το όνομά σας και ένα τηλέφωνο ή WhatsApp. Απαντάμε μέσα σε 24 ώρες.",
    email="Email (προαιρετικό)",
    interest="Ενδιαφέρομαι για {title}",
    thanks_d="Το αίτημά σας για αυτή την αγγελία στάλθηκε.",
 ),
}

def listing_interest(lang, title):
    return LISTING_LEAD[lang]["interest"].replace("{title}", title)

def listing_request_link(lang, href_target):
    label = LISTING_LEAD[lang]["request"]
    return f'<a class="request" href="{e(href_target)}">{e(label)}</a>'

def listing_form(lang, item, path):
    """Same FormSubmit address as the other lead forms. No script: the button is an anchor."""
    a = LEAD[lang]
    lead = LISTING_LEAD[lang]
    title = item["title"][lang]
    interest = listing_interest(lang, title)
    thanks = absu(loc(lang, "/real-estate/thanks/"))
    subject = e("MyCyTax lead: " + title)
    return f'''<section class="cta listing-lead" id="listing-lead"><h2>{e(lead["request"])}</h2><p>{e(lead["p"])}</p>
<form class="lead listing-form" action="https://formsubmit.co/{LEADS_EMAIL}" method="POST">
<input type="hidden" name="_subject" value="{subject}">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_next" value="{e(thanks)}">
<input type="hidden" name="listing" value="{e(title)}">
<input type="hidden" name="page url" value="{e(absu(path))}">
<p class="hp"><label>{e(a["honey"])}<input name="_honey" tabindex="-1" autocomplete="off"></label></p>
<label class="fld"><span>{e(a["name"])}</span><input name="name" required autocomplete="name"></label>
<label class="fld"><span>{e(a["phone"])}</span><input name="phone" required autocomplete="tel" inputmode="tel"></label>
<label class="fld"><span>{e(lead["email"])}</span><input type="email" name="email" autocomplete="email"></label>
<label class="fld"><span>{e(a["msg"])}</span><textarea name="message">{e(interest)}</textarea></label>
<label class="chk"><input type="checkbox" name="consent" value="yes" required><span>{e(a["consent"])}</span></label>
<button class="send" type="submit">{e(a["send"])}</button></form></section>'''

def listing_thanks(lang):
    u = UI[lang]
    lead = LISTING_LEAD[lang]
    path = loc(lang, "/real-estate/thanks/")
    def alt(l):
        return loc(l, "/real-estate/thanks/")
    title = u["thanks_t"]
    body = f'''<main id="main" class="wrap page"><h1>{e(title)}</h1><p>{e(lead["thanks_d"])}</p><p>{e(u["thanks_i"])}</p>
<p><a href="{href(loc(lang, "/real-estate/"))}">{e(u["real_estate"])}</a></p></main>'''
    return page_shell(lang, f"{title} | {SITE}", lead["thanks_d"], path, alt, body, robots="noindex,follow")

def listings_block(lang, rows=None):
    labels = PROPERTY_LABELS[lang]
    rows = published_listings() if rows is None else [row for row in rows if row["published"]]
    if not rows:
        return f'<h2 class="sec">{e(labels["listings"])}</h2><p class="empty">{e(labels["empty"])}</p>'
    cards = []
    for item in rows:
        photo = ""
        if item["photos"] and os.path.isfile(os.path.join(ROOT, item["photos"][0])):
            photo = f'<img src="{href("/" + item["photos"][0])}" alt="{e(item["title"][lang])}">'
        meta = " · ".join(e(bit) for bit in listing_facts(lang, item))
        url = href(loc(lang, f"/real-estate/{item['id']}/"))
        cards.append(
            f'<article class="prop-card">{photo}<div class="pad"><h2>{e(item["title"][lang])}</h2>'
            f'<p class="prop-meta">{meta}</p>'
            f'{listing_request_link(lang, url + "#listing-lead")}'
            f'<p>{e(item["description"][lang])}</p>'
            f'<a class="more" href="{url}">{e(UI[lang]["read"])}</a></div></article>'
        )
    return f'<h2 class="sec">{e(labels["listings"])}</h2><div class="prop-grid">{"".join(cards)}</div>'

# Public notes, not inventory. No developer site, no developer photograph.
OTHER_PROJECT_COPY = {
 "en": dict(
    h="Notes on other new projects",
    note="These are not MyCyTax listings and not links to the developer. A price below is the figure on the developer page, and it can change.",
    cta="Get independent advice",
 ),
 "ru": dict(
    h="Заметки о других новых проектах",
    note="Это не объявления MyCyTax и не ссылки на застройщика. Цена ниже — цифра со страницы застройщика, и она может измениться.",
    cta="Независимая консультация",
 ),
 "el": dict(
    h="Σημειώσεις για άλλα νέα έργα",
    note="Δεν είναι αγγελίες του MyCyTax και δεν είναι σύνδεσμοι προς τον κατασκευαστή. Η τιμή από κάτω είναι το ποσό στη σελίδα του κατασκευαστή και μπορεί να αλλάξει.",
    cta="Ανεξάρτητη συμβουλή",
 ),
}
OTHER_PROJECTS = (
 dict(name=":eden coast",
      place={"en": "Geroskipou, Paphos", "ru": "Героскипу, Пафос", "el": "Γεροσκήπου, Πάφος"},
      price={"en": "From €940,000 on the developer page", "ru": "От €940 000 на странице застройщика", "el": "Από €940.000 στη σελίδα του κατασκευαστή"},
      line={"en": "A BBF project. The developer summary lists 16 homes.",
            "ru": "Проект BBF. В сводке застройщика 16 объектов.",
            "el": "Έργο της BBF. Η σύνοψη του κατασκευαστή αναφέρει 16 κατοικίες."}),
 dict(name=":dream tower",
      place={"en": "Agios Tychonas, Limassol", "ru": "Агиос Тихонас, Лимассол", "el": "Άγιος Τύχωνας, Λεμεσός"},
      price={"en": "From €890,000 on the developer page", "ru": "От €890 000 на странице застройщика", "el": "Από €890.000 στη σελίδα του κατασκευαστή"},
      line={"en": "A 27-storey tower in the BBF sales portfolio.",
            "ru": "Башня в 27 этажей в портфеле продаж BBF.",
            "el": "Πύργος 27 ορόφων στο χαρτοφυλάκιο πωλήσεων της BBF."}),
 dict(name="KEAN",
      place={"en": "Limassol", "ru": "Лиμαссол", "el": "Λεμεσός"},
      price={"en": "Price on request", "ru": "Цена по запросу", "el": "Τιμή κατόπιν αιτήματος"},
      line={"en": "A BBF project in Limassol. No sale price is stated here.",
            "ru": "Проект BBF в Лимассоле. Продажная цена здесь не указана.",
            "el": "Έργο της BBF στη Λεμεσό. Εδώ δεν αναφέρεται τιμή πώλησης."}),
)

def other_projects_block(lang):
    copy = OTHER_PROJECT_COPY[lang]
    advice = contact_href(lang, "buy")
    cards = []
    for item in OTHER_PROJECTS:
        cards.append(
            f'<article class="prop-card"><div class="pad"><h2>{e(item["name"])}</h2>'
            f'<p class="prop-meta">{e(item["place"][lang])}</p>'
            f'<p>{e(item["price"][lang])}</p>'
            f'<p>{e(item["line"][lang])}</p>'
            f'<a class="request" href="{e(advice)}">{e(copy["cta"])}</a></div></article>'
        )
    return (
        f'<h2 class="sec">{e(copy["h"])}</h2><p>{e(copy["note"])}</p>'
        f'<div class="prop-grid">{"".join(cards)}</div>'
    )

def real_estate_page(lang):
    u = UI[lang]
    labels = PROPERTY_LABELS[lang]
    missing = [slug for slug in REAL_ESTATE_GUIDES if slug not in GUIDES]
    if missing:
        raise SystemExit("real estate section lists unknown guides: " + ", ".join(missing))
    guides = []
    for slug in REAL_ESTATE_GUIDES:
        meta, _ = load_md(lang, slug)
        guides.append(
            f'<article class="card"><h2>{e(meta["title"])}</h2><p>{e(meta["description"])}</p>'
            f'<a class="more" href="{href(loc(lang, "/guides/"+slug+"/"))}">{e(u["read"])}</a></article>'
        )
    calcs = []
    for slug in CALC_ORDER:
        title, desc = CALCS[slug][lang]
        calcs.append(
            f'<article class="card"><h2>{e(title)}</h2><p>{e(desc)}</p>'
            f'<a class="more" href="{href(loc(lang, "/calculators/"+slug+"/"))}">{e(u["open"])}</a></article>'
        )
    path = loc(lang, "/real-estate/")
    def alt(l):
        return loc(l, "/real-estate/")
    body = f'''<main id="main" class="wrap page"><h1>{e(u["real_estate"])}</h1><p class="lede">{e(u["real_estate_desc"])}</p>
{listings_block(lang)}
{other_projects_block(lang)}
<h2 class="sec">{e(labels["guides"])}</h2><div class="grid">{"".join(guides)}</div>
<h2 class="sec">{e(labels["calcs"])}</h2><div class="grid">{"".join(calcs)}</div>
{lead_card(lang)}</main>'''
    return page_shell(lang, f'{u["real_estate"]} | {SITE}', u["real_estate_desc"], path, alt, body)

def listing_detail(lang, item):
    u = UI[lang]
    labels = PROPERTY_LABELS[lang]
    path = loc(lang, f"/real-estate/{item['id']}/")
    def alt(l, item=item):
        return loc(l, f"/real-estate/{item['id']}/")
    gallery = "".join(
        f'<img src="{href("/" + photo)}" alt="{e(item["title"][lang])}">' for photo in item["photos"]
        if os.path.isfile(os.path.join(ROOT, photo))
    )
    gallery = f'<div class="gallery">{gallery}</div>' if gallery else ""
    facts = "".join(f"<span>{e(bit)}</span>" for bit in listing_facts(lang, item))
    badge = labels["status"][item["status"]]
    body = f'''<main id="main" class="wrap page"><p class="meta"><a href="{href(loc(lang, "/real-estate/"))}">{e(u["real_estate"])}</a></p>
<article><h1>{e(item["title"][lang])}</h1>
<p class="listing-request">{listing_request_link(lang, "#listing-lead")}</p>
<p class="meta"><span class="badge{" sold" if item["status"]=="sold" else ""}">{e(badge)}</span></p>
{gallery}
<p class="listing-facts">{facts}</p>
<div class="body"><p>{e(item["description"][lang])}</p></div>
{listing_calc_links(lang, item)}
{listing_form(lang, item, path)}
{lead_card(lang)}
<p><a href="{href(loc(lang, "/contact/"))}">{e(u["contact"])}</a></p>
</article></main>'''
    return page_shell(lang, f'{item["title"][lang]} | {SITE}', item["description"][lang], path, alt, body)

def sitemap():
    paths = ["/"]
    for slug in ("about", "contact", "privacy", "cookies", "terms", "affiliate-disclosure", "property-consultation", "services", "buying-checklist", "calculators", "guides"):
        paths.append(f"/{slug}/")
    for slug in CALC_ORDER:
        paths.append(f"/calculators/{slug}/")
    for slug in GUIDE_ORDER:
        paths.append(f"/guides/{slug}/")
    urls = [loc(lang, p) for lang in LANGS for p in paths]
    for lang in LANGS:
        urls.append(loc(lang, "/real-estate/"))
        for item in published_listings():
            urls.append(loc(lang, f"/real-estate/{item['id']}/"))
        urls.append(loc(lang, "/links/"))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        # Atom and any other XML feed stay on the site, but they are not pages.
        if u.endswith(".xml"):
            continue
        lines.append(f"<url><loc>{e(absu(u))}</loc><lastmod>{page_lastmod(u)}</lastmod></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"

def atom_feed(lang):
    """One Atom feed of the guides that have their own text in this language."""
    u = UI[lang]
    path = loc(lang, "/feed.xml")
    updated = page_lastmod(path)
    entries = []
    for slug in GUIDE_ORDER:
        if lang in GUIDES[slug]["missing"]:
            continue
        meta = GUIDES[slug]["text"][lang]
        gpath = loc(lang, f"/guides/{slug}/")
        when = page_lastmod(gpath)
        entries.append(
            "<entry>"
            f"<title>{e(meta['title'])}</title>"
            f'<link href="{e(absu(gpath))}"/>'
            f"<id>{e(absu(gpath))}</id>"
            f"<updated>{when}T00:00:00Z</updated>"
            f"<summary>{e(meta['description'])}</summary>"
            "</entry>"
        )
    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f"<title>{e(u['feed'])}</title>\n"
        f'<link href="{e(absu(path))}" rel="self"/>\n'
        f'<link href="{e(absu(loc(lang, "/guides/")))}"/>\n'
        f"<updated>{updated}T00:00:00Z</updated>\n"
        f"<id>{e(absu(path))}</id>\n"
        f"<author><name>{e(SITE)}</name></author>\n"
        f"{body}\n"
        "</feed>\n"
    )

def main():
    # Headlines are fetched once. A timeout or any other failure leaves the
    # static CyNews24 link in place and does not stop the build.
    refresh_cynews()
    for slug, guide in GUIDES.items():
        src = _clean((guide.get("image") or {}).get("src"))
        if src and not os.path.isfile(os.path.join(HERE, "static", "guides", src)):
            raise SystemExit(f"missing guide image for {slug}: {src}")
    # admin/ is the CMS and is not generated. A rebuild must not delete it.
    keep = {"source", ".git", "admin", "data", "docs", "images"}
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
    js_dir = os.path.join(OUT, "assets", "js")
    os.makedirs(js_dir, exist_ok=True)
    shutil.copy(AFFILIATES_PATH, os.path.join(js_dir, "affiliates.js"))
    icons_dir = os.path.join(HERE, "static", "icons")
    for fn in os.listdir(icons_dir):
        shutil.copy(os.path.join(icons_dir, fn), os.path.join(OUT, fn))
    og_src = os.path.join(HERE, "static", "og.png")
    if not os.path.isfile(og_src):
        raise SystemExit(f"missing {og_src}")
    shutil.copy(og_src, os.path.join(OUT, "assets", "og.png"))
    guide_img = os.path.join(HERE, "static", "guides")
    if os.path.isdir(guide_img):
        dest = os.path.join(OUT, "assets", "guides")
        os.makedirs(dest, exist_ok=True)
        for name in os.listdir(guide_img):
            if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                shutil.copy(os.path.join(guide_img, name), os.path.join(dest, name))
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
        for slug in PAGE_ORDER:
            w(loc(lang, f"/{slug}/") + "index.html", static_page(lang, slug))
        w(loc(lang, "/contact/") + "index.html", contact(lang))
        w(loc(lang, "/contact/thanks/") + "index.html", thanks(lang))
        w(loc(lang, "/property-consultation/") + "index.html", consultation_page(lang))
        w(loc(lang, "/property-consultation/thanks/") + "index.html", consultation_thanks(lang))
        w(loc(lang, "/services/") + "index.html", services_page(lang))
        w(loc(lang, "/buying-checklist/") + "index.html", checklist_gate_page(lang))
        w(loc(lang, "/buying-checklist/2026/") + "index.html", checklist_page(lang))
        w(loc(lang, "/real-estate/") + "index.html", real_estate_page(lang))
        w(loc(lang, "/real-estate/thanks/") + "index.html", listing_thanks(lang))
        for item in published_listings():
            w(loc(lang, f"/real-estate/{item['id']}/") + "index.html", listing_detail(lang, item))
        w(loc(lang, "/links/") + "index.html", links_page(lang))
        w(loc(lang, "/feed.xml"), atom_feed(lang))
    w("/sitemap.xml", sitemap())
    w(f"/{INDEXNOW_KEY}.txt", INDEXNOW_KEY + "\n")
    w("/robots.txt", (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /feed.xml\n"
        "Disallow: /ru/feed.xml\n"
        "Disallow: /el/feed.xml\n"
        "\n"
        f"Sitemap: {BASE}/sitemap.xml\n"
    ))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    # GitHub Pages custom domain. Rewritten on every build so a rebuild cannot drop it.
    w("/CNAME", "mycytax.com\n")
    # Google Search Console verification. Rewritten on every build so a rebuild cannot drop it.
    w("/google62249645dc64d12b.html", "google-site-verification: google62249645dc64d12b.html\n")
    w("/ads.txt", ADS_TXT)
    short = [x for x in words if x[2] < 800]
    print("built", BASE)
    print("untranslated", {
        "guides": {l: [s for s in GUIDE_ORDER if l in GUIDES[s]["missing"]] for l in ("en", "el")},
        "pages": {l: [s for s in PAGE_ORDER if l in PAGES[s]["missing"]] for l in ("en", "el")},
    })
    for lang, slug, n in words:
        flag = " SHORT" if n < 800 or n > 1600 else ""
        print(f"  {lang} {slug} {n}{flag}")
    if short:
        # A short new guide must still publish. The old generator stopped the build;
        # that would leave the owner's CMS save on main without updating the site.
        print("warning: guides under 800 words:", ", ".join(f"{a}/{b}={c}" for a, b, c in short))

if __name__ == "__main__":
    main()
