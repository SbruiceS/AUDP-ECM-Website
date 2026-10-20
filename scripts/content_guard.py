#!/usr/bin/env python3
"""Pre-publish guard for the public AUDP-ECM website.

The site is informational only. This check fails the build when a published
file contains anything that looks like a secret or that names internals of the
private core, and it validates links and the page security posture.

It also enforces SEO basics on every indexable page (title, description,
canonical, Open Graph/Twitter, one <h1>, image alt text, valid schema.org
JSON-LD, sitemap coverage) so they cannot silently regress.

Usage: python3 scripts/content_guard.py site
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# --- secrets / credentials ----------------------------------------------------
SECRET_PATTERNS = {
    "GitHub token": r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})",
    "token in URL": r"x-access-token:[^@\s]+@",
    "private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "SSH public/private key material": r"\bssh-(ed25519|rsa) AAAA[0-9A-Za-z+/]{20,}",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "generic secret assignment": r"(?i)\b(secret|password|passwd|api[_-]?key|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    "CI secret name": r"\bCORE_DEPLOY_KEY\b",
}

# --- private-core internals (architecture must not be published) -------------
INTERNAL_PATTERNS = {
    "internal crate name": r"\becm-(kernels|core|polynomials|finite-fields|algebraic-codes|probabilistic|"
                           r"simulation|graph-codes|decoder|audp-adapter|geometric-codes|topological-codes|ffi)\b",
    "internal identifier": r"\b(KernelId|KERNEL_CATALOG|MathContext|GfMatrix|k_pipeline_\w+|k_rs_\w+|k_gf_\w+)\b",
    "internal path": r"\b(crates|research|cpp/include|docs/architecture)/",
    "private repository URL": r"github\.com/SbruiceS/AUDP-ECM(?![-\w])",
    "deploy key mention": r"(?i)deploy[- ]key",
}

TEXT_SUFFIXES = {".html", ".css", ".txt", ".svg", ".xml", ".json", ".md", ".js"}
BASE_URL = "https://sbruices.github.io/AUDP-ECM-Website/"


class PageCheck(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.problems: list[str] = []
        self.has_csp = False
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None
        self.title = ""
        self.h1 = 0
        self.jsonld: list[str] = []
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json" and "src" not in a:
                self._in = "jsonld"
                self.jsonld.append("")
            else:
                self.problems.append("<script> is not allowed (only inline application/ld+json data)")
        if tag == "title":
            self._in = "title"
        if tag == "h1":
            self.h1 += 1
        if tag == "img" and not (a.get("alt") or "").strip():
            self.problems.append(f"<img src={a.get('src')!r}> without alt text")
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key.lower()] = a.get("content") or ""
        if tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")
        if "style" in a:
            self.problems.append(f"inline style attribute on <{tag}> (blocked by CSP)")
        for name in a:
            if name.startswith("on"):
                self.problems.append(f"inline event handler {name} on <{tag}>")
        if tag == "meta" and (a.get("http-equiv") or "").lower() == "content-security-policy":
            self.has_csp = True
        for attr in ("href", "src"):
            if a.get(attr) and not (tag == "link" and (a.get("rel") or "").lower() == "canonical"):
                self.links.append(a[attr])

    def handle_endtag(self, tag):
        if tag in ("script", "title"):
            self._in = None

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "jsonld":
            self.jsonld[-1] += data


def seo_problems(rel: str, pc: PageCheck, sitemap: set[str]) -> list[str]:
    out = []
    if rel == "404.html":
        if "noindex" not in pc.meta.get("robots", ""):
            out.append("404 page must be noindex")
        return out
    url = BASE_URL + ("" if rel == "index.html" else rel)
    if not 15 <= len(pc.title.strip()) <= 70:
        out.append(f"title length {len(pc.title.strip())} (want 15-70)")
    desc = pc.meta.get("description", "")
    if not 70 <= len(desc) <= 170:
        out.append(f"meta description length {len(desc)} (want 70-170)")
    if pc.canonical != url:
        out.append(f"canonical {pc.canonical!r} != {url!r}")
    for key in ("og:title", "og:description", "og:url", "og:image", "og:type", "twitter:card"):
        if not pc.meta.get(key):
            out.append(f"missing {key}")
    if pc.meta.get("og:url") and pc.meta["og:url"] != url:
        out.append("og:url does not match canonical")
    if pc.h1 != 1:
        out.append(f"{pc.h1} <h1> elements (want exactly 1)")
    if not pc.jsonld:
        out.append("missing schema.org JSON-LD")
    for block in pc.jsonld:
        try:
            data = json.loads(block)
        except ValueError as e:
            out.append(f"invalid JSON-LD: {e}")
            continue
        if data.get("@context") != "https://schema.org":
            out.append("JSON-LD @context must be https://schema.org")
    if url not in sitemap:
        out.append("page missing from sitemap.xml")
    return out


def main(root: Path) -> int:
    errors: list[str] = []
    files = [p for p in root.rglob("*") if p.is_file()]
    sm_path = root / "sitemap.xml"
    sitemap = set(re.findall(r"<loc>([^<]+)</loc>", sm_path.read_text(encoding="utf-8"))) if sm_path.exists() else set()
    if not sitemap:
        errors.append("sitemap.xml missing or empty")
    for loc in sitemap:
        name = loc[len(BASE_URL):] or "index.html"
        if not loc.startswith(BASE_URL) or not (root / name).is_file():
            errors.append(f"sitemap.xml: {loc} does not map to a page")
    if not files:
        print(f"no files under {root}")
        return 1

    for path in files:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pat in {**SECRET_PATTERNS, **INTERNAL_PATTERNS}.items():
            for m in re.finditer(pat, text):
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{rel}:{line}: {label}: {m.group(0)[:40]!r}")

        if path.suffix.lower() == ".html":
            pc = PageCheck()
            pc.feed(text)
            errors += [f"{rel}: {p}" for p in pc.problems]
            if not pc.has_csp:
                errors.append(f"{rel}: missing Content-Security-Policy meta tag")
            errors += [f"{rel}: SEO: {p}" for p in seo_problems(rel, pc, sitemap)]
            for link in pc.links:
                if link.startswith(("mailto:", "#")):
                    continue
                if link.startswith("http://"):
                    errors.append(f"{rel}: insecure link {link}")
                    continue
                if link.startswith("https://"):
                    continue
                target = link.split("#", 1)[0].split("?", 1)[0]
                if target.startswith("/AUDP-ECM-Website/"):
                    target = target[len("/AUDP-ECM-Website/"):]
                    base = root
                else:
                    base = path.parent
                candidate = (base / target) if target else base
                if candidate.is_dir():
                    candidate = candidate / "index.html"
                if not candidate.exists():
                    errors.append(f"{rel}: broken link {link}")

    if errors:
        print("content guard FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"content guard passed ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "site")))
