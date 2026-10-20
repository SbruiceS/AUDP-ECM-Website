/*
 * AUDP-ECM website — progressive enhancement (the site works without it).
 * No dependencies, no network requests, no HTML-string injection, no dynamic code.
 *
 * Includes a small, self-contained Reed–Solomon codec over GF(256) used only
 * for the in-browser demo. It follows the standard textbook construction
 * (primitive polynomial 0x11D, generator roots α^1…α^r, systematic layout
 * with parity first) and is tested by scripts/test_demo.mjs.
 *
 * © 2026 Sbruice Singh / Agriculture Service of Product Farm (ASPF). All rights reserved.
 */
"use strict";

/* ------------------------------------------------------------------ theme */
(function initTheme() {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.classList.add("js");
  let saved = null;
  try { saved = window.localStorage.getItem("audp-theme"); } catch (_) { /* storage blocked */ }
  if (saved === "light" || saved === "dark") root.dataset.theme = saved;
})();

/* ------------------------------------------------------- GF(256) + RS codec */
const RS = (() => {
  const EXP = new Uint8Array(512);
  const LOG = new Uint8Array(256);
  let x = 1;
  for (let i = 0; i < 255; i++) {
    EXP[i] = x;
    LOG[x] = i;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d;
  }
  for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];

  const mul = (a, b) => (a && b ? EXP[LOG[a] + LOG[b]] : 0);
  const inv = (a) => EXP[255 - LOG[a]];
  const alphaPow = (e) => EXP[((e % 255) + 255) % 255];

  /** Generator g(x) = Π_{i=1..r} (x − α^i), coefficients low → high (monic). */
  function generator(r) {
    let g = [1];
    for (let i = 1; i <= r; i++) {
      const root = alphaPow(i);
      const next = new Array(g.length + 1).fill(0);
      for (let j = 0; j < g.length; j++) {
        next[j] ^= mul(g[j], root);
        next[j + 1] ^= g[j];
      }
      g = next;
    }
    return g;
  }

  /** Systematic encode: returns parity (r symbols) followed by the data. */
  function encode(data, r) {
    const g = generator(r);
    const p = new Array(r).fill(0);
    for (let d = data.length - 1; d >= 0; d--) {
      const fb = data[d] ^ p[r - 1];
      for (let i = r - 1; i > 0; i--) p[i] = p[i - 1] ^ mul(g[i], fb);
      p[0] = mul(g[0], fb);
    }
    return p.concat(Array.from(data));
  }

  function syndromes(word, r) {
    const s = [];
    for (let i = 1; i <= r; i++) {
      const root = alphaPow(i);
      let acc = 0;
      for (let j = word.length - 1; j >= 0; j--) acc = mul(acc, root) ^ word[j];
      s.push(acc);
    }
    return s;
  }

  const evalPoly = (p, xv) => {
    let acc = 0;
    for (let i = p.length - 1; i >= 0; i--) acc = mul(acc, xv) ^ p[i];
    return acc;
  };

  /** Berlekamp–Massey: error-locator Λ(x), low → high. */
  function berlekampMassey(S) {
    let C = [1];
    let B = [1];
    let L = 0;
    let m = 1;
    let b = 1;
    for (let n = 0; n < S.length; n++) {
      let d = S[n];
      for (let i = 1; i <= L; i++) d ^= mul(C[i] || 0, S[n - i]);
      if (d === 0) {
        m++;
        continue;
      }
      const T = C.slice();
      const coef = mul(d, inv(b));
      while (C.length < B.length + m) C.push(0);
      for (let i = 0; i < B.length; i++) C[i + m] ^= mul(coef, B[i]);
      if (2 * L <= n) {
        L = n + 1 - L;
        B = T;
        b = d;
        m = 1;
      } else {
        m++;
      }
    }
    while (C.length > 1 && C[C.length - 1] === 0) C.pop();
    return C;
  }

  /**
   * Decode `word` (length n) with `r` parity symbols.
   * Returns {ok, data, positions} or {ok:false, reason}.
   */
  function decode(word, r) {
    const n = word.length;
    const S = syndromes(word, r);
    if (S.every((v) => v === 0)) return { ok: true, data: word.slice(r), positions: [] };
    const lambda = berlekampMassey(S);
    const deg = lambda.length - 1;
    if (deg === 0 || 2 * deg > r) return { ok: false, reason: "too many errors" };
    const positions = [];
    for (let j = 0; j < n; j++) if (evalPoly(lambda, alphaPow(-j)) === 0) positions.push(j);
    if (positions.length !== deg) return { ok: false, reason: "too many errors" };
    // Ω(x) = S(x)·Λ(x) mod x^r ; Λ'(x) keeps the odd-degree terms
    const omega = new Array(r).fill(0);
    for (let i = 0; i < S.length; i++)
      for (let j = 0; j < lambda.length && i + j < r; j++) omega[i + j] ^= mul(S[i], lambda[j]);
    const dLambda = lambda.map((c, i) => (i % 2 === 1 ? c : 0)).slice(1);
    const fixed = word.slice();
    for (const pos of positions) {
      const xInv = alphaPow(-pos);
      const den = evalPoly(dLambda, xInv);
      if (den === 0) return { ok: false, reason: "inconsistent" };
      fixed[pos] ^= mul(evalPoly(omega, xInv), inv(den));
    }
    if (!syndromes(fixed, r).every((v) => v === 0)) return { ok: false, reason: "verification failed" };
    return { ok: true, data: fixed.slice(r), positions };
  }

  return { encode, decode, syndromes, generator };
})();

if (typeof module !== "undefined") module.exports = RS; // for scripts/test_demo.mjs

/* ------------------------------------------------------------- UI helpers */
function onReady(fn) {
  if (typeof document === "undefined") return;
  if (document.readyState !== "loading") fn();
  else document.addEventListener("DOMContentLoaded", fn);
}

function el(tag, attrs = {}, text) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else node.setAttribute(k, v);
  }
  if (text !== undefined) node.textContent = text;
  return node;
}

onReady(() => {
  const root = document.documentElement;

  /* theme toggle: auto → light → dark → auto */
  const themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    const label = () => {
      const t = root.dataset.theme || "auto";
      themeBtn.setAttribute("aria-label", `Theme: ${t}. Change theme`);
      themeBtn.dataset.mode = t;
    };
    label();
    themeBtn.addEventListener("click", () => {
      const order = ["auto", "light", "dark"];
      const next = order[(order.indexOf(root.dataset.theme || "auto") + 1) % 3];
      if (next === "auto") delete root.dataset.theme;
      else root.dataset.theme = next;
      try {
        if (next === "auto") window.localStorage.removeItem("audp-theme");
        else window.localStorage.setItem("audp-theme", next);
      } catch (_) { /* storage blocked */ }
      label();
    });
  }

  /* mobile navigation */
  const navBtn = document.getElementById("nav-toggle");
  const header = document.querySelector(".top");
  if (navBtn && header) {
    navBtn.addEventListener("click", () => {
      const open = header.classList.toggle("open");
      navBtn.setAttribute("aria-expanded", String(open));
    });
    header.querySelectorAll("nav a").forEach((a) =>
      a.addEventListener("click", () => {
        header.classList.remove("open");
        navBtn.setAttribute("aria-expanded", "false");
      }),
    );
  }

  /* copy buttons on code blocks */
  document.querySelectorAll("pre > code").forEach((code) => {
    const btn = el("button", { class: "copy", type: "button", "aria-label": "Copy code" }, "Copy");
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(code.textContent);
        btn.textContent = "Copied";
      } catch (_) {
        btn.textContent = "Select & copy";
      }
      setTimeout(() => (btn.textContent = "Copy"), 1600);
    });
    code.parentElement.classList.add("has-copy");
    code.parentElement.appendChild(btn);
  });

  /* reveal-on-scroll (skipped when reduced motion is preferred) */
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const revealables = document.querySelectorAll(".reveal");
  const showAll = () => revealables.forEach((r) => r.classList.add("in"));
  // anything already on screen appears immediately; a fallback guarantees
  // content is never left hidden (e.g. print, unusual viewports, crawlers)
  revealables.forEach((r) => {
    if (r.getBoundingClientRect().top < window.innerHeight) r.classList.add("in");
  });
  setTimeout(showAll, 2500);
  if (!reduce && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      }),
      { rootMargin: "0px 0px -8% 0px" },
    );
    revealables.forEach((r) => io.observe(r));
  } else {
    showAll();
  }

  initDemo();
});

/* --------------------------------------------------------------- RS demo */
function initDemo() {
  const box = document.getElementById("demo-app");
  if (!box) return;
  box.hidden = false;
  const msgIn = document.getElementById("demo-msg");
  const parityIn = document.getElementById("demo-parity");
  const parityOut = document.getElementById("demo-parity-out");
  const tOut = document.getElementById("demo-t");
  const grid = document.getElementById("demo-grid");
  const status = document.getElementById("demo-status");
  const out = {
    orig: document.getElementById("demo-orig"),
    recv: document.getElementById("demo-recv"),
    recovered: document.getElementById("demo-recovered"),
    detected: document.getElementById("m-detected"),
    injected: document.getElementById("m-injected"),
    meter: document.getElementById("m-meter"),
    positions: document.getElementById("m-positions"),
    time: document.getElementById("m-time"),
  };
  const enc = new TextEncoder();
  const dec = new TextDecoder("utf-8", { fatal: false });

  let seed = 20261020;
  const rand = (k) => {
    seed = (Math.imul(seed, 1103515245) + 12345) >>> 0;
    return seed % k;
  };

  let clean = [];
  let rx = [];
  let r = 8;
  let data = new Uint8Array();

  function rebuild() {
    r = Number(parityIn.value);
    parityOut.value = String(r);
    tOut.value = String(r / 2);
    data = enc.encode(msgIn.value).slice(0, 48);
    clean = RS.encode(data, r);
    rx = clean.slice();
    render();
  }

  /**
   * Median per-call decode time (µs) over 5 loops of about 6 ms each. The
   * iteration cap keeps the loop finite even where timers are clamped or
   * virtualised (privacy-hardened browsers, headless renderers).
   */
  function timeDecode() {
    const samples = [];
    for (let rep = 0; rep < 5; rep++) {
      let calls = 0;
      const t0 = performance.now();
      let t1 = t0;
      while (t1 - t0 < 6 && calls < 5000) {
        RS.decode(rx, r);
        calls++;
        t1 = performance.now();
      }
      if (t1 > t0) samples.push(((t1 - t0) * 1000) / calls);
    }
    if (!samples.length) return NaN;
    samples.sort((a, b) => a - b);
    return samples[Math.floor(samples.length / 2)];
  }

  const text = (bytes) => dec.decode(Uint8Array.from(bytes));

  function render() {
    const result = RS.decode(rx, r);
    const corrupted = rx.map((v, i) => v !== clean[i]);
    const fixedSet = new Set(result.ok ? result.positions : []);
    grid.replaceChildren();
    rx.forEach((v, i) => {
      const cell = el("button", {
        type: "button",
        class: [
          "sym",
          i < r ? "parity" : "data",
          corrupted[i] ? "bad" : "",
          fixedSet.has(i) ? "fixed" : "",
        ].join(" ").trim(),
        "aria-label": `Symbol ${i} (${i < r ? "parity" : "data"})${corrupted[i] ? ", corrupted" : ""}. Toggle corruption`,
        "aria-pressed": String(corrupted[i]),
      }, v.toString(16).padStart(2, "0"));
      cell.addEventListener("click", () => {
        rx[i] = corrupted[i] ? clean[i] : clean[i] ^ (1 + rand(255));
        render();
      });
      grid.appendChild(cell);
    });

    const nBad = corrupted.filter(Boolean).length;
    const nBadData = corrupted.slice(r).filter(Boolean).length;
    const t = r / 2;
    const detected = RS.syndromes(rx, r).some((v) => v !== 0);

    out.orig.textContent = text(data);
    out.recv.textContent = text(rx.slice(r));
    out.recv.classList.toggle("damaged", nBadData > 0);
    out.detected.textContent = detected ? "yes: syndromes are non-zero" : "no: the word is a valid codeword";
    out.injected.textContent =
      `${nBad} corrupted symbol${nBad === 1 ? "" : "s"} (${nBadData} data, ${nBad - nBadData} parity), capacity t = ${t}`;
    out.meter.max = Math.max(t, 1);
    out.meter.value = Math.min(nBad, t);
    out.meter.classList.toggle("over", nBad > t);
    const us = timeDecode();
    out.time.textContent = Number.isFinite(us)
      ? `${us.toFixed(1)} µs per decode (JavaScript, this browser)`
      : "not measurable (timer resolution is restricted in this browser)";

    status.className = "demo-status";
    if (nBad === 0) {
      out.positions.textContent = "none needed";
      out.recovered.textContent = text(data);
      status.textContent = `Clean frame: ${rx.length} symbols (${data.length} data + ${r} parity). Click symbols or add noise.`;
      return;
    }
    if (result.ok) {
      out.positions.textContent = result.positions.length ? result.positions.join(", ") : "none";
      out.recovered.textContent = text(result.data);
      const exact = result.data.every((v, i) => v === data[i]);
      if (exact) {
        status.classList.add("good");
        status.textContent =
          `Repaired ${result.positions.length} of at most ${t} correctable symbols. ` +
          "The recovered payload is byte-for-byte identical to the original.";
      } else {
        status.classList.add("warn");
        status.textContent =
          `${nBad} errors exceed the capacity t = ${t}. The damaged word happened to lie within ${t} symbols ` +
          "of a different valid codeword, so the decoder produced the wrong payload (miscorrection). " +
          "AUDP-ECM burst framing adds a CRC-16 on top to detect exactly this case.";
      }
    } else {
      out.positions.textContent = "none: frame rejected";
      out.recovered.textContent = "(rejected)";
      status.classList.add("bad");
      status.textContent =
        `${nBad} errors exceed the capacity t = ${t}. No codeword lies within ${t} symbols of what was received, ` +
        `so the decoder refuses (${result.reason}) instead of guessing. The failure is detected and reported, never silently accepted.`;
    }
  }

  function corrupt(positions) {
    positions.forEach((i) => {
      if (rx[i] === clean[i]) rx[i] = clean[i] ^ (1 + rand(255));
    });
    render();
  }

  document.getElementById("demo-one").addEventListener("click", () => corrupt([rand(rx.length)]));
  document.getElementById("demo-noise").addEventListener("click", () => {
    const k = Math.max(1, Math.round(rx.length * 0.06));
    corrupt(Array.from({ length: k }, () => rand(rx.length)));
  });
  document.getElementById("demo-burst").addEventListener("click", () => {
    const len = Math.min(rx.length, r / 2); // a burst of exactly t symbols: correctable
    const start = rand(rx.length - len + 1);
    corrupt(Array.from({ length: len }, (_, j) => start + j));
  });
  document.getElementById("demo-reset").addEventListener("click", () => {
    rx = clean.slice();
    render();
  });
  msgIn.addEventListener("input", rebuild);
  parityIn.addEventListener("input", rebuild);
  rebuild();
}
