# -*- coding: utf-8 -*-
"""Submit sitemap URLs to IndexNow.

The key lives in source/site.json. The public file is https://mycytax.com/<key>.txt
and is written by source/build.py.

On a normal push that changes source/, this script does nothing: Build site
submits after it regenerates the sitemap and GitHub Pages has published it.
Pass --from-build from that workflow. Any other push submits the changed
sitemap URLs, or every sitemap URL when the change is not a single page.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
HOST = "mycytax.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_RE = re.compile(r"^[0-9a-f]{32}$")
# Build site regenerates pages when these change. A push of them must not
# submit the sitemap from the pre-build commit.
REBUILD_FILES = {
    ".github/workflows/build.yml",
    ".github/workflows/telegram.yml",
}


def load_config(path=None):
    path = path or os.path.join(HERE, "site.json")
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected an object")
    key = str(data.get("indexnow_key") or "").strip().lower()
    if not KEY_RE.fullmatch(key):
        raise SystemExit(f"{path}: indexnow_key must be 32 hex characters")
    return key


def parse_sitemap(text):
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text or "")


def triggers_rebuild(path):
    if path == "source/content/telegram-posted.json":
        return False
    if path.startswith("source/"):
        return True
    return path in REBUILD_FILES


def file_to_url(path):
    """Map a generated page in the repo to its public URL. None if it is not a page."""
    if path == "index.html":
        return f"https://{HOST}/"
    if path == "feed.xml":
        return f"https://{HOST}/feed.xml"
    if path.endswith("/index.html"):
        return f"https://{HOST}/{path[:-len('index.html')]}"
    if path.endswith("feed.xml") and "/" in path:
        return f"https://{HOST}/{path}"
    return None


def forces_all(path):
    if path in ("sitemap.xml", "robots.txt"):
        return True
    # The key file sits at the site root. A new key means every URL should be sent.
    return "/" not in path and path.endswith(".txt")


def plan(files, sitemap_urls, from_build=False):
    """Return ('submit', urls) or ('skip', []).

    `files` is None when the changed set is unknown: submit the whole sitemap.
    """
    ordered = list(dict.fromkeys(sitemap_urls))
    allowed = set(ordered)
    if from_build or files is None:
        return "submit", ordered
    if any(triggers_rebuild(path) for path in files):
        return "skip", []
    if any(forces_all(path) for path in files):
        return "submit", ordered
    chosen = []
    for path in files:
        url = file_to_url(path)
        if url and url in allowed:
            chosen.append(url)
    return "submit", list(dict.fromkeys(chosen))


def payload(key, urls):
    return {
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": list(urls),
    }


def diff_files(before, head="HEAD", runner=None):
    """Changed paths between two commits. None when the range is unknown."""
    if not before or set(before) <= {"0"}:
        return None
    run = runner or subprocess.run
    proc = run(
        ["git", "diff", "--name-only", before, head],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]


def key_is_live(key, fetch):
    url = f"https://{HOST}/{key}.txt"
    try:
        body = fetch(url)
    except Exception:
        return False
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    return (body or "").strip() == key


def wait_for_key(key, fetch, attempts=18, pause=10, sleep=time.sleep):
    """Poll the public key file. Pages may still be publishing the new commit."""
    for attempt in range(1, attempts + 1):
        if key_is_live(key, fetch):
            print(f"IndexNow: key file is live ({attempt}/{attempts})")
            return True
        print(f"IndexNow: key file not live yet ({attempt}/{attempts})")
        if attempt < attempts:
            sleep(pause)
    return False


def _http_get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "mycytax-indexnow"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read(4096)


def submit(key, urls, opener=None):
    body = json.dumps(payload(key, urls), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "mycytax-indexnow",
        },
        method="POST",
    )
    open_url = opener or urllib.request.urlopen
    with open_url(request, timeout=30) as response:
        status = getattr(response, "status", None) or response.getcode()
        raw = response.read(4000)
    return status, raw


def main(argv=None):
    parser = argparse.ArgumentParser(description="Submit MyCyTax URLs to IndexNow")
    parser.add_argument("--from-build", action="store_true", help="submit the sitemap just built")
    parser.add_argument("--wait", action="store_true", help="wait until the key file is on https://mycytax.com")
    parser.add_argument("--dry-run", action="store_true", help="print the payload and do not call IndexNow")
    parser.add_argument("--sitemap", default=os.path.join(ROOT, "sitemap.xml"))
    args = parser.parse_args(argv)

    key = load_config()
    with open(args.sitemap, encoding="utf8") as f:
        urls = parse_sitemap(f.read())
    if not urls:
        print(f"IndexNow: no URLs in {args.sitemap}", file=sys.stderr)
        return 1
    files = None if args.from_build else diff_files(os.environ.get("INDEXNOW_BEFORE", ""))
    action, chosen = plan(files, urls, from_build=args.from_build)
    if action == "skip":
        print("IndexNow: source changed. Build site submits after the new sitemap is published.")
        return 0
    if not chosen:
        print("IndexNow: no sitemap URL changed.")
        return 0
    print(f"IndexNow: {len(chosen)} URL(s), keyLocation https://{HOST}/{key}.txt")
    if args.dry_run:
        print(json.dumps(payload(key, chosen), ensure_ascii=False, indent=2))
        return 0
    if args.wait and not wait_for_key(key, _http_get):
        print("IndexNow: the key file was not reachable.", file=sys.stderr)
        return 1
    status = 0
    raw = b""
    for attempt in range(1, 4):
        try:
            status, raw = submit(key, chosen)
        except Exception as exc:
            print(f"IndexNow: attempt {attempt} failed ({type(exc).__name__}: {exc})", file=sys.stderr)
            status = 0
        if status in (200, 202):
            print(f"IndexNow: accepted ({status}) for {len(chosen)} URL(s)")
            return 0
        if status and status not in (429, 500, 502, 503):
            break
        time.sleep(5 * attempt)
    text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)
    print(f"IndexNow: {status} {text[:500]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
