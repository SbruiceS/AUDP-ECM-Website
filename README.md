<p align="center"><img src="site/assets/logo-1200.png" alt="AUDP-ECM logo" width="560"></p>

# AUDP-ECM website

[![Website](https://github.com/SbruiceS/AUDP-ECM-Website/actions/workflows/pages.yml/badge.svg?branch=main)](https://github.com/SbruiceS/AUDP-ECM-Website/actions/workflows/pages.yml)
[![Site](https://img.shields.io/badge/site-sbruices.github.io%2FAUDP--ECM--Website-0b7285)](https://sbruices.github.io/AUDP-ECM-Website/)
[![Security](https://img.shields.io/badge/CSP-strict%2C%20first--party%20only-success)](#security-posture)
[![License](https://img.shields.io/badge/license-proprietary%20(ASPF)-lightgrey)](LICENSE)

Public, **informational** website for AUDP-ECM:
**https://sbruices.github.io/AUDP-ECM-Website/**

It describes what AUDP-ECM does and how to use the public bindings
([Python](https://github.com/SbruiceS/AUDP-ECM-Python), [D](https://github.com/SbruiceS/AUDP-ECM-D)).
It intentionally contains no secrets and no internal architecture of the private core.

## Layout

| Path | Purpose |
|------|---------|
| `site/` | everything that is published (static HTML/CSS/JS) |
| `scripts/build_site.py` | generates every page (head, SEO, schema.org, header/footer) — CI fails on drift |
| `site/assets/app.js` | progressive enhancement: theme toggle, mobile menu, copy buttons, reveal, live Reed–Solomon demo |
| `scripts/test_demo.mjs` | tests the demo codec (known answers + 1 800 round trips) |
| `site/.well-known/security.txt` | RFC 9116 security contact |
| `scripts/content_guard.py` | pre-publish guard (see below) |
| `.github/workflows/pages.yml` | CI (guard) and CD (GitHub Pages deploy from `main`) |

## Pages and search

| Page | Targets searches for |
|------|----------------------|
| `index.html` | AUDP-ECM, agricultural telemetry error correction |
| `about.html` | Agriculture Service of Product Farm (ASPF) |
| `research.html` | agriculture research and innovation |
| `sbruice-singh.html` | Sbruice Singh |

Every page carries a canonical URL, Open Graph / Twitter card metadata and a schema.org
JSON-LD graph (`Organization`, `Person`, `WebSite`, `SoftwareApplication`, breadcrumbs).
`sitemap.xml` lists all pages; `og-image.png` (1200×630) and `logo.png` (512×512) are the share image and logo.

## Content guard

Every push and pull request runs `python3 scripts/content_guard.py site`, which fails on:

- secret-like strings (tokens, private keys, key material, secret names);
- names of private-core internals or links to the private repository;
- broken internal links and insecure `http://` links;
- `<script>` (other than inline schema.org JSON-LD data), inline styles or event handlers, and pages without a Content-Security-Policy;
- missing or malformed SEO: title / description length, canonical URL, Open Graph and Twitter tags,
  exactly one `<h1>`, image `alt` text, valid JSON-LD, and sitemap coverage.

Deployment only happens after the guard passes.

## Security posture

- Static files plus one first-party script; no cookies, no third-party requests, no network calls from JS.
- Strict CSP (`default-src 'none'; script-src 'self'`, no `unsafe-inline`/`unsafe-eval`).
- The guard rejects `eval`, `Function`, `innerHTML`, `document.write`, `fetch`/XHR/WebSocket and external URLs in JS.
- Everything works without JavaScript; the live demo is the only JS-only feature.
- Deployed by GitHub Actions with least-privilege permissions to the `github-pages` environment.

## Local preview

```bash
python3 scripts/content_guard.py site
python3 -m http.server -d site 8000      # then open http://localhost:8000
```

© 2026 Sbruice Singh / Agriculture Service of Product Farm (ASPF). All rights reserved.
Proprietary — see [LICENSE](LICENSE). Not open source.
