"""Writes workflows/seamfix/*.json: one ComfyUI graph per open-ended clip.

MiniMax H3 reference-to-video treats frame 0 as a guide, not a pin, and renders
at 480x864. Cut straight from a 576x1024 Pika loop into it and the picture pops:
same layout, slightly squeezed, a touch darker, repainted. Each graph rescales
the clip back to 576x1024 and dissolves from the anchor keyframe over the first
six frames (a quarter second), so the cut starts on the exact frame the loop
ends on. Audio passes through untouched.

    python3 seamfix.py
Then put each H3 render in input/ as h3_<clip>.mp4 and queue its graph.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FADE = 6
CLIPS = {
    "d1_zip_cap": "k1_decision1.png", "d1_ladder_cap": "k1_decision1.png", "d1_door_cap": "k1_decision1.png",
    "d2_train_safe": "k2_decision2.png", "d2_board_safe": "k2_decision2.png", "d2_antenna_safe": "k2_decision2.png",
    "d2_train_cap": "k2_decision2.png", "d2_board_cap": "k2_decision2.png", "d2_antenna_cap": "k2_decision2.png",
}


def graph(clip, anchor):
    p, n = {}, iter(range(1, 1000))
    nid = lambda: str(next(n))
    lv = nid(); p[lv] = {"class_type": "LoadVideo", "inputs": {"file": f"h3_{clip}.mp4"}}
    gc = nid(); p[gc] = {"class_type": "GetVideoComponents", "inputs": {"video": [lv, 0]}}
    sc = nid(); p[sc] = {"class_type": "ImageScale", "inputs": {"image": [gc, 0], "upscale_method": "lanczos", "width": 576, "height": 1024, "crop": "disabled"}}
    an = nid(); p[an] = {"class_type": "LoadImage", "inputs": {"image": anchor}}
    acc = None
    for i in range(FADE):
        f = nid(); p[f] = {"class_type": "ImageFromBatch", "inputs": {"image": [sc, 0], "batch_index": i, "length": 1}}
        b = nid(); p[b] = {"class_type": "ImageBlend", "inputs": {"image1": [f, 0], "image2": [an, 0], "blend_factor": round((FADE - i) / FADE, 3), "blend_mode": "normal"}}
        if acc is None:
            acc = b
        else:
            c = nid(); p[c] = {"class_type": "ImageBatch", "inputs": {"image1": [acc, 0], "image2": [b, 0]}}; acc = c
    rest = nid(); p[rest] = {"class_type": "ImageFromBatch", "inputs": {"image": [sc, 0], "batch_index": FADE, "length": 4096}}
    al = nid(); p[al] = {"class_type": "ImageBatch", "inputs": {"image1": [acc, 0], "image2": [rest, 0]}}
    cv = nid(); p[cv] = {"class_type": "CreateVideo", "inputs": {"images": [al, 0], "fps": 24, "audio": [gc, 1], "bit_depth": "auto", "codec": "none", "color_space": "sRGB"}}
    sv = nid(); p[sv] = {"class_type": "SaveVideo", "inputs": {"video": [cv, 0], "filename_prefix": f"splitsecond/seamfix/{clip}", "format": "auto", "codec": "auto", "format.codec": "auto"}}
    return p


if __name__ == "__main__":
    out = ROOT / "workflows" / "seamfix"
    out.mkdir(parents=True, exist_ok=True)
    for clip, anchor in CLIPS.items():
        (out / f"{clip}.json").write_text(json.dumps(graph(clip, anchor), indent=1))
    print(f"wrote {len(CLIPS)} graphs to {out}")
