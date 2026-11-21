(() => {
  const initial = () => ({ m: [-0.7, 1.0], v: [0.81, 0.64] });
  const elbo = (s, rho) => {
    const d = 1 - rho * rho;
    return -0.5 * ((s.v[0] + s.v[1] + s.m[0] ** 2 + s.m[1] ** 2 -
      2 * rho * s.m[0] * s.m[1]) / d - 2 + Math.log(d / (s.v[0] * s.v[1])));
  };
  const update = (s, rho, j) => {
    const next = { m: [...s.m], v: [...s.v] };
    next.m[j] = rho * s.m[1 - j];
    next.v[j] = 1 - rho * rho;
    return next;
  };
  if (typeof module !== "undefined") module.exports = { initial, elbo, update };
  if (typeof document === "undefined") return;
  const NS = "http://www.w3.org/2000/svg";
  const add = (parent, name, attrs, text) => {
    const e = document.createElementNS(NS, name);
    for (const [key, value] of Object.entries(attrs)) e.setAttribute(key, value);
    if (text !== undefined) e.textContent = text;
    parent.append(e);
    return e;
  };
  const path = (points) => points.map((p, i) => (i ? "L" : "M") + p.join(",")).join(" ");
  document.querySelectorAll("[data-cavi]").forEach(box => {
    box.querySelector(".vi-cavi-live").hidden = false;
    box.querySelector("[data-cavi-fallback]").hidden = true;
    const joint = box.querySelector("[data-cavi-joint]");
    const factors = [...box.querySelectorAll("[data-cavi-factor]")];
    const trace = box.querySelector("[data-cavi-elbo]");
    const stepButton = box.querySelector("[data-cavi-step]");
    const playButton = box.querySelector("[data-cavi-play]");
    const slider = box.querySelector("[data-cavi-rho]");
    const status = box.querySelector("[data-cavi-status]");
    const values = box.querySelector("[data-cavi-values]");
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    let rho = +slider.value, state = initial(), history = [initial()];
    let running = false, frame = 0, moving = false, active = -1, lastGain = 0;
    const blue = "#409bd5", orange = "#e58a4b", ink = "currentColor";
    const line = (svg, x1, y1, x2, y2, color, dash) =>
      add(svg, "line", { x1, y1, x2, y2, stroke: color, "stroke-width": 1.2, ...(dash ? { "stroke-dasharray": dash } : {}) });
    const text = (svg, x, y, value, attrs = {}) => add(svg, "text", { x, y, fill: ink, ...attrs }, value);
    const draw = (fraction = 0) => {
      const n = history.length - 1, currentL = elbo(state, rho);
      joint.replaceChildren();
      const scale = 30, cx = 210, cy = 161;
      const xy = (x, y) => [cx + x * scale, cy - y * scale];
      text(joint, 20, 22, "Joint distribution");
      line(joint, 35, cy, 385, cy, ink); line(joint, cx, 35, cx, 287, ink);
      for (const t of [-4, -2, 2, 4]) {
        text(joint, cx + t * scale, cy + 17, String(t), { "text-anchor": "middle", class: "vi-cavi-tick" });
        text(joint, cx - 10, cy - t * scale + 4, String(t), { "text-anchor": "end", class: "vi-cavi-tick" });
      }
      text(joint, 385, cy - 8, "z₁"); text(joint, cx + 10, 43, "z₂");
      for (const r of [1, 2]) {
        add(joint, "ellipse", { cx, cy, rx: r * Math.sqrt(1 + rho) * scale, ry: r * Math.sqrt(1 - rho) * scale,
          transform: "rotate(-45 " + cx + " " + cy + ")", fill: blue, "fill-opacity": .04, stroke: blue, "stroke-width": 2 });
      }
      const route = history.map(s => xy(...s.m));
      if (moving) route.push(xy(...state.m));
      add(joint, "path", { d: path(route), fill: "none", stroke: orange, "stroke-width": 1.5, "stroke-dasharray": "3 4", opacity: .75 });
      for (const r of [1, 2]) {
        const [x, y] = xy(...state.m);
        add(joint, "ellipse", { cx: x, cy: y, rx: r * Math.sqrt(state.v[0]) * scale, ry: r * Math.sqrt(state.v[1]) * scale,
          fill: orange, "fill-opacity": .045, stroke: orange, "stroke-width": 2 });
      }
      const [mx, my] = xy(...state.m);
      add(joint, "circle", { cx: mx, cy: my, r: 4, fill: orange });
      text(joint, 30, 310, "Blue: target     Orange: approximation", { class: "vi-cavi-tick" });
      factors.forEach((svg, j) => {
        svg.replaceChildren();
        const highlighted = active === j;
        const sub = j === 0 ? "₁" : "₂";
        text(svg, 25, 22, "q" + sub + (highlighted ? "  · updating" : moving ? "  · held fixed" : ""), { fill: highlighted ? orange : ink });
        const px = z => 30 + (z + 5) * 30;
        const py = p => 126 - p * 76;
        line(svg, 30, 126, 330, 126, ink);
        const curve = (m, v) => Array.from({ length: 181 }, (_, i) => {
          const z = -5 + i / 18;
          return [px(z), py(Math.exp(-((z - m) ** 2) / (2 * v)) / Math.sqrt(2 * Math.PI * v))];
        });
        add(svg, "path", { d: path(curve(0, 1)), fill: "none", stroke: blue, "stroke-width": 1.7, "stroke-dasharray": "4 4" });
        add(svg, "path", { d: path(curve(state.m[j], state.v[j])), fill: "none", stroke: orange, "stroke-width": highlighted ? 3 : 2 });
        text(svg, 30, 149, "m" + sub + " = " + state.m[j].toFixed(2) + "     v" + sub + " = " + state.v[j].toFixed(3), { class: "vi-cavi-tick" });
      });
      trace.replaceChildren();
      const bottom = Math.floor(elbo(history[0], rho) - 1);
      const x = i => 65 + i / Math.max(12, n + (moving ? 1 : 0)) * 650;
      const y = l => 47 + (-l) / (-bottom) * 125;
      text(trace, 20, 20, "ELBO after each factor update");
      line(trace, 65, y(0), 715, y(0), blue, "5 4");
      text(trace, 715, 39, "log Z = 0", { "text-anchor": "end", fill: blue });
      const best = .5 * Math.log(1 - rho * rho);
      line(trace, 65, y(best), 715, y(best), orange, "4 5");
      text(trace, 80, 195, "Best mean-field ELBO: " + best.toFixed(3), { fill: orange });
      text(trace, 715, 195, "Factor updates", { "text-anchor": "end" });
      text(trace, 55, y(0) + 5, "0", { "text-anchor": "end" });
      text(trace, 55, y(bottom) + 4, String(bottom), { "text-anchor": "end" });
      const points = history.map((s, i) => [x(i), y(elbo(s, rho))]);
      if (moving) points.push([x(n + fraction), y(currentL)]);
      add(trace, "path", { d: path(points), fill: "none", stroke: orange, "stroke-width": 2.5 });
      history.forEach((s, i) => add(trace, "circle", { cx: x(i), cy: y(elbo(s, rho)), r: 3, fill: orange }));
      for (let i = 0; i <= Math.max(12, n); i += Math.max(2, Math.ceil(n / 8))) text(trace, x(i), 181, String(i), { "text-anchor": "middle", class: "vi-cavi-tick" });
      values.textContent = "Update " + n + " · ELBO " + currentL.toFixed(4) + " · KL " + (-currentL).toFixed(4) +
        (n ? " · Last improvement +" + lastGain.toFixed(4) : "");
    };
    const settled = () => {
      const gap = .5 * Math.log(1 - rho * rho) - elbo(state, rho);
      return gap < 1e-7;
    };
    const pause = () => { running = false; playButton.textContent = "Play updates"; };
    const step = () => {
      if (moving || settled()) return;
      active = (history.length - 1) % 2;
      const from = { m: [...state.m], v: [...state.v] }, to = update(from, rho, active);
      const before = elbo(from, rho);
      moving = true; stepButton.disabled = true;
      status.textContent = "Updating q" + (active === 0 ? "₁; q₂" : "₂; q₁") + " stays fixed.";
      const started = performance.now();
      const tick = now => {
        const t = reduced.matches ? 1 : Math.min(1, (now - started) / 850);
        const ease = t * t * (3 - 2 * t);
        state = { m: from.m.map((m, i) => m + ease * (to.m[i] - m)), v: from.v.map((v, i) => v + ease * (to.v[i] - v)) };
        draw(ease);
        if (t < 1) { frame = requestAnimationFrame(tick); return; }
        state = to; lastGain = elbo(to, rho) - before; history.push(to);
        moving = false; active = -1; stepButton.disabled = settled();
        stepButton.textContent = "Update q" + ((history.length - 1) % 2 ? "₂" : "₁");
        status.textContent = settled() ? "The best mean-field fit is reached. Any remaining gap is due to the family." :
          "Update complete: ELBO increased by " + lastGain.toFixed(4) + ". Next, " + stepButton.textContent.toLowerCase() + ".";
        draw();
        if (settled() || history.length > 200) pause();
        if (running) frame = requestAnimationFrame(step);
      };
      frame = requestAnimationFrame(tick);
    };
    const reset = () => {
      cancelAnimationFrame(frame); pause(); moving = false; active = -1;
      rho = +slider.value; state = initial(); history = [state]; lastGain = 0;
      box.querySelector("[data-rho-label]").textContent = rho.toFixed(2);
      stepButton.disabled = false; stepButton.textContent = "Update q₁";
      status.textContent = "Start with q₁; q₂ stays fixed."; draw();
    };
    stepButton.addEventListener("click", () => { pause(); step(); });
    playButton.addEventListener("click", () => {
      if (running) { pause(); return; }
      if (settled()) reset();
      running = true; playButton.textContent = "Pause"; step();
    });
    slider.addEventListener("input", reset);
    box.querySelector("[data-cavi-reset]").addEventListener("click", reset);
    document.addEventListener("visibilitychange", () => { if (document.hidden) pause(); });
    box.closest(".vi-paper-theory")?.addEventListener("toggle", event => { if (!event.target.open) pause(); });
    new IntersectionObserver(items => { if (!items[0].isIntersecting) pause(); }).observe(box);
    reset();
  });
})();
