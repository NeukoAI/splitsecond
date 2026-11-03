"""Builds the Split Second review board (one HTML page) from story.json and the document.

    python3 v2/review/build_review.py > v2/review/index.html

Every clip shows its own first and last frame next to the first frame of each
scene it can cut to, so a bad seam is visible at a glance. Feedback is saved per
item in the artifact's db (collection "feedback", doc id = item id).
"""
import html
import json
from pathlib import Path

V2 = Path(__file__).resolve().parent.parent
story = json.loads((V2 / "story.json").read_text())
doc = json.loads((V2 / "split_second_v2.json").read_text())
scenes = {s["id"]: s for s in story["scenes"]}
nodes = doc["nodes"]

# node id -> scene id
scene_of = {nid: Path(n["props"]["src"]).name for nid, n in nodes.items() if n["type"] == "video"}
media = json.loads((V2 / "media.json").read_text())
by_file = {Path(u).name: k for k, u in media.items()}
scene_of = {nid: by_file[f].removesuffix("_2") for nid, f in scene_of.items()}

KEYFRAME = {"title": "Title card", "stakes": "The chip", "k0": "Rooftop, chip in hand", "k0b": "The Hound lands",
            "k1": "D1 · The Edge", "k2": "D2 · The Market", "k3": "D3 · The Platform", "k4": "D4 · The Drop",
            "k5": "Van cab, Dex driving", "k6": "Hound watches the van go", "c_vent": "Capture at the vent", "c_alley": "Capture in the alley", "c_board": "Capture in the carriage", "c_run": "Capture on the train roof", "v_exit": "Van takes the exit", "gameover": "FLATLINED card", "win": "DELIVERED card"}


def exits(nid):
    """(label, target node) for each way out of a video node."""
    n = nodes[nid]["props"]
    out = []
    for ov in n.get("overlays", []):
        t = nodes[ov]
        if t["props"]["kind"] == "hotspot":
            out.append((t["title"].replace("tap · ", "tap: "), t["next"]))
        elif "options" in t["props"]:
            for o in t["props"]["options"]:
                out.append((f"button: {o['label']}", o["next"]))
    nxt = n["exits"][0]["next"]
    if nxt:
        label = "no tap in time" if n.get("overlays") and nodes[n["overlays"][0]]["props"]["kind"] == "hotspot" else "plays into"
        out.append((label, nxt))
    return out


ORDER = ["v_title", "v_stakes", "v_intro_call", "v_intro_hound"]
for d in story["decisions"]:
    safe = d["safe"]
    wrong = d["timeout"]
    ORDER += [f"v_{d['id']}_loop", f"v_{d['id']}_{safe}", f"v_{d['id']}_{wrong}"]
ORDER += ["v_finale_van", "v_finale_hound", "v_win", "v_gameover"]

GROUPS = [("Opening", "First run only. TRY AGAIN skips straight to the Hound's arrival.", ORDER[:4])]
for i, d in enumerate(story["decisions"]):
    GROUPS.append((f"Decision {i + 1} · {d['name']}",
                   f"Safe pick: {d['targets'][d['safe']]['label']}. Clue on screen: {d['clue']}.",
                   ORDER[4 + 3 * i: 7 + 3 * i]))
GROUPS.append(("Ending", "The drop, then DELIVERED. FLATLINED plays after every capture.", ORDER[-4:]))


def esc(s):
    return html.escape(str(s), quote=True)


REVISED = {"title", "stakes", "intro_call", "intro_hound", "d1_loop", "d1_jump", "d1_vent", "d2_crowd", "d2_alley",
           "d3_loop", "d3_roof", "d3_board", "d4_loop", "d4_van", "d4_run", "finale_van", "finale_hound"}


def card(nid):
    sid = scene_of[nid]
    s = scenes[sid]
    if s["kind"] == "flf" and s.get("from") == s.get("to"):
        kind = "Decision loop, pinned to the same frame at both ends (H3 Max)"
    elif s["kind"] == "flf":
        kind = "Pinned at both ends to sheet-drawn keyframes, hard cut where the place changes (H3 Max)"
    elif s["kind"] == "end":
        kind = "End pinned on the D1 frame, free start (H3 Max)"
    else:
        kind = "Starts on a keyframe, then plays out freely (H3 Max)"
    anchors = KEYFRAME.get(s.get("from", ""), s.get("from", "").replace(":last", " last frame"))
    outs = []
    for label, tgt in exits(nid):
        tsid = scene_of[tgt]
        outs.append(f'<figure class="next"><img src="review/{tsid}_first.jpg" alt="" loading="lazy">'
                    f'<figcaption><span class="lbl">{esc(label)}</span>{esc(nodes[tgt]["title"])}</figcaption></figure>')
    caps = "".join(f'<li>{esc(t)}</li>' for _, _, t in s.get("captions", []))
    caps_html = f'<ul class="caps"><span>On-screen text</span>{caps}</ul>' if caps else ""
    tag = "caught" if s.get("caught") else ("loop" if sid.endswith("_loop") else "")
    return f'''
<article class="card {tag}" data-item="{esc(sid)}" id="{esc(sid)}">
  <header><h3>{esc(nodes[nid]["title"])}</h3>{'<span class="new">v2.9</span>' if sid in REVISED else ''}<code>{esc(sid)}</code><span class="len">{s["sec"]}s</span></header>
  <div class="media">
    <video src="review/{sid}.mp4" poster="review/{sid}_first.jpg" controls playsinline preload="none"></video>
    <div class="seam">
      <figure><img src="review/{sid}_first.jpg" alt="" loading="lazy"><figcaption><span class="lbl">first frame</span></figcaption></figure>
      <figure><img src="review/{sid}_last.jpg" alt="" loading="lazy"><figcaption><span class="lbl">last frame</span></figcaption></figure>
      <div class="arrow" aria-hidden="true">cuts to</div>
      {"".join(outs) or '<p class="end">ends the run</p>'}
    </div>
  </div>
  <p class="kind">{esc(kind)} · <b>{esc(anchors)}</b></p>
  {caps_html}
  <details><summary>Prompt</summary><p class="prompt">{esc(s["prompt"])}</p></details>
  <div class="fb" data-fb></div>
</article>'''


def still(key, title, note):
    return f'''
<article class="card still" data-item="{esc(key)}" id="{esc(key)}">
  <header><h3>{esc(title)}</h3><code>{esc(key)}</code></header>
  <img class="sheet" src="review/{key}.jpg" alt="{esc(title)} character sheet" loading="lazy">
  <p class="kind">{esc(note)}</p>
  <div class="fb" data-fb></div>
</article>'''


cast = story["cast"]
sections = [f'''<section id="cast"><div class="sec-head"><h2>Cast</h2><p>Qwen Image 2.1 Turbo sheets. Every keyframe is an edit of these, so the faces and costumes hold.</p></div>
<div class="grid sheets">{still("sheet_rin", "Rin", cast["rin"])}{still("sheet_hound", "The Hound", cast["hound"])}{still("sheet_dex", "Dex", cast["dex"])}</div></section>''']
for title, sub, ids in GROUPS:
    sections.append(f'<section><div class="sec-head"><h2>{esc(title)}</h2><p>{esc(sub)}</p></div>'
                    f'<div class="grid">{"".join(card(n) for n in ids)}</div></section>')

TREE = """flowchart TD
  T[Title] --> S[The chip: stakes] --> C[Dex's call] --> H[Rin runs, the Hound lands far off]
  H --> D1{D1 The Edge}
  D1 -- jump to the billboard --> J[Leap the gap] --> D2{D2 The Market}
  D1 -- hide in the vent / no tap --> X1[He waits at the other end]
  D2 -- vanish into the crowd --> CR[Lost in the umbrellas] --> D3{D3 The Platform}
  D2 -- run the alley / no tap --> X2[He is in the side alley]
  D3 -- climb to the roof --> R[Leap to the other train] --> D4{D4 The Drop}
  D3 -- board the train / no tap --> X3[He sits across from her]
  D4 -- tap the van in time --> V[Dive into the van] --> F1[Cutting it close] --> F2[Next time, courier] --> W[DELIVERED]
  D4 -- no tap in time --> X4[The van peels away, he grabs her]
  X1 & X2 & X3 & X4 --> G[FLATLINED]
  G -- TRY AGAIN --> H
  G -- START OVER --> T
  W -- PLAY AGAIN --> T
  classDef bad fill:#3a0d1c,stroke:#ff2e63,color:#ffd6e0
  classDef good fill:#062a2e,stroke:#00e5ff,color:#d6fbff
  classDef pick fill:#2b2a05,stroke:#f5e94b,color:#fffbd0
  class X1,X2,X3,X4,G bad
  class W,F1,F2 good
  class D1,D2,D3,D4 pick"""

page = (V2 / "review" / "template.html").read_text()
page = page.replace("{{TREE}}", esc(TREE)).replace("{{SECTIONS}}", "\n".join(sections))
page = page.replace("{{LOGLINE}}", esc(story["logline"]))
print(page)
