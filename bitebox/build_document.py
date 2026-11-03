"""Turns story.json into a complete bitebox document (spec 0.7).

    python3 bitebox/build_document.py bitebox/media.json > bitebox/split_second.json

bitebox has no random rule, so the rotation is unrolled: one copy of the run per
layout (A, B, C). Every capture plays into the next copy's opening, so the route
that saved you last run gets you caught this one. Each decision loop is chained
LOOP_PLAYS times; letting the last play run out plays the hesitation capture.

Each loop video lists its tap targets in props.overlays (Target Overlays with the
SAM3 glow outline as their marker) and keeps a single autoplay exit to the next
loop play. The bitebox player reads exactly that shape.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOOP_PLAYS = 3
DUR_MS = 5167
W, H = 576, 1024


def build(story, media, title="Split Second"):
    rot = story["rotation"]
    copies = "ABC"[: len(rot)]
    nodes = {}

    for i, d in enumerate(story["decisions"]):
        for j, (t, spec) in enumerate(d["targets"].items()):
            nodes[f"glow_{t}"] = {
                "type": "image", "title": f"glow · {t}", "ui": {"x": -400, "y": (i * 3 + j) * 160},
                "props": {"src": media[f"glow_{t}"], "alt": spec["label"], "displayInExperience": False},
                "next": None,
            }

    def video(nid, title, scene, x, y, nxt=None, overlays=None):
        props = {"src": media[scene], "width": W, "height": H, "durationMs": DUR_MS, "displayInExperience": False,
                 "exits": [{"id": f"exit.{nid}.autoplay", "label": "Storyline", "mode": "autoplay", "next": nxt}]}
        if overlays:
            props["overlays"] = overlays
        nodes[nid] = {"type": "video", "title": title, "ui": {"x": x, "y": y}, "props": props}

    def hotspot(hid, t, rect, dst, x, y):
        cx, cy, w, h = rect
        nodes[hid] = {
            "type": "trigger", "title": f"tap · {t}", "ui": {"x": x, "y": y},
            "props": {"kind": "hotspot", "position": {"x": cx, "y": cy}, "rect": {"width": w, "height": h},
                      "size": 0.4, "active": {"startMs": 0}, "onClick": "instant", "image": f"glow_{t}",
                      "displayInExperience": True},
            "next": dst,
        }

    for ci, c in enumerate(copies):
        layout = rot[ci]
        nxt_copy = copies[(ci + 1) % len(copies)]
        Y = ci * 2400
        x = 400
        first_loop = {}
        for di, d in enumerate(story["decisions"]):
            safe = layout[d["id"]]
            targets = list(d["targets"])
            hes = story["hesitation"][d["id"]]
            if hes == safe:
                hes = next(t for t in targets if t != safe)
            last = di == len(story["decisions"]) - 1
            for k, t in enumerate(targets):
                kind = "safe" if t == safe else "cap"
                nid = f"{c}_{d['id']}_{t}_{kind}"
                if kind == "cap":
                    after = f"{nxt_copy}_opening"
                else:
                    after = None if last else f"{c}_{story['decisions'][di + 1]['loop']}_1"
                video(nid, f"{c} · {d['id']} {t} {'escape' if kind == 'safe' else 'caught'}",
                      f"{d['id']}_{t}_{kind}", x + 400 * (LOOP_PLAYS + 1), Y + k * 320, after)
            for p in range(LOOP_PLAYS):
                lid = f"{c}_{d['loop']}_{p + 1}"
                after = f"{c}_{d['loop']}_{p + 2}" if p + 1 < LOOP_PLAYS else f"{c}_{d['id']}_{hes}_cap"
                hids = []
                for k, t in enumerate(targets):
                    kind = "safe" if t == safe else "cap"
                    hid = f"{lid}_hs_{t}"
                    hotspot(hid, t, d["targets"][t]["rect"], f"{c}_{d['id']}_{t}_{kind}", x + 400 * p, Y + 320 + k * 240)
                    hids.append(hid)
                video(lid, f"{c} · {d['id']} decide {p + 1}/{LOOP_PLAYS}", d["loop"], x + 400 * p, Y, after, hids)
            first_loop[d["id"]] = f"{c}_{d['loop']}_1"
            x += 400 * (LOOP_PLAYS + 2)
        video(f"{c}_opening", f"{c} · opening", "opening", 0, Y, first_loop[story["decisions"][0]["id"]])

    return {"spec": "0.7", "title": title, "start": f"{copies[0]}_opening", "nodes": nodes}


def main():
    story = json.loads((ROOT / "story.json").read_text())
    media = json.loads(Path(sys.argv[1]).read_text())
    json.dump(build(story, media), sys.stdout, indent=1)


if __name__ == "__main__":
    main()
