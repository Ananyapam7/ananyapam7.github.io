from __future__ import annotations

from pathlib import Path

from .model import SIBLING_EDGE_TYPES, FamilyTree, Person

NODE_W = 180
NODE_H = 72
GAP_X = 42
GAP_Y = 126
MARGIN = 48

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Family Tree</title>
  <style>
    :root {
      --bg: #f7f3ec;
      --card: #fffdf8;
      --ink: #241f18;
      --muted: #756a5a;
      --line: #b7a68c;
      --spouse: #8a7459;
      --sibling: #6f8b76;
      --spouse-active: #b45f3c;
      --sibling-active: #3f8a7e;
      --accent: #2d2a26;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--ink);
      min-height: 100vh;
    }
    header {
      padding: 1.4rem 1.5rem 0.8rem;
      background: #fffaf1;
      border-bottom: 1px solid #e5dccd;
      position: sticky;
      top: 0;
      z-index: 3;
    }
    h1 {
      margin: 0 0 0.25rem;
      font-size: 1.35rem;
      font-weight: 650;
    }
    p.sub {
      margin: 0;
      color: var(--muted);
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-top: 0.8rem;
      color: var(--muted);
      font-size: 0.84rem;
    }
    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.6rem;
      margin-top: 0.9rem;
    }
    .zoom-label {
      color: var(--muted);
      font-size: 0.84rem;
      min-width: 3.5rem;
      text-align: center;
    }
    .zoom-btn {
      appearance: none;
      border: 1px solid #d8cdbd;
      background: #fffdf8;
      color: var(--ink);
      border-radius: 999px;
      padding: 0.45rem 0.8rem;
      font: inherit;
      font-size: 0.88rem;
      cursor: pointer;
      transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
    }
    .zoom-btn:hover {
      background: #f4ede2;
      border-color: #cdbca4;
    }
    .zoom-btn:active {
      transform: translateY(1px);
    }
    .sample-line {
      display: inline-block;
      width: 2rem;
      border-top: 2px solid var(--line);
    }
    .sample-line.spouse {
      border-color: var(--spouse);
      border-top-style: dashed;
    }
    .sample-line.sibling {
      border-color: var(--sibling);
      border-top-style: dotted;
    }
    .tree-shell {
      overflow: auto;
      padding: 1.25rem;
    }
    .tree-stage {
      display: inline-block;
      transform-origin: top left;
      transition: transform 0.12s ease;
    }
    .tree-canvas {
      position: relative;
      width: __WIDTH__px;
      height: __HEIGHT__px;
      min-width: __WIDTH__px;
      background: #fffaf3;
      border: 1px solid #e1d7c8;
      border-radius: 10px;
      box-shadow: 0 8px 28px rgba(36, 31, 24, 0.08);
    }
    .tree-links {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      overflow: visible;
      pointer-events: none;
    }
    .tree-link {
      fill: none;
      stroke: var(--line);
      stroke-width: 2;
      stroke-linecap: round;
    }
    .tree-link.spouse {
      stroke: var(--spouse);
      stroke-dasharray: 6 5;
    }
    .tree-link.sibling {
      stroke: var(--sibling);
      stroke-dasharray: 2 6;
    }
    .generation-label {
      position: absolute;
      left: 16px;
      width: 10rem;
      color: var(--muted);
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .person {
      position: absolute;
      width: __NODE_W__px;
      min-height: __NODE_H__px;
      background: var(--card);
      border: 1px solid #d9cbb8;
      border-radius: 8px;
      padding: 0.7rem 0.75rem;
      box-shadow: 0 3px 12px rgba(36, 31, 24, 0.08);
      cursor: pointer;
      transition: opacity 0.15s ease, transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    }
    .person:hover {
      transform: translateY(-1px);
      border-color: #cdbca4;
      box-shadow: 0 6px 18px rgba(36, 31, 24, 0.12);
    }
    .person .name {
      font-weight: 700;
      line-height: 1.16;
      margin-bottom: 0.3rem;
    }
    .person .meta {
      font-size: 0.78rem;
      line-height: 1.25;
      color: var(--muted);
    }
    .person .id {
      font-size: 0.64rem;
      color: #a19380;
      margin-top: 0.35rem;
    }
    .tree-canvas.selection-mode .person,
    .tree-canvas.selection-mode .tree-link {
      opacity: 0.2;
    }
    .tree-canvas.selection-mode .generation-label {
      opacity: 0.35;
    }
    .person.selected,
    .person.is-child,
    .person.is-sibling,
    .person.is-parent,
    .person.is-ancestor,
    .person.is-spouse {
      opacity: 1 !important;
    }
    .person.selected {
      border-color: var(--accent);
      background: #f4ede2;
      box-shadow: 0 0 0 3px rgba(45, 42, 38, 0.12), 0 10px 26px rgba(36, 31, 24, 0.18);
    }
    .person.is-child {
      border-color: #8b5e34;
      background: #fff4e9;
      box-shadow: 0 0 0 2px rgba(139, 94, 52, 0.12);
    }
    .person.is-sibling {
      border-color: var(--sibling-active);
      background: #edf8f5;
      box-shadow: 0 0 0 2px rgba(63, 138, 126, 0.12);
    }
    .person.is-parent {
      border-color: #4c6b88;
      background: #eef5fb;
      box-shadow: 0 0 0 2px rgba(76, 107, 136, 0.12);
    }
    .person.is-ancestor {
      border-color: #7f88a6;
      background: #f3f4fb;
      box-shadow: 0 0 0 2px rgba(127, 136, 166, 0.1);
    }
    .person.is-spouse {
      border-color: var(--spouse-active);
      background: #fbf0eb;
      box-shadow: 0 0 0 2px rgba(180, 95, 60, 0.1);
    }
    .tree-link {
      transition: opacity 0.15s ease, stroke 0.15s ease, stroke-width 0.15s ease, filter 0.15s ease;
    }
    .tree-link.edge-child,
    .tree-link.edge-sibling,
    .tree-link.edge-parent,
    .tree-link.edge-ancestor,
    .tree-link.edge-spouse {
      opacity: 1 !important;
    }
    .tree-link.edge-spouse {
      stroke: var(--spouse-active);
      stroke-width: 4;
      filter: drop-shadow(0 2px 4px rgba(180, 95, 60, 0.2));
    }
    .tree-link.edge-sibling {
      stroke: var(--sibling-active);
      stroke-width: 4;
      filter: drop-shadow(0 2px 4px rgba(63, 138, 126, 0.2));
    }
    .tree-link.edge-parent {
      stroke: #4c6b88;
      stroke-width: 4;
      filter: drop-shadow(0 2px 4px rgba(76, 107, 136, 0.18));
    }
    .tree-link.edge-child {
      stroke: #8b5e34;
      stroke-width: 4;
      filter: drop-shadow(0 2px 4px rgba(139, 94, 52, 0.18));
    }
    .tree-link.edge-ancestor {
      stroke: #7f88a6;
      stroke-width: 3.5;
      filter: drop-shadow(0 1px 3px rgba(127, 136, 166, 0.16));
    }
    .search-wrap {
      display: flex;
      align-items: center;
      gap: 0.55rem;
      margin-left: auto;
      min-width: min(100%, 22rem);
    }
    .search-field {
      flex: 1 1 16rem;
      min-width: 12rem;
      appearance: none;
      border: 1px solid #d8cdbd;
      background: #fffdf8;
      color: var(--ink);
      border-radius: 999px;
      padding: 0.5rem 0.85rem;
      font: inherit;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    }
    .search-field:focus {
      border-color: #b89b73;
      box-shadow: 0 0 0 3px rgba(184, 155, 115, 0.14);
      background: #fffaf3;
    }
    .search-status {
      color: var(--muted);
      font-size: 0.82rem;
      min-width: 4rem;
      text-align: right;
      white-space: nowrap;
    }
    .search-results[hidden] {
      display: none;
    }
    .search-results {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 0.5rem;
      margin-top: 0.85rem;
    }
    .search-result {
      appearance: none;
      width: 100%;
      text-align: left;
      border: 1px solid #dfd4c4;
      background: rgba(255, 253, 248, 0.96);
      color: var(--ink);
      border-radius: 12px;
      padding: 0.7rem 0.8rem;
      cursor: pointer;
      transition: border-color 0.15s ease, background 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
    }
    .search-result:hover {
      transform: translateY(-1px);
      border-color: #cdbca4;
      background: #fff8ee;
      box-shadow: 0 8px 18px rgba(36, 31, 24, 0.08);
    }
    .search-result.active {
      border-color: #b89b73;
      background: #fff5e8;
      box-shadow: 0 0 0 3px rgba(184, 155, 115, 0.12);
    }
    .search-result-name {
      display: block;
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: 0.2rem;
    }
    .search-result-meta {
      display: block;
      color: var(--muted);
      font-size: 0.78rem;
      line-height: 1.25;
    }
    .tree-canvas.search-mode .person {
      opacity: 0.24;
    }
    .tree-canvas.search-mode .person.search-match {
      opacity: 1;
    }
    .person.search-match {
      border-color: #b89b73;
      background: #fff7eb;
      box-shadow: 0 0 0 2px rgba(184, 155, 115, 0.1);
    }
    .person.search-active {
      border-color: #9a6f2d;
      box-shadow: 0 0 0 3px rgba(154, 111, 45, 0.16), 0 10px 24px rgba(36, 31, 24, 0.16);
    }
    @media (max-width: 820px) {
      .search-wrap {
        margin-left: 0;
        width: 100%;
      }
      .search-status {
        min-width: 0;
      }
    }
    .empty {
      text-align: center;
      color: var(--muted);
      padding: 4rem 1rem;
    }
    footer {
      padding: 1rem 1.5rem;
      font-size: 0.8rem;
      color: var(--muted);
    }
    @media print {
      @page { size: landscape; margin: 0.25in; }
      header { position: static; }
      .tree-shell { padding: 0; overflow: visible; }
      .toolbar { display: none; }
      .tree-stage { transform: none !important; }
      .tree-canvas { box-shadow: none; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Family Tree</h1>
    <p class="sub">__PERSON_COUNT__ people · __REL_COUNT__ relationships</p>
    <div class="legend">
      <span><i class="sample-line"></i>Parent / child</span>
      <span><i class="sample-line spouse"></i>Spouse</span>
      <span><i class="sample-line sibling"></i>Sibling</span>
    </div>
    <div class="toolbar">
      <button class="zoom-btn" id="zoom-out" type="button">Zoom out</button>
      <div class="zoom-label" id="zoom-label">35%</div>
      <button class="zoom-btn" id="zoom-in" type="button">Zoom in</button>
      <button class="zoom-btn" id="zoom-reset" type="button">Reset</button>
      <label class="search-wrap" for="people-search">
        <input class="search-field" id="people-search" type="search" placeholder="Search people" autocomplete="off" spellcheck="false">
        <span class="search-status" id="search-status">Type to search</span>
      </label>
    </div>
    <div class="search-results" id="search-results" hidden></div>
  </header>
  <main class="tree-shell">
__TREE__
  </main>
  <footer>Standalone share file generated from your local family tree data.</footer>
  <script>
    (function () {
      const stage = document.getElementById("tree-stage");
      const label = document.getElementById("zoom-label");
      const zoomIn = document.getElementById("zoom-in");
      const zoomOut = document.getElementById("zoom-out");
      const zoomReset = document.getElementById("zoom-reset");
      const searchInput = document.getElementById("people-search");
      const searchStatus = document.getElementById("search-status");
      const searchResults = document.getElementById("search-results");
      const shell = document.querySelector(".tree-shell");
      const canvas = document.querySelector(".tree-canvas");
      if (!stage || !canvas || !shell) return;

      let scale = 0.35;
      let selectedId = null;
      let searchMatches = [];
      let activeSearchIndex = 0;

      const people = Array.from(document.querySelectorAll(".person")).map((node) => ({
        id: node.dataset.personId,
        node,
        name: (node.querySelector(".name")?.textContent || "").trim(),
        meta: (node.querySelector(".meta")?.textContent || "").trim(),
        searchText: [
          node.querySelector(".name")?.textContent || "",
          node.querySelector(".meta")?.textContent || "",
          node.getAttribute("title") || "",
        ].join(" ").toLowerCase(),
      }));
      const peopleById = new Map(people.map((person) => [person.id, person]));

      const links = Array.from(document.querySelectorAll(".tree-link")).map((path) => ({
        path,
        type: path.dataset.type,
        from: path.dataset.from || null,
        to: path.dataset.to || null,
      }));

      const parentsByChild = new Map();
      const childrenByParent = new Map();
      const siblingsByPerson = new Map();
      const spousesByPerson = new Map();

      function addToMapSet(map, key, value) {
        if (!key || !value) return;
        if (!map.has(key)) map.set(key, new Set());
        map.get(key).add(value);
      }

      for (const link of links) {
        if (link.type === "parent") {
          addToMapSet(parentsByChild, link.to, link.from);
          addToMapSet(childrenByParent, link.from, link.to);
        } else if (link.type === "sibling") {
          addToMapSet(siblingsByPerson, link.from, link.to);
          addToMapSet(siblingsByPerson, link.to, link.from);
        } else if (link.type === "spouse") {
          addToMapSet(spousesByPerson, link.from, link.to);
          addToMapSet(spousesByPerson, link.to, link.from);
        }
      }

      for (const [childId, parentSet] of parentsByChild.entries()) {
        const parents = Array.from(parentSet);
        for (const parentId of parents) {
          const siblings = childrenByParent.get(parentId) || new Set();
          for (const siblingId of siblings) {
            if (siblingId !== childId) addToMapSet(siblingsByPerson, childId, siblingId);
          }
        }
      }

      function clearSelectionState() {
        canvas.classList.remove("selection-mode");
        for (const person of people) {
          person.node.classList.remove(
            "selected",
            "is-child",
            "is-sibling",
            "is-parent",
            "is-ancestor",
            "is-spouse"
          );
        }
        for (const link of links) {
          link.path.classList.remove(
            "edge-child",
            "edge-sibling",
            "edge-parent",
            "edge-ancestor",
            "edge-spouse"
          );
        }
      }

      function clearSearchState() {
        canvas.classList.remove("search-mode");
        for (const person of people) {
          person.node.classList.remove("search-match", "search-active");
        }
      }

      function centerPerson(personId) {
        const person = peopleById.get(personId);
        if (!person) return;
        const rect = shell.getBoundingClientRect();
        const centerX = (person.node.offsetLeft + person.node.offsetWidth / 2) * scale;
        const centerY = (person.node.offsetTop + person.node.offsetHeight / 2) * scale;
        shell.scrollLeft = Math.max(0, centerX - rect.width / 2);
        shell.scrollTop = Math.max(0, centerY - rect.height / 2);
      }

      function renderSearchResults() {
        if (!searchResults || !searchStatus) return;
        searchResults.replaceChildren();
        const query = searchInput?.value.trim() || "";
        if (!query) {
          searchResults.hidden = true;
          searchStatus.textContent = "Type to search";
          return;
        }
        if (!searchMatches.length) {
          searchResults.hidden = true;
          searchStatus.textContent = "No matches";
          return;
        }

        searchStatus.textContent = `${searchMatches.length} match${searchMatches.length === 1 ? "" : "es"}`;
        const limit = Math.min(searchMatches.length, 8);
        for (let index = 0; index < limit; index += 1) {
          const person = searchMatches[index];
          const button = document.createElement("button");
          button.type = "button";
          button.className = "search-result";
          if (index === activeSearchIndex) button.classList.add("active");

          const name = document.createElement("span");
          name.className = "search-result-name";
          name.textContent = person.name || "Unnamed person";

          const meta = document.createElement("span");
          meta.className = "search-result-meta";
          meta.textContent = person.meta || "—";

          button.append(name, meta);
          button.addEventListener("click", function () {
            activeSearchIndex = index;
            applySelection(person.id);
            renderSearch();
            centerPerson(person.id);
          });
          searchResults.appendChild(button);
        }
        searchResults.hidden = false;
      }

      function renderSearch() {
        clearSearchState();
        const query = searchInput?.value.trim().toLowerCase() || "";
        if (!query) {
          searchMatches = [];
          activeSearchIndex = 0;
          renderSearchResults();
          return;
        }

        searchMatches = people.filter((person) => person.searchText.includes(query));
        if (!searchMatches.length) {
          activeSearchIndex = 0;
          renderSearchResults();
          return;
        }

        activeSearchIndex = Math.max(0, Math.min(activeSearchIndex, searchMatches.length - 1));
        canvas.classList.add("search-mode");
        for (const person of searchMatches) person.node.classList.add("search-match");
        searchMatches[activeSearchIndex]?.node.classList.add("search-active");
        renderSearchResults();
      }

      function focusSearchMatch(index) {
        if (!searchMatches.length) return;
        activeSearchIndex = (index + searchMatches.length) % searchMatches.length;
        const person = searchMatches[activeSearchIndex];
        if (!person) return;
        applySelection(person.id);
        renderSearch();
        centerPerson(person.id);
      }

      function collectAncestors(personId) {
        const ancestors = new Set();
        const stack = [...(parentsByChild.get(personId) || [])];
        while (stack.length) {
          const nextId = stack.pop();
          if (!nextId || ancestors.has(nextId)) continue;
          ancestors.add(nextId);
          for (const parentId of parentsByChild.get(nextId) || []) {
            if (!ancestors.has(parentId)) stack.push(parentId);
          }
        }
        return ancestors;
      }

      function applySelection(personId) {
        selectedId = personId;
        clearSelectionState();
        if (!personId) return;

        canvas.classList.add("selection-mode");
        const childIds = new Set(childrenByParent.get(personId) || []);
        const parentIds = new Set(parentsByChild.get(personId) || []);
        const siblingIds = new Set(siblingsByPerson.get(personId) || []);
        const spouseIds = new Set(spousesByPerson.get(personId) || []);
        const ancestorIds = collectAncestors(personId);
        for (const parentId of parentIds) ancestorIds.delete(parentId);

        for (const link of links) {
          if (link.type === "parent") {
            if (link.from === personId && childIds.has(link.to)) {
              link.path.classList.add("edge-child");
            } else if (link.to === personId && parentIds.has(link.from)) {
              link.path.classList.add("edge-parent");
            } else if (ancestorIds.has(link.from) && (ancestorIds.has(link.to) || parentIds.has(link.to))) {
              link.path.classList.add("edge-ancestor");
            }
          } else if (link.type === "sibling") {
            if (link.from === personId || link.to === personId) {
              link.path.classList.add("edge-sibling");
            }
          } else if (link.type === "spouse") {
            if (link.from === personId || link.to === personId) {
              link.path.classList.add("edge-spouse");
            }
          }
        }

        for (const person of people) {
          if (person.id === personId) {
            person.node.classList.add("selected");
          } else if (childIds.has(person.id)) {
            person.node.classList.add("is-child");
          } else if (siblingIds.has(person.id)) {
            person.node.classList.add("is-sibling");
          } else if (parentIds.has(person.id)) {
            person.node.classList.add("is-parent");
          } else if (ancestorIds.has(person.id)) {
            person.node.classList.add("is-ancestor");
          } else if (spouseIds.has(person.id)) {
            person.node.classList.add("is-spouse");
          }
        }
      }

      function toggleSelection(personId) {
        applySelection(selectedId === personId ? null : personId);
      }

      function renderZoom() {
        stage.style.transform = `scale(${scale})`;
        label.textContent = `${Math.round(scale * 100)}%`;
      }

      function setZoom(nextScale) {
        const clamped = Math.max(0.35, Math.min(2, nextScale));
        if (clamped === scale) return;
        const rect = shell.getBoundingClientRect();
        const centerX = shell.scrollLeft + rect.width / 2;
        const centerY = shell.scrollTop + rect.height / 2;
        const ratio = clamped / scale;
        scale = clamped;
        renderZoom();
        shell.scrollLeft = centerX * ratio - rect.width / 2;
        shell.scrollTop = centerY * ratio - rect.height / 2;
      }

      zoomIn?.addEventListener("click", function () {
        setZoom(Number((scale + 0.1).toFixed(2)));
      });

      zoomOut?.addEventListener("click", function () {
        setZoom(Number((scale - 0.1).toFixed(2)));
      });

      zoomReset?.addEventListener("click", function () {
        setZoom(1);
      });

      for (const person of people) {
        person.node.setAttribute("tabindex", "0");
        person.node.setAttribute("role", "button");
        person.node.addEventListener("click", function (event) {
          event.stopPropagation();
          toggleSelection(person.id);
        });
        person.node.addEventListener("keydown", function (event) {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            toggleSelection(person.id);
          }
        });
      }

      searchInput?.addEventListener("input", function () {
        activeSearchIndex = 0;
        renderSearch();
        if (!searchMatches.length) {
          applySelection(null);
          return;
        }
        applySelection(searchMatches[0].id);
        renderSearch();
        centerPerson(searchMatches[0].id);
      });

      searchInput?.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
          focusSearchMatch(activeSearchIndex);
        } else if (event.key === "ArrowDown") {
          event.preventDefault();
          focusSearchMatch(activeSearchIndex + 1);
        } else if (event.key === "ArrowUp") {
          event.preventDefault();
          focusSearchMatch(activeSearchIndex - 1);
        } else if (event.key === "Escape") {
          searchInput.value = "";
          applySelection(null);
          renderSearch();
        }
      });

      shell.addEventListener("click", function (event) {
        if (!event.target.closest(".person")) applySelection(null);
      });

      renderZoom();
      renderSearch();
    })();
  </script>
</body>
</html>
"""


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _meta_line(person: Person) -> str:
    parts = []
    if person.birth:
        parts.append(f"b. {person.birth}")
    if person.death:
        parts.append(f"d. {person.death}")
    if person.gender:
        parts.append(person.gender)
    if person.occupation:
        parts.append(person.occupation)
    return " · ".join(parts) if parts else "—"


def _order_with_spouses(people: list[Person], tree: FamilyTree) -> list[Person]:
    ids = {person.id for person in people}
    ordered: list[Person] = []
    used: set[str] = set()

    for person in people:
        if person.id in used:
            continue
        ordered.append(person)
        used.add(person.id)
        for spouse in tree.spouses_of(person.id):
            if spouse.id in ids and spouse.id not in used:
                ordered.append(spouse)
                used.add(spouse.id)
                break

    return ordered


def _layout(tree: FamilyTree) -> tuple[int, int, dict[str, tuple[int, int]], list[list[Person]]]:
    generations = [_order_with_spouses(gen, tree) for gen in tree.generations()]
    max_count = max((len(generation) for generation in generations), default=0)
    width = max(900, MARGIN * 2 + max_count * NODE_W + max(0, max_count - 1) * GAP_X)
    height = MARGIN * 2 + len(generations) * NODE_H + max(0, len(generations) - 1) * GAP_Y
    positions: dict[str, tuple[int, int]] = {}

    for gen_index, generation in enumerate(generations):
        row_width = len(generation) * NODE_W + max(0, len(generation) - 1) * GAP_X
        start_x = max(MARGIN, (width - row_width) // 2)
        y = MARGIN + gen_index * (NODE_H + GAP_Y)
        for index, person in enumerate(generation):
            positions[person.id] = (start_x + index * (NODE_W + GAP_X), y)

    return width, height, positions, generations


def _person_node(person: Person, x: int, y: int) -> str:
    notes = f"\n    <div class=\"meta\">{_escape(person.notes)}</div>" if person.notes else ""
    title_parts = [person.name, _meta_line(person)]
    if person.birth_place:
        title_parts.append(f"Born in {person.birth_place}")
    if person.death_place:
        title_parts.append(f"Died in {person.death_place}")
    if person.sources:
        title_parts.append(f"Sources: {person.sources}")
    title = _escape(" | ".join(title_parts))
    return f"""  <article class="person" data-person-id="{_escape(person.id)}" style="left:{x}px;top:{y}px" title="{title}">
    <div class="name">{_escape(person.name)}</div>
    <div class="meta">{_escape(_meta_line(person))}</div>{notes}
    <div class="id">id: {_escape(person.id)}</div>
  </article>"""


def _parent_path(parent_id: str, child_id: str, parent: tuple[int, int], child: tuple[int, int]) -> str:
    start_x = parent[0] + NODE_W / 2
    start_y = parent[1] + NODE_H
    end_x = child[0] + NODE_W / 2
    end_y = child[1]
    mid_y = start_y + (end_y - start_y) * 0.55
    return (
        f'<path class="tree-link" data-type="parent" data-from="{_escape(parent_id)}" data-to="{_escape(child_id)}" d="M {start_x:.1f} {start_y:.1f} '
        f'C {start_x:.1f} {mid_y:.1f}, {end_x:.1f} {mid_y:.1f}, '
        f'{end_x:.1f} {end_y:.1f}" />'
    )


def _spouse_path(first_id: str, second_id: str, first: tuple[int, int], second: tuple[int, int]) -> str:
    start, end = (first, second) if first[0] <= second[0] else (second, first)
    start_id, end_id = (
        (first_id, second_id) if first[0] <= second[0] else (second_id, first_id)
    )
    y = start[1] + NODE_H / 2
    return (
        f'<path class="tree-link spouse" data-type="spouse" data-from="{_escape(start_id)}" data-to="{_escape(end_id)}" d="M {start[0] + NODE_W:.1f} {y:.1f} '
        f'C {start[0] + NODE_W + 18:.1f} {y - 18:.1f}, '
        f'{end[0] - 18:.1f} {y - 18:.1f}, {end[0]:.1f} {y:.1f}" />'
    )


def _sibling_path(first_id: str, second_id: str, first: tuple[int, int], second: tuple[int, int]) -> str:
    start, end = (first, second) if first[0] <= second[0] else (second, first)
    start_id, end_id = (
        (first_id, second_id) if first[0] <= second[0] else (second_id, first_id)
    )
    y = max(start[1], end[1]) + NODE_H + 16
    start_x = start[0] + NODE_W / 2
    end_x = end[0] + NODE_W / 2
    return (
        f'<path class="tree-link sibling" data-type="sibling" data-from="{_escape(start_id)}" data-to="{_escape(end_id)}" d="M {start_x:.1f} {y:.1f} '
        f'C {start_x:.1f} {y + 18:.1f}, {end_x:.1f} {y + 18:.1f}, '
        f'{end_x:.1f} {y:.1f}" />'
    )


def _render_tree(tree: FamilyTree) -> tuple[str, int, int]:
    if not tree.people:
        return '<p class="empty">No people in the tree yet.</p>', 900, 360

    width, height, positions, generations = _layout(tree)
    link_parts: list[str] = []
    node_parts: list[str] = []
    label_parts: list[str] = []

    for gen_index, generation in enumerate(generations):
        if not generation:
            continue
        y = MARGIN + gen_index * (NODE_H + GAP_Y)
        label = "Earliest generation" if gen_index == 0 else f"Generation {gen_index + 1}"
        label_parts.append(
            f'  <div class="generation-label" style="top:{max(8, y - 28)}px">{_escape(label)}</div>'
        )

    for rel in tree.relationships:
        first = positions.get(rel.person_a)
        second = positions.get(rel.person_b)
        if not first or not second:
            continue
        if rel.type == "parent":
            link_parts.append(_parent_path(rel.person_a, rel.person_b, first, second))
        elif rel.type == "spouse":
            link_parts.append(_spouse_path(rel.person_a, rel.person_b, first, second))
        elif rel.type in SIBLING_EDGE_TYPES:
            link_parts.append(_sibling_path(rel.person_a, rel.person_b, first, second))

    for person in tree.people.values():
        position = positions.get(person.id)
        if position:
            node_parts.append(_person_node(person, *position))

    links = "\n    ".join(link_parts)
    labels = "\n".join(label_parts)
    nodes = "\n".join(node_parts)
    body = f"""<div class="tree-stage" id="tree-stage">
<div class="tree-canvas">
  <svg class="tree-links" viewBox="0 0 {width} {height}" aria-hidden="true">
    {links}
  </svg>
{labels}
{nodes}
</div>
</div>"""
    return body, width, height


def export_html_document(tree: FamilyTree) -> str:
    body, width, height = _render_tree(tree)
    return (
        HTML_TEMPLATE.replace("__PERSON_COUNT__", str(len(tree.people)))
        .replace("__REL_COUNT__", str(len(tree.relationships)))
        .replace("__TREE__", body)
        .replace("__WIDTH__", str(width))
        .replace("__HEIGHT__", str(height))
        .replace("__NODE_W__", str(NODE_W))
        .replace("__NODE_H__", str(NODE_H))
    )


def export_html(tree: FamilyTree, output: Path) -> Path:
    html = export_html_document(tree)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output
