# Split Second

**A cyberpunk chase you play by tapping the world.** Rin, a courier with a chrome arm, carries the cure for 40,000 people. The Hound, a corporate hunter, wants it buried. Four split-second choices across rooftops, a night market and a speeding train. Read the clue, tap where she runs. Pick wrong, or wait too long, and you flatline.

**Play it:** https://bitebox.gg/play/fcca8ed4-d460-4d24-b2fd-499931ade1f0

Every character sheet, keyframe, clip, voice line and tap target is generated in ComfyUI with open-weights models: Qwen Image 2.1 Turbo, LTX 2.5 and SAM3.

> Built for the [Open Source Higgsfield](https://comfy.org/open-source-higgsfield) challenge by [NEUKO](https://neuko.ai).

## v2 (current): `v2/`

```mermaid
flowchart TD
  T[Title] --> S[The chip: stakes] --> C[Dex's call] --> H[Rin runs, the Hound lands]
  H --> D1{D1 The Edge}
  D1 -- jump to the billboard --> D2{D2 The Market}
  D1 -- hide in the vent / no tap --> G[FLATLINED]
  D2 -- vanish into the crowd --> D3{D3 The Platform}
  D2 -- run the alley / no tap --> G
  D3 -- climb to the roof --> D4{D4 The Drop}
  D3 -- board the train / no tap --> G
  D4 -- jump for the van --> W[DELIVERED]
  D4 -- keep running / no tap --> G
  G -- TRY AGAIN --> H
  G -- START OVER --> T
  W -- PLAY AGAIN --> T
```

1. **Cast first.** `Qwen Image 2.1 Turbo` text to image makes one reference sheet per character (front, side, back, face): Rin, the Hound, Dex.
2. **Keyframes from the cast.** `Qwen Image 2.1 Turbo` image edit takes the sheets as reference images, so every frame keeps the same faces and costumes. Only the first decision gets a made keyframe. The Hound stays out of the decision frames: he appears inside the clips, when you choose wrong.
3. **Clips between clean frames.** `LTX 2.5`. Every decision frame is redrawn from the character sheets, so the art style can't drift down the chain. The decision loop is pinned to its frame at both ends so it holds still while you choose. Each escape runs from one decision frame to the next, with a hard cut where the place changes, so two different scenes never have to morph into each other. Captures start on the decision frame and end on a drawn capture frame, so the Hound always lands the grab. LTX 2.5 also makes the sound in the same pass; dialogue lives in captions.
4. **Tap targets.** `SAM3` finds each object from a sentence. The mask is grown, the original subtracted and the ring colored, so each object gets its own glowing outline that the player draws exactly where SAM3 found it.
5. **Assemble.** `v2/build_document.py` turns `v2/story.json` plus the hosted media into a bitebox document: Target Overlays for taps, the loop's autoplay exit as the 5-second timeout, and end cards that hold until you tap TRY AGAIN, START OVER or PLAY AGAIN.

| Path | What it is |
| --- | --- |
| `v2/story.json` | Cast, the four decisions with their clues, every scene's prompt, duration and anchors |
| `v2/cast.json` | The character descriptions and the shared style line |
| `v2/build_document.py` | Story + media → bitebox document (spec 0.7) |
| `v2/targets.json` | Tap target positions from the SAM3 masks |
| `v2/review/` | The review board: every clip with first, last and next frames, and per-clip feedback |
| `tools/review_media.sh` | GitHub Action helper that makes small review copies of every hosted clip |

## v1 (first submission draft)


**A rooftop chase you play by tapping the world.** A courier, three ninjas, one way off the roof. Tap what glows. Pick wrong and they catch you, and the chase starts over with a different safe route.

Everything is made in ComfyUI with open-weights models: the keyframes, every clip, and the glowing tap targets.

> Built for the [Open Source Higgsfield](https://comfy.org/open-source-higgsfield) challenge by [NEUKO](https://neuko.ai).

## The idea: pick the moment first

Most AI video stories generate forward and then try to hide the seams between clips. Split Second works backwards. It picks the **decision frames** first, then generates every clip *to* or *from* those frames with first/last-frame video. Every cut lands on identical pixels, so a 15-clip branching story plays like one continuous shot.

```mermaid
flowchart LR
  K0[approach frame] -->|opening| K1((decision 1 frame))
  K1 -->|idle loop, starts and ends here| K1
  K1 -->|zip / ladder / door: safe| K2((decision 2 frame))
  K1 -->|zip / ladder / door: caught| R[restart, next layout]
  K2 -->|idle loop| K2
  K2 -->|train / billboard / antenna: safe| W[escaped]
  K2 -->|train / billboard / antenna: caught| R
  R --> K0
```

Three more pieces make it a game:

- **Tap the world, not a button.** SAM3 finds each object from a sentence ("the red metal door of the small stairwell hut"). The workflow grows the mask, subtracts the original and colors the ring, so each object gets its own glowing outline PNG. The player places those outlines exactly where SAM3 found the objects.
- **Hesitation is a choice.** You get one idle loop to decide. Let it run out and they catch you.
- **The safe route rotates.** Every object has both a safe clip and a capture clip. Each run uses a different layout (zipline then train, door then billboard, ladder then antenna), so what saved you last time gets you caught now.

## What's in here

| Path | What it is |
| --- | --- |
| `build_workflows.py` | Generates every workflow below from one place: prompts, seeds, settings |
| `workflows/01_keyframes.json` | The three decision frames, Z-Image Turbo |
| `workflows/02_targets.json` | SAM3 masks and glowing outline crops for the six tap targets |
| `workflows/clips/*.json` | One job per clip (15 clips), picture and sound in one pass |
| `story.json` | The story graph: scenes, decisions, tap targets, rotation (points at the hosted clips) |
| `bitebox/build_document.py` | Unrolls `story.json` into a bitebox document: three run copies, chained decision loops, SAM3 outlines as Target Overlays |
| `bitebox/split_second.json` | The generated bitebox document |
| `player/index.html` | A dependency-free player for that graph |

## Run it

**1. Models.** Put these in your ComfyUI `models/` folders (all open weights):

| File | Folder |
| --- | --- |
| `z_image_turbo_bf16.safetensors` | `diffusion_models` |
| `qwen_3_4b.safetensors` | `text_encoders` |
| `ae.safetensors` | `vae` |
| `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | `diffusion_models` |
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | `diffusion_models` |
| `pika_h3_flex_fl2va_v1_bf16.safetensors` | `loras` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `text_encoders` |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `vae` |
| `minimax_h3_audio_vae_fp32.safetensors` | `vae` |
| `sam3.1_multiplex_fp16.safetensors` | `checkpoints` |

Only core ComfyUI nodes are used. No custom node packs.

**2. Keyframes.** Queue `workflows/01_keyframes.json`. Copy the three images from `output/splitsecond/` into `input/` as `k0_approach.png`, `k1_decision1.png` and `k2_decision2.png`.

**3. Tap targets.** Queue `workflows/02_targets.json` to get the masks. Put each object's crop box in `targets.json`, rerun `python3 build_workflows.py`, and queue it again to get the glowing outlines.

**4. Clips.** Queue each file in `workflows/clips/`. Each takes about a minute on Comfy Cloud. Clips that must land on a decision frame (opening, the idle loops, the decision 1 escapes) use Pika H3 Flex with both ends pinned. Captures and the final escapes only need to start on the frame, so they use MiniMax H3 with the first frame as a guide.

**4b. Seam pass.** MiniMax H3 treats the first frame as a guide, not a pin, and renders at 480×864, so cutting into it from a Pika loop pops. Run `python3 seamfix.py`, put each H3 render in `input/` as `h3_<clip>.mp4`, and queue its graph in `workflows/seamfix/`. It scales the clip to 576×1024 and dissolves from the anchor keyframe over the first quarter second, so every cut starts on the frame the loop ends on.

**5. Play.** `story.json` already points at the hosted clips and outlines, so the local player works as is. To use your own renders, point the `scenes` and `glow` entries at your files. Then serve the folder and open `player/`:

```sh
python3 -m http.server 8000
# open http://localhost:8000/player/
```

To change the story, edit the prompts in `build_workflows.py` and rerun it.

## Settings

Pinned clips: Pika H3 Flex LoRA on MiniMax H3 first/last-frame, 576×1024, 124 frames at 24 fps with audio, 6 steps lcm (manual sigmas), seed 7.
Open-ended clips: MiniMax H3 reference-to-video with a frame 0 guide, 480×864, 124 frames at 24 fps with audio, 20 steps res_multistep, seed 7; then the seam pass (lanczos to 576×1024, 6-frame dissolve from the anchor).
Keyframes: Z-Image Turbo, 576×1024, 8 steps, cfg 1, res_multistep, shift 3.

## Play it on bitebox

The hosted build runs on [bitebox](https://bitebox.gg), NEUKO's interactive video player. ComfyUI makes every pixel; bitebox does the part ComfyUI can't: branching, timing, taps and the run-to-run rotation.

bitebox has no random rule, so `bitebox/build_document.py` unrolls the rotation into copies of the run. Every capture plays into the next copy's opening. Each decision gives you one five-second loop with the glowing SAM3 outlines on top as tap targets; let it run out and the hesitation capture plays. bitebox's publish check walks at most 200 paths, so the hosted build alternates two layouts (43 paths); the local player rotates all three.

```sh
python3 bitebox/build_document.py bitebox/media.json > bitebox/split_second.json
```

## License

MIT. See [LICENSE](LICENSE).
