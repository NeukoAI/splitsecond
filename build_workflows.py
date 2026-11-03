"""Generates every ComfyUI workflow in this repo (API format) from one place.

    python3 build_workflows.py

Writes:
    workflows/01_keyframes.json        three decision frames, Z-Image Turbo
    workflows/02_targets.json          SAM3 masks + glowing tap-target outlines
    workflows/clips/<name>.json        one job per clip: Pika H3 Flex (both ends pinned) or MiniMax H3 (start pinned)

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

# The map (script v2): she starts on the low EAST ROOF. Across the street is the WEST TOWER, with a billboard
# catwalk on its face, the elevated train below and a radio antenna on top. Zipline, water-tower jump and the
# stairwell's skybridge all lead to that catwalk. The ninjas are never within reach in a decision frame.
KEYFRAMES = {
    # name: (prompt, seeds)
    "k0_approach": (STYLE + (
        f"Low wide shot across a flat wet rooftop. {GIRL} sprints toward the camera, mid-stride, splashing through "
        "puddles, looking back over her shoulder in fear. Behind her the rooftop stretches back: a tall wooden water "
        "tower with a metal ladder on the left, a small stairwell hut with a red metal door in the center, a short "
        "pole on the right edge. Behind the roof rises the dark wall of a taller building. No other people."), [4242, 77]),
    "k1_decision1": (STYLE + (
        f"High three-quarter shot from behind. {GIRL} stands alone in the middle of a flat wet rooftop, seen from "
        "behind, facing a tall neon skyscraper across the street at the top of the frame. On the left, a tall "
        "wooden water tower with a metal ladder up its side. In the center, a small stairwell hut with a red metal "
        "door, and from the top of the hut an enclosed glass skybridge stretches across the street to the "
        "skyscraper. On the right edge, a short pole with a taut steel zipline cable that slopes down across the "
        "street to a lit catwalk on the skyscraper. Far away in the upper left, small, on the parapet of a taller "
        f"neighboring building, {NINJAS} crouch, watching her. Lots of empty wet roof between her and everything."), [4242, 31]),
    "k2_decision2": (STYLE + (
        f"Shot from behind and slightly above. {GIRL} crouches on a narrow steel catwalk bolted to the side of a "
        "skyscraper, high above the street. On the left, the catwalk runs past a giant glowing billboard of abstract "
        "pink and blue light shapes with no words. Above the billboard, on the skyscraper roof, a tall red and white "
        "radio antenna mast with a ladder. Far below on the right, an elevated train with lit windows runs on its "
        "track. Across the street on the right, much lower and far away, a small flat rooftop with a water tower, "
        f"where {NINJAS} stand tiny in the distance; a steel cable slopes from that rooftop up to the catwalk. "
        "She is alone on the catwalk."), [11, 97]),
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
    for name, (prompt, seeds) in KEYFRAMES.items():
        g[str(n)] = node("CLIPTextEncode", f"Prompt: {name}", clip=["3", 0], text=prompt)
        for k, seed in enumerate(seeds):
            m = n + 1 + 3 * k
            g[str(m)] = node("KSampler", f"Sample: {name} seed {seed}", model=["2", 0], seed=seed, steps=8, cfg=1,
                             sampler_name="res_multistep", scheduler="simple", positive=[str(n), 0],
                             negative=["5", 0], latent_image=["6", 0], denoise=1)
            g[str(m + 1)] = node("VAEDecode", f"Decode: {name} seed {seed}", samples=[str(m), 0], vae=["4", 0])
            g[str(m + 2)] = node("SaveImage", f"Save: {name} seed {seed}", images=[str(m + 1), 0],
                                 filename_prefix=f"splitsecond/{name}_s{seed}")
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
# Two open-weights MiniMax H3 routes, both local int8:
#   pika  = Pika H3 Flex LoRA on MiniMax H3 first/last-frame (FL2VA). Both ends pinned.
#           Used for every clip that must land on a decision frame: opening, loops, decision-1 escapes.
#   h3    = MiniMax H3 reference-to-video with a guide at frame 0. Start pinned, end free.
#           Used for captures and the final escapes.
# Both render picture and sound in one pass.
VIDEO = dict(seconds=5.17, frames=124, fps=24, seed=7, width=576, height=1024)

ROOF = ("the wooden water tower with its ladder on the left, the steel zipline cable on the right edge, "
        "the stairwell hut with the red door in the background")
CAT = ("the giant glowing pink and blue billboard, the elevated train passing below on the right, "
       "the red and white antenna on the left")
K1_END = (f"The shot settles into the final composition of Picture 2 and holds: the girl standing in the center "
          f"foreground seen from behind, {ROOF}, and the three ninjas crouched on the hut roof.")
K2_END = (f"The shot settles into the final composition of Picture 2 and holds: the girl crouched on the catwalk "
          f"seen from behind, {CAT}, and the three ninjas standing at the far left end of the catwalk.")
PIKA_STYLE = ("Hand-painted 2D anime cel animation: clean confident linework, flat cel shading with soft painted "
              "backgrounds, rich pink and teal neon light, steady diagonal rain and wet reflective rooftops at night. "
              "The courier girl has a short black bob, a bright yellow raincoat with the hood down and a dark green "
              "messenger bag; the three ninjas wear all black with red scarves over their faces. Characters keep the "
              "same proportions, outlines and colors in every frame.")

# Scene descriptions MiniMax H3 uses to tie each pinned picture to the prompt.
FRAME_DESC = {
    "k1_decision1": ("a wide shot of the flat wet rooftop at night in the rain, <Subject 1> standing in the center "
                     "foreground seen from behind, a wooden water tower with a ladder on the left, a steel zipline "
                     "cable on the right edge, and a small stairwell hut with a red door in the background, with "
                     "<Subject 2> crouched motionless on the hut roof, against a pink and teal neon city"),
    "k2_decision2": ("<Subject 1> crouching on a narrow steel catwalk high above the street, seen from behind, in "
                     "front of a giant glowing pink and blue billboard, an elevated train with lit windows passing "
                     "below on the right, a red and white radio antenna tower on the left, and <Subject 2> standing "
                     "still at the far left end of the catwalk"),
}

# name: (route, start frame, end frame, description, soundscape[, summary for h3])
CLIPS = {
    "opening": ("pika", "k0_approach", "k1_decision1",
        f"The shot begins exactly on Picture 1: the girl sprinting across the empty wet rooftop from the lower left, looking back over her shoulder, {ROOF}. At about one second the three ninjas drop out of the rainy sky one after another and land crouched on the roof of the stairwell hut. At about two and a half seconds the girl skids to a stop in the middle of the roof, cornered, catching her breath. {K1_END}",
        "Heavy rain, fast splashing footsteps, three soft thuds as the ninjas land, a skid on wet concrete, her hard breathing, the distant city."),
    "loop1": ("pika", "k1_decision1", "k1_decision1",
        f"The shot begins exactly on Picture 1 and the camera stays locked off. The girl stands still, breathing hard, her shoulders rising and falling; the hem of her raincoat stirs in the wind; the three ninjas stay crouched and motionless on the hut roof; rain falls and the puddles ripple. Gentle idle motion only. {K1_END}",
        "Steady heavy rain, her hard breathing, wind across the rooftop, the distant city."),
    "d1_zip_safe": ("pika", "k1_decision1", "k2_decision2",
        "The shot begins exactly on Picture 1: wide view of the rooftop, the girl standing in the center foreground seen from behind, the wooden water tower with its ladder on the left, the steel zipline cable on the right edge, the stairwell hut with the red door in the background and the three ninjas crouched on its roof. At about half a second she turns and sprints to the right edge of the roof, splashing through puddles, as the ninjas spring up behind her. At about one and a half seconds she loops her bag strap over the zipline cable and leaps, sliding fast across the street above the neon traffic, the camera following her across. At about three and a half seconds she drops onto a narrow steel catwalk in front of a giant glowing pink and blue billboard and lands in a crouch. " + K2_END,
        "Heavy rain on concrete, quick splashing footsteps, the rising metallic whine of the cable under her weight, a rush of wind, a heavy clang as she lands on the steel grating, the rumble of the train below and the distant city."),
    "d1_ladder_safe": ("pika", "k1_decision1", "k2_decision2",
        f"The shot begins exactly on Picture 1. At about half a second the girl sprints to the wooden water tower on the left and climbs its ladder fast as the ninjas spring up behind her. At about two seconds she reaches the top, runs across the tank lid and leaps out over the street. At about three and a half seconds she lands on a narrow steel catwalk in front of a giant glowing billboard and drops into a crouch. {K2_END}",
        "Heavy rain, splashing footsteps, rapid clangs on the metal ladder, a rush of wind, a heavy landing on steel grating, the rumble of the train below."),
    "d1_door_safe": ("pika", "k1_decision1", "k2_decision2",
        f"The shot begins exactly on Picture 1. At about half a second the girl sprints to the stairwell hut and slips through the red door just before the ninjas can drop on her. At about one and a half seconds she races up a dark concrete stairwell lit by flickering red light. At about three seconds she bursts out of a door onto a narrow steel catwalk in front of a giant glowing billboard and drops into a crouch. {K2_END}",
        "Heavy rain, splashing footsteps, a metal door slamming, fast footsteps echoing up concrete stairs, a door banging open, rain on steel grating."),
    "loop2": ("pika", "k2_decision2", "k2_decision2",
        f"The shot begins exactly on Picture 1 and the camera stays locked off. The girl stays crouched on the catwalk, breathing hard; the billboard light pulses gently; the train keeps rolling past below; the three ninjas stand motionless at the far end; rain falls. Gentle idle motion only. {K2_END}",
        "Steady rain on steel grating, the rumble of the train below, a low electric hum from the billboard, her breathing."),
    "d1_zip_cap": ("h3", "k1_decision1", None,
        "<Subject 1> sprints to the right edge of the roof and grabs the steel zipline cable. One of <Subject 2> lands on the zipline pole above her and pins the cable, and the other two close in on both sides and seize her arms. She is caught, held between them, as the camera holds steady.",
        "Heavy rain, splashing footsteps, the cable twanging, a thud as a ninja lands, a sharp gasp, the distant city.",
        "<Subject 1> tries the zipline and is caught."),
    "d1_ladder_cap": ("h3", "k1_decision1", None,
        "<Subject 1> sprints to the wooden water tower and climbs its ladder fast. Near the top, one of <Subject 2> rises up over the edge of the tank and grabs her wrist, while the other two wait at the bottom of the ladder. She is caught, hanging from the ladder in his grip, as the camera holds steady.",
        "Heavy rain, clangs on the metal ladder, a sharp gasp, the creak of the wooden tank, the distant city.",
        "<Subject 1> climbs the water tower and is caught at the top."),
    "d1_door_cap": ("h3", "k1_decision1", None,
        "<Subject 1> runs to the stairwell hut and yanks the red metal door open. Two of <Subject 2> burst out of the dark doorway and seize her by both arms while the third drops from the hut roof behind her. She struggles and freezes, caught, as the camera holds steady.",
        "Heavy rain, splashing footsteps, a metal door banging open, a sharp gasp, cloth and rain, distant city traffic.",
        "<Subject 1> tries the stairwell door and is caught by ninjas bursting out of it."),
    "d2_train_safe": ("h3", "k2_decision2", None,
        "<Subject 1> vaults over the catwalk railing and drops onto the roof of the passing elevated train below. She lands in a crouch and rides away into the glowing neon city, looking back as <Subject 2> are left standing on the catwalk, shrinking into the distance. She has escaped.",
        "Rain, a rush of wind, a heavy thud on the train roof, the roaring rumble of the train, the city fading behind.",
        "<Subject 1> escapes by dropping onto the passing train."),
    "d2_board_safe": ("h3", "k2_decision2", None,
        "<Subject 1> slips behind the giant glowing billboard into its dark scaffolding, slides down a drainpipe into a narrow alley, and runs off into a crowded neon street, disappearing among umbrellas. Up on the catwalk, <Subject 2> look around, having lost her. She has escaped.",
        "Rain, the electric hum of the billboard, a fast slide down a metal pipe, splashing footsteps, a busy street crowd.",
        "<Subject 1> escapes behind the billboard."),
    "d2_antenna_safe": ("h3", "k2_decision2", None,
        "<Subject 1> climbs the red and white radio antenna tower, then leaps from it onto the roof of a neighboring building, rolls, and sprints away into the rainy city. <Subject 2> are left behind on the catwalk. She has escaped.",
        "Rain, fast clangs on the antenna ladder, wind, a rolling landing on a wet roof, running footsteps fading away.",
        "<Subject 1> escapes by leaping from the antenna."),
    "d2_train_cap": ("h3", "k2_decision2", None,
        "<Subject 1> vaults over the catwalk railing toward the passing train, but one of <Subject 2> leaps and catches her mid-air, and the other two drag her back onto the catwalk. She is caught, held between them, as the camera holds steady.",
        "Rain, a rush of wind, the roar of the train, a grunt, boots on steel grating.",
        "<Subject 1> jumps for the train and is caught."),
    "d2_board_cap": ("h3", "k2_decision2", None,
        "<Subject 1> slips behind the giant glowing billboard to hide in its scaffolding. A ninja's shadow falls across her, then one of <Subject 2> steps around the edge and grabs her shoulder while the other two block the way out. She is caught, as the camera holds steady.",
        "Rain, the electric hum of the billboard, held breath, a footstep, a sharp gasp.",
        "<Subject 1> hides behind the billboard and is caught."),
    "d2_antenna_cap": ("h3", "k2_decision2", None,
        "<Subject 1> climbs the red and white radio antenna tower. <Subject 2> surround its base and one climbs up after her. At the top she has nowhere left to go; the ninja reaches her and grabs her ankle. She is caught, as the camera holds steady.",
        "Rain, wind howling around the antenna, clangs on metal rungs, a sharp gasp.",
        "<Subject 1> climbs the antenna and is trapped."),
}


def pika_prompt(desc, sound):
    return (f"How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second "
            f"mark of the target video; Picture 2 (from Shot 1) aligns with the {VIDEO['seconds']:.2f}-second mark of the "
            f"target video.\n\nintegrated_multimodal_description: [Shot 1] {PIKA_STYLE} {desc}\n\n"
            f"overall_soundscape: {sound}\n\nnon_diegetic_music: None.")


def h3_prompt(start, summary, action, sound):
    return "\n".join([
        "subject_definitions:",
        "<Subject 1> is the courier girl in <Picture 1>, a young woman with a short black bob haircut, wearing a bright yellow raincoat with the hood down and a dark green messenger bag across her body.",
        "<Subject 2> are the three ninjas, dressed all in black with red scarves covering their faces.",
        f"<Picture 1> is the first frame of [Shot 1], showing {FRAME_DESC[start]}.",
        "", "summary:",
        f"[first frame continuation + reference generation] The target video is one continuous shot of a rooftop chase in hand-painted anime cel style. {summary}",
        "", "retention_analysis:",
        "<Subject 1> (appears in [Shot 1]): fully_preserved - her face, short black bob, bright yellow raincoat and dark green messenger bag stay identical throughout.",
        "<Picture 1> ([Shot 1] first frame): fully_preserved - the video starts exactly from <Picture 1>'s framing, subject positions, lighting and setting.",
        "", "detailed_description:",
        "The target video is a single continuous shot in a hand-painted 2D anime cel style with clean linework, rich pink and teal neon light, steady rain and wet reflective surfaces. Characters keep consistent proportions and outlines in every frame.",
        "", f"[Shot 1] The shot begins from <Picture 1>. {action}",
        "", "overall_soundscape:", sound, "", "non_diegetic_music:", "None."])


def _h3_shared():
    return {
        "119": node("VAELoader", "H3 video VAE", vae_name="minimax_h3_video_vae_int8_convrot.safetensors"),
        "120": node("VAELoader", "H3 audio VAE", vae_name="minimax_h3_audio_vae_fp32.safetensors"),
        "128": node("CLIPLoader", "Qwen3-VL 32B (H3)", clip_name="qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", type="minimax", device="default"),
        "129": node("RandomNoise", "Seed", noise_seed=VIDEO["seed"]),
    }


def _decode_save(g, name, latent):
    g["122"] = node("VAEDecode", "Decode video", samples=latent, vae=["119", 0])
    g["121"] = node("VAEDecodeAudio", "Decode audio", samples=latent, vae=["120", 0])
    g["130"] = node("CreateVideo", "Video + audio", images=["122", 0], audio=["121", 0], fps=VIDEO["fps"])
    g["92"] = node("SaveVideo", f"Save: {name}", video=["130", 0], filename_prefix=f"splitsecond/{name}",
                   **{"format": "mp4", "format.codec": "h264"})


def clip_graph(name):
    route, start, end, desc, sound, *summary = CLIPS[name]
    g = _h3_shared()
    g["148"] = node("LoadImage", f"First frame: {start}", image=f"{start}.png")
    if route == "pika":
        g["147"] = node("LoadImage", f"Last frame: {end}", image=f"{end}.png")
        g["127"] = node("UNETLoader", "MiniMax H3 FL2VA", unet_name="minimax_h3_fl2va_pruned_int8_convrot.safetensors", weight_dtype="default")
        g["134"] = node("LoraLoaderModelOnly", "Pika H3 Flex", model=["127", 0], lora_name="pika_h3_flex_fl2va_v1_bf16.safetensors", strength_model=1)
        g["131"] = node("MiniMaxH3ImageToVideo", f"Pin both ends: {name}", clip=["128", 0], vae=["119", 0],
                        first_frame=["148", 0], last_frame=["147", 0], width=VIDEO["width"], height=VIDEO["height"],
                        length=VIDEO["frames"], prompt=pika_prompt(desc, sound))
        g["126"] = node("BasicGuider", "Guider", model=["134", 0], conditioning=["131", 0])
        g["123"] = node("KSamplerSelect", "LCM", sampler_name="lcm")
        g["143"] = node("ManualSigmas", "6-step schedule", sigmas="1.0, 0.972973, 0.923077, 0.8, 0.571429, 0.333333, 0.0")
        g["125"] = node("SamplerCustomAdvanced", "Sample", noise=["129", 0], guider=["126", 0], sampler=["123", 0],
                        sigmas=["143", 0], latent_image=["131", 1])
    else:
        g["127"] = node("UNETLoader", "MiniMax H3 ref2va", unet_name="minimax_h3_ref2va_pruned_int8_convrot.safetensors", weight_dtype="default")
        g["136"] = node("MiniMaxH3ReferenceToVideo", f"References: {name}", clip=["128", 0], vae=["119", 0], audio_vae=["120", 0],
                        prompt=h3_prompt(start, summary[0], desc, sound), width=480, height=864, length=VIDEO["frames"],
                        ref_image_size="match", **{"ref_images.ref_image_0": ["148", 0]})
        g["147"] = node("MiniMaxH3AddGuide", "Pin first frame", positive=["136", 0], latent=["136", 1], frame_idx=0,
                        vae=["119", 0], audio_vae=["120", 0], image=["148", 0])
        g["126"] = node("BasicGuider", "Guider", model=["127", 0], conditioning=["147", 0])
        g["123"] = node("KSamplerSelect", "res_multistep", sampler_name="res_multistep")
        g["124"] = node("BasicScheduler", "20 steps", model=["127", 0], scheduler="simple", steps=20, denoise=1)
        g["125"] = node("SamplerCustomAdvanced", "Sample", noise=["129", 0], guider=["126", 0], sampler=["123", 0],
                        sigmas=["124", 0], latent_image=["136", 1])
    _decode_save(g, name, ["125", 0])
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
    print(f"wrote {2 + len(CLIPS)} workflows to {OUT}")


def write(path, graph):
    path.write_text(json.dumps(graph, indent=1) + "\n")


if __name__ == "__main__":
    main()
