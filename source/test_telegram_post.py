# -*- coding: utf-8 -*-
"""Unit tests for the Telegram poster. No network and no messages to the channel."""
from __future__ import annotations

import contextlib
import datetime
import html
import io
import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

import build
import telegram_post as tg

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDES = os.path.join(HERE, "content", "guides")
STATE = os.path.join(HERE, "content", "telegram-posted.json")
ROOT = os.path.normpath(os.path.join(HERE, ".."))

# Guides that already existed when posting was added. New files are not listed,
# so publishing a guide does not fail the build for lack of a state entry.
ORIGINAL = [
    "buying-as-a-foreigner",
    "non-dom",
    "off-plan",
    "renting-out",
    "residence-permit",
    "selling-and-taxes",
    "tax-residency",
    "taxes-overview",
    "title-deeds",
    "total-cost",
]


def page(title: str, slug: str, *, russian: bool = True, noindex: bool = False) -> bytes:
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    path = f"/ru/guides/{slug}/" if russian else f"/guides/{slug}/"
    lang = "ru" if russian else "en"
    escaped = html.escape(title, quote=True)
    return (
        f'<!doctype html><html lang="{lang}"><head><title>{escaped}</title>'
        f'<meta name="robots" content="{robots}">'
        f'<link rel="canonical" href="https://mycytax.com{path}">'
        f"</head><body><h1>{escaped}</h1></body></html>"
    ).encode("utf-8")


class Clock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def guide(slug="new-guide", title="Новый справочник", description="Короткое описание"):
    return tg.Guide(slug, title, description)


def write_ru_page(root: str, slug: str) -> None:
    path = os.path.join(root, "ru", "guides", slug)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "index.html"), "w", encoding="utf-8") as handle:
        handle.write("page")


class MessageTests(unittest.TestCase):
    def test_html_escape_structure_and_preview(self):
        text = tg.render_message(
            "Том & Джерри <закон>",
            'Описание с "кавычками" и <тегом>',
            "https://mycytax.com/ru/guides/slug/",
            "Читать справочник",
            "#налогиКипр #недвижимостьКипр",
        )
        self.assertIn("<b>Том &amp; Джерри &lt;закон&gt;</b>", text)
        self.assertIn('Описание с "кавычками" и &lt;тегом&gt;', text)
        self.assertIn('<a href="https://mycytax.com/ru/guides/slug/">Читать справочник</a>', text)
        self.assertIn("#налогиКипр #недвижимостьКипр", text)
        self.assertNotIn("<закон>", text)
        self.assertNotIn("<тегом>", text)
        self.assertLessEqual(len(text), tg.TEXT_LIMIT)
        self.assertLessEqual(tg.visible_length(text), tg.TEXT_LIMIT)

    def test_long_text_stays_within_4096_and_keeps_the_link(self):
        text = tg.render_message(
            "Заголовок & <тест> " * 400,
            "слово " * 5000,
            "https://mycytax.com/ru/guides/very-long-slug-name/",
            tg.LINK_TEXT,
            tg.hashtag_line(),
        )
        self.assertLessEqual(len(text), 4096)
        self.assertLessEqual(tg.visible_length(text), 4096)
        self.assertIn(tg.LINK_TEXT, text)
        self.assertIn("#налогиКипр", text)
        self.assertIn("#недвижимостьКипр", text)
        self.assertIn("&amp;", text)
        self.assertIn("&lt;тест&gt;", text)
        self.assertNotIn("<тест>", text)

    def test_russian_url_and_default_language_fallback(self):
        self.assertTrue(tg.russian_page_exists(ROOT, "taxes-overview"))
        self.assertEqual(
            tg.page_url("https://mycytax.com", "taxes-overview", russian=True),
            "https://mycytax.com/ru/guides/taxes-overview/",
        )
        self.assertEqual(
            tg.page_url("https://mycytax.com/", "taxes-overview", russian=False),
            "https://mycytax.com/guides/taxes-overview/",
        )
        self.assertEqual(build.loc("ru", "/guides/taxes-overview/"), "/ru/guides/taxes-overview/")
        self.assertEqual(build.loc("en", "/guides/taxes-overview/"), "/guides/taxes-overview/")

    def test_built_russian_page_counts_as_ready(self):
        with open(os.path.join(ROOT, "ru", "guides", "taxes-overview", "index.html"), "rb") as handle:
            body = handle.read()
        guide = next(item for item in tg.load_guides(GUIDES) if item.slug == "taxes-overview")
        self.assertTrue(tg.is_page_ready(body, guide.slug, guide.title, russian=True))
        self.assertIn(guide.title, html.unescape(body.decode("utf-8")))
        missing = page("Другой заголовок", "taxes-overview", noindex=True)
        self.assertFalse(tg.is_page_ready(missing, "taxes-overview", guide.title, russian=True))
        self.assertFalse(tg.is_page_ready(b"missing", "taxes-overview", guide.title, russian=True))
        self.assertFalse(tg.is_page_ready(page(guide.title, "taxes-overview"), "taxes-overview", guide.title, russian=False))

    def test_slugify_matches_the_site_builder(self):
        sample = "Налоги на недвижимость Кипра: обзор"
        self.assertEqual(tg.slugify(sample), build.slugify(sample))
        self.assertEqual(tg.DEFAULT_CHANNEL, "@mycytax")
        self.assertEqual(tg.resolve_channel(""), "@mycytax")
        self.assertEqual(tg.resolve_channel("mycytax"), "@mycytax")
        with self.assertRaises(SystemExit):
            tg.resolve_channel("bad channel")


class LoadTests(unittest.TestCase):
    def write(self, directory, name, payload):
        path = os.path.join(directory, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
        return path

    def test_slug_comes_from_the_field_the_filename_or_the_russian_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "from-file.json", {
                "ru": {"title": "Новый закон", "description": "Коротко"},
            })
            self.write(tmp, "!!.json", {
                "ru": {"title": "Новый закон", "description": "Коротко"},
            })
            self.write(tmp, "kept.json", {
                "slug": "kept-slug",
                "ru": {"title": "  Русский  ", "description": "  Описание  "},
            })
            guides = {item.slug: item for item in tg.load_guides(tmp)}
        self.assertEqual(tg.slugify("Новый закон"), "novyj-zakon")
        self.assertEqual(guides["from-file"].title, "Новый закон")
        self.assertEqual(guides["novyj-zakon"].description, "Коротко")
        self.assertEqual(guides["kept-slug"].title, "Русский")
        self.assertEqual(guides["kept-slug"].description, "Описание")

    def test_rejects_bad_guide_and_duplicate_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, "bad.json", {"ru": {"title": "Только заголовок"}})
            with self.assertRaises(SystemExit):
                tg.load_guide(path)
        with tempfile.TemporaryDirectory() as tmp:
            body = {"slug": "same", "ru": {"title": "A", "description": "B"}}
            self.write(tmp, "a.json", body)
            self.write(tmp, "b.json", body)
            with self.assertRaises(SystemExit):
                tg.load_guides(tmp)


class PlanTests(unittest.TestCase):
    def test_new_guide_is_sent_once(self):
        state = tg.empty_state()
        actions = tg.plan([guide()], state)
        self.assertEqual([(item.kind, item.guide.slug) for item in actions], [("send", "new-guide")])

    def test_edit_does_not_repost(self):
        state = tg.empty_state()
        tg.mark(state, "new-guide", "sent", tg.utcnow())
        changed = guide(title="Другой заголовок", description="Другое описание")
        self.assertEqual(tg.plan([changed], state), [])

    def test_seeded_guides_are_not_planned(self):
        guides = tg.load_guides(GUIDES)
        state = tg.initial_seed(guides)
        self.assertEqual(tg.plan(guides, state), [])


class ExecuteTests(unittest.TestCase):
    def run_execute(self, guides, state, *, token="token", dry_run=False, http_get=None,
                    send=None, max_wait=360, clock=None, root=None, channel="@mycytax"):
        logs = []
        saves = []
        clock = clock or Clock()
        root = root or ROOT
        if http_get is None:
            def http_get(url):
                slug = url.rstrip("/").split("/")[-1]
                match = next(item for item in guides if item.slug == slug)
                russian = "/ru/guides/" in url
                return 200, page(match.title, slug, russian=russian)
        if send is None:
            def send(payload):
                return True, "10"
        code = tg.execute(
            guides, state,
            now=datetime.datetime(2026, 11, 13, 12, 0, tzinfo=datetime.timezone.utc),
            token=token, dry_run=dry_run, base="https://mycytax.com", root=root,
            channel=channel, max_wait=max_wait,
            http_get=http_get, sleep=clock.sleep, monotonic=clock.monotonic,
            send=send, log=logs.append, save=lambda: saves.append(json.loads(tg.serialize(state))),
        )
        return logs, saves, code

    def test_posts_text_once_with_preview_enabled(self):
        sent = []
        story = guide(title='Налоги & сборы', description="Коротко <важно>")
        with tempfile.TemporaryDirectory() as root:
            write_ru_page(root, story.slug)
            state = tg.empty_state()
            logs, saves, code = self.run_execute(
                [story], state, root=root,
                send=lambda payload: sent.append(payload) or (True, "7"),
            )
        self.assertEqual(code, 0)
        self.assertEqual(len(sent), 1)
        post = sent[0]
        self.assertEqual(post["method"], "sendMessage")
        self.assertEqual(post["chat_id"], "@mycytax")
        self.assertEqual(post["parse_mode"], "HTML")
        self.assertEqual(post["link_preview_options"], {
            "is_disabled": False,
            "url": "https://mycytax.com/ru/guides/new-guide/",
        })
        self.assertNotIn("disable_web_page_preview", post)
        self.assertIn("<b>Налоги &amp; сборы</b>", post["text"])
        self.assertIn("Коротко &lt;важно&gt;", post["text"])
        self.assertIn(">Читать справочник</a>", post["text"])
        self.assertIn("#налогиКипр #недвижимостьКипр", post["text"])
        self.assertLessEqual(len(post["text"]), 4096)
        self.assertEqual(state["posted"]["new-guide"]["status"], "sent")
        self.assertGreaterEqual(len(saves), 1)
        again = []
        edited = guide(title="Изменённый заголовок", description="Новое описание")
        self.run_execute([edited], state, send=lambda payload: again.append(payload) or (True, "8"))
        self.assertEqual(again, [])
        self.assertTrue(any("Nothing new to post." in line for line in self.run_execute([edited], state)[0]))

    def test_missing_russian_page_links_to_the_default_language_url(self):
        sent = []
        story = guide(slug="fallback-guide")
        with tempfile.TemporaryDirectory() as root:
            state = tg.empty_state()
            self.run_execute([story], state, root=root, send=lambda payload: sent.append(payload) or (True, "1"))
        self.assertEqual(sent[0]["link_preview_options"]["url"], "https://mycytax.com/guides/fallback-guide/")
        self.assertIn('href="https://mycytax.com/guides/fallback-guide/"', sent[0]["text"])
        self.assertIn("<b>Новый справочник</b>", sent[0]["text"])

    def test_does_not_send_until_the_page_returns_200(self):
        story = guide()
        clock = Clock()
        calls = {"n": 0}

        def http_get(url):
            calls["n"] += 1
            if clock.now < 20:
                return 404, b"missing"
            return 200, page(story.title, story.slug)

        sent = []
        state = tg.empty_state()
        with tempfile.TemporaryDirectory() as root:
            write_ru_page(root, story.slug)
            logs, _saves, code = self.run_execute(
                [story], state, root=root, clock=clock, http_get=http_get,
                send=lambda payload: sent.append(payload) or (True, "3"),
            )
        self.assertEqual(code, 0)
        self.assertGreater(clock.now, 0)
        self.assertEqual(len(sent), 1)
        self.assertTrue(any("HTTP 404" in line for line in logs))
        self.assertEqual(state["posted"][story.slug]["status"], "sent")

    def test_live_failure_does_not_mark(self):
        story = guide(slug="second")
        state = tg.empty_state()

        def http_get(url):
            return 503, b"no"

        with tempfile.TemporaryDirectory() as root:
            write_ru_page(root, story.slug)
            logs, saves, code = self.run_execute(
                [story], state, root=root, max_wait=0, http_get=http_get,
            )
        self.assertEqual(code, 1)
        self.assertEqual(saves, [])
        self.assertNotIn("second", state["posted"])
        self.assertTrue(any("not HTTP 200" in line for line in logs))

    def test_telegram_failure_does_not_mark(self):
        story = guide()
        state = tg.empty_state()
        with tempfile.TemporaryDirectory() as root:
            write_ru_page(root, story.slug)
            self.run_execute([story], state, root=root, send=lambda payload: (False, "Bad Request"))
        self.assertNotIn(story.slug, state["posted"])

    def test_missing_token_does_not_advance_state_or_send(self):
        sent = []
        story = guide()
        state = tg.empty_state()
        before = tg.serialize(state)
        logs, saves, code = self.run_execute(
            [story], state, token="",
            send=lambda payload: sent.append(payload) or (True, "1"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(sent, [])
        self.assertEqual(saves, [])
        self.assertEqual(tg.serialize(state), before)
        self.assertTrue(any("TELEGRAM_BOT_TOKEN" in line and "not set" in line for line in logs))
        self.assertTrue(any(line.startswith("::notice") for line in logs))

    def test_dry_run_logs_the_message_and_does_not_send_or_write(self):
        sent = []
        story = guide(title="Заголовок")
        state = tg.empty_state()
        before = tg.serialize(state)
        with tempfile.TemporaryDirectory() as root:
            write_ru_page(root, story.slug)
            logs, saves, code = self.run_execute(
                [story], state, root=root, token="secret-token", dry_run=True,
                send=lambda payload: sent.append(payload) or (True, "1"),
            )
        self.assertEqual(code, 0)
        self.assertEqual(sent, [])
        self.assertEqual(saves, [])
        self.assertEqual(tg.serialize(state), before)
        text = "\n".join(logs)
        self.assertIn("DRY RUN @mycytax sendMessage slug=new-guide page=ru live=yes", text)
        self.assertIn("link_preview: https://mycytax.com/ru/guides/new-guide/", text)
        self.assertIn("<b>Заголовок</b>", text)
        self.assertIn("Читать справочник", text)
        self.assertIn("#налогиКипр", text)
        self.assertIn("Nothing was sent", text)
        self.assertIn("TELEGRAM_BOT_TOKEN is configured (value not printed).", text)
        self.assertNotIn("secret-token", text)

    def test_channel_can_be_overridden(self):
        sent = []
        story = guide(slug="other")
        with tempfile.TemporaryDirectory() as root:
            write_ru_page(root, story.slug)
            self.run_execute(
                [story], tg.empty_state(), root=root, channel="@otherchannel",
                send=lambda payload: sent.append(payload) or (True, "1"),
            )
        self.assertEqual(sent[0]["chat_id"], "@otherchannel")

    def test_api_retries_429_and_redacts_the_token(self):
        calls = []

        def post(url, data):
            calls.append((url, data))
            if len(calls) == 1:
                return 429, json.dumps({
                    "ok": False,
                    "description": "Too Many Requests secret-token",
                    "parameters": {"retry_after": 1},
                }).encode()
            return 200, json.dumps({"ok": True, "result": {"message_id": 42}}).encode()

        slept = []
        ok, info = tg.send_telegram(
            "secret-token",
            {
                "method": "sendMessage",
                "chat_id": "@mycytax",
                "text": "Hi",
                "parse_mode": "HTML",
                "link_preview_options": {"is_disabled": False, "url": "https://mycytax.com/ru/guides/x/"},
                "url": "https://mycytax.com/ru/guides/x/",
                "russian": True,
            },
            post=post, sleep=slept.append,
        )
        self.assertTrue(ok)
        self.assertEqual(info, "42")
        self.assertEqual(slept, [1])
        body = json.loads(calls[0][1].decode())
        self.assertNotIn("url", body)
        self.assertNotIn("russian", body)
        self.assertEqual(body["parse_mode"], "HTML")
        self.assertEqual(body["text"], "Hi")
        self.assertEqual(body["link_preview_options"]["is_disabled"], False)
        self.assertIn("/botsecret-token/sendMessage", calls[0][0])

        def bad_request(url, data):
            calls.append(url)
            return 400, json.dumps({"ok": False, "description": "boom secret-token"}).encode()

        calls.clear()
        ok, info = tg.send_telegram(
            "secret-token",
            {"method": "sendMessage", "chat_id": "@mycytax"},
            post=bad_request, sleep=slept.append,
        )
        self.assertFalse(ok)
        self.assertNotIn("secret-token", info)
        self.assertIn("boom", info)
        self.assertEqual(len(calls), 1)

    def test_cli_missing_token_keeps_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            guides_dir = os.path.join(tmp, "guides")
            os.makedirs(guides_dir)
            with open(os.path.join(guides_dir, "story.json"), "w", encoding="utf-8") as handle:
                json.dump({"slug": "cli-story", "ru": {"title": "Справочник", "description": "Кратко"}}, handle)
            state_path = os.path.join(tmp, "telegram-posted.json")
            with open(state_path, "w", encoding="utf-8") as handle:
                handle.write(tg.serialize(tg.empty_state()))
            with open(state_path, encoding="utf-8") as handle:
                before = handle.read()
            env = os.environ.copy()
            env.pop("TELEGRAM_BOT_TOKEN", None)
            env.pop("DRY_RUN", None)
            env.pop("PUSH_STATE", None)
            env.pop("TELEGRAM_CHANNEL", None)
            with mock.patch.dict(os.environ, env, clear=True):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = tg.main([
                        "--guides", guides_dir,
                        "--state", state_path,
                        "--root", tmp,
                        "--max-wait", "0",
                    ])
            self.assertEqual(code, 0)
            self.assertIn("TELEGRAM_BOT_TOKEN", output.getvalue())
            self.assertIn("@mycytax", output.getvalue())
            with open(state_path, encoding="utf-8") as handle:
                self.assertEqual(handle.read(), before)


class SeedAndWorkflowTests(unittest.TestCase):
    def test_original_guides_are_seeded_and_match_the_loader(self):
        self.assertTrue(os.path.exists(STATE))
        with open(STATE, encoding="utf-8") as handle:
            raw = handle.read()
        state = tg.load_state(STATE)
        self.assertEqual(raw, tg.serialize(state))
        found = []
        for name in ORIGINAL:
            path = os.path.join(GUIDES, name + ".json")
            self.assertTrue(os.path.exists(path), name)
            found.append(tg.load_guide(path))
            self.assertTrue(tg.russian_page_exists(ROOT, name), name)
        expected = tg.initial_seed(found)
        for slug, entry in expected["posted"].items():
            self.assertEqual(state["posted"].get(slug), entry)
        self.assertEqual(tg.plan(found, state), [])

    def test_workflows_avoid_a_posting_loop_and_do_not_print_the_token(self):
        with open(os.path.join(ROOT, ".github", "workflows", "build.yml"), encoding="utf-8") as handle:
            build_yml = handle.read()
        with open(os.path.join(ROOT, ".github", "workflows", "telegram.yml"), encoding="utf-8") as handle:
            poster = handle.read()
        self.assertEqual(build_yml.count("!source/content/telegram-posted.json"), 2)
        self.assertIn("git reset -q -- source/content/telegram-posted.json", build_yml)
        self.assertIn("Test Telegram poster", build_yml)
        self.assertIn("name: Build site", build_yml)
        self.assertIn('workflows: ["Build site"]', poster)
        self.assertIn("types: [completed]", poster)
        self.assertIn("branches: [main]", poster)
        self.assertIn("workflow_dispatch", poster)
        self.assertIn("dry_run", poster)
        self.assertIn("TELEGRAM_BOT_TOKEN", poster)
        self.assertIn("value not printed", poster)
        self.assertIn('TELEGRAM_CHANNEL: "@mycytax"', poster)
        self.assertIn("PUSH_STATE", poster)
        self.assertIn("cancel-in-progress: false", poster)
        self.assertIn("[skip ci]", tg.COMMIT_MESSAGE)
        self.assertNotIn('echo "$TELEGRAM_BOT_TOKEN"', poster)
        self.assertNotIn("echo $TELEGRAM_BOT_TOKEN", poster)
        self.assertNotIn("api.telegram.org", poster)

    def test_commit_and_push_only_the_state_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            bare = os.path.join(tmp, "bare.git")
            work = os.path.join(tmp, "work")
            subprocess.check_call(["git", "init", "--bare", "-b", "main", bare], stdout=subprocess.DEVNULL)
            subprocess.check_call(["git", "init", "-b", "main", work], stdout=subprocess.DEVNULL)
            subprocess.check_call(["git", "-C", work, "config", "user.email", "test@example.com"])
            subprocess.check_call(["git", "-C", work, "config", "user.name", "Test"])
            subprocess.check_call(["git", "-C", work, "config", "commit.gpgsign", "false"])
            with open(os.path.join(work, "README"), "w", encoding="utf-8") as handle:
                handle.write("site\n")
            subprocess.check_call(["git", "-C", work, "add", "README"])
            subprocess.check_call(["git", "-C", work, "commit", "-q", "-m", "init"])
            subprocess.check_call(["git", "-C", work, "remote", "add", "origin", bare])
            subprocess.check_call(["git", "-C", work, "push", "-q", "origin", "HEAD:main"])
            state = os.path.join(work, "source", "content", "telegram-posted.json")
            os.makedirs(os.path.dirname(state))
            with open(state, "w", encoding="utf-8") as handle:
                handle.write(tg.serialize(tg.empty_state()))
            with open(os.path.join(work, "README"), "a", encoding="utf-8") as handle:
                handle.write("dirty but must not be committed\n")
            with contextlib.redirect_stdout(io.StringIO()):
                tg.commit_and_push(work, state)
            shown = subprocess.check_output(
                ["git", "-C", work, "show", "--name-only", "--pretty=format:%s", "HEAD"],
                text=True,
            )
            self.assertIn(tg.COMMIT_MESSAGE, shown)
            self.assertIn("[skip ci]", shown)
            self.assertIn("source/content/telegram-posted.json", shown)
            self.assertNotIn("dirty", shown)
            clone = os.path.join(tmp, "clone")
            subprocess.check_call(["git", "clone", "-q", bare, clone])
            self.assertTrue(os.path.exists(os.path.join(clone, "source", "content", "telegram-posted.json")))
            with open(os.path.join(clone, "README"), encoding="utf-8") as handle:
                readme = handle.read()
            self.assertNotIn("dirty", readme)


if __name__ == "__main__":
    unittest.main()
