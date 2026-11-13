# MyCyTax

Trilingual (English, Russian, Greek) calculators and guides for Cyprus property taxes. English is the primary language. The publisher is Anna, based in Cyprus. Contact: info@mycytax.com.

The site is published from `anlap26/mycytax` on GitHub Pages. The public origin is https://mycytax.com/.

## Как править сайт

Откройте https://mycytax.com/admin/ и войдите токеном GitHub (отдельный сервер входа не нужен). В панели по-русски: справочники, страницы «О сайте», «Конфиденциальность», «Файлы cookie», «Условия», главная, контакты и текст оговорки внизу страниц. Калькуляторы в панели не редактируются.

Обязателен русский текст. Английский и греческий можно не заполнять: сайт покажет русский и закроет эту версию от поиска, пока перевод не появится. Адрес новой страницы можно оставить пустым — он соберётся из русского заголовка латинскими буквами. Уже опубликованный адрес лучше не менять: старая ссылка перестанет открываться.

Токен — fine-grained personal access token. В доступе к репозиториям должен быть именно **anlap26/mycytax** (токена только для anlap26/cynews24 недостаточно: в него нужно добавить mycytax или выпустить новый). Право: Contents — Read and write. Сохранение пишет JSON в `source/content/` на ветке `main`. Через несколько минут действие «Build site» пересобирает страницы. Домен mycytax.com при этом не меняется.

Справочник короче 800 слов сборка не опубликует.

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

Replace `pub-XXXXXXXXXXXXXXXX` with the real publisher ID. Do not publish a placeholder ID. Then put the ad unit code inside the elements marked `data-ad`. The privacy and cookie pages are edited in the admin panel (Страницы), not in `source/build.py`.

## Form

The contact form posts to FormSubmit at info@mycytax.com. The first submission sends a confirmation email to that address. Messages are not delivered until that link is opened.
