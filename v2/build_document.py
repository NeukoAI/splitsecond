"""Turns v2/story.json plus hosted media into a bitebox document (spec 0.7).

    python3 v2/build_document.py v2/media.json v2/targets.json > v2/split_second_v2.json

One linear chase with four decisions. Each decision loop shows two tap targets
(Target Overlays with a SAM3 glow outline). The safe pick plays the escape into
the next decision. The wrong pick, or no pick before the loop ends, plays the
caught clip, then GAME OVER with a TRY AGAIN choice that restarts the chase.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 576, 1024
FPS = 24


def build(story, media, targets, title="Split Second"):
    scenes = {s["id"]: s for s in story["scenes"]}
    nodes = {}

    def base(sid):
        return sid[:-2] if sid.endswith("_2") else sid

    def dur(sid):
        return int(round((scenes[base(sid)]["sec"] * FPS + 1) / FPS * 1000))

    def video(nid, sid, x, y, nxt, overlays=None, title=None):
        props = {"src": media[sid], "width": W, "height": H, "durationMs": dur(sid), "displayInExperience": False,
                 "exits": [{"id": f"exit.{nid}.autoplay", "label": "Storyline", "mode": "autoplay", "next": nxt}]}
        if overlays:
            props["overlays"] = overlays
        caps = scenes[base(sid)].get("captions")
        if caps:
            props["captions"] = {"language": "en", "cues": [{"startMs": a, "endMs": b, "text": t} for a, b, t in caps]}
        nodes[nid] = {"type": "video", "title": title or sid.replace("_", " "), "ui": {"x": x, "y": y}, "props": props}

    def choice(cid, opts, x, y, start_ms=0):
        nodes[cid] = {
            "type": "trigger", "title": "choice · " + " / ".join(o[0] for o in opts), "ui": {"x": x, "y": y},
            "props": {"kind": "choiceOverlay", "active": {"startMs": start_ms}, "onClick": "instant",
                      "interaction": "click", "result": "branch", "displayInExperience": True,
                      "interactions": [{"interaction": "click", "onClick": "instant", "result": "branch", "name": o[0]} for o in opts],
                      "options": [{"id": f"choice-{i}", "label": o[0], "next": o[1]} for i, o in enumerate(opts)],
                      "pulseOuts": [{"id": f"choice-{i}"} for i in range(len(opts))]},
        }

    for i, d in enumerate(story["decisions"]):
        for j, (t, spec) in enumerate(d["targets"].items()):
            nodes[f"gl_{t}"] = {
                "type": "image", "title": f"glow · {t}", "ui": {"x": -400, "y": (i * 2 + j) * 160},
                "props": {"src": media[f"glow_{t}"], "alt": spec["label"], "displayInExperience": False},
                "next": None,
            }

    restart = "v_intro_hound"
    # first run: title, the stakes, Dex's call. TRY AGAIN skips straight to the Hound.
    video("v_title", "title", 0, 0, "v_stakes")
    video("v_stakes", "stakes", 400, 0, "v_intro_call", title="the stakes")
    video("v_intro_call", "intro_call", 800, 0, "v_intro_hound")
    video("v_intro_hound", "intro_hound", 1200, 0, "v_d1_loop")

    x = 1600
    decisions = story["decisions"]
    for di, d in enumerate(decisions):
        did = d["id"]
        safe = d["safe"]
        wrong = next(t for t in d["targets"] if t != safe)
        hids = []
        for k, t in enumerate(d["targets"]):
            hid = f"hs_{did}_{t}"
            r = targets[t]
            nodes[hid] = {
                "type": "trigger", "title": f"tap · {d['targets'][t]['label']}", "ui": {"x": x, "y": 320 + k * 240},
                "props": {"kind": "hotspot", "position": {"x": r["x"], "y": r["y"]},
                          "rect": {"width": r["w"], "height": r["h"]}, "size": 0.4,
                          "active": {"startMs": 0}, "onClick": "instant", "image": f"gl_{t}",
                          "displayInExperience": True},
                "next": f"v_{did}_{t}",
            }
            hids.append(hid)
        # no pick before the loop ends plays the wrong route's capture
        video(f"v_{did}_loop", f"{did}_loop", x, 0, f"v_{did}_{wrong}", hids, title=f"{d['name']} · decide")
        nxt = f"v_{decisions[di + 1]['id']}_loop" if di + 1 < len(decisions) else "v_finale_van"
        video(f"v_{did}_{safe}", f"{did}_{safe}", x + 400, 0, nxt, title=f"{d['name']} · {d['targets'][safe]['label']}")
        video(f"v_{did}_{wrong}", f"{did}_{wrong}", x + 400, 320, "v_gameover",
              title=f"{d['name']} · caught")
        x += 800

    video("v_finale_van", "finale_van", x, 0, "v_finale_hound")
    video("v_finale_hound", "finale_hound", x + 400, 0, "v_win")

    # End cards hold until a tap: each card ping-pongs between two copies of its clip
    # (a Video cannot loop into itself) and its buttons are Target Overlays.
    # Choice Overlays were tried first; they auto-pick a default when their window closes.
    buttons = {"try": ("TRY AGAIN", 0.5, 0.64), "over": ("START OVER", 0.5, 0.76), "play": ("PLAY AGAIN", 0.5, 0.9)}
    for b, (label, _, _) in buttons.items():
        nodes[f"gl_btn_{b}"] = {"type": "image", "title": f"button · {label}", "ui": {"x": x, "y": 1400 + 160 * list(buttons).index(b)},
                                "props": {"src": media[f"btn_{b}"], "alt": label, "displayInExperience": False}, "next": None}

    def button(hid, b, dst, bx, by):
        label, cx, cy = buttons[b]
        nodes[hid] = {"type": "trigger", "title": f"tap · {label}", "ui": {"x": bx, "y": by},
                      "props": {"kind": "hotspot", "position": {"x": cx, "y": cy}, "rect": {"width": 0.6, "height": 0.08},
                                "size": 0.4, "active": {"startMs": 0}, "onClick": "instant", "image": f"gl_btn_{b}",
                                "displayInExperience": True},
                      "next": dst}
        return hid

    win = [button("hs_win_play", "play", "v_title", x + 800, 320), button("hs_win2_play", "play", "v_title", x + 1200, 320)]
    video("v_win", "win", x + 800, 0, "v_win_2", [win[0]], title="DELIVERED")
    video("v_win_2", "win_2", x + 1200, 0, "v_win", [win[1]], title="DELIVERED (hold)")
    go1 = [button("hs_go_try", "try", restart, x, 960), button("hs_go_over", "over", "v_title", x, 1200)]
    go2 = [button("hs_go2_try", "try", restart, x + 400, 960), button("hs_go2_over", "over", "v_title", x + 400, 1200)]
    video("v_gameover", "gameover", x, 640, "v_gameover_2", go1, title="GAME OVER")
    video("v_gameover_2", "gameover_2", x + 400, 640, "v_gameover", go2, title="GAME OVER (hold)")

    return {"spec": "0.7", "title": title, "start": "v_title", "nodes": nodes}


def main():
    story = json.loads((HERE / "story.json").read_text())
    media = json.loads(Path(sys.argv[1]).read_text())
    targets = json.loads(Path(sys.argv[2]).read_text())
    json.dump(build(story, media, targets), sys.stdout, indent=1)


if __name__ == "__main__":
    main()
