"""Generates every ComfyUI workflow in this repo (API format) from one place.

    python3 build_workflows.py

Writes:
    workflows/01_keyframes.json        three decision frames, Z-Image Turbo
    workflows/02_targets.json          SAM3 masks + glowing tap-target outlines
    workflows/clips/<name>.json        one Wan 2.1 first/last-frame job per clip
    workflows/03_all_clips.json        every clip in one graph (needs a GPU with no job time limit)

Everything is open weights and core ComfyUI nodes. No custom node packs.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "workflows"

# ---------------------------------------------------------------- keyframes
STYLE = ("Anime film still, hand-painted cel style, cinematic lighting, rich color, clean linework, "
         "vertical 9:16 frame, night, steady rain, dense neon city in pink and teal. ")
GIRL = ("a young courier girl in a bright yellow raincoat with the hood down, short black bob haircut, "
        "a dark green messenger bag across her body")
NINJAS = "three ninjas dressed all in black with red scarves"

KEYFRAMES = {
    # name: (prompt, seed)
    "k0_approach": (STYLE + (
        f"Wide shot of a flat wet rooftop. {GIRL} sprints into the frame from the lower left, mid-stride, "
        "splashing through puddles, looking back over her shoulder. On the left side of the rooftop stands a "
        "tall wooden water tower with a metal ladder up its side. On the right edge of the roof, a taut steel "
        "zipline cable runs from a short pole out across the street. In the background center, a small rooftop "
        "stairwell hut with a red metal door. The rooftop is otherwise empty."), 4242),
    "k1_decision1": (STYLE + (
        f"Wide shot of a flat wet rooftop. {GIRL} stands in the center foreground, seen from behind at a "
        "three-quarter angle, cornered and catching her breath. On the left side of the rooftop stands a tall "
        "wooden water tower with a metal ladder up its side. On the right edge of the roof, a taut steel zipline "
        "cable runs from a short pole out across the street. In the background center, a small rooftop stairwell "
        f"hut with a red metal door. At the far back edge of the roof, {NINJAS} crouch on the ledge, watching "
        "her, motionless. The lower quarter of the frame is wet rooftop with puddles and reflections."), 4242),
    "k2_decision2": (STYLE + (
        f"{GIRL} crouches on a narrow metal catwalk high above the street, seen from behind at a three-quarter "
        "angle, in front of a giant glowing billboard with abstract pink and blue light shapes and no words. "
        "Below on the right, an elevated subway train with lit windows passes on its track. On the left, a tall "
        f"red and white radio antenna tower with a ladder. Far away on the left end of the catwalk, {NINJAS} "
        "stand still in a row, watching her. The lower quarter of the frame is the steel catwalk grating, wet "
        "with rain."), 11),
}
KF_NEGATIVE = "text, letters, words, watermark, signature, blurry, extra limbs, deformed"


def keyframes_graph():
    g = {
        "1": node("UNETLoader", "Z-Image Turbo", unet_name="z_image_turbo_bf16.safetensors", weight_dtype="default"),
        "2": node("ModelSamplingAuraFlow", "Shift", model=["1", 0], shift=3),
        "3": node("CLIPLoader", "Qwen3 4B text encoder", clip_name="qwen_3_4b.safetensors", type="lumina2"),
        "4": node("VAELoader", "VAE", vae_name="ae.safetensors"),
        "5": node("CLIPTextEncode", "Negative", clip=["3", 0], text=KF_NEGATIVE),
        "6": node("EmptySD3LatentImage", "576x1024", width=576, height=1024, batch_size=1),
    }
    n = 10
    for name, (prompt, seed) in KEYFRAMES.items():
        g[str(n)] = node("CLIPTextEncode", f"Prompt: {name}", clip=["3", 0], text=prompt)
        g[str(n + 1)] = node("KSampler", f"Sample: {name}", model=["2", 0], seed=seed, steps=8, cfg=1,
                             sampler_name="res_multistep", scheduler="simple", positive=[str(n), 0],
                             negative=["5", 0], latent_image=["6", 0], denoise=1)
        g[str(n + 2)] = node("VAEDecode", f"Decode: {name}", samples=[str(n + 1), 0], vae=["4", 0])
        g[str(n + 3)] = node("SaveImage", f"Save: {name}", images=[str(n + 2), 0], filename_prefix=f"splitsecond/{name}")
        n += 10
    return g


# ---------------------------------------------------------------- tap targets
# (frame, target, SAM3 text prompt). Crop boxes are filled in from the masks (targets.json).
TARGETS = [
    ("k1_decision1", "zip", "the steel zipline cable and its pole on the right edge of the roof"),
    ("k1_decision1", "ladder", "the wooden water tower with a ladder"),
    ("k1_decision1", "door", "the red metal door of the small stairwell hut"),
    ("k2_decision2", "train", "the elevated subway train"),
    ("k2_decision2", "board", "the giant glowing billboard"),
    ("k2_decision2", "antenna", "the red and white radio antenna tower"),
]
GLOW_RGB = 0x00E5FF  # cyan
GLOW_PX = 9


def targets_graph(crops=None):
    """SAM3 finds each object from a sentence; the outline ring (grown mask minus mask) becomes a
    transparent cyan PNG cropped to the object. With crops=None it saves the raw masks instead."""
    g = {
        "1": node("CheckpointLoaderSimple", "SAM3", ckpt_name="sam3.1_multiplex_fp16.safetensors"),
        "2": node("LoadImage", "Decision 1 frame", image="k1_decision1.png"),
        "3": node("LoadImage", "Decision 2 frame", image="k2_decision2.png"),
        "4": node("EmptyImage", "Glow color", width=576, height=1024, batch_size=1, color=GLOW_RGB),
    }
    n = 10
    for frame, name, text in TARGETS:
        img = "2" if frame == "k1_decision1" else "3"
        i = lambda k: str(n + k)  # noqa: E731
        g[i(0)] = node("CLIPTextEncode", f"Find: {name}", clip=["1", 1], text=text)
        g[i(1)] = node("SAM3_Detect", f"Segment: {name}", model=["1", 0], image=[img, 0], threshold=0.35,
                       refine_iterations=2, individual_masks=False, conditioning=[i(0), 0])
        if crops is None:
            g[i(2)] = node("MaskToImage", f"Mask: {name}", mask=[i(1), 0])
            g[i(3)] = node("SaveImage", f"Save mask: {name}", images=[i(2), 0], filename_prefix=f"splitsecond/mask_{name}")
        else:
            x, y, w, h = crops[name]
            g[i(2)] = node("GrowMask", f"Grow: {name}", mask=[i(1), 0], expand=GLOW_PX, tapered_corners=True)
            g[i(3)] = node("MaskComposite", f"Ring: {name}", destination=[i(2), 0], source=[i(1), 0], x=0, y=0, operation="subtract")
            g[i(4)] = node("InvertMask", f"Alpha: {name}", mask=[i(3), 0])
            g[i(5)] = node("JoinImageWithAlpha", f"Color ring: {name}", image=["4", 0], alpha=[i(4), 0])
            g[i(6)] = node("ImageCrop", f"Crop: {name}", image=[i(5), 0], width=w, height=h, x=x, y=y)
            g[i(7)] = node("SaveImage", f"Save glow: {name}", images=[i(6), 0], filename_prefix=f"splitsecond/glow_{name}")
        n += 10
    return g


# ---------------------------------------------------------------- clips
CLIP_STYLE = ("Anime film, hand-painted cel style, consistent character, stable scene, smooth natural motion, "
              "rainy neon city rooftops at night. ")
G = "the girl in the yellow raincoat"
NJ = "ninjas in black with red scarves"
CLIP_NEGATIVE = ("glitch, distortion, graffiti, color shift, morphing, melting, abstract shapes, blurry, low quality, "
                 "extra limbs, deformed face, text, watermark, subtitles")

# name: (start frame, end frame or None, prompt). Every clip is pinned to a decision frame.
CLIPS = {
    "opening": ("k0_approach", "k1_decision1", f"{G} sprints across the wet rooftop, splashing through puddles, glancing back. {NJ} leap down onto the roof of the stairwell hut and crouch. She skids to a stop in the middle of the roof, cornered. Camera holds steady."),
    "loop1": ("k1_decision1", "k1_decision1", f"Locked-off camera. {G} stands still, breathing hard, shoulders rising and falling. The {NJ} crouch motionless on the hut roof. Steady rain, rippling puddles. Gentle idle motion only."),
    "d1_zip_safe": ("k1_decision1", "k2_decision2", f"{G} turns and runs to the right edge of the roof, grabs the steel zipline cable with her bag strap and slides away across the street, landing on a metal catwalk in front of a giant glowing billboard. She crouches to catch her breath."),
    "d1_ladder_safe": ("k1_decision1", "k2_decision2", f"{G} runs to the wooden water tower, climbs its ladder fast, and leaps from the top across the street, landing on a metal catwalk in front of a giant glowing billboard. She crouches to catch her breath."),
    "d1_door_safe": ("k1_decision1", "k2_decision2", f"{G} dashes through the red metal door of the stairwell hut, races up a dark stairwell and bursts out onto a metal catwalk in front of a giant glowing billboard. She crouches to catch her breath."),
    "d1_zip_cap": ("k1_decision1", None, f"{G} runs to the right edge of the roof and grabs the steel zipline cable. A ninja in black with a red scarf lands on the pole and holds the cable still, and the other ninjas close in around her. She is caught. Camera holds steady."),
    "d1_ladder_cap": ("k1_decision1", None, f"{G} runs to the wooden water tower and climbs its ladder. At the top, a ninja in black with a red scarf rises up and grabs her wrist. She is caught. Camera holds steady."),
    "d1_door_cap": ("k1_decision1", None, f"{G} runs to the stairwell hut and pulls the red metal door open. Two {NJ} burst out of the doorway and seize her arms. She is caught. Camera holds steady."),
    "loop2": ("k2_decision2", "k2_decision2", f"Locked-off camera. {G} crouches still on the catwalk, breathing hard. The {NJ} stand motionless at the far end. The train keeps rolling past below, the billboard glows. Gentle idle motion only."),
    "d2_train_safe": ("k2_decision2", None, f"{G} vaults over the catwalk railing and drops onto the roof of the passing train below. She lands in a crouch and rides away into the neon city as the {NJ} are left behind on the catwalk. Camera follows the train."),
    "d2_board_safe": ("k2_decision2", None, f"{G} slips behind the glowing billboard, slides down a drainpipe into a dark alley, and runs off into the crowded neon street, safe. The ninjas look around the catwalk, losing her."),
    "d2_antenna_safe": ("k2_decision2", None, f"{G} climbs the red and white radio antenna tower, then leaps from it onto the roof of a neighboring building and disappears into the rainy city, safe. The ninjas are left behind on the catwalk."),
    "d2_train_cap": ("k2_decision2", None, f"{G} vaults over the catwalk railing toward the passing train, but a ninja in black with a red scarf leaps and catches her mid-air, pulling her back onto the catwalk. She is caught. Camera holds steady."),
    "d2_board_cap": ("k2_decision2", None, f"{G} slips behind the glowing billboard to hide. A ninja's shadow falls across her, then a ninja in black with a red scarf steps around the edge and grabs her shoulder. She is caught. Camera holds steady."),
    "d2_antenna_cap": ("k2_decision2", None, f"{G} climbs the red and white radio antenna tower. The {NJ} surround its base and one climbs up after her. At the top she has nowhere to go and is caught. Camera holds steady."),
}
VIDEO = dict(width=480, height=848, length=81, fps=16, seed=7, steps=25, cfg=5, shift=5)


def _clip_shared():
    return {
        "1": node("UNETLoader", "Wan 2.1 FLF2V 14B", unet_name="wan2.1_flf2v_720p_14B_fp8_e4m3fn.safetensors", weight_dtype="default"),
        "2": node("ModelSamplingSD3", "Shift", model=["1", 0], shift=VIDEO["shift"]),
        "3": node("CLIPLoader", "UMT5 text encoder", clip_name="umt5_xxl_fp8_e4m3fn_scaled.safetensors", type="wan"),
        "4": node("VAELoader", "Wan VAE", vae_name="wan_2.1_vae.safetensors"),
        "5": node("CLIPVisionLoader", "CLIP Vision H", clip_name="clip_vision_h.safetensors"),
        "6": node("CLIPTextEncode", "Negative", clip=["3", 0], text=CLIP_NEGATIVE),
    }


FRAME_NODES = {"k0_approach": ("20", "21"), "k1_decision1": ("22", "23"), "k2_decision2": ("24", "25")}


def _add_frame(g, frame):
    load, vis = FRAME_NODES[frame]
    if load not in g:
        g[load] = node("LoadImage", f"Frame: {frame}", image=f"{frame}.png")
        g[vis] = node("CLIPVisionEncode", f"Vision: {frame}", clip_vision=["5", 0], image=[load, 0], crop="center")
    return load, vis


def _add_clip(g, base, name, start, end, prompt):
    s_load, s_vis = _add_frame(g, start)
    i = lambda k: str(base + k)  # noqa: E731
    g[i(0)] = node("CLIPTextEncode", f"Prompt: {name}", clip=["3", 0], text=CLIP_STYLE + prompt)
    flf = dict(positive=[i(0), 0], negative=["6", 0], vae=["4", 0], width=VIDEO["width"], height=VIDEO["height"],
               length=VIDEO["length"], batch_size=1, start_image=[s_load, 0], clip_vision_start_image=[s_vis, 0])
    if end:
        e_load, e_vis = _add_frame(g, end)
        flf.update(end_image=[e_load, 0], clip_vision_end_image=[e_vis, 0])
    g[i(1)] = node("WanFirstLastFrameToVideo", f"Pin to frame: {name}", **flf)
    g[i(2)] = node("KSampler", f"Sample: {name}", model=["2", 0], seed=VIDEO["seed"], steps=VIDEO["steps"], cfg=VIDEO["cfg"],
                   sampler_name="uni_pc", scheduler="simple", positive=[i(1), 0], negative=[i(1), 1],
                   latent_image=[i(1), 2], denoise=1)
    g[i(3)] = node("VAEDecode", f"Decode: {name}", samples=[i(2), 0], vae=["4", 0])
    g[i(4)] = node("CreateVideo", f"Video: {name}", images=[i(3), 0], fps=float(VIDEO["fps"]))
    g[i(5)] = node("SaveVideo", f"Save: {name}", video=[i(4), 0], filename_prefix=f"splitsecond/{name}",
                   **{"format": "mp4", "format.codec": "h264"})


def clip_graph(name):
    g = _clip_shared()
    _add_clip(g, 100, name, *CLIPS[name])
    return g


def all_clips_graph():
    g = _clip_shared()
    for k, name in enumerate(CLIPS):
        _add_clip(g, 100 + 10 * k, name, *CLIPS[name])
    return g


def node(cls, title, **inputs):
    return {"class_type": cls, "inputs": inputs, "_meta": {"title": title}}


def main():
    (OUT / "clips").mkdir(parents=True, exist_ok=True)
    write(OUT / "01_keyframes.json", keyframes_graph())
    crops_path = Path(__file__).parent / "targets.json"
    crops = json.loads(crops_path.read_text())["crops"] if crops_path.exists() else None
    write(OUT / "02_targets.json", targets_graph(crops))
    for name in CLIPS:
        write(OUT / "clips" / f"{name}.json", clip_graph(name))
    write(OUT / "03_all_clips.json", all_clips_graph())
    print(f"wrote {3 + len(CLIPS)} workflows to {OUT}")


def write(path, graph):
    path.write_text(json.dumps(graph, indent=1) + "\n")


if __name__ == "__main__":
    main()
