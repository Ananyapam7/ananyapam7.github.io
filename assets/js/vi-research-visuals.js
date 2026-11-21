/* Small numerical illustrations for the paper notes. No network dependencies. */
(() => {
  'use strict';
  const concrete = (logits, noise, temperature) => {
    const values = logits.map((v, i) => (v + noise[i]) / temperature);
    const maximum = Math.max(...values);
    const weights = values.map(v => Math.exp(v - maximum));
    const sum = weights.reduce((a, b) => a + b, 0);
    return weights.map(v => v / sum);
  };
  const gradients = (mean, scale, epsilon) => ({
    total: -mean - scale * epsilon,
    stl: -mean + (1 / scale - scale) * epsilon
  });
  if (typeof module !== 'undefined') module.exports = { concrete, gradients };
  if (typeof document === 'undefined') return;
  const NS = 'http://www.w3.org/2000/svg';
  function element(tag, attrs, content) {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (content !== undefined) node.textContent = content;
    return node;
  }
  function generator(seed) {
    return () => {
      seed = (Math.imul(1664525, seed) + 1013904223) >>> 0;
      return (seed + 0.5) / 4294967296;
    };
  }
  function initConcrete(root) {
    const rng = generator(24017);
    const logits = [.55, .30, .15].map(Math.log);
    const vertices = [[230, 32], [45, 330], [415, 330]];
    const colors = ['var(--vi-demo-red)', 'var(--vi-demo-teal)', 'var(--vi-demo-blue)'];
    const input = root.querySelector('input');
    const output = root.querySelector('[data-value]');
    const button = root.querySelector('[data-play]');
    const group = root.querySelector('[data-points]');
    const samples = Array.from({ length: 100 }, () => {
      const noise = logits.map(() => -Math.log(-Math.log(rng())));
      const scores = noise.map((v, i) => v + logits[i]);
      const winner = scores.indexOf(Math.max(...scores));
      const dot = element('circle', { r: 3.8, fill: colors[winner], opacity: .65 });
      group.append(dot);
      return { noise, dot };
    });
    function render() {
      const temperature = Number(input.value);
      output.value = temperature.toFixed(2);
      samples.forEach(({ noise, dot }) => {
        const p = concrete(logits, noise, temperature);
        dot.setAttribute('cx', p.reduce((sum, w, i) => sum + w * vertices[i][0], 0));
        dot.setAttribute('cy', p.reduce((sum, w, i) => sum + w * vertices[i][1], 0));
      });
    }
    let frame = null;
    function stop() {
      if (frame !== null) cancelAnimationFrame(frame);
      frame = null;
      button.textContent = 'Cool the samples';
      button.setAttribute('aria-pressed', 'false');
    }
    input.addEventListener('input', () => { stop(); render(); });
    button.addEventListener('click', () => {
      if (frame !== null) { stop(); return; }
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        input.value = .08; render(); return;
      }
      button.textContent = 'Pause';
      button.setAttribute('aria-pressed', 'true');
      const start = performance.now();
      function animate(now) {
        if (document.hidden || !root.closest('details').open) { stop(); return; }
        const progress = Math.min(1, (now - start) / 6500);
        input.value = Math.exp(Math.log(3) * (1 - progress) + Math.log(.08) * progress);
        render();
        if (progress < 1) frame = requestAnimationFrame(animate);
        else stop();
      }
      frame = requestAnimationFrame(animate);
    });
    document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
    root.closest('details').addEventListener('toggle', event => { if (!event.target.open) stop(); });
    render();
  }
  function initSTL(root) {
    const rng = generator(28023);
    // Symmetric pairs isolate spread from accidental finite-sample mean shifts.
    const noise = Array.from({ length: 18 }, () => Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng()));
    const epsilons = noise.flatMap(e => [e, -e]);
    const meanInput = root.querySelector('#vi-stl-mean');
    const scaleInput = root.querySelector('#vi-stl-scale');
    const plot = root.querySelector('[data-gradient-plot]');
    function render() {
      const mean = Number(meanInput.value), scale = Number(scaleInput.value);
      root.querySelector('[data-mean-value]').value = mean.toFixed(2);
      root.querySelector('[data-scale-value]').value = scale.toFixed(2);
      const values = epsilons.map(e => gradients(mean, scale, e));
      const extent = Math.max(4, Math.ceil(Math.max(...values.flatMap(v => [Math.abs(v.total), Math.abs(v.stl)]))));
      const x = value => 32 + (value + extent) * 456 / (2 * extent);
      plot.replaceChildren();
      plot.append(element('line', { x1: x(-mean), x2: x(-mean), y1: 38, y2: 245, stroke: '#777', 'stroke-dasharray': '4 5' }));
      plot.append(element('text', { x: x(-mean), y: 25, 'text-anchor': 'middle', fill: 'currentColor' }, 'Exact mean gradient'));
      [['total', 103, 'var(--vi-demo-red)', 'Total derivative'], ['stl', 207, 'var(--vi-demo-teal)', 'Sticking the Landing']].forEach(([key, y, color, title]) => {
        plot.append(element('text', { x: 32, y: y - 32, fill: color }, title));
        plot.append(element('line', { x1: 32, x2: 488, y1: y + 22, y2: y + 22, stroke: 'currentColor', opacity: .3 }));
        [-extent, -extent / 2, 0, extent / 2, extent].forEach(tick => {
          plot.append(element('text', { x: x(tick), y: y + 42, 'text-anchor': 'middle', fill: 'currentColor' }, String(tick)));
        });
        values.forEach((value, i) => plot.append(element('circle', {
          cx: x(value[key]), cy: y + ((i % 7) - 3) * 3, r: 3.5, fill: color, opacity: .6
        })));
      });
      plot.append(element('text', { x: 260, y: 285, 'text-anchor': 'middle', fill: 'currentColor' }, 'Mean-gradient estimate (shared horizontal scale)'));
      root.querySelector('[data-reading]').textContent = `Exact expectation: ${(-mean).toFixed(2)} · Total-derivative variance: ${(scale * scale).toFixed(2)} · STL variance: ${((1 / scale - scale) ** 2).toFixed(2)}`;
    }
    meanInput.addEventListener('input', render);
    scaleInput.addEventListener('input', render);
    root.querySelector('[data-fit]').addEventListener('click', () => { meanInput.value = 0; scaleInput.value = 1; render(); });
    render();
  }
  function init() {
    document.querySelectorAll('[data-vi-demo]').forEach(root => {
      if (root.dataset.initialized) return;
      root.dataset.initialized = 'true';
      if (root.dataset.viDemo === 'concrete') initConcrete(root);
      if (root.dataset.viDemo === 'stl') initSTL(root);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
