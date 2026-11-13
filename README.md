# MyCyTax

Trilingual (English, Russian, Greek) calculators and guides for Cyprus property taxes. English is the primary language. The publisher is Anna, based in Cyprus. Contact: info@mycytax.com.

The site is published from `anlap26/mycytax` on GitHub Pages. The public origin is https://mycytax.com/.

## Как править сайт

Откройте https://mycytax.com/admin/ . На странице входа выберите вход по токену GitHub (отдельного сайта для входа нет).

Токен создаётся на GitHub: Settings → Developer settings → Personal access tokens → Fine-grained tokens. В нём должно быть:

- доступ **только к репозиторию anlap26/mycytax** (не к другим репозиториям и не «все репозитории», если можно выбрать один);
- разрешение **Contents: Read and write**.

Без записи в `anlap26/mycytax` панель откроется, но не сможет сохранить текст. Токен показывается один раз — сохраните его. Никому его не отправляйте. Если токен потерялся, удалите его на GitHub и создайте новый.

В панели можно править справочники и страницы «О сайте», «Конфиденциальность», «Файлы cookie» и «Условия». Обязателен русский текст. Английский и греческий можно не заполнять: на этих языках покажется русский текст, а страница не попадёт в поиск, пока перевод не будет добавлен. Адрес новой страницы можно оставить пустым — он соберётся из русского заголовка латинскими буквами. Уже опубликованный адрес лучше не менять.

Калькуляторы из панели не меняются. После сохранения страница на сайте обновляется сама, обычно через несколько минут.

## Editing

- **In the browser:** https://mycytax.com/admin/ (Sveltia CMS, `admin/config.yml`). Sign in with a GitHub fine-grained token that has *Contents: Read and write* on `anlap26/mycytax`. Token login only; there is no OAuth server.
- **By hand:** one JSON file per guide in `source/content/guides/` and one per page in `source/content/pages/` (`about`, `privacy`, `cookies`, `terms`). Russian (`ru`) is required; `en` and `el` are optional. A missing translation falls back to the Russian text and that language page is marked `noindex`.
- The page address is the `slug` field, otherwise the file name, otherwise the Russian title in Latin letters. `seq` sets the order on the home page (empty goes last).

Guide fields: `title`, `description`, `body` (paragraphs separated by a blank line, `## ` headings, optional `- ` lists and `[text](https://…)` links), `faq` (`q`, `a`), `sources` (`name`, `url`).

## Build

From the repository root:

```bash
BASE=https://mycytax.com python3 source/build.py
```

`BASE` is the site origin with no trailing slash. The path inside it becomes the link prefix.

When the domain **mycytax.com** is connected, rebuild and redeploy with:

```bash
BASE=https://mycytax.com python3 source/build.py
```

Point the domain at the host that serves this site root, then set `BASE` to `https://mycytax.com` so canonical URLs, the sitemap and hreflang use the new origin. No calculator logic changes.

## Ads

Advertising boxes in the HTML are empty. No ad script is included.

When an AdSense publisher ID exists, add a file named `ads.txt` at the site root (the same folder as `index.html`) with one line:

```text
google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
```

Replace `pub-XXXXXXXXXXXXXXXX` with the real publisher ID. Do not publish a placeholder ID. Then put the ad unit code inside the elements marked `data-ad`. Update the privacy and cookie pages in `source/content/pages/` before those tags go live, including a consent tool for visitors in the EEA.

## Publishing

A push to `main` that touches `source/` starts the **Build site** workflow (`.github/workflows/build.yml`). It runs `python3 source/build.py` with `BASE=https://mycytax.com` and, when the generated pages changed, commits them back to `main`. Pages keeps serving `main` / root. `CNAME` is `mycytax.com` and is rewritten on every build. A normal push already starts a Pages deployment. A commit this workflow pushes does not, so the workflow requests a Pages build only after its own commit, and also on a manual run. Pull requests run the build as a check. The workflow does not run for an `admin/`-only push; GitHub Pages still publishes that push, which is how the editor itself is served. A commit that only changes `source/content/telegram-posted.json` does not rebuild the site.

## Telegram

After **Build site** succeeds on `main`, **Post to Telegram** (`.github/workflows/telegram.yml`) posts each new guide once to `@mycytax`. The message is the Russian title, the short description and a link to `https://mycytax.com/ru/guides/<slug>/` (the default-language URL is used only when that Russian page is not in the build). Guides that already existed when posting was added are listed in `source/content/telegram-posted.json` and are not posted. Editing a guide does not post it again.

The bot token is the repository secret `TELEGRAM_BOT_TOKEN`. If that secret is missing, the job logs a notice and exits successfully without changing the state file. Run the workflow manually with **dry run** to print the message without sending it.

## Form

The contact form posts to FormSubmit at info@mycytax.com. The first submission sends a confirmation email to that address. Messages are not delivered until that link is opened.
