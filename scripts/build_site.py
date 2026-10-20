"""Build the static pages of SbruiceS/AUDP-ECM-Website.

Usage: python3 scripts/build_site.py site

Single source of truth for every page's head (security policy, SEO, social
metadata, schema.org graph), header and footer. CI rebuilds the site and fails
if the committed files differ, so pages can never drift apart.
"""
import html
import json
import sys
from pathlib import Path

SITE = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
BASE = "https://sbruices.github.io/AUDP-ECM-Website/"
TODAY = "2026-10-20"
EMAIL = "sbruicesingh@haclon.in"
LICENSE_URL = "https://github.com/SbruiceS/AUDP-ECM-Python/blob/main/LICENSE"

ORG_ID, PERSON_ID, SITE_ID, SW_ID = BASE + "#aspf", BASE + "sbruice-singh.html#person", BASE + "#website", BASE + "#audp-ecm"

ORG = {
    "@type": "Organization", "@id": ORG_ID,
    "name": "Agriculture Service of Product Farm",
    "alternateName": ["ASPF", "Agriculture Service of Product Farm (ASPF)"],
    "url": BASE + "about.html",
    "logo": {"@type": "ImageObject", "url": BASE + "assets/icon-512.png", "width": 512, "height": 512},
    "image": [BASE + "assets/logo-1200.png", BASE + "og-image.png"],
    "email": EMAIL,
    "description": ("Agriculture Service of Product Farm (ASPF) is an agriculture research and innovation "
                    "organisation building dependable data technology for farms: the AUDP device protocol "
                    "family and the AUDP-ECM error-correction engine for agricultural sensors and telemetry."),
    "knowsAbout": ["agriculture research", "agricultural innovation", "precision agriculture", "agritech",
                   "agricultural sensors", "farm telemetry", "error-correcting codes", "data reliability"],
    "member": {"@id": PERSON_ID},
    "contactPoint": {"@type": "ContactPoint", "contactType": "research collaboration and licensing", "email": EMAIL},
}
PERSON = {
    "@type": "Person", "@id": PERSON_ID,
    "name": "Sbruice Singh",
    "jobTitle": "Researcher",
    "description": ("Sbruice Singh is a researcher and the developer of AUDP-ECM at Agriculture Service of "
                    "Product Farm (ASPF), working on dependable data for agricultural sensors and telemetry."),
    "url": BASE + "sbruice-singh.html",
    "image": BASE + "og-image.png",
    "worksFor": {"@id": ORG_ID},
    "affiliation": {"@type": "Organization", "name": "High Association Of Science & Technology (HACLON)",
                    "url": "https://www.haclon.in"},
    "sameAs": ["https://github.com/SbruiceS", "https://x.com/Sbruice1"],
    "knowsAbout": ["agriculture research", "agricultural innovation", "error-correcting codes",
                   "Reed–Solomon codes", "finite fields", "agricultural telemetry", "Rust", "Python", "D"],
}
WEBSITE = {"@type": "WebSite", "@id": SITE_ID, "url": BASE, "inLanguage": "en",
           "name": "AUDP-ECM — Agriculture Service of Product Farm (ASPF)", "publisher": {"@id": ORG_ID}}
SOFTWARE = {
    "@type": "SoftwareApplication", "@id": SW_ID,
    "name": "AUDP-ECM", "alternateName": "AUDP Error Correction Mathematics Engine",
    "applicationCategory": "DeveloperApplication", "operatingSystem": "Linux, Windows, macOS",
    "description": ("Error-correction engine for agricultural sensors and telemetry: Reed–Solomon, BCH, "
                    "CRC-16 and burst-resilient framing, with Python and D bindings."),
    "url": BASE, "author": {"@id": PERSON_ID}, "publisher": {"@id": ORG_ID}, "license": LICENSE_URL,
    "image": BASE + "assets/logo-1200.png",
    "softwareVersion": "0.2.0",
    "downloadUrl": "https://github.com/SbruiceS/AUDP-ECM-Python/releases",
}

NAV = [("index.html", "Home"), ("index.html#demo", "Live demo"), ("about.html", "About ASPF"),
       ("research.html", "Research &amp; Innovation"), ("sbruice-singh.html", "Sbruice Singh")]

LOGO = """<picture class="logo-light">
          <source srcset="assets/logo-640.webp" type="image/webp">
          <img src="assets/logo-640.png" alt="AUDP-ECM logo" width="640" height="92" class="{cls}">
        </picture>
        <picture class="logo-dark">
          <source srcset="assets/logo-dark-640.webp" type="image/webp">
          <img src="assets/logo-dark-640.png" alt="AUDP-ECM logo" width="640" height="92" class="{cls}">
        </picture>"""

PAGES = {}


def page(fname, title, description, h1_label, page_type, body, crumbs, main_entity=None, og_type="website"):
    body = body.replace("{LOGO_HERO}", LOGO_HERO)
    url = BASE + ("" if fname == "index.html" else fname)
    webpage = {"@type": page_type, "@id": url + "#webpage", "url": url, "name": title, "description": description,
               "isPartOf": {"@id": SITE_ID}, "inLanguage": "en", "dateModified": TODAY,
               "primaryImageOfPage": {"@type": "ImageObject", "url": BASE + "og-image.png"},
               "breadcrumb": {"@id": url + "#breadcrumb"}}
    if main_entity:
        webpage["mainEntity"] = {"@id": main_entity}
    if page_type in ("AboutPage", "WebPage", "ProfilePage"):
        webpage["about"] = {"@id": ORG_ID} if page_type != "ProfilePage" else {"@id": PERSON_ID}
    bc = {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + ("" if f == "index.html" else f)}
        for i, (f, n) in enumerate(crumbs)]}
    graph = {"@context": "https://schema.org", "@graph": [WEBSITE, ORG, PERSON, SOFTWARE, webpage, bc]}
    nav = "\n".join(
        f'        <a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{t}</a>' for h, t in NAV)
    crumb_html = " <span aria-hidden=\"true\">›</span> ".join(
        (f'<a href="{f}">{html.escape(n)}</a>' if i < len(crumbs) - 1 else f'<span>{html.escape(n)}</span>')
        for i, (f, n) in enumerate(crumbs))
    breadcrumb_block = "" if fname == "index.html" else f"""
    <nav class="wrap crumbs" aria-label="Breadcrumb">{crumb_html}</nav>"""
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="author" content="Sbruice Singh">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#0b7285">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="icon" href="assets/icon-192.png" type="image/png" sizes="192x192">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">
  <link rel="sitemap" type="application/xml" href="sitemap.xml">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="AUDP-ECM — Agriculture Service of Product Farm">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE}og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="AUDP-ECM by Agriculture Service of Product Farm (ASPF): reliable data from every field sensor">
  <meta property="og:locale" content="en_GB">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:creator" content="@Sbruice1">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{BASE}og-image.png">
  <link rel="stylesheet" href="style.css">
  <script src="assets/app.js" defer></script>
  <script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=1)}
  </script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="top">
    <div class="wrap bar">
      <a class="brand" href="index.html" aria-label="AUDP-ECM home">
        {LOGO.format(cls="brand-logo")}
      </a>
      <div class="bar-actions">
        <button id="theme-toggle" class="icon-btn needs-js" type="button" aria-label="Change theme">
          <span class="i-sun" aria-hidden="true"></span><span class="i-moon" aria-hidden="true"></span>
        </button>
        <button id="nav-toggle" class="icon-btn menu needs-js" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Menu">
          <span aria-hidden="true"></span>
        </button>
      </div>
      <nav id="site-nav" aria-label="Main">
{nav}
      </nav>
    </div>
  </header>
{breadcrumb_block}
  <main id="main">
{body}
  </main>

  <footer class="foot">
    <div class="wrap">
      <p class="foot-logo">{LOGO.format(cls="foot-brand")}</p>
      <p><a href="about.html">Agriculture Service of Product Farm (ASPF)</a> ·
        <a href="research.html">Agriculture research &amp; innovation</a> ·
        <a href="sbruice-singh.html">Sbruice Singh</a></p>
      <p>© 2026 Sbruice Singh · Agriculture Service of Product Farm (ASPF). All rights reserved.</p>
      <p class="small">AUDP-ECM is proprietary software of ASPF and is not open source. Any use requires a
        written licence agreement with ASPF — licensing and research enquiries:
        <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <p class="small">This site is informational. It sets no cookies and loads no third-party resources.</p>
    </div>
  </footer>
</body>
</html>
"""
    (SITE / fname).write_text(doc, encoding="utf-8", newline="\n")
    PAGES[fname] = url
    assert h1_label


LOGO_HERO = """<picture class="logo-light">
          <source srcset="assets/logo-640.webp" type="image/webp">
          <img src="assets/logo-1200.png" alt="AUDP-ECM — AUDP Error Correction Mathematics Engine logo" width="1200" height="173" class="hero-img" fetchpriority="high">
        </picture>
        <picture class="logo-dark">
          <source srcset="assets/logo-dark-640.webp" type="image/webp">
          <img src="assets/logo-dark-640.png" alt="AUDP-ECM — AUDP Error Correction Mathematics Engine logo" width="640" height="92" class="hero-img">
        </picture>"""


# ---------------------------------------------------------------------------- index
page("index.html",
     "AUDP-ECM — Error Correction for Agricultural Telemetry | ASPF",
     "AUDP-ECM by Agriculture Service of Product Farm (ASPF): error correction for reliable data from "
     "agricultural sensors and farm telemetry, with Python and D bindings.",
     "home", "WebPage", """    <section class="hero hero-home">
      <div class="wrap">
        <div class="hero-logo">{LOGO_HERO}</div>
        <p class="eyebrow">Agriculture Service of Product Farm (ASPF) · AUDP Error Correction Mathematics Engine</p>
        <h1>Reliable data from <span class="grad">every field sensor.</span></h1>
        <p class="lead">AUDP-ECM turns noisy or incomplete sensor and telemetry frames into exact
          payloads using classical algebraic coding: Reed–Solomon, BCH, CRC-16 and burst-resilient
          interleaving. It is developed by <a href="about.html">Agriculture Service of Product Farm (ASPF)</a>
          as part of its <a href="research.html">agriculture research and innovation</a> work.</p>
        <p class="cta">
          <a class="btn" href="#demo">Try the live demo</a>
          <a class="btn ghost" href="https://github.com/SbruiceS/AUDP-ECM-Python">Python binding</a>
          <a class="btn ghost" href="https://github.com/SbruiceS/AUDP-ECM-D">D binding</a>
        </p>
      </div>
    </section>

    <section class="wrap stats reveal" aria-label="Key facts">
      <div class="stat"><strong>2e + s ≤ n − k</strong><span>errors and erasures corrected</span></div>
      <div class="stat"><strong>2</strong><span>language bindings: Python &amp; D</span></div>
      <div class="stat"><strong>4</strong><span>wheel platforms incl. ARM64</span></div>
      <div class="stat"><strong>0</strong><span>unsafe code in the bindings</span></div>
    </section>

    <section id="demo" class="wrap demo reveal">
      <h2>Live demo: watch errors get corrected</h2>
      <p>This runs entirely in your browser — nothing is sent anywhere. Type a sensor message, choose how much
        parity to add, then damage the transmitted symbols and see Reed–Solomon repair them.</p>
      <noscript><p class="note">The live demo needs JavaScript. Everything else on this site works without it.</p></noscript>
      <div id="demo-app" class="demo-app" hidden>
        <div class="demo-controls">
          <label class="field"><span>Sensor message</span>
            <input id="demo-msg" type="text" maxlength="48" value="node=17;soil=0.42;temp=21.7" spellcheck="false" autocomplete="off">
          </label>
          <label class="field"><span>Parity symbols: <output id="demo-parity-out" for="demo-parity">8</output>
            → corrects up to <output id="demo-t">4</output> errors</span>
            <input id="demo-parity" type="range" min="2" max="32" step="2" value="8">
          </label>
        </div>
        <div class="demo-actions">
          <button class="btn small" id="demo-one" type="button">Corrupt 1 symbol</button>
          <button class="btn small" id="demo-noise" type="button">Add random noise</button>
          <button class="btn small" id="demo-burst" type="button">Burst of t symbols</button>
          <button class="btn small ghost" id="demo-reset" type="button">Reset channel</button>
        </div>
        <p class="legend"><span class="sym parity">pp</span> parity <span class="sym data">dd</span> data
          <span class="sym bad">xx</span> corrupted <span class="sym bad fixed">ok</span> repaired — click any symbol to toggle damage</p>
        <div id="demo-grid" class="demo-grid" aria-label="Transmitted symbols (hex)"></div>
        <p id="demo-status" class="demo-status" role="status" aria-live="polite"></p>
        <p class="demo-out">Decoded payload: <code id="demo-decoded"></code></p>
      </div>
    </section>

    <section id="what" class="wrap reveal">
      <h2>What it is</h2>
      <p>Field devices in agriculture send small messages over radio, long cables and shared
        channels. Interference flips symbols, bursts wipe out runs of bytes, and weak signals
        leave values unknown. AUDP-ECM is the software layer that detects and repairs this
        damage before the data reaches farm management, research analysis or automated control.</p>
      <div class="grid three">
        <div class="card"><h3>Detect</h3><p>CRC-16 and syndromes reveal that a frame was corrupted.</p></div>
        <div class="card"><h3>Correct</h3><p>Reed–Solomon and BCH repair a bounded number of wrong symbols or bits.</p></div>
        <div class="card"><h3>Recover</h3><p>Known-bad symbols are treated as erasures, which cost half as much redundancy as unknown errors.</p></div>
      </div>
      <p class="note"><strong>Not cryptography.</strong> Error correction handles channel noise. It does not
        authenticate data or resist a deliberate attacker; use a MAC or AEAD for that.</p>
    </section>

    <section id="capabilities" class="wrap reveal">
      <h2>Capabilities</h2>
      <div class="table-scroll"><table>
        <thead><tr><th>Feature</th><th>What you get</th></tr></thead>
        <tbody>
          <tr><td>Reed–Solomon over GF(256)</td><td>Corrects <em>e</em> unknown errors and <em>s</em> erasures whenever 2e + s ≤ n − k; two independent decoders</td></tr>
          <tr><td>Burst-resilient framing</td><td>Exact-length payload back; any contiguous burst up to <em>depth × t</em> symbols corrected</td></tr>
          <tr><td>Binary BCH</td><td>Bit-level correction for bit-oriented links</td></tr>
          <tr><td>CRC-16/CCITT-FALSE</td><td>Residual-error detection after decoding</td></tr>
          <tr><td>Soft information</td><td>Low-reliability symbols become erasures, bounded to the code's budget</td></tr>
          <tr><td>Channel models</td><td>Seeded symbol-error, burst and erasure channels for simulation</td></tr>
        </tbody>
      </table></div>
    </section>

    <section id="bindings" class="wrap reveal">
      <h2>Bindings</h2>
      <div class="grid two">
        <article class="card">
          <h3>Python</h3>
          <p>CPython ≥ 3.10 · Linux, Windows, macOS · no runtime dependencies.</p>
<pre><code>import audp_ecm as ecm

rs = ecm.ReedSolomon(31, 23)        # corrects 4 errors
cw = rs.encode(bytes(23))
rx = bytearray(cw); rx[3] ^= 0xFF
assert rs.decode(rx).data == bytes(23)

codec = ecm.BurstCodec.for_burst(31, 23, 64, 16)
tx = codec.protect(b"node=17;temp=21.7")
assert codec.recover(tx) == b"node=17;temp=21.7"</code></pre>
          <p><a href="https://github.com/SbruiceS/AUDP-ECM-Python">Repository &amp; documentation →</a></p>
        </article>
        <article class="card">
          <h3>D</h3>
          <p>DMD or LDC · <code>@safe</code> API · RAII-managed resources.</p>
<pre><code>import audp_ecm;

auto rs = ReedSolomon(31, 23);
auto cw = rs.encode(new ubyte[23]);
cw[0] ^= 0xFF;
assert(rs.decode(cw).correctedSymbols == 1);

auto msg = cast(immutable(ubyte)[]) "node=17;temp=21.7";
auto codec = BurstCodec(31, 23, 4);
assert(codec.recover(codec.protect(msg)) == msg);</code></pre>
          <p><a href="https://github.com/SbruiceS/AUDP-ECM-D">Repository &amp; documentation →</a></p>
        </article>
      </div>
    </section>

    <section id="quality" class="wrap reveal">
      <h2>Engineering quality</h2>
      <ul class="checks">
        <li>Memory-safe by construction: no unsafe code in the bindings; the D API is <code>@safe</code>.</li>
        <li>Invalid input is rejected with typed errors — never a crash, never silent corruption.</li>
        <li>Results are verified before they are returned; burst frames carry a CRC as a second check.</li>
        <li>Known-answer, differential, property-based and adversarial tests run on Linux, Windows and macOS.</li>
        <li>Dependencies are audited continuously; releases ship checksums and signed build provenance.</li>
      </ul>
    </section>

    <section id="security" class="wrap reveal">
      <h2>Security &amp; contact</h2>
      <p>Found a vulnerability? Please report it privately through GitHub's
        <em>Report a vulnerability</em> button on the affected repository, or by email to
        <a href="mailto:sbruicesingh@haclon.in">sbruicesingh@haclon.in</a>. Do not open a public issue.
        See also <a href=".well-known/security.txt">security.txt</a>.</p>
    </section>""", [("index.html", "Home")], main_entity=SW_ID)

# ---------------------------------------------------------------------------- about ASPF
page("about.html",
     "Agriculture Service of Product Farm (ASPF) — Research & Innovation",
     "Agriculture Service of Product Farm (ASPF) is an agriculture research and innovation organisation "
     "building dependable data technology for farms.",
     "about", "AboutPage", """    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">About the organisation</p>
        <h1>Agriculture Service of Product Farm (ASPF)</h1>
        <p class="lead">Agriculture Service of Product Farm (ASPF) is an agriculture research and innovation
          organisation focused on one problem that every modern farm depends on: <strong>data that arrives
          complete and correct</strong>, from the sensor in the field to the decision that uses it.</p>
      </div>
    </section>

    <section class="wrap">
      <h2>What ASPF works on</h2>
      <div class="grid three">
        <div class="card"><h3>AUDP — ASPF Unified Device Protocol</h3><p>A protocol family for agricultural devices: sensors, controllers and gateways exchanging small, frequent messages over constrained links.</p></div>
        <div class="card"><h3>AUDP-ECM</h3><p>The error-correction engine of AUDP: detects, corrects and recovers damaged telemetry so soil, climate and equipment data stay trustworthy. <a href="index.html">Learn more →</a></p></div>
        <div class="card"><h3>Research &amp; innovation</h3><p>Applied research on reliable farm telemetry, signal quality and data integrity in real agricultural environments. <a href="research.html">Research areas →</a></p></div>
      </div>
    </section>

    <section class="wrap">
      <h2>Where it is used</h2>
      <ul class="checks">
        <li>Agricultural sensors: soil moisture, temperature, humidity, water and crop monitoring</li>
        <li>Farm telemetry over radio, long cables and shared or congested channels</li>
        <li>Distributed field devices, gateways and firmware communication links</li>
        <li>Constrained networks where retransmission is slow, costly or impossible</li>
      </ul>
    </section>

    <section class="wrap">
      <h2>Principles</h2>
      <ul class="checks">
        <li><strong>Mathematics first</strong> — proven coding theory rather than black-box hardware.</li>
        <li><strong>Correctness you can check</strong> — every recovered value is verified before it is used.</li>
        <li><strong>Safety by design</strong> — memory-safe software, strict input validation, continuous testing.</li>
        <li><strong>Honest scope</strong> — error correction protects against noise, not attackers; security layers stay separate.</li>
      </ul>
    </section>

    <section class="wrap">
      <h2>People</h2>
      <div class="card">
        <h3><a href="sbruice-singh.html">Sbruice Singh</a></h3>
        <p>Researcher and developer of AUDP-ECM at Agriculture Service of Product Farm (ASPF).</p>
      </div>
    </section>

    <section class="wrap">
      <h2>Collaborate with ASPF</h2>
      <p>ASPF welcomes contact from agriculture research organisations, universities, agritech innovators and
        farm operators interested in dependable field data. AUDP-ECM is proprietary software; evaluation and
        licensing are arranged by written agreement.</p>
      <p class="cta"><a class="btn" href="mailto:sbruicesingh@haclon.in">Contact ASPF</a>
        <a class="btn ghost" href="research.html">Research &amp; innovation</a></p>
    </section>""", [("index.html", "Home"), ("about.html", "About ASPF")], main_entity=ORG_ID)

# ---------------------------------------------------------------------------- research & innovation
page("research.html",
     "Agriculture Research & Innovation — Reliable Farm Data | ASPF",
     "Agriculture research and innovation at Agriculture Service of Product Farm (ASPF): reliable farm "
     "telemetry, sensor data quality and precision agriculture.",
     "research", "WebPage", """    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Agriculture Service of Product Farm (ASPF)</p>
        <h1>Agriculture research &amp; innovation</h1>
        <p class="lead">ASPF's research turns the mathematics of reliable communication into practical
          tools for agriculture, so that precision farming, crop research and automated field systems can
          rely on the data they collect.</p>
      </div>
    </section>

    <section class="wrap">
      <h2>Research areas</h2>
      <div class="grid two">
        <article class="card"><h3>Reliable farm telemetry</h3>
          <p>Rural radio links suffer bursts of interference from weather, machinery and distance. ASPF studies
            how to spread data so that long bursts remain correctable, and measures the effect under realistic
            channel conditions.</p></article>
        <article class="card"><h3>Sensor signal quality</h3>
          <p>Receivers often know which values are doubtful. Using that knowledge lets a decoder recover roughly
            twice as much damaged data, an approach ASPF applies to low-power agricultural sensors.</p></article>
        <article class="card"><h3>Channel modelling &amp; simulation</h3>
          <p>Reproducible simulations of noise, bursts and dropouts in farm environments, used to choose the right
            amount of protection for each device and link.</p></article>
        <article class="card"><h3>Trustworthy agricultural software</h3>
          <p>Memory-safe implementations, exhaustive and property-based testing, and verified results, so
            that field data systems fail safely instead of silently.</p></article>
      </div>
    </section>

    <section class="wrap">
      <h2>From research to practice</h2>
      <p>Research results flow into <a href="index.html">AUDP-ECM</a>, the error-correction engine of the
        ASPF Unified Device Protocol, and its <a href="https://github.com/SbruiceS/AUDP-ECM-Python">Python</a>
        and <a href="https://github.com/SbruiceS/AUDP-ECM-D">D</a> bindings used by agricultural data pipelines.</p>
    </section>

    <section class="wrap">
      <h2>Work with us</h2>
      <p>Agriculture research organisations, universities, agritech start-ups and innovation programmes are
        welcome to get in touch about joint research, field trials or evaluation of AUDP-ECM.</p>
      <p class="cta"><a class="btn" href="mailto:sbruicesingh@haclon.in">Contact ASPF research</a>
        <a class="btn ghost" href="about.html">About ASPF</a></p>
    </section>""", [("index.html", "Home"), ("research.html", "Research & Innovation")])

# ---------------------------------------------------------------------------- person
page("sbruice-singh.html",
     "Sbruice Singh — Researcher, Agriculture Service of Product Farm (ASPF)",
     "Sbruice Singh is a researcher and the developer of AUDP-ECM at Agriculture Service of Product Farm "
     "(ASPF), working on reliable agricultural sensor data.",
     "person", "ProfilePage", """    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Researcher · Agriculture Service of Product Farm (ASPF)</p>
        <h1>Sbruice Singh</h1>
        <p class="lead">Sbruice Singh is a researcher and the developer of AUDP-ECM, the error-correction
          engine of the ASPF Unified Device Protocol at
          <a href="about.html">Agriculture Service of Product Farm (ASPF)</a>.</p>
      </div>
    </section>

    <section class="wrap">
      <h2>Work</h2>
      <ul class="checks">
        <li><a href="index.html">AUDP-ECM</a> — error correction for agricultural sensors and farm telemetry.</li>
        <li><a href="https://github.com/SbruiceS/AUDP-ECM-Python">AUDP-ECM for Python</a> and
          <a href="https://github.com/SbruiceS/AUDP-ECM-D">AUDP-ECM for D</a> — safe language bindings.</li>
        <li><a href="research.html">Agriculture research &amp; innovation</a> at ASPF — reliable farm telemetry and data integrity.</li>
      </ul>
    </section>

    <section class="wrap">
      <h2>Areas of expertise</h2>
      <p>Error-correcting codes (Reed–Solomon, BCH), finite-field mathematics, agricultural telemetry and
        sensor networks, and safe systems software in Rust, Python and D.</p>
    </section>

    <section class="wrap">
      <h2>Affiliations &amp; profiles</h2>
      <ul class="checks">
        <li>Agriculture Service of Product Farm (ASPF) — <a href="about.html">about the organisation</a></li>
        <li>High Association Of Science &amp; Technology (HACLON) — <a href="https://www.haclon.in" rel="me">haclon.in</a></li>
        <li>GitHub — <a href="https://github.com/SbruiceS" rel="me">github.com/SbruiceS</a></li>
        <li>X — <a href="https://x.com/Sbruice1" rel="me">@Sbruice1</a></li>
        <li>Email — <a href="mailto:sbruicesingh@haclon.in">sbruicesingh@haclon.in</a></li>
      </ul>
    </section>""", [("index.html", "Home"), ("sbruice-singh.html", "Sbruice Singh")],
     main_entity=PERSON_ID, og_type="profile")

# ---------------------------------------------------------------------------- 404 (absolute paths: served at any depth)
P = "/AUDP-ECM-Website/"
(SITE / "404.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="robots" content="noindex">
  <title>Page not found — AUDP-ECM</title>
  <link rel="icon" href="{P}favicon.ico" sizes="any">
  <link rel="stylesheet" href="{P}style.css">
  <script src="{P}assets/app.js" defer></script>
</head>
<body>
  <main id="main" class="wrap notfound">
    <p class="hero-logo"><picture class="logo-light"><img src="{P}assets/logo-640.png" alt="AUDP-ECM logo" width="640" height="92" class="hero-img"></picture>
      <picture class="logo-dark"><img src="{P}assets/logo-dark-640.png" alt="AUDP-ECM logo" width="640" height="92" class="hero-img"></picture></p>
    <h1>Page not found</h1>
    <p class="lead">The page you are looking for does not exist.</p>
    <p class="cta"><a class="btn" href="{P}">AUDP-ECM home</a>
      <a class="btn ghost" href="{P}about.html">About ASPF</a></p>
  </main>
</body>
</html>
""", encoding="utf-8", newline="\n")

# ---------------------------------------------------------------------------- web app manifest
(SITE / "site.webmanifest").write_text(json.dumps({
    "name": "AUDP-ECM — Agriculture Service of Product Farm",
    "short_name": "AUDP-ECM",
    "description": "Error correction for reliable agricultural sensor and telemetry data.",
    "start_url": P, "scope": P, "display": "standalone",
    "background_color": "#ffffff", "theme_color": "#0b7285",
    "icons": [
        {"src": P + "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": P + "assets/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    ],
}, indent=2) + "\n", encoding="utf-8", newline="\n")

# ---------------------------------------------------------------------------- sitemap + robots
urls = "\n".join(
    f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n"
    f"    <priority>{'1.0' if f == 'index.html' else '0.8'}</priority>\n  </url>" for f, u in PAGES.items())
(SITE / "sitemap.xml").write_text(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
    encoding="utf-8", newline="\n")
(SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8", newline="\n")
print("wrote", ", ".join(PAGES), "+ sitemap.xml, robots.txt")
