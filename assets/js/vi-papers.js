(() => {
  const library = document.querySelector(".vi-library");
  if (!library) return;
  const cards = [...library.querySelectorAll(".vi-paper")];
  const groups = [...library.querySelectorAll(".vi-paper-group")];
  const input = library.querySelector("#vi-paper-search");
  const count = library.querySelector("[data-vi-count]");
  const normalize = (s) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const texts = cards.map(card => normalize(card.textContent));
  const network = library.querySelector(".vi-network");
  if (network) {
    const svg = network.querySelector(".vi-network-canvas");
    const world = network.querySelector(".vi-network-world");
    const centerX = svg.viewBox.baseVal.width / 2;
    const centerY = svg.viewBox.baseVal.height / 2;
    const nodes = [...network.querySelectorAll(".vi-network-node")];
    const edges = [...network.querySelectorAll(".vi-network-edge")];
    const byId = new Map(nodes.map(node => [node.dataset.paper, node]));
    const hubs = [...network.querySelectorAll(".vi-network-hub")];
    const search = network.querySelector("[data-network-search]");
    const results = network.querySelector("[data-network-results]");
    const cardById = new Map(cards.map(card => [card.id, card]));
    const searchText = new Map(cards.map((card, i) => [card.id, texts[i]]));
    const original = new Map(nodes.map(node => [node.dataset.paper, { x: +node.dataset.x, y: +node.dataset.y }]));
    let selected = null, activeGroup = "all", drag = null, skipClick = false;
    const camera = { x: 0, y: 0, k: 1 };
    const drawCamera = () => {
      world.setAttribute("transform", "translate(" + camera.x + "," + camera.y + ") scale(" + camera.k + ")");
      network.classList.toggle("zoomed", camera.k >= 1.65);
      network.querySelector("[data-network-scale]").textContent = Math.round(camera.k * 100) + "%";
    };
    const highlight = id => {
      const neighbors = new Set(id ? [id] : []);
      edges.forEach(edge => {
        const connected = !!id && (edge.dataset.from === id || edge.dataset.to === id);
        edge.classList.toggle("active", connected);
        edge.classList.toggle("dim", !!id && !connected);
        if (connected) { neighbors.add(edge.dataset.from); neighbors.add(edge.dataset.to); }
      });
      nodes.forEach(node => {
        const related = neighbors.has(node.dataset.paper);
        node.classList.toggle("active", node.dataset.paper === id);
        node.classList.toggle("related", related);
        node.classList.toggle("dim", id ? !related : activeGroup !== "all" && node.dataset.group !== activeGroup);
      });
      hubs.forEach(hub => hub.classList.toggle("dim", !!id || (activeGroup !== "all" && hub.dataset.hub !== activeGroup)));
    };
    const dialog = network.querySelector(".vi-network-dialog");
    const detail = dialog.querySelector("[data-network-detail]");
    let placeholder = null, openedCard = null, wasOpen = false;
    const clearSelection = () => { selected = null; highlight(null); };
    const closePaper = () => { if (dialog.open) dialog.close(); else clearSelection(); };
    dialog.addEventListener("close", () => {
      if (openedCard) {
        openedCard.querySelector(".vi-paper-theory").open = wasOpen;
        placeholder.replaceWith(openedCard);
        openedCard = null; placeholder = null;
      }
      document.body.classList.remove("vi-dialog-open");
      clearSelection();
    });
    dialog.querySelector("[data-network-close]").addEventListener("click", closePaper);
    dialog.addEventListener("click", event => {
      if (event.target === dialog) {
        const rect = dialog.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) closePaper();
      }
      if (event.target.closest('a[href^="#"]')) closePaper();
    });
    const openPaper = id => {
      if (selected === id && dialog.open) { closePaper(); return; }
      const card = cardById.get(id);
      if (!card) return;
      selected = id; highlight(id);
      openedCard = card; placeholder = document.createComment("paper position");
      card.replaceWith(placeholder); detail.replaceChildren(card);
      wasOpen = card.querySelector(".vi-paper-theory").open;
      card.querySelector(".vi-paper-theory").open = true;
      dialog.showModal(); dialog.scrollTop = 0;
      document.body.classList.add("vi-dialog-open");
      dialog.querySelector("[data-network-close]").focus();
    };
    let cameraFrame = 0;
    const animateCamera = target => {
      cancelAnimationFrame(cameraFrame);
      const start = { ...camera }, began = performance.now();
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const step = now => {
        const t = reduce ? 1 : Math.min(1, (now - began) / 260), eased = 1 - Math.pow(1 - t, 3);
        for (const key of ["x", "y", "k"]) camera[key] = start[key] + (target[key] - start[key]) * eased;
        drawCamera(); if (t < 1) cameraFrame = requestAnimationFrame(step);
      };
      cameraFrame = requestAnimationFrame(step);
    };
    const zoomAt = (factor, x = centerX, y = centerY) => {
      const next = Math.max(.65, Math.min(3.5, camera.k * factor));
      animateCamera({x: x - (x - camera.x) * next / camera.k, y: y - (y - camera.y) * next / camera.k, k: next});
    };
    const centerOn = (x, y, k) => {
      animateCamera({k, x: centerX - x * k, y: centerY - y * k});
    };
    const drawEdges = () => {
      edges.forEach(edge => {
        const a = byId.get(edge.dataset.from), b = byId.get(edge.dataset.to);
        const x = +a.dataset.x, y = +a.dataset.y, xx = +b.dataset.x, yy = +b.dataset.y;
        edge.setAttribute("d", "M" + x + "," + y + " Q" + ((x + xx) / 2 + 12) + "," + ((y + yy) / 2 - 18) + " " + xx + "," + yy);
      });
    };
    nodes.forEach(node => {
      const id = node.dataset.paper;
      node.addEventListener("pointerenter", event => { if (!drag && event.pointerType !== "touch") highlight(id); });
      node.addEventListener("focus", () => highlight(id));
      node.addEventListener("click", event => {
        event.preventDefault();
        if (skipClick) { skipClick = false; return; }
        openPaper(id);
      });
    });
    svg.addEventListener("pointerleave", () => { if (!drag) highlight(selected); });
    network.querySelectorAll("[data-network-zoom]").forEach(button =>
      button.addEventListener("click", () => zoomAt(button.dataset.networkZoom === "in" ? 1.3 : 1 / 1.3)));
    const selectGroup = group => {
      activeGroup = group; selected = null;
      network.querySelectorAll("[data-network-group]").forEach(button => {
        const on = button.dataset.networkGroup === group;
        button.classList.toggle("active", on); button.setAttribute("aria-pressed", String(on));
      });
      if (group === "all") centerOn(centerX, centerY, 1);
      else {
        const hub = hubs.find(item => item.dataset.hub === group);
        centerOn(+hub.dataset.x, +hub.dataset.y, window.matchMedia("(max-width:600px)").matches ? 2.5 : 2);
      }
      highlight(null);
    };
    network.querySelectorAll("[data-network-group]").forEach(button =>
      button.addEventListener("click", () => selectGroup(button.dataset.networkGroup)));
    network.querySelector("[data-network-reset]").addEventListener("click", () => {
      nodes.forEach(node => {
        const p = original.get(node.dataset.paper);
        node.dataset.x = p.x; node.dataset.y = p.y;
        node.setAttribute("transform", "translate(" + p.x + "," + p.y + ")");
      });
      drawEdges(); search.value = ""; results.hidden = true; selectGroup("all");
    });
    search.addEventListener("input", () => {
      const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
      results.replaceChildren(); results.hidden = !words.length;
      if (!words.length) { highlight(selected); return; }
      const titleScore = card => words.filter(word => normalize(card.querySelector("h4").textContent).includes(word)).length;
      const matches = cards.filter(card => words.every(word => searchText.get(card.id).includes(word)))
        .sort((a, b) => titleScore(b) - titleScore(a));
      nodes.forEach(node => node.classList.toggle("dim", !matches.some(card => card.id === node.dataset.paper)));
      if (!matches.length) {
        const empty = document.createElement("p"); empty.textContent = "No matching papers. Try another title, author, or idea."; results.append(empty);
      }
      matches.slice(0, 8).forEach(card => {
        const button = document.createElement("button"); button.type = "button";
        button.textContent = card.querySelector("h4").textContent + " · " + card.querySelector(".vi-paper-meta span").textContent;
        button.addEventListener("click", () => {
          const node = byId.get(card.id); centerOn(+node.dataset.x, +node.dataset.y, 2);
          results.hidden = true; openPaper(card.id);
        });
        results.append(button);
      });
    });
    search.addEventListener("keydown", event => {
      if (event.key === "Escape") { search.value = ""; results.hidden = true; highlight(selected); }
      if (event.key === "ArrowDown") { event.preventDefault(); results.querySelector("button")?.focus(); }
    });
    const point = event => {
      const p = new DOMPoint(event.clientX, event.clientY);
      return p.matrixTransform(svg.getScreenCTM().inverse());
    };
    svg.addEventListener("pointerdown", event => {
      if (event.button !== 0 || drag) return;
      cancelAnimationFrame(cameraFrame);
      skipClick = false;
      const p = point(event), node = event.target.closest(".vi-network-node");
      drag = { id: event.pointerId, node, x: p.x, y: p.y, cx: camera.x, cy: camera.y,
        nx: node ? +node.dataset.x : 0, ny: node ? +node.dataset.y : 0, moved: false };
      svg.classList.add("dragging");
    });
    svg.addEventListener("pointermove", event => {
      if (!drag || drag.id !== event.pointerId) return;
      const p = point(event), dx = p.x - drag.x, dy = p.y - drag.y;
      if (Math.hypot(dx, dy) > 4) drag.moved = true;
      if (!drag.moved) return;
      if (!svg.hasPointerCapture(event.pointerId)) svg.setPointerCapture(event.pointerId);
      if (drag.node) {
        const x = drag.nx + dx / camera.k, y = drag.ny + dy / camera.k;
        drag.node.dataset.x = x; drag.node.dataset.y = y;
        drag.node.setAttribute("transform", "translate(" + x + "," + y + ")");
        drawEdges();
      } else {
        camera.x = drag.cx + dx; camera.y = drag.cy + dy; drawCamera();
      }
    });
    const endDrag = event => {
      if (!drag || drag.id !== event.pointerId) return;
      skipClick = drag.moved;
      const backgroundClick = !drag.moved && !drag.node;
      drag = null; svg.classList.remove("dragging");
      if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId);
      if (backgroundClick) clearSelection();
      setTimeout(() => { skipClick = false; }, 0);
    };
    svg.addEventListener("pointerup", endDrag);
    svg.addEventListener("pointercancel", endDrag);
    svg.addEventListener("wheel", event => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault(); const p = point(event); zoomAt(event.deltaY < 0 ? 1.12 : 1 / 1.12, p.x, p.y);
    }, { passive: false });
    svg.addEventListener("keydown", event => {
      if (event.key === "+" || event.key === "=") { event.preventDefault(); zoomAt(1.3); }
      else if (event.key === "-") { event.preventDefault(); zoomAt(1 / 1.3); }
      else if (event.key === "Escape") { clearSelection(); }
      else if (event.target === svg && ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
        event.preventDefault();
        camera.x += event.key === "ArrowLeft" ? 60 : event.key === "ArrowRight" ? -60 : 0;
        camera.y += event.key === "ArrowUp" ? 60 : event.key === "ArrowDown" ? -60 : 0;
        drawCamera();
      }
    });
    if (window.matchMedia("(max-width:600px)").matches) selectGroup("0");
    else drawCamera();
  }
  library.querySelector(".vi-library-tools").hidden = false;
  const filter = () => {
    const words = normalize(input.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach((card, i) => {
      card.hidden = !words.every(word => texts[i].includes(word));
      if (!card.hidden) visible++;
    });
    groups.forEach(group => { group.hidden = ![...group.querySelectorAll(".vi-paper")].some(card => !card.hidden); });
    count.textContent = words.length ? visible + " of " + cards.length + " papers" : cards.length + " papers · explore by idea or follow the connections";
    library.querySelector("[data-vi-empty]").hidden = visible > 0;
  };
  input.addEventListener("input", filter);
  library.querySelector("[data-vi-clear]").addEventListener("click", () => { input.value = ""; filter(); input.focus(); });
  const reveal = () => {
    const id = location.hash.slice(1);
    const target = document.getElementById(id);
    if (!target || !library.contains(target)) return;
    if (input.value) { input.value = ""; filter(); }
    if (target.classList.contains("vi-paper")) target.querySelector(".vi-paper-theory") && (target.querySelector(".vi-paper-theory").open = true);
    const containingTheory = target.closest(".vi-paper-theory");
    if (containingTheory) containingTheory.open = true;
    requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
  };
  window.addEventListener("hashchange", reveal);
  library.addEventListener("click", event => {
    if (event.defaultPrevented) return;
    const link = event.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash) reveal();
  });
  filter();
  if (window.MathJax?.startup?.promise) window.MathJax.startup.promise.then(reveal);
  else window.addEventListener("load", reveal, { once: true });
})();
