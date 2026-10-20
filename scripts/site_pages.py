"""Documentation pages: how it works (mathematics), security model, evidence, benchmarks.

Called from build_site.py with its `page()` function so every page shares the
same head (CSP, SEO, schema.org), header and footer. Only public conventions
and results are described here — never internal design of the private core.
"""
import html
import json
from pathlib import Path

PY_REPO = "https://github.com/SbruiceS/AUDP-ECM-Python"
D_REPO = "https://github.com/SbruiceS/AUDP-ECM-D"
DATA = Path(__file__).resolve().parent.parent / "data" / "benchmarks"


def _how_it_works():
    return """    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Mathematics &amp; conventions</p>
        <h1>How AUDP-ECM works</h1>
        <p class="lead">The exact finite-field conventions, code construction, decoding guarantees and framing
          rules, so results can be verified independently and implementations can interoperate.</p>
      </div>
    </section>

    <section class="wrap doc reveal" id="field">
      <h2>1 · The finite field GF(2<sup>8</sup>)</h2>
      <ul class="checks">
        <li>Symbols are bytes, interpreted as elements of GF(2<sup>8</sup>) = GF(2)[x] / p(x) with the primitive
          polynomial <strong>p(x) = x<sup>8</sup> + x<sup>4</sup> + x<sup>3</sup> + x<sup>2</sup> + 1</strong> (0x11D).</li>
        <li>Bit <em>i</em> of a byte is the coefficient of x<sup><em>i</em></sup>. The primitive element is
          <strong>α = x</strong> (byte 0x02); every non-zero element is α<sup><em>e</em></sup> for a unique 0 ≤ e ≤ 254.</li>
        <li>Addition is bitwise XOR. Multiplication is polynomial multiplication reduced modulo p(x),
          for example 0x53 · 0xCA = 0x8F and 0x80 · 0x02 = 0x1D.</li>
      </ul>
    </section>

    <section class="wrap doc reveal" id="codes">
      <h2>2 · Reed–Solomon code parameters</h2>
      <div class="table-scroll"><table>
        <thead><tr><th>Symbol</th><th>Meaning</th><th>Constraint</th></tr></thead>
        <tbody>
          <tr><td><em>n</em></td><td>codeword length in bytes</td><td>2 ≤ n ≤ 255</td></tr>
          <tr><td><em>k</em></td><td>data bytes per codeword</td><td>1 ≤ k &lt; n</td></tr>
          <tr><td><em>r</em> = n − k</td><td>parity bytes</td><td>—</td></tr>
          <tr><td><em>t</em> = ⌊r / 2⌋</td><td>unknown symbol errors always corrected</td><td>—</td></tr>
          <tr><td><em>d</em> = n − k + 1</td><td>minimum distance (maximum distance separable)</td><td>meets the Singleton bound</td></tr>
        </tbody>
      </table></div>
    </section>

    <section class="wrap doc reveal" id="encoding">
      <h2>3 · Generator polynomial and systematic encoding</h2>
      <p>The generator has the <em>r</em> consecutive roots α<sup>1</sup> … α<sup>r</sup> (first consecutive root b = 1):</p>
      <p class="formula">g(x) = (x − α)(x − α<sup>2</sup>) ··· (x − α<sup>r</sup>), &nbsp; deg g = r, monic.</p>
      <p>For data bytes m<sub>0</sub> … m<sub>k−1</sub>, with m(x) = Σ m<sub>j</sub> x<sup>j</sup>, the codeword is</p>
      <p class="formula">c(x) = x<sup>r</sup>·m(x) + p(x), &nbsp;&nbsp; p(x) = x<sup>r</sup>·m(x) mod g(x).</p>
      <p><strong>Byte layout:</strong> byte <em>j</em> of the transmitted codeword is the coefficient of x<sup>j</sup>.
        The r parity bytes come first (j &lt; r), followed by the k data bytes unchanged. Every codeword satisfies
        c(α<sup>i</sup>) = 0 for i = 1 … r.</p>
    </section>

    <section class="wrap doc reveal" id="decoding">
      <h2>4 · Decoding</h2>
      <ol class="steps">
        <li><strong>Syndromes</strong> S<sub>i</sub> = y(α<sup>i</sup>), i = 1 … r, of the received word y. All zero ⇔ y is a codeword,
          so no correction is needed.</li>
        <li><strong>Error locator</strong> Λ(x) from the key equation S(x)·Λ(x) ≡ Ω(x) (mod x<sup>r</sup>), solved by the
          <em>Berlekamp–Massey</em> algorithm. An independent <em>Euclidean-algorithm</em> decoder solves the same equation and is
          cross-checked against it in testing.</li>
        <li><strong>Erasures</strong> (known-bad positions) enter as the erasure locator Γ(x) = Π (1 − α<sup>j</sup>x) through
          modified (Forney) syndromes. The combined errata locator is Λ<sub>e</sub>(x)·Γ(x).</li>
        <li><strong>Chien search:</strong> error positions are the j with Λ(α<sup>−j</sup>) = 0. The number of roots must equal deg Λ.</li>
        <li><strong>Forney's formula</strong> gives each error value: e<sub>j</sub> = Ω(α<sup>−j</sup>) / Λ′(α<sup>−j</sup>).</li>
        <li><strong>Verification:</strong> a result is returned only if the corrected word is a valid codeword. Otherwise
          decoding fails with an explicit error.</li>
      </ol>
      <p class="note"><strong>Guarantee.</strong> With <em>e</em> unknown errors and <em>s</em> erasures, decoding is unique and
        correct whenever <strong>2e + s ≤ n − k</strong>. An erasure costs one parity byte; an unknown error costs two.</p>
    </section>

    <section class="wrap doc reveal" id="limits">
      <h2>5 · Correction limits: what happens beyond capacity</h2>
      <p>When 2e + s &gt; n − k, no decoder can guarantee the original data. Exactly one of three things happens:</p>
      <div class="grid three">
        <div class="card"><h3>Rejected (most common)</h3><p>No codeword lies close enough to the received word. Decoding fails
          with an explicit error, so the frame is <strong>detected as bad</strong> and never silently accepted.</p></div>
        <div class="card"><h3>Miscorrected (rare)</h3><p>The damage moved the word within <em>t</em> symbols of a
          <em>different</em> valid codeword, which the decoder then returns. This is a fundamental property of every
          error-correcting code, not an implementation bug.</p></div>
        <div class="card"><h3>Caught by CRC</h3><p>Burst framing adds a CRC-16 over the payload. A miscorrection must also pass that
          16-bit check, so wrong payloads are rejected except with probability about 2<sup>−16</sup>.</p></div>
      </div>
      <p><strong>Measured:</strong> across 1,800 test frames with exactly <em>t</em> + 1 errors, using codes with 2–32 parity bytes,
        98.4 % were rejected and 1.6 % miscorrected before any CRC. Miscorrection becomes rarer as the parity count grows.
        You can reproduce both outcomes in the <a href="index.html#demo">live demo</a> by corrupting more than <em>t</em> symbols.</p>
      <p><strong>Erasure caveat:</strong> each marked erasure consumes budget. Marking too many positions as unreliable
        can turn a correctable frame into an uncorrectable one, so marking is bounded to n − k.</p>
    </section>

    <section class="wrap doc reveal" id="burst">
      <h2>6 · Burst-resilient framing and its assumptions</h2>
      <p class="formula">frame = len (u16, big-endian) ‖ payload ‖ CRC-16(len ‖ payload), zero-padded to depth·k bytes</p>
      <p>The frame is split into <em>depth</em> consecutive k-byte blocks, each encoded as one RS(n, k) codeword. Byte j of codeword i
        is transmitted at position <strong>j·depth + i</strong>. A contiguous burst of L bytes therefore touches at most
        ⌈L / depth⌉ bytes of any one codeword, so <strong>every burst of up to depth·t bytes is corrected</strong>.</p>
      <p>Recovery returns the exact payload (its length is part of the frame) after the CRC matches. The guarantees assume:</p>
      <ul class="checks">
        <li><strong>Symbol synchronisation:</strong> the receiver gets exactly n·depth bytes in order. Insertions, deletions
          and bit slips are not corrected and must be handled by the link layer.</li>
        <li><strong>Per-codeword budget:</strong> the rule is that every codeword individually satisfies 2e + s ≤ n − k.
          A single burst of ≤ depth·t bytes always meets it; several bursts in one frame may not.</li>
        <li><strong>Erasure positions</strong>, when supplied, index the transmitted stream. They are mapped to codewords automatically.</li>
        <li><strong>Payload size</strong> ≤ depth·k − 4 bytes and ≤ 65,535 bytes. The receiver buffers n·depth bytes,
          which adds latency equal to one full frame.</li>
      </ul>
    </section>

    <section class="wrap doc reveal" id="crc">
      <h2>7 · CRC-16 parameters</h2>
      <p>CRC-16/CCITT-FALSE: polynomial 0x1021, initial value 0xFFFF, no input or output reflection, no final XOR.
        It is appended big-endian. Check value: CRC("123456789") = <strong>0x29B1</strong>. A CRC detects accidental errors;
        it does not authenticate data (see <a href="security.html">security model</a>).</p>
    </section>

    <section class="wrap doc reveal" id="vectors">
      <h2>8 · Test vectors</h2>
      <div class="table-scroll"><table>
        <thead><tr><th>Item</th><th>Input</th><th>Expected</th></tr></thead>
        <tbody>
          <tr><td>GF(2<sup>8</sup>) multiply</td><td>0x53 · 0xCA · 0xFF·0xFF · 0x80·0x02</td><td>0x8F · 0xE2 · 0x1D</td></tr>
          <tr><td>Generator, r = 4</td><td>g(x) low → high</td><td><code>74 E7 D8 1E 01</code></td></tr>
          <tr><td>RS(7,3) codeword</td><td>data <code>01 02 03</code></td><td><code>17 3A 51 52 01 02 03</code></td></tr>
          <tr><td>RS(15,11) parity</td><td>data <code>01 02 … 0B</code></td><td><code>08 11 65 70</code></td></tr>
          <tr><td>CRC-16/CCITT-FALSE</td><td>ASCII "123456789"</td><td><code>0x29B1</code></td></tr>
        </tbody>
      </table></div>
      <p>These vectors are checked in the Python, D and in-browser test suites. The in-browser codec is byte-identical to the
        library on 300 randomised cross-checks.</p>
    </section>"""


def _security():
    return """    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Security model</p>
        <h1>Error correction is not security</h1>
        <p class="lead">AUDP-ECM protects data against <strong>accidental</strong> damage: noise, interference, fading
          and dropped bytes. It does not protect against a <strong>deliberate</strong> attacker. Both matter, and they need
          different tools.</p>
      </div>
    </section>

    <section class="wrap doc reveal">
      <h2>What it does and does not protect against</h2>
      <div class="table-scroll"><table>
        <thead><tr><th>Threat</th><th>AUDP-ECM</th><th>What you need</th></tr></thead>
        <tbody>
          <tr><td>Random noise, interference, fading</td><td>✔ corrected up to capacity, detected beyond it</td><td>—</td></tr>
          <tr><td>Bursts of lost or garbled bytes</td><td>✔ corrected up to depth·t with burst framing</td><td>—</td></tr>
          <tr><td>Deliberate modification of a frame</td><td>✘ an attacker can craft valid codewords and CRCs</td><td>MAC (e.g. HMAC-SHA-256) or AEAD</td></tr>
          <tr><td>Forged frames from an impostor</td><td>✘</td><td>Authentication: MAC/AEAD with per-device keys, or signatures</td></tr>
          <tr><td>Replay of old frames</td><td>✘</td><td>Sequence numbers or nonces inside the authenticated data</td></tr>
          <tr><td>Eavesdropping</td><td>✘</td><td>Encryption: AEAD such as AES-GCM or ChaCha20-Poly1305</td></tr>
          <tr><td>Jamming / denial of service</td><td>partial: tolerates noise up to capacity</td><td>Physical-layer and network measures</td></tr>
        </tbody>
      </table></div>
      <p class="note"><strong>A CRC is not a MAC.</strong> CRC-16 and Reed–Solomon parity are public, linear functions. Anyone can
        recompute them after changing the data, so a matching CRC proves only the absence of <em>accidental</em> errors.</p>
    </section>

    <section class="wrap doc reveal">
      <h2>Recommended layering</h2>
      <ol class="steps">
        <li><strong>Sender:</strong> encrypt and authenticate the payload with an AEAD (or append a MAC). Include a sequence number.</li>
        <li><strong>Then</strong> protect the authenticated bytes with AUDP-ECM (error correction is the outermost layer on the link).</li>
        <li><strong>Receiver:</strong> decode with AUDP-ECM first. If that fails, drop the frame or request a retransmission.</li>
        <li><strong>Then</strong> verify and decrypt with the AEAD. Reject the frame if authentication fails, or if the sequence number repeats.</li>
      </ol>
      <p>This order lets error correction repair channel damage before the authentication check, which would otherwise
        reject every frame with a single flipped bit.</p>
    </section>

    <section class="wrap doc reveal">
      <h2>How the library itself is hardened</h2>
      <ul class="checks">
        <li>Memory-safe implementation. The bindings forbid unsafe code (Python) or expose only <code>@safe</code> APIs (D).</li>
        <li>Every input is validated, and failures raise typed errors. Malformed input never crashes or corrupts memory.</li>
        <li>Decoded data is verified before it is returned. Burst frames add a CRC-16 as a second check.</li>
        <li>Bounded resource use: input sizes, interleave depth and erasure lists are capped.</li>
        <li>Fuzzing, property-based tests and memory-safety checking in continuous integration. Dependencies are audited.</li>
        <li>Release artifacts carry SHA-256 checksums and signed build-provenance attestations.</li>
      </ul>
    </section>

    <section class="wrap doc reveal">
      <h2>Reporting a vulnerability</h2>
      <p>Use GitHub's <em>Report a vulnerability</em> button on the affected repository, or email
        <a href="mailto:sbruicesingh@haclon.in">sbruicesingh@haclon.in</a>. Please do not open a public issue.
        See <a href=".well-known/security.txt">security.txt</a>.</p>
    </section>"""


def _evidence():
    return f"""    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Documentation &amp; evidence</p>
        <h1>API docs, testing, platforms and releases</h1>
        <p class="lead">Everything needed to evaluate AUDP-ECM: reference documentation, how it is tested,
          where it runs, and verifiable release artifacts.</p>
      </div>
    </section>

    <section class="wrap doc reveal">
      <h2>API documentation</h2>
      <div class="grid two">
        <div class="card"><h3>Python</h3><p>Classes, functions, errors and limits.</p>
          <p><a href="{PY_REPO}/blob/main/docs/api.md">API reference</a> · <a href="{PY_REPO}/blob/main/docs/security.md">security model</a> ·
          <a href="{PY_REPO}/blob/main/docs/development.md">building &amp; CI</a> · <a href="{PY_REPO}/blob/main/docs/releasing.md">releases</a></p></div>
        <div class="card"><h3>D</h3><p>The <code>@safe</code> API, exceptions and linking on each platform.</p>
          <p><a href="{D_REPO}/blob/main/docs/api.md">API reference</a> · <a href="{D_REPO}/blob/main/docs/security.md">security model</a> ·
          <a href="{D_REPO}/blob/main/docs/building.md">building &amp; linking</a> · <a href="{D_REPO}/blob/main/docs/releasing.md">releases</a></p></div>
      </div>
      <p>Mathematical conventions and guarantees: <a href="how-it-works.html">how it works</a>.</p>
    </section>

    <section class="wrap doc reveal">
      <h2>Test methodology</h2>
      <div class="table-scroll"><table>
        <thead><tr><th>Kind</th><th>What it establishes</th><th>Where</th></tr></thead>
        <tbody>
          <tr><td>Known-answer vectors</td><td>Field arithmetic, generator, codewords and CRC match the published values</td><td>core, Python, D, browser</td></tr>
          <tr><td>Exhaustive small cases</td><td>Every single-symbol error in RS(7,3), corrected by both decoders</td><td>core</td></tr>
          <tr><td>Errata budget sweep</td><td>Every combination 2e + s ≤ n − k decodes exactly</td><td>core, Python, D</td></tr>
          <tr><td>Property-based tests</td><td>Random messages, error patterns and bursts within capacity always recover</td><td>core, Python (Hypothesis)</td></tr>
          <tr><td>Differential tests</td><td>Two independent decoders agree; table arithmetic equals a reference; language bindings equal the native library</td><td>core, browser (300 cross-checks)</td></tr>
          <tr><td>Adversarial and fuzz testing</td><td>Garbage input, wrong lengths and bad indices produce errors, never crashes</td><td>core (coverage-guided fuzzing), Python, D</td></tr>
          <tr><td>Soundness of verification</td><td>Any successful decode returns a valid codeword within the claimed distance</td><td>core</td></tr>
          <tr><td>Memory-safety checking</td><td>The native boundary is checked under an undefined-behaviour interpreter</td><td>core CI</td></tr>
          <tr><td>Concurrency</td><td>Shared decoder objects are safe across threads</td><td>Python, D</td></tr>
          <tr><td>Release-artifact tests</td><td>Each built wheel is installed and tested before it is released</td><td>Python CD</td></tr>
        </tbody>
      </table></div>
      <p>Continuous integration runs on every change: Python on Linux, Windows and macOS with Python 3.10, 3.12 and 3.13;
        D with DMD and LDC on Linux, Windows and macOS. Changes reach the main branch only through reviewed pull requests
        whose required checks pass.</p>
    </section>

    <section class="wrap doc reveal">
      <h2>Supported platforms</h2>
      <div class="table-scroll"><table>
        <thead><tr><th>Binding</th><th>Platforms</th><th>Requirements</th></tr></thead>
        <tbody>
          <tr><td>Python</td><td>Linux x86_64 and aarch64 (manylinux2014), Windows x64, macOS universal2 (Intel and Apple Silicon)</td><td>CPython ≥ 3.10 (one abi3 wheel per platform); no runtime dependencies</td></tr>
          <tr><td>D</td><td>Linux, Windows (DMD, LDC); macOS (LDC)</td><td>DMD ≥ 2.105 or LDC ≥ 1.35; native library ABI ≥ 2</td></tr>
        </tbody>
      </table></div>
    </section>

    <section class="wrap doc reveal">
      <h2>Releases</h2>
      <div class="table-scroll"><table>
        <thead><tr><th>Package</th><th>Version</th><th>Artifacts</th><th>Notes</th></tr></thead>
        <tbody>
          <tr><td>audp-ecm (Python)</td><td><a href="{PY_REPO}/releases/tag/v0.2.0">v0.2.0</a></td><td>4 wheels, SHA256SUMS, build provenance</td><td>Every wheel is tested after install before release</td></tr>
          <tr><td>audp-ecm (D)</td><td><a href="{D_REPO}/releases/tag/v0.2.0">v0.2.0</a></td><td>source archive, C header, SHA256SUMS, build provenance</td><td>Full test matrix before release</td></tr>
        </tbody>
      </table></div>
      <p><strong>Verify a download:</strong></p>
<pre><code>sha256sum -c SHA256SUMS
gh attestation verify &lt;file&gt; --repo SbruiceS/AUDP-ECM-Python   # or AUDP-ECM-D</code></pre>
      <p>Release tags are immutable, and the main branches are protected: changes land only through pull requests
        whose required checks pass. AUDP-ECM is proprietary software of ASPF; use requires a written licence agreement.</p>
    </section>"""


def _bench_table(results, mem_key, mem_label):
    rows = "\n".join(
        f"          <tr><td>{html.escape(r['code'])}</td><td>{html.escape(r['op'].replace('_', ' '))}</td>"
        f"<td class=\"num\">{r['median_ns'] / 1e3:.2f}</td><td class=\"num\">{r['min_ns'] / 1e3:.2f}</td>"
        f"<td class=\"num\">{r['throughput_mb_s']:.1f}</td><td class=\"num\">{r.get(mem_key, 0)}</td></tr>"
        for r in results)
    return f"""<div class="table-scroll"><table class="bench">
        <thead><tr><th>Code</th><th>Operation</th><th class="num">Median µs</th><th class="num">Min µs</th><th class="num">MB/s</th><th class="num">{mem_label}</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table></div>"""


def _benchmarks():
    version = "v0.2.0"
    blocks = []
    for lang, title, mem_key, mem_label in [("python", "Python", "heap_peak_bytes", "Heap B/call"),
                                            ("d", "D", "gc_bytes_per_call", "GC B/call")]:
        files = sorted((DATA / version / lang).glob("*.json")) if (DATA / version / lang).exists() else []
        if not files:
            blocks.append(f'<section class="wrap doc reveal"><h2>{title}</h2><p>Results pending.</p></section>')
            continue
        parts = []
        for f in files:
            d = json.loads(f.read_text(encoding="utf-8"))
            env = (f"{html.escape(d.get('platform') or d.get('os', ''))} · {html.escape(d.get('cpu', 'unknown CPU'))} · "
                   + (f"Python {html.escape(d['python'])}" if lang == "python" else html.escape(d.get("compiler", ""))))
            label = f.stem.replace("bench-", "")
            rss = d.get("peak_rss_bytes")
            extra = f" · peak RSS {rss // 1024:,} KiB" if rss else ""
            noisy = ' <span class="tag warn">noisy run</span>' if d.get("noisy") else ""
            parts.append(f"""      <details class="bench-env"{' open' if 'x86_64' in label else ''}>
        <summary><strong>{html.escape(label)}</strong>{noisy}<span class="small"> · {env}{extra}</span></summary>
        {_bench_table(d["results"], mem_key, mem_label)}
      </details>""")
        runs_file = DATA / version / "runs.json"
        run_url = json.loads(runs_file.read_text(encoding="utf-8")).get(lang) if runs_file.exists() else None
        source = (f'<p class="small">Raw JSON and logs: <a href="{run_url}">CI run</a> · data committed in the website '
                  f'repository under <code>data/benchmarks/{version}/{lang}/</code>.</p>') if run_url else ""
        blocks.append(f"""    <section class="wrap doc reveal" id="{lang}">
      <h2>{title} binding · {version}</h2>
{chr(10).join(parts)}
      {source}
    </section>""")
    return f"""    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Reproducible performance</p>
        <h1>Benchmarks</h1>
        <p class="lead">Latency, throughput and memory of the released <strong>{version}</strong> packages, measured on
          GitHub-hosted runners with a published method. Anyone can rerun them.</p>
      </div>
    </section>

    <section class="wrap doc reveal">
      <h2>Method</h2>
      <ul class="checks">
        <li><strong>What is measured:</strong> the public API, exactly as applications call it. Python uses the released wheels
          (checksum-verified); D builds the release tag against the native library version it pins.</li>
        <li><strong>Operations:</strong> encode; decode of a clean word; decode with exactly t errors; decode with n − k
          erasures; burst framing of a 64-byte payload with one burst of depth·t bytes.</li>
        <li><strong>Timing:</strong> warm-up, then 7 rounds, each a batch sized to about 50 ms. Reported: median and minimum
          per call. A run is flagged <em>noisy</em> if any operation varies by more than 1.5× between rounds.</li>
        <li><strong>Memory:</strong> Python heap allocated per call (including result objects) and process peak RSS
          (which includes the Python interpreter); for D, garbage-collected bytes per call.</li>
        <li><strong>Inputs:</strong> seeded (20261020), so every run measures identical data.</li>
      </ul>
      <p><strong>Reproduce:</strong> run the <em>Benchmarks</em> workflow in the
        <a href="{PY_REPO}/actions/workflows/benchmarks.yml">Python</a> or <a href="{D_REPO}/actions/workflows/benchmarks.yml">D</a>
        repository, or locally:</p>
<pre><code>python benchmarks/bench.py            # Python, after pip install audp-ecm
dub run :bench -b release             # D, with AUDP_ECM_LIB_DIR set</code></pre>
      <p class="small">Shared CI runners and laptops vary, so compare numbers within one table rather than across machines.
        Throughput counts payload bytes only.</p>
    </section>

{chr(10).join(blocks)}"""


def register(page, BASE):
    page("how-it-works.html",
         "How AUDP-ECM Works — Reed–Solomon Mathematics & Limits",
         "The finite-field conventions, generator polynomial, decoding algorithms, correction limits and "
         "burst-framing assumptions behind AUDP-ECM error correction.",
         "how", "WebPage", _how_it_works(),
         [("index.html", "Home"), ("how-it-works.html", "How it works")])
    page("security.html",
         "Security Model — Error Correction Is Not Security | AUDP-ECM",
         "What AUDP-ECM error correction protects against and what it does not, why a CRC is not a MAC, "
         "and how to layer encryption and authentication correctly.",
         "security", "WebPage", _security(),
         [("index.html", "Home"), ("security.html", "Security model")])
    page("evidence.html",
         "Documentation & Evidence — APIs, Testing, Platforms | AUDP-ECM",
         "AUDP-ECM API documentation, test methodology, continuous-integration matrix, supported platforms "
         "and verifiable versioned releases for the Python and D bindings.",
         "evidence", "WebPage", _evidence(),
         [("index.html", "Home"), ("evidence.html", "Evidence")])
    page("benchmarks.html",
         "Benchmarks — Reproducible Performance of AUDP-ECM v0.2.0",
         "Reproducible latency, throughput and memory benchmarks of AUDP-ECM Python and D bindings on Linux, "
         "Windows and macOS, with the full method and raw data.",
         "bench", "WebPage", _benchmarks(),
         [("index.html", "Home"), ("benchmarks.html", "Benchmarks")])
