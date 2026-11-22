(() => {
  const library = document.querySelector(".vi-library");
  if (!library) return;
  const cards = [...library.querySelectorAll(".vi-paper")];
  const methodCount = cards.filter(card => card.dataset.kind === "method").length;
  const groups = [...library.querySelectorAll(".vi-paper-group")];
  const input = library.querySelector("#vi-paper-search");
  const count = library.querySelector("[data-vi-count]");
  const normalize = (s) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const texts = cards.map(card => normalize(card.textContent));
  const network = library.querySelector(".vi-network");
  if (network) {
    const nodes = [...network.querySelectorAll("[data-paper]")];
    const edges = [...network.querySelectorAll(".vi-network-edge")];

    const preview = (id) => {
      const card = document.getElementById(id);
      if (!card) return;

      const neighbors = new Set([id]);
      edges.forEach(edge => {
        const connected = edge.dataset.from === id || edge.dataset.to === id;
        edge.classList.toggle("active", connected);
        if (connected) { neighbors.add(edge.dataset.from); neighbors.add(edge.dataset.to); }
      });
      nodes.forEach(node => {
        node.classList.toggle("active", node.dataset.paper === id);
        node.classList.toggle("dim", !neighbors.has(node.dataset.paper));
      });
      network.querySelector("[data-network-title]").textContent = card.querySelector("h4").textContent;
      network.querySelector("[data-network-category]").textContent = [...card.querySelectorAll(".vi-paper-meta span")].map(e => e.textContent).join(" · ");
      network.querySelector("[data-network-authors]").textContent = card.querySelector(".vi-paper-authors").textContent;
      network.querySelector("[data-network-description]").textContent = card.querySelector(".vi-paper-change").textContent.replace(/^The move\.\s*/, "");
      const image = network.querySelector("[data-network-image]");
      image.src = card.querySelector(".vi-paper-source img").getAttribute("src");
      image.alt = card.querySelector(".vi-paper-source img").alt;
      image.hidden = false;
      const link = network.querySelector("[data-network-open]");
      link.href = "#" + id; link.hidden = false;
    };
    nodes.forEach(node => {
      node.addEventListener("pointerenter", event => { if (event.pointerType !== "touch") preview(node.dataset.paper); });
      node.addEventListener("focus", () => preview(node.dataset.paper));
      node.addEventListener("click", event => {
        if (event.pointerType === "touch") { event.preventDefault(); preview(node.dataset.paper); }
      });
    });

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
    count.textContent = words.length ? visible + " of " + cards.length + " entries" : (cards.length - methodCount) + " papers + " + methodCount + " methods · explore by idea or follow the connections";
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
    const link = event.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash) reveal();
  });
  filter();
  if (window.MathJax?.startup?.promise) window.MathJax.startup.promise.then(reveal);
  else window.addEventListener("load", reveal, { once: true });
})();
