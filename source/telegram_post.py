# -*- coding: utf-8 -*-
"""Post each new MyCyTax guide once to the Telegram channel @mycytax.

The message is the Russian title, the short description, and a link to the
Russian page (https://mycytax.com/ru/guides/<slug>/). Guides have no images,
so this is a sendMessage text post with the link preview left on. If the
build has no Russian page for a guide, the link uses the default-language
URL (https://mycytax.com/guides/<slug>/) instead.

Slugs already handled are stored in source/content/telegram-posted.json.
The file is pre-seeded with every guide that existed when posting was added,
and an entry is never removed, so edits do not post again.

TELEGRAM_BOT_TOKEN is the repository secret. When it is missing this script
logs a notice, leaves the state file untouched and exits 0. It never prints
the token. DRY_RUN=1 (or --dry-run) prints the messages and does not call
Telegram or write state.

The channel is TELEGRAM_CHANNEL, or @mycytax when that env var is unset.
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DEFAULT_GUIDES = os.path.join(ROOT, "source", "content", "guides")
DEFAULT_STATE = os.path.join(ROOT, "source", "content", "telegram-posted.json")
DEFAULT_BASE = "https://mycytax.com"
DEFAULT_CHANNEL = "@mycytax"
LINK_TEXT = "Читать справочник"
HASHTAGS = ("#налогиКипр", "#недвижимостьКипр")
TEXT_LIMIT = 4096
SEEDED_AT = "2026-11-13T00:00:00Z"
NOTE = (
    "Guides already handled for Telegram (@mycytax). "
    "An entry means do not post again, including after edits."
)
# Keep in sync with source/build.py so a missing slug field still matches the site.
_TR = dict(zip("абвгдеёзийклмнопрстуфхыэ", "abvgdeezijklmnoprstufhye")) | {
    "ж": "zh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ю": "yu", "я": "ya", "ъ": "", "ь": "",
}
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
USER_AGENT = "mycytax-telegram-poster"
COMMIT_MESSAGE = "Telegram: отмечены отправленные справочники [skip ci]"


def slugify(value) -> str:
    text = "".join(_TR.get(ch, ch) for ch in str(value).lower())
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text)).strip("-")[:70].strip("-")


def _clean(value) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return ""
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def stamp(moment: datetime.datetime) -> str:
    return moment.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def escape_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_attr(value: str) -> str:
    return escape_text(value).replace('"', "&quot;")


def resolve_channel(value: str | None = None) -> str:
    raw = (value if value is not None else os.environ.get("TELEGRAM_CHANNEL", "")).strip()
    channel = raw or DEFAULT_CHANNEL
    if any(ch.isspace() for ch in channel) or "/" in channel:
        raise SystemExit(f"invalid TELEGRAM_CHANNEL {channel!r}")
    if not channel.startswith("@"):
        channel = "@" + channel
    return channel


def hashtag_line() -> str:
    return " ".join(HASHTAGS)


def russian_page_exists(root: str, slug: str) -> bool:
    """The generator writes Russian guides to /ru/guides/<slug>/index.html."""
    return os.path.isfile(os.path.join(root, "ru", "guides", slug, "index.html"))


def page_url(base: str, slug: str, *, russian: bool) -> str:
    """Russian page when the build has one, otherwise the default-language URL."""
    path = f"/ru/guides/{slug}/" if russian else f"/guides/{slug}/"
    return base.rstrip("/") + path


def clip(text: str, room: int) -> str:
    """Shorten text to at most `room` characters, keeping a word boundary when it fits."""
    if room <= 0 or not text:
        return ""
    if len(text) <= room:
        return text
    if room == 1:
        return "…"
    budget = room - 1
    cut = text[:budget].rstrip()
    space = cut.rfind(" ")
    if space >= budget // 2:
        cut = cut[:space].rstrip()
    if not cut:
        cut = text[:budget]
    return cut + "…"


def visible_length(message_html: str) -> int:
    text = re.sub(r"<[^>]+>", "", message_html)
    return len(html.unescape(text))


def render_message(title: str, description: str, url: str, link_text: str, tags: str) -> str:
    """HTML text post. Raw and visible length both stay within Telegram's 4096."""
    title = " ".join((title or "").split())
    description = " ".join((description or "").split())
    link_text = " ".join((link_text or "").split())
    tags = " ".join((tags or "").split())

    def pack(title_text: str, desc_text: str) -> str:
        blocks = []
        if title_text:
            blocks.append(f"<b>{escape_text(title_text)}</b>")
        if desc_text:
            blocks.append(escape_text(desc_text))
        blocks.append(f'<a href="{escape_attr(url)}">{escape_text(link_text)}</a>')
        if tags:
            blocks.append(escape_text(tags))
        return "\n\n".join(blocks)

    def fits(title_text: str, desc_text: str) -> bool:
        message = pack(title_text, desc_text)
        return len(message) <= TEXT_LIMIT and visible_length(message) <= TEXT_LIMIT

    if not fits(title, description):
        if fits(title, ""):
            best = ""
            lo, hi = 0, len(description)
            while lo <= hi:
                mid = (lo + hi) // 2
                candidate = clip(description, mid) if mid else ""
                if fits(title, candidate):
                    best = candidate
                    lo = mid + 1
                else:
                    hi = mid - 1
            description = best
        else:
            description = ""
            best = ""
            lo, hi = 0, len(title)
            while lo <= hi:
                mid = (lo + hi) // 2
                candidate = clip(title, mid) if mid else ""
                if candidate and fits(candidate, ""):
                    best = candidate
                    lo = mid + 1
                else:
                    hi = mid - 1
            title = best
    if not fits(title, description):
        raise RuntimeError("Telegram message still exceeds 4096 characters")
    return pack(title, description)


@dataclass(frozen=True)
class Guide:
    slug: str
    title: str
    description: str


@dataclass(frozen=True)
class Action:
    kind: str  # send, skip
    guide: Guide


def load_guide(path: str) -> Guide:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: guide must be a JSON object")
    stem = os.path.splitext(os.path.basename(path))[0]
    ru = data.get("ru") if isinstance(data.get("ru"), dict) else {}
    slug = slugify(_clean(data.get("slug")) or stem) or slugify(ru.get("title", ""))
    if not slug or not SLUG_RE.fullmatch(slug):
        raise SystemExit(f"{path}: cannot make a page address (slug)")
    title = _clean(ru.get("title"))
    description = _clean(ru.get("description"))
    if not title or not description:
        raise SystemExit(f"{path}: Russian title and description are required")
    return Guide(slug, title, description)


def load_guides(directory: str) -> list[Guide]:
    if not os.path.isdir(directory):
        raise SystemExit(f"Guides directory not found: {directory}")
    names = sorted(name for name in os.listdir(directory) if name.endswith(".json"))
    guides = [load_guide(os.path.join(directory, name)) for name in names]
    slugs = [guide.slug for guide in guides]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate guide slugs: {duplicates}")
    return guides


def empty_state() -> dict:
    return {"note": NOTE, "posted": {}}


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        raise SystemExit(f"{path} is missing; refusing to post without the dedupe file")
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("posted"), dict):
        raise SystemExit(f"{path}: expected an object with a posted map")
    for slug, record in data["posted"].items():
        if not isinstance(slug, str) or not isinstance(record, dict):
            raise SystemExit(f"{path}: {slug} must be an object")
        if not isinstance(record.get("status"), str) or not record["status"]:
            raise SystemExit(f"{path}: {slug} must be an object with a status")
        if not isinstance(record.get("at"), str) or not record["at"]:
            raise SystemExit(f"{path}: {slug} must include at")
    if "note" not in data:
        data["note"] = NOTE
    return data


def serialize(state: dict) -> str:
    return json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def save_state(path: str, state: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        handle.write(serialize(state))
    os.replace(temporary, path)


def is_marked(state: dict, slug: str) -> bool:
    entry = state.get("posted", {}).get(slug)
    return isinstance(entry, dict)


def mark(state: dict, slug: str, status: str, moment: datetime.datetime) -> None:
    posted = state.setdefault("posted", {})
    if slug not in posted:
        posted[slug] = {"at": stamp(moment), "status": status}


def initial_seed(guides: list[Guide]) -> dict:
    """Mark every current guide handled, so the first real run posts nothing old."""
    posted = {}
    for guide in sorted(guides, key=lambda item: item.slug):
        posted[guide.slug] = {"at": SEEDED_AT, "status": "seeded"}
    return {"note": NOTE, "posted": posted}


def plan(guides: list[Guide], state: dict) -> list[Action]:
    actions = []
    for guide in sorted(guides, key=lambda item: item.slug):
        if is_marked(state, guide.slug):
            continue
        actions.append(Action("send", guide))
    return actions


def build_post(guide: Guide, base: str, root: str, channel: str) -> dict:
    russian = russian_page_exists(root, guide.slug)
    url = page_url(base, guide.slug, russian=russian)
    text = render_message(guide.title, guide.description, url, LINK_TEXT, hashtag_line())
    return {
        "method": "sendMessage",
        "chat_id": channel,
        "parse_mode": "HTML",
        "text": text,
        "link_preview_options": {"is_disabled": False, "url": url},
        "url": url,
        "russian": russian,
    }


def is_page_ready(body: bytes, slug: str, title: str, *, russian: bool, base: str = DEFAULT_BASE) -> bool:
    """True when this body is the guide page we are about to link.

    The default-language path is a suffix of the Russian path (`/guides/`
    sits inside `/ru/guides/`), so the match is the absolute URL or a quoted
    href of the exact path. A Russian page must also show its Russian title
    and must not be noindex.
    """
    text = body.decode("utf-8", errors="replace")
    path = f"/ru/guides/{slug}/" if russian else f"/guides/{slug}/"
    origin = base.rstrip("/")
    markers = (f"{origin}{path}", f'href="{path}"', f"href='{path}'")
    if not any(marker in text for marker in markers):
        return False
    if 'content="noindex' in text or "content='noindex" in text:
        return False
    if russian and title not in html.unescape(text):
        return False
    return True


def http_get(url: str, timeout: float = 20) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        return exc.code, body
    except Exception:
        return 0, b""


def http_post(url: str, data: bytes, timeout: float = 30) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        return exc.code, body
    except Exception as exc:
        return 0, str(exc).encode("utf-8", errors="replace")


def redact(text: str, token: str) -> str:
    if token and token in text:
        text = text.replace(token, "***")
    return text


def parse_telegram(status: int, raw: bytes) -> tuple[bool, str, int | None]:
    try:
        data = json.loads(raw.decode("utf-8", errors="replace") or "{}")
    except json.JSONDecodeError:
        return False, f"HTTP {status}", None
    if data.get("ok"):
        message_id = (data.get("result") or {}).get("message_id")
        return True, "" if message_id is None else str(message_id), None
    retry = (data.get("parameters") or {}).get("retry_after")
    try:
        retry_after = int(retry) if retry is not None else None
    except (TypeError, ValueError):
        retry_after = None
    description = data.get("description") or f"HTTP {status}"
    return False, str(description), retry_after


def send_telegram(token: str, payload: dict, *, post, sleep, attempts: int = 4) -> tuple[bool, str]:
    method = payload["method"]
    body = {key: value for key, value in payload.items() if key not in {"method", "url", "russian"}}
    endpoint = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last = "no response"
    for attempt in range(attempts):
        try:
            status, raw = post(endpoint, data)
        except Exception as exc:
            last = redact(str(exc), token)
            if attempt == attempts - 1:
                return False, last
            sleep(2)
            continue
        ok, info, retry_after = parse_telegram(status, raw)
        if ok:
            return True, info
        last = redact(info, token)
        transient = status in {0, 429, 500, 502, 503, 504}
        if not transient or attempt == attempts - 1:
            return False, last
        sleep(retry_after if retry_after is not None else 2)
    return False, last


def wait_until_live(guide: Guide, base: str, root: str, channel: str, *, get, sleep, monotonic, deadline, log) -> bool:
    post = build_post(guide, base, root, channel)
    waits = (15, 30, 45, 60)
    attempt = 0
    while True:
        status, body = get(post["url"])
        if status == 200 and is_page_ready(body, guide.slug, guide.title, russian=post["russian"], base=base):
            log(f"live {post['url']}")
            return True
        log(f"waiting for {post['url']} (HTTP {status})")
        remaining = deadline - monotonic()
        if remaining <= 0:
            return False
        step = min(waits[min(attempt, len(waits) - 1)], remaining)
        attempt += 1
        log(f"retrying in {int(step)}s")
        sleep(step)


def _git(repo: str, args: list[str], env: dict, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=repo, env=env, text=True, capture_output=True)
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        shown = args[1:] if args and args[0] == "git" else args
        raise SystemExit(f"git {' '.join(shown)} failed: {detail}")
    return result


def commit_and_push(repo: str, path: str) -> None:
    """Commit only the state file and push it to main. Retries if main moved."""
    env = os.environ.copy()
    env["GIT_MERGE_AUTOEDIT"] = "no"
    env["GIT_TERMINAL_PROMPT"] = "0"
    _git(repo, ["git", "config", "user.name", "mycytax-telegram[bot]"], env)
    _git(repo, ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], env)
    _git(repo, ["git", "config", "commit.gpgsign", "false"], env)
    _git(repo, ["git", "add", "--", path], env)
    diff = _git(repo, ["git", "diff", "--cached", "--quiet"], env, check=False)
    if diff.returncode == 0:
        print("State file unchanged; not committing.", flush=True)
        return
    if diff.returncode != 1:
        raise SystemExit((diff.stderr or "git diff failed").strip())
    _git(repo, ["git", "commit", "-q", "-m", COMMIT_MESSAGE], env)
    for attempt in range(1, 4):
        push = _git(repo, ["git", "push", "origin", "HEAD:main"], env, check=False)
        if push.returncode == 0:
            print("Pushed Telegram state to main.", flush=True)
            return
        print(f"Push failed ({attempt}/3); rebasing onto origin/main.", flush=True)
        detail = redact((push.stderr or push.stdout or "").strip(), os.environ.get("TELEGRAM_BOT_TOKEN", ""))
        print(detail, flush=True)
        pull = _git(repo, ["git", "pull", "--rebase", "-q", "origin", "main"], env, check=False)
        if pull.returncode != 0:
            _git(repo, ["git", "rebase", "--abort"], env, check=False)
            raise SystemExit((pull.stderr or pull.stdout or "could not rebase telegram state").strip())
    raise SystemExit("could not push telegram state")


def _dry_line(action: Action, base: str, root: str, channel: str, get) -> str:
    guide = action.guide
    post = build_post(guide, base, root, channel)
    status, body = get(post["url"])
    live = status == 200 and is_page_ready(body, guide.slug, guide.title, russian=post["russian"], base=base)
    where = "ru" if post["russian"] else "default"
    lines = [
        f"DRY RUN {post['chat_id']} sendMessage slug={guide.slug} page={where} live={'yes' if live else 'no'}",
        f"link_preview: {post['link_preview_options']['url']}",
        "text:",
        post["text"],
        "---",
    ]
    return "\n".join(lines)


def execute(
    guides: list[Guide],
    state: dict,
    *,
    now: datetime.datetime,
    token: str,
    dry_run: bool,
    base: str,
    root: str,
    channel: str,
    max_wait: float,
    http_get,
    sleep,
    monotonic,
    send,
    log,
    save,
) -> int:
    actions = plan(guides, state)
    log(
        "TELEGRAM_BOT_TOKEN is "
        + ("configured" if token else "not set")
        + " (value not printed)."
    )
    log(f"Channel {channel}.")
    if dry_run:
        if not actions:
            log("DRY RUN nothing new to post.")
        for action in actions:
            log(_dry_line(action, base, root, channel, http_get))
        log(
            "DRY RUN summary: "
            f"would send {sum(item.kind == 'send' for item in actions)}. "
            "Nothing was sent and the state file was not changed."
        )
        return 0
    if not token:
        pending = sum(item.kind == "send" for item in actions)
        log(
            "::notice title=Telegram::TELEGRAM_BOT_TOKEN is not set, so nothing was posted "
            f"({pending} post(s) pending). The state file was not changed."
        )
        return 0
    if not actions:
        log("Nothing new to post.")
        return 0

    deadline = monotonic() + max_wait
    failures = []
    sent = 0
    dirty = False

    def flush() -> bool:
        nonlocal dirty
        if not dirty:
            return True
        try:
            save()
        except SystemExit as exc:
            log(f"::error title=Telegram::{exc}")
            return False
        dirty = False
        return True

    for action in actions:
        guide = action.guide
        if not flush():
            return 1
        if not wait_until_live(
            guide, base, root, channel,
            get=http_get, sleep=sleep, monotonic=monotonic, deadline=deadline, log=log,
        ):
            failures.append(f"{guide.slug}: page was not HTTP 200 in time")
            log(f"::error title=Telegram::{failures[-1]}")
            continue
        post = build_post(guide, base, root, channel)
        ok, info = send(post)
        if not ok:
            failures.append(f"{guide.slug}: {info}")
            log(f"::error title=Telegram::{failures[-1]}")
            continue
        mark(state, guide.slug, "sent", now)
        dirty = True
        sent += 1
        log(f"sent {post['chat_id']} sendMessage slug={guide.slug} message_id={info or '-'}")
        if not flush():
            return 1
        sleep(1)
    if not flush():
        return 1
    log(f"Telegram: sent {sent}, failed {len(failures)}")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Post new MyCyTax guides to Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="print messages without sending or writing state")
    parser.add_argument("--guides", default=DEFAULT_GUIDES)
    parser.add_argument("--state", default=DEFAULT_STATE)
    parser.add_argument("--root", default=ROOT)
    parser.add_argument("--base", default=os.environ.get("BASE", DEFAULT_BASE))
    parser.add_argument("--channel", default="")
    parser.add_argument("--max-wait", type=float, default=float(os.environ.get("TELEGRAM_MAX_WAIT", "360")))
    args = parser.parse_args(argv)
    dry_run = args.dry_run or env_flag("DRY_RUN")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    channel = resolve_channel(args.channel or None)
    guides = load_guides(args.guides)
    state = load_state(args.state)
    base = args.base.rstrip("/")
    push = env_flag("PUSH_STATE") and not dry_run and bool(token)

    def save() -> None:
        save_state(args.state, state)
        if push:
            commit_and_push(args.root, args.state)

    def send(payload: dict) -> tuple[bool, str]:
        return send_telegram(token, payload, post=http_post, sleep=time.sleep)

    return execute(
        guides,
        state,
        now=utcnow(),
        token=token,
        dry_run=dry_run,
        base=base,
        root=args.root,
        channel=channel,
        max_wait=args.max_wait,
        http_get=http_get,
        sleep=time.sleep,
        monotonic=time.monotonic,
        send=send,
        log=lambda message: print(message, flush=True),
        save=save,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as exc:
        if isinstance(exc.code, int):
            raise
        print(exc.code or exc, file=sys.stderr)
        sys.exit(1)
