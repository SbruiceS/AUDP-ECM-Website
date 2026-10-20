// Tests for the in-browser Reed–Solomon demo codec (site/assets/app.js).
// Run: node scripts/test_demo.mjs
import { createRequire } from "node:module";
import assert from "node:assert/strict";

const require = createRequire(import.meta.url);
const RS = require("../site/assets/app.js");

// Known answers — identical to the core library's test vectors.
assert.deepEqual(RS.generator(4), [0x74, 0xe7, 0xd8, 0x1e, 0x01], "generator, 4 roots");
assert.deepEqual(RS.encode([1, 2, 3], 4), [0x17, 0x3a, 0x51, 0x52, 1, 2, 3], "RS(7,3) codeword");

let seed = 12345;
const rand = (k) => ((seed = (Math.imul(seed, 1103515245) + 12345) >>> 0) % k);

let roundtrips = 0;
let beyond = { rejected: 0, miscorrected: 0, exact: 0 };
for (const r of [2, 4, 6, 8, 16, 32]) {
  for (let trial = 0; trial < 300; trial++) {
    const k = 1 + rand(48);
    const data = Array.from({ length: k }, () => rand(256));
    const cw = RS.encode(data, r);
    assert.equal(cw.length, k + r);
    assert.ok(RS.syndromes(cw, r).every((v) => v === 0), "encoder output is a codeword");

    // up to t errors: always corrected exactly
    const t = r / 2;
    const e = rand(t + 1);
    const rx = cw.slice();
    const used = new Set();
    while (used.size < e) used.add(rand(cw.length));
    for (const p of used) rx[p] ^= 1 + rand(255);
    const res = RS.decode(rx, r);
    assert.ok(res.ok, `RS(${k + r},${k}) with ${e} errors must decode`);
    assert.deepEqual(res.data, data);
    assert.equal(res.positions.length, e);
    roundtrips++;

    // beyond t: must reject or return a *valid* codeword, never garbage
    if (cw.length > t + 1) {
      const rx2 = cw.slice();
      const used2 = new Set();
      while (used2.size < t + 1) used2.add(rand(cw.length));
      for (const p of used2) rx2[p] ^= 1 + rand(255);
      const res2 = RS.decode(rx2, r);
      if (!res2.ok) beyond.rejected++;
      else {
        assert.ok(RS.syndromes(RS.encode(res2.data, r), r).every((v) => v === 0));
        if (res2.data.every((v, i) => v === data[i])) beyond.exact++;
        else beyond.miscorrected++;
      }
    }
  }
}
console.log(`demo codec OK: ${roundtrips} round trips; beyond t:`, beyond);
