# -*- coding: utf-8 -*-
"""MyCyTax static generator. English, Russian and Greek.

    BASE=https://mycytax.com python3 source/build.py

The custom domain is mycytax.com. BASE is the origin with no trailing slash.
The path inside BASE becomes the link prefix. No trailing slash.
"""
import datetime, html, json, os, re, shutil
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
PUBLISHER = "Anna"
CYNEWS = "https://cynews24.net/"
TG_RU = "https://t.me/mycytax"
TG_EN = "https://t.me/mycytaxen"
LANGS = ["en", "ru", "el"]
# Editable copy lives in source/content/ (one JSON file per guide or page) and is
# loaded below. Calculator logic and the chrome around it stay in this file.
CONTENT = os.path.join(HERE, "content")
GUIDE_DIR = os.path.join(CONTENT, "guides")
PAGE_DIR = os.path.join(CONTENT, "pages")
PAGE_ORDER = ("about", "privacy", "cookies", "terms")

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
    tg="Follow us on Telegram",
    tg_other="Russian channel",
    tg_short="Telegram",
    home_h="Cyprus property and tax calculators",
    home_desc="Transfer fees, VAT, capital gains, rental income and a mortgage payment, plus practical guides.",
    home_intro="Work out the Land Registry fee, VAT, stamp duty, capital gains tax, rental tax and a mortgage payment. Every rate on MyCyTax is tied to a source. The publisher is Anna, in Cyprus.",
    list_calcs="Cyprus property calculators: transfer fees, stamp duty, VAT, capital gains, rental income and mortgage payments.",
    list_guides="Practical guides to buying, selling, tax residency, non-dom status, title deeds and renting property in Cyprus.",
    contact_t="Contact", contact_d="Write to MyCyTax about buying or selling. The form goes to info@mycytax.com.",
    contact_i="The publisher is Anna. Email info@mycytax.com, or use the form. The first message to this address asks FormSubmit to send a confirmation email. Until that link is opened, the form will not deliver. We reply within 24 hours.",
    thanks_t="Thank you", thanks_d="Your message has been sent.",
    thanks_i="Thank you. If this address is already confirmed with FormSubmit, we will reply within 24 hours. If this was the first message, Anna still needs to open the confirmation email before it is delivered."),
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
    tg="Подписывайтесь на наш Telegram-канал",
    tg_other="Английский канал",
    tg_short="Telegram",
    home_h="Калькуляторы недвижимости и налогов Кипра",
    home_desc="Сборы кадастра, НДС, прирост капитала, аренда и ипотечный платёж, плюс практические справочники.",
    home_intro="Посчитайте сбор Земельного кадастра, НДС, гербовый сбор, налог на прирост капитала, налог с аренды и ипотечный платёж. Каждая ставка на MyCyTax привязана к источнику. Издатель — Анна, Кипр.",
    list_calcs="Калькуляторы по недвижимости Кипра: сборы кадастра, гербовый сбор, НДС, прирост капитала, аренда и ипотека.",
    list_guides="Практические справочники о покупке, продаже, налоговом резидентстве, статусе non-dom, титулах и аренде на Кипре.",
    contact_t="Контакты", contact_d="Напишите MyCyTax о покупке или продаже. Форма уходит на info@mycytax.com.",
    contact_i="Издатель — Анна. Пишите на info@mycytax.com или через форму. Первое сообщение на этот адрес FormSubmit подтверждает письмом. Пока ссылка не открыта, форма не доставляет заявки. Ответим в течение 24 часов.",
    thanks_t="Спасибо", thanks_d="Сообщение отправлено.",
    thanks_i="Спасибо. Если адрес уже подтверждён в FormSubmit, ответим в течение 24 часов. Если это первое сообщение, Анне ещё нужно открыть письмо подтверждения, прежде чем оно будет доставлено."),
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
    tg="Ακολουθήστε μας στο Telegram",
    tg_other="Ρωσικό κανάλι",
    tg_short="Telegram",
    home_h="Υπολογιστές ακινήτων και φόρων Κύπρου",
    home_desc="Τέλη μεταβίβασης, ΦΠΑ, κεφαλαιουχικά κέρδη, ενοίκιο και δόση δανείου, μαζί με πρακτικούς οδηγούς.",
    home_intro="Υπολογίστε το τέλος του Κτηματολογίου, τον ΦΠΑ, το χαρτόσημο, τον φόρο κεφαλαιουχικών κερδών, τον φόρο ενοικίου και τη δόση στεγαστικού. Κάθε συντελεστής στο MyCyTax δένεται με πηγή. Εκδότρια είναι η Άννα, στην Κύπρο.",
    list_calcs="Υπολογιστές ακινήτων Κύπρου: τέλη μεταβίβασης, χαρτόσημο, ΦΠΑ, κεφαλαιουχικά κέρδη, ενοίκιο και δόση δανείου.",
    list_guides="Πρακτικοί οδηγοί για αγορά, πώληση, φορολογική κατοικία, καθεστώς non-dom, τίτλους και ενοικίαση στην Κύπρο.",
    contact_t="Επικοινωνία", contact_d="Γράψτε στο MyCyTax για αγορά ή πώληση. Η φόρμα πηγαίνει στο info@mycytax.com.",
    contact_i="Εκδότρια είναι η Άννα. Στείλτε email στο info@mycytax.com ή χρησιμοποιήστε τη φόρμα. Το πρώτο μήνυμα σε αυτή τη διεύθυνση το επιβεβαιώνει το FormSubmit με email. Μέχρι να ανοίξει ο σύνδεσμος, η φόρμα δεν παραδίδει αιτήματα. Απαντάμε μέσα σε 24 ώρες.",
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
        slug = slugify(_clean(d.get("slug")) or stem) or slugify(ru.get("title", ""))
        if not slug:
            raise SystemExit(f"{path}: cannot make a page address (slug)")
        if not _guide_ok(ru):
            raise SystemExit(f"{path}: Russian title, description and text are required")
        g = {"slug": slug, "seq": _seq(d.get("seq")), "missing": set(), "text": {}}
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
form.lead{display:grid;gap:12px;max-width:720px}
.choices{border:1px solid var(--line);border-radius:10px;padding:10px 12px;display:flex;flex-wrap:wrap;gap:8px 16px}
.choices legend{font-weight:700;padding:0 6px}
.cta{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--copper);border-radius:16px;padding:18px 18px 16px;margin:22px 0;max-width:720px}
.cta h2{font-family:Georgia,Palatino,serif;font-size:26px;line-height:1.2;margin:0 0 8px}
.cta p{margin:0 0 14px}
.cta-btns{display:flex;flex-wrap:wrap;gap:10px}
a.go{display:inline-flex;align-items:center;justify-content:center;text-align:center;text-decoration:none;line-height:1.3}
.cta-btns a{flex:1 1 240px}
a.go.alt{background:#fff;color:var(--pine);border:2px solid var(--pine)}
a.go.alt:hover{background:var(--pine);color:#fff}
p.consult{margin:14px 0 0;font-weight:700}
@media(max-width:600px){.cta-btns{flex-direction:column}.cta-btns a{flex-basis:auto}}
a.tg-nav{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:999px;background:#229ED9;color:#fff;flex:none}
a.tg-nav:hover{background:#1b86b8;color:#fff}
.tg-mark{width:18px;height:18px;display:block;flex:none}
footer a.tg-foot{display:inline-flex;align-items:center;gap:6px}
footer a.tg-foot .tg-mark{width:16px;height:16px}
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
@media(max-width:800px){.grid{grid-template-columns:1fr}.bar{align-items:flex-start;flex-direction:column}}
'''

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
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{absu(path)}">
{chr(10).join(alts)}
<meta name="robots" content="{robots}">
<meta property="og:site_name" content="{e(u["name"])}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{absu(path)}"><meta property="og:type" content="website">
<meta name="theme-color" content="#1e3d34">
<link rel="stylesheet" href="{href("/assets/style.css")}">{ld}{extra}{ADSENSE}</head>'''

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
{tg_icon_link(lang)}<span class="langs">{langs}</span></nav></div></header>'''

def footer(lang):
    u = UI[lang]
    links = [
        (loc(lang, "/about/"), u["about"]), (loc(lang, "/contact/"), u["contact"]),
        (loc(lang, "/privacy/"), u["privacy"]), (loc(lang, "/cookies/"), u["cookies"]),
        (loc(lang, "/terms/"), u["terms"]),
    ]
    nav = "".join(f'<a href="{href(path)}">{e(name)}</a>' for path, name in links)
    return f'''<footer><div class="wrap"><nav class="cols">{nav}<a href="{CYNEWS}">{e(u["cynews"])}</a>{tg_footer_link(lang)}</nav>
<p>{e(DISCLAIMER[lang])}</p><p>© 2026 {SITE}. {e(PUBLISHER)}, Cyprus. <a href="mailto:{EMAIL}">{EMAIL}</a></p></div></footer></body></html>'''

def ad(label):
    return f'<div class="adslot" data-ad="{e(label)}" aria-label="{e(UI["en"]["ad"])}"><!-- AdSense slot "{e(label)}": leave empty until a unit is approved. --></div>'

def org():
    return {"@type":"Organization","name":SITE,"url":absu("/"),"email":EMAIL,
            "address":{"@type":"PostalAddress","addressCountry":"CY"},
            "founder":{"@type":"Person","name":PUBLISHER},
            "sameAs":[CYNEWS, TG_RU, TG_EN]}

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

def page_shell(lang, title, desc, path, alt, body, jsonld=None, active_path=None, robots="index,follow,max-image-preview:large"):
    def path_for(l, alt=alt):
        return alt(l)
    return head(lang, title, desc, path, alt, jsonld, robots=robots) + header(lang, path_for) + body + footer(lang)

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
    return f'''<form class="lead" id="leadform" action="https://formsubmit.co/{EMAIL}" method="POST">
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
    ld = [{"@context":"https://schema.org","@type":"WebSite","name":SITE,"url":absu(alt(lang)),"inLanguage":lang,"publisher":org()},
          {"@context":"https://schema.org",**org()}]
    body = f'''<main id="main"><div class="wrap hero"><h1>{e(title)}</h1><p class="lede">{e(intro)}</p>
<p class="banner">{e(DISCLAIMER[lang])}</p>{ad("home-top")}</div>
<div class="wrap"><h2 class="sec">{e(u["calcs"])}</h2><div class="grid">{"".join(cards)}</div>
<h2 class="sec">{e(u["guides"])}</h2><div class="grid">{"".join(guides)}</div>
{lead_card(lang)}{ad("home-bottom")}</div></main>'''
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
<div id="calc" data-consult="{contact_href(lang,"buy")}" data-calc="{e({"transfer-fees":"transfer","stamp-duty":"stamp","vat":"vat","capital-gains":"cgt","rental-yield":"rental","mortgage":"mortgage"}[slug])}"></div>
{lead_card(lang)}
<div class="body"><h2>{e(u["sources"])}</h2><p>{note}</p></div>{ad("calc-bottom")}
{telegram_card(lang)}</main>
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
         "author":{"@type":"Organization","name":SITE,"url":absu("/"),"sameAs":[TG_RU, TG_EN]},
         "publisher":{"@type":"Organization","name":SITE,"url":absu("/"),"sameAs":[TG_RU, TG_EN]}},
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
{lead_card(lang)}
{ad("guide-bottom")}
{telegram_card(lang)}</article></main>'''
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
    # admin/ is the CMS and is not generated. A rebuild must not delete it.
    keep = {"source", ".git", "admin"}
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
        for slug in PAGE_ORDER:
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
