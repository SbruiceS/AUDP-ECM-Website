# AUDP-ECM website

[![Website](https://github.com/SbruiceS/AUDP-ECM-Website/actions/workflows/pages.yml/badge.svg?branch=main)](https://github.com/SbruiceS/AUDP-ECM-Website/actions/workflows/pages.yml)
[![Site](https://img.shields.io/badge/site-sbruices.github.io%2FAUDP--ECM--Website-0b7285)](https://sbruices.github.io/AUDP-ECM-Website/)
[![No JavaScript](https://img.shields.io/badge/JavaScript-none-success)](#security-posture)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Public, **informational** website for AUDP-ECM:
**https://sbruices.github.io/AUDP-ECM-Website/**

It describes what AUDP-ECM does and how to use the public bindings
([Python](https://github.com/SbruiceS/AUDP-ECM-Python), [D](https://github.com/SbruiceS/AUDP-ECM-D)).
It intentionally contains no secrets and no internal architecture of the private core.

## Layout

| Path | Purpose |
|------|---------|
| `site/` | everything that is published (static HTML/CSS, no build step) |
| `site/.well-known/security.txt` | RFC 9116 security contact |
| `scripts/content_guard.py` | pre-publish guard (see below) |
| `.github/workflows/pages.yml` | CI (guard) and CD (GitHub Pages deploy from `main`) |

## Content guard

Every push and pull request runs `python3 scripts/content_guard.py site`, which fails on:

- secret-like strings (tokens, private keys, key material, secret names);
- names of private-core internals or links to the private repository;
- broken internal links and insecure `http://` links;
- `<script>`, inline styles or event handlers, and pages without a Content-Security-Policy.

Deployment only happens after the guard passes.

## Security posture

- Static files only; no JavaScript, no cookies, no third-party requests.
- Strict CSP (`default-src 'none'`), `no-referrer`.
- Deployed by GitHub Actions with least-privilege permissions to the `github-pages` environment.

## Local preview

```bash
python3 scripts/content_guard.py site
python3 -m http.server -d site 8000      # then open http://localhost:8000
```

© 2026 Sbruice Singh / Agriculture Service of Product Farm (ASPF).
