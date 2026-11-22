"""Build the VI paper library from editable Markdown notes and JSON metadata.

Run from any directory: python scripts/build_vi_library.py
Requires: pip install Markdown
The generated include is committed so Jekyll needs no extra plugin.
"""
from pathlib import Path
import html
import json
import re
import textwrap
import markdown

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "resources/vi-papers"

def render_network(data, papers):
    esc = html.escape
    positions = {}
    colors = ["#299caa", "#6b91dc", "#cc8251", "#a184d1", "#c77a97", "#63a382", "#b39a48", "#7996ab"]
    for gi, group in enumerate(data["groups"]):
        for i, pid in enumerate(group["papers"]):
            positions[pid] = (60 + (gi % 4)*310 + (i % 2)*145, 115 + (gi // 4)*395 + (i // 2)*60, gi)
    parts = ['<section class="vi-network" aria-labelledby="vi-network-title"><div class="vi-network-heading"><p class="vi-network-eyebrow">An atlas of variational inference</p><h3 id="vi-network-title">Follow an idea through the papers</h3><p>Hover or focus a node to preview its contribution and highlight related methods. Select it to open the full paper entry below. Lines show reading connections, not historical priority.</p></div>',
             '<div class="vi-network-layout"><div class="vi-network-scroll" tabindex="0" role="region" aria-label="Paper network; scroll horizontally on small screens"><svg viewBox="0 0 1240 810" role="group" aria-label="51 papers and methods grouped into eight connected ideas">']
    edges = set()
    for pid, p in papers.items():
        for other in p.get("connections", []):
            edges.add(tuple(sorted((pid, other))))
    for a,b in sorted(edges):
        x,y,_ = positions[a]; xx,yy,_ = positions[b]
        parts.append(f'<path class="vi-network-edge" data-from="{a}" data-to="{b}" d="M{x},{y} C{(x+xx)/2},{y} {(x+xx)/2},{yy} {xx},{yy}" />')
    for gi,group in enumerate(data["groups"]):
        x=(gi%4)*310; y=(gi//4)*395
        parts.append(f'<rect class="vi-network-cluster" x="{x+8}" y="{y+10}" width="298" height="380" rx="18" />')
        parts.append(f'<text class="vi-network-group" x="{x+24}" y="{y+44}" fill="{colors[gi]}">{esc(group["label"])}</text>')
    for pid,p in papers.items():
        x,y,gi=positions[pid]
        label = "".join(f'<tspan x="{x-30}" dy="{0 if i == 0 else 14}">{esc(line)}</tspan>' for i,line in enumerate(textwrap.wrap(p["short"], width=21)))
        parts.append(f'<a class="vi-network-node" href="#{pid}" data-paper="{pid}" aria-label="{esc(p["title"])}: open full entry"><title>{esc(p["title"])} — {esc(p["year"])}</title><circle cx="{x}" cy="{y}" r="7" fill="{colors[gi]}"/><text x="{x-30}" y="{y+25}">{label}</text></a>')
    parts.append('</svg></div><aside class="vi-network-preview" aria-label="Paper preview"><p class="vi-network-eyebrow" data-network-category>Start anywhere</p><h4 data-network-title>One foundation. Many directions.</h4><img data-network-image hidden alt=""><p data-network-authors></p><p data-network-description>Choose a node to see what the paper changes, then follow its connections to nearby ideas.</p><a data-network-open hidden>Read the full explanation →</a></aside></div><p class="vi-network-footnote">On touch screens, tap a node to preview it, then use “Read the full explanation”. The question-by-question index below offers another way to navigate.</p></section>')
    return "\n".join(parts)


def render_math_markdown(source):
    saved = []

    def protect(match):
        token = f"VILIBRARYMATH{len(saved)}END"
        raw = match.group().replace("<", r"\lt ").replace(">", r"\gt ")
        display = raw.startswith(r"\[")
        tag = "div" if display else "span"
        saved.append(f'<{tag} class="vi-math">{raw}</{tag}>')
        return f"\n\n{token}\n\n" if display else token

    source = re.sub(r"\\\[.*?\\\]|\\\(.*?\\\)", protect, source, flags=re.S)
    result = markdown.markdown(source, extensions=["extra"])
    for i, value in enumerate(saved):
        token = f"VILIBRARYMATH{i}END"
        result = result.replace(f"<p>{token}</p>", value).replace(token, value)
    return result


def build():
    data = json.loads((DATA / "papers.json").read_text(encoding="utf-8"))
    papers = {p["id"]: p for p in data["papers"]}
    assert len(papers) == len(data["papers"]), "Duplicate paper IDs"
    esc = html.escape
    parts = ['<div class="vi-library" id="paper-library" markdown="0">']
    parts.append(render_network(data, papers))
    parts.append('<nav class="vi-idea-map" aria-label="Explore papers by question">')
    for group in data["groups"]:
        parts.append(f'<a href="#{esc(group["id"])}"><strong>{esc(group["label"])}</strong><span>{esc(group["question"])}</span></a>')
    parts.append('</nav><div class="vi-library-tools" hidden>')
    parts.append('<label for="vi-paper-search">Find a paper or idea</label><input id="vi-paper-search" type="search" placeholder="Try: entropy, control variates, Kingma…" autocomplete="off">')
    parts.append('<button type="button" data-vi-clear>Clear search</button><p data-vi-count role="status" aria-live="polite"></p></div>')
    parts.append('<p data-vi-empty hidden>No matching papers. Try a method name, author, or year.</p>')
    for group in data["groups"]:
        parts.append(f'<section class="vi-paper-group" id="{esc(group["id"])}" aria-labelledby="{esc(group["id"])}-title">')
        parts.append(f'<h3 id="{esc(group["id"])}-title">{esc(group["question"])}</h3><p class="vi-group-intro">{esc(group["intro"])}</p>')
        for pid in group["papers"]:
            p = papers[pid]
            note = (DATA / p["note"]).read_text(encoding="utf-8")
            if p.get("visual"):
                note = note.replace("<!-- VISUAL -->", (ROOT / p["visual"]).read_text(encoding="utf-8"))
            for linked in re.findall(r"#paper-(\d+)", note):
                assert f"paper-{linked}" in papers, f"Broken link in {pid}"
            assert (ROOT / p["image"].lstrip("/")).is_file(), p["image"]
            theory = render_math_markdown(note)
            kind = esc(p.get("kind", "paper"))
            source_title = p.get("source_title", p["title"])
            parts.append(f'<article class="vi-paper" data-kind="{kind}" id="{pid}" aria-labelledby="{pid}-title">')
            parts.append('<figure class="vi-paper-source">')
            parts.append(f'<a href="{esc(p["pdf"])}" target="_blank" rel="noopener" aria-label="Open {esc(source_title)} PDF">')
            parts.append(f'<img loading="lazy" src="{p["image"]}" width="{p.get("image_width", 773)}" height="1000" alt="First article page of {esc(source_title)}"></a>')
            parts.append(f'<figcaption><p class="vi-paper-authors">{esc(", ".join(p["authors"]))}</p>')
            parts.append(f'<a href="{esc(p["source"])}" target="_blank" rel="noopener">Paper &amp; source</a>')
            if p.get("version"):
                parts.append(f'<p class="vi-paper-version">{esc(p["version"])}</p>')
            parts.append('</figcaption></figure><div class="vi-paper-content">')
            parts.append(f'<div class="vi-paper-meta"><span>{esc(p["year"])}</span><span>{esc(p["changes"])}</span></div>')
            parts.append(f'<h4 id="{pid}-title"><a href="#{pid}">{esc(p["title"])}</a></h4>')
            if p.get("source_title"):
                parts.append(f'<p class="vi-paper-connections">Source paper: <a href="{esc(p["source"])}" target="_blank" rel="noopener">{esc(source_title)}</a></p>')
            parts.append(f'<p class="vi-paper-change"><strong>The move.</strong> {esc(p["move"])}</p>')
            if p.get("connections"):
                parts.append('<p class="vi-paper-connections"><span>Read with</span> ')
                parts.append(' · '.join(f'<a href="#{link}">{esc(papers[link]["short"])}</a>' for link in p["connections"]))
                parts.append('</p>')
            opened = ''
            parts.append(f'<details class="vi-paper-theory"{opened}><summary>The idea and the mathematics</summary><div class="vi-paper-prose">{theory}</div></details>')
            parts.append('</div></article>')
        parts.append('</section>')
    parts.append('</div>')
    output = ROOT / "_includes/vi-papers.html"
    output.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Built {len(papers)} entries in {len(data['groups'])} idea groups: {output}")


if __name__ == "__main__":
    build()
