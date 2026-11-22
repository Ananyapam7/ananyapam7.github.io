"""Render a navigable, dependency-free paper constellation from the reading metadata."""
import html
import math
import textwrap


def render_network(data, papers):
    esc = html.escape
    groups = data["groups"]
    grouped_ids = [pid for group in groups for pid in group["papers"]]
    assert len(grouped_ids) == len(set(grouped_ids)), "Duplicate paper placement"
    assert set(grouped_ids) == set(papers), "Every paper needs an idea group"
    colors = ["#71d6cf", "#9aaeff", "#f2b78a", "#c1a1f1", "#ed99ba", "#a3d6ad", "#e6cf85", "#9fc4e0", "#7ac9ef", "#e4b8d8"]
    centers = [(375, 290), (740, 150), (1015, 350), (755, 450),
               (480, 685), (190, 600), (160, 145), (980, 725), (1300, 245), (1300, 630)]
    names = ["Foundations", "Pathwise gradients", "Discrete variables", "Gradient noise",
             "Objectives", "Expressive families", "Amortization", "Accuracy & guarantees", "Gaussian processes", "Neural weights"]
    positions = {}
    degrees = {pid: 0 for pid in papers}
    edges = set()
    for pid, paper in papers.items():
        for target in paper.get("connections", []):
            assert target in papers, f"Unknown connection: {target}"
            if target != pid:
                edges.add(tuple(sorted((pid, target))))
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1
    for gi, group in enumerate(groups):
        # A deterministic orbital layout prevents motion and label jitter while reading.
        cx, cy = centers[gi] if gi < len(centers) else (600, 450)
        n = len(group["papers"])
        radius = 65 + 4.6 * n
        for i, pid in enumerate(group["papers"]):
            angle = -math.pi / 2 + 2 * math.pi * i / n + gi * .16
            r = radius * (1 + .09 * math.sin(i * 2.4))
            positions[pid] = (cx + r * math.cos(angle), cy + .83 * r * math.sin(angle), gi)
    out = [
        '<section class="vi-network" aria-labelledby="vi-network-title">',
        '<header class="vi-network-heading"><p class="vi-network-eyebrow">THE IDEA ATLAS</p>',
        '<h3 id="vi-network-title">One foundation. Many directions.</h3>',
        '<p>Explore the connections. Follow the question that interests you.</p></header>',
        '<div class="vi-network-toolbar"><label class="vi-network-search-label"><span>Find a paper</span>',
        '<input type="search" data-network-search placeholder="Title, author, or idea…" autocomplete="off" aria-label="Find a paper in the network"></label>',
        '<div class="vi-network-controls"><button type="button" data-network-zoom="in" aria-label="Zoom in">+</button><button type="button" data-network-zoom="out" aria-label="Zoom out">−</button><button type="button" data-network-reset>Reset view</button></div></div>',
        '<div class="vi-network-results" data-network-results hidden aria-label="Matching papers"></div>',
        '<nav class="vi-network-legend" aria-label="Explore an idea"><button type="button" data-network-group="all" class="active" aria-pressed="true">All ideas</button>'
    ]
    for gi, group in enumerate(groups):
        out.append(f'<button type="button" data-network-group="{gi}" aria-pressed="false" style="--node-color:{colors[gi % len(colors)]}"><i></i>{esc(names[gi] if gi < len(names) else group["label"])}</button>')
    out += ['</nav>', '<div class="vi-network-stage">',
            f'<svg class="vi-network-canvas" viewBox="0 0 1500 900" tabindex="0" role="group" aria-label="Interactive map of {len(papers)} papers. Drag to pan, use plus and minus to zoom. Select a paper to open its details. Press Escape to deselect.">',
            '<defs><radialGradient id="vi-atlas-halo"><stop offset="0" stop-color="currentColor" stop-opacity=".12"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></radialGradient><pattern id="vi-atlas-dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#8098b8" opacity=".16"/></pattern></defs>',
            '<rect width="1500" height="900" fill="url(#vi-atlas-dots)" pointer-events="none"/>',
            '<g class="vi-network-world">']
    for gi, group in enumerate(groups):
        cx, cy = centers[gi] if gi < len(centers) else (600, 450)
        color = colors[gi % len(colors)]
        radius = 115 + len(group["papers"]) * 5
        out.append(f'<circle class="vi-network-halo" cx="{cx}" cy="{cy}" r="{radius}" fill="url(#vi-atlas-halo)" style="color:{color}" pointer-events="none"/>')
    for a, b in sorted(edges):
        x, y, _ = positions[a]; xx, yy, _ = positions[b]
        out.append(f'<path class="vi-network-edge" data-from="{a}" data-to="{b}" d="M{x:.2f},{y:.2f} Q{(x+xx)/2+12:.2f},{(y+yy)/2-18:.2f} {xx:.2f},{yy:.2f}"/>')
    for gi, group in enumerate(groups):
        cx, cy = centers[gi] if gi < len(centers) else (600, 450)
        color = colors[gi % len(colors)]
        out.append(f'<g class="vi-network-hub" data-hub="{gi}" data-x="{cx}" data-y="{cy}" transform="translate({cx},{cy})" style="--node-color:{color}"><text text-anchor="middle">{esc(names[gi] if gi < len(names) else group["label"])}</text><text class="vi-network-hub-count" text-anchor="middle" y="19">{len(group["papers"])} papers</text></g>')
    for pid, p in papers.items():
        x, y, gi = positions[pid]
        group_papers = groups[gi]["papers"]
        featured = sorted(group_papers, key=lambda k: -degrees[k])[:3]
        cx, cy = centers[gi] if gi < len(centers) else (600, 450)
        lines = textwrap.wrap(p["short"], width=21)
        dx, dy = x-cx, y-cy
        length = math.hypot(dx, dy)
        # Labels point away from their hub and stay inside the canvas.
        lx = max(75-x, min(1425-x, dx/length*40))
        ly = 25 if dy > length*.3 else -18-14*(len(lines)-1) if dy < -length*.3 else 4
        label = "".join(f'<tspan x="{lx:.1f}" dy="{0 if i == 0 else 14}">{esc(line)}</tspan>'
                        for i, line in enumerate(lines))
        radius = min(9, 4.5 + degrees[pid] * .3)
        out.append(f'<a class="vi-network-node{" featured" if pid in featured else ""}" href="#{pid}" data-paper="{pid}" data-group="{gi}" data-x="{x:.2f}" data-y="{y:.2f}" transform="translate({x:.2f},{y:.2f})" style="--node-color:{colors[gi % len(colors)]}" aria-label="{esc(p["title"])} ({esc(p["year"])}): preview paper"><title>{esc(p["title"])} — {esc(p["year"])}</title><circle class="vi-network-hit" r="19"/><circle class="vi-network-ring" r="{radius+5:.1f}"/><circle class="vi-network-dot" r="{radius:.1f}"/><text text-anchor="middle" y="{ly}">{label}</text></a>')
    out += ['</g></svg><p class="vi-network-gesture">Drag to explore · Click a paper for details · Esc to clear</p>',
            '<span class="vi-network-scale" data-network-scale>100%</span></div>',
            '<dialog class="vi-network-dialog" aria-labelledby="vi-dialog-title"><header class="vi-dialog-bar"><span id="vi-dialog-title">Paper details</span><button type="button" data-network-close aria-label="Close paper details">Close <span aria-hidden="true">×</span></button></header><div data-network-detail></div></dialog>',
            f'<footer class="vi-network-footnote"><span>{len(papers)} papers · {len(groups)} connected ideas</span><span>Connections are conceptual, not citation counts.</span></footer></section>']
    return "\n".join(out)
