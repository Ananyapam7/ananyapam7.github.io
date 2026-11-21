const assert = require('node:assert/strict');
const { concrete, gradients } = require('../assets/js/vi-research-visuals.js');
const close = (a, b, tolerance = 1e-7) => assert.ok(Math.abs(a - b) < tolerance, `${a} != ${b}`);
const logq = (z, m, s) => -Math.log(s) - .5 * ((z - m) / s) ** 2;
const logWeight = (z, m, s) => -.5 * z * z - logq(z, m, s);
const h = 1e-5;
for (const m of [-2, 0, .8]) for (const s of [.3, 1, 2]) for (const e of [-2, 0, 1.3]) {
  const g = gradients(m, s, e);
  // Differentiate the actual sampled log weight along a fixed noise draw.
  const total = (logWeight(m + h + s * e, m + h, s) - logWeight(m - h + s * e, m - h, s)) / (2 * h);
  close(g.total, total);
  // STL retains the spatial derivative, holding density parameters fixed.
  const z = m + s * e;
  const stl = (logWeight(z + h, m, s) - logWeight(z - h, m, s)) / (2 * h);
  close(g.stl, stl);
  close((g.total + gradients(m, s, -e).total) / 2, -m);
  close((g.stl + gradients(m, s, -e).stl) / 2, -m);
  if (s === 1) close(g.stl, -m);
}
const logits = [.55, .30, .15].map(Math.log), noise = [.7, -.2, .1];
for (const temperature of [.08, .5, 1.2, 3]) {
  const y = concrete(logits, noise, temperature);
  close(y.reduce((a, b) => a + b), 1);
  assert.ok(y.every(v => v > 0 && v < 1));
  assert.equal(y.indexOf(Math.max(...y)), 0);
  // Check the stated softmax derivative with respect to the first logit.
  const plus = concrete(logits.map((v, i) => v + (i === 0 ? h : 0)), noise, temperature);
  const minus = concrete(logits.map((v, i) => v - (i === 0 ? h : 0)), noise, temperature);
  y.forEach((v, i) => close((plus[i] - minus[i]) / (2 * h), v * ((i === 0 ? 1 : 0) - y[0]) / temperature));
}
assert.ok(concrete(logits, noise, .08)[0] > .999);
console.log('Verified Concrete probabilities and derivatives; Gaussian total and STL gradients, symmetry, and exact-fit cancellation.');
