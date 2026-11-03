"""spec_check.py bible.json frames.json takes.json [--prompts]
Refuses a shot spec that breaks the build rules, then (with --prompts) assembles every prompt."""
import json, re, sys

bible, frames, takes = (json.load(open(p)) for p in sys.argv[1:4])
F = {f["id"]: f for f in frames}
errors, warns = [], []
BANNED = r"\b(no|not|without|never|don't|doesn't|like a|like an|as if|as though|button|subtitle|caption)\b"
SIDE = {"camera": ("screen-right", "screen-left"), "away": ("screen-left", "screen-right")}

def err(i, m): errors.append(f"{i}: {m}")
def warn(i, m): warns.append(f"{i}: {m}")

for f in frames:
    i = f["id"]
    if f["place"] not in bible["places"]: err(i, f"unknown place {f['place']}")
    if f.get("method") == "edit" and f.get("moves_character"): err(i, "edits that move a character duplicate her: redraw from the plate")
    for c in f["cast"]:
        if c["who"] not in bible["characters"]: err(i, f"{c['who']} has no reference")
        if c.get("facing") not in SIDE: err(i, f"{c['who']} needs facing: camera or away")
    for word in re.findall(BANNED, f["picture"].lower()): warn(i, f"'{word}' in the picture text draws what it names")

prev_end = {}
for t in takes:
    i, a, b = t["id"], F.get(t["start"]), F.get(t["end"])
    if not a or not b: err(i, "start and end must be drawn frames"); continue
    if a["place"] != b["place"]: err(i, "two places in one take: split it and hard-cut in the mix")
    for ca in a["cast"]:
        cb = next((c for c in b["cast"] if c["who"] == ca["who"]), None)
        if cb and ca.get("scale") != cb.get("scale") and not t.get("camera_follows"):
            err(i, f"{ca['who']} changes scale {ca.get('scale')} to {cb.get('scale')}: she will pop; make the camera follow or redraw")
    if not (a.get("approved") and b.get("approved")): err(i, "pins are not approved on the keyframe board")
    if len(re.findall(r"\bthen\b|;", t["action"])) > 1: warn(i, "more than two actions: one beat per take")
    for word in re.findall(BANNED, t["action"].lower()): warn(i, f"'{word}' in the action draws what it names")
    if t.get("seam_in", "cut") != "cut" and prev_end.get(t["seam_in"]) != t["start"]:
        err(i, f"seam_in says it continues {t['seam_in']} but does not start on its last frame")
    if t.get("loop") and t["start"] != t["end"]: err(i, "a decision loop starts and ends on the same frame")
    prev_end[i] = t["end"]

print("\n".join(["ERROR " + e for e in errors] + ["WARN  " + w for w in warns]) or "spec clean")
if errors: sys.exit(1)

def card(who, facing):
    ch = bible["characters"][who]
    her_left, her_right = SIDE[facing]  # her left is screen-right when she faces the camera
    return ch["card"].replace("{left}", her_left).replace("{right}", her_right)

if "--prompts" in sys.argv:
    out = {}
    for f in frames:
        refs = [bible["places"][f["place"]]["plate"]] + [bible["characters"][c["who"]][f"ref_{'back' if c['facing']=='away' else 'front'}"] for c in f["cast"]]
        people = " ".join(f"{card(c['who'], c['facing'])} {c['position']}" for c in f["cast"])
        n = len(f["cast"])
        out[f["id"]] = {"model": "nano-banana-pro", "imageUrls": refs, "prompt":
            f"Use Image 1 as the place and camera: {bible['places'][f['place']]['description']} "
            f"There {'is exactly one person' if n == 1 else f'are exactly {n} people'} in the whole picture. {people} "
            f"{f['picture']} {bible['sky']} {bible['style']} No text."}
    for t in takes:
        a = F[t["start"]]
        locks = " ".join(bible["characters"][c["who"]]["locks"] for c in a["cast"])
        cam = "The camera follows right behind her at her speed, so she stays the same size." if t.get("camera_follows") else "Camera locked off."
        out[t["id"]] = {"model": "minimax-h3-max", "start": t["start"], "end": t["end"],
                        "input": {"duration": str(t.get("sec", 5)), "seed": t.get("seed", 1), "prompt_expansion_mode": "disabled"},
                        "prompt": f"{cam} {t['action']} {t.get('ambient', bible['ambient'])} {locks} Nobody speaks."}
    json.dump(out, open("prompts.json", "w"), indent=1)
    print(f"wrote prompts.json ({len(out)} prompts)")
