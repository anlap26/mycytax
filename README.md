# MyCyTax

Trilingual (English, Russian, Greek) calculators and guides for Cyprus property taxes. English is the primary language. The publisher is Anna, based in Cyprus. Contact: info@mycytax.com.

The site is published from `anlap26/mycytax` on GitHub Pages. The public origin is https://mycytax.com/.

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

Replace `pub-XXXXXXXXXXXXXXXX` with the real publisher ID. Do not publish a placeholder ID. Then put the ad unit code inside the elements marked `data-ad`. Update the privacy and cookie pages in `source/build.py` before those tags go live, including a consent tool for visitors in the EEA.

## Form

The contact form posts to FormSubmit at info@mycytax.com. The first submission sends a confirmation email to that address. Messages are not delivered until that link is opened.
