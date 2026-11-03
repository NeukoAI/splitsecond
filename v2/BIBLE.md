# Split Second: build bible

The one page every frame and clip is checked against.

## Story

Rin carries a chip that is the cure for 40,000 people. The Hound, a corp assassin, hunts her across the Lower City. Dex waits with a yellow van. Four choices, each a split second. The wrong choice, or no choice in time, and the Hound catches her.

| Beat | Where | Safe pick | Wrong pick / no tap |
| --- | --- | --- | --- |
| Open | Rooftop. Dex calls, the Hound lands far behind her | | |
| D1 The Edge | Rooftop edge. Billboard with a ladder on the left, open vent on the right, drones sweeping the vents | Jump: she catches the ladder and slides straight down to the market | Vent: she tries to climb in and he hauls her out |
| D2 The Market | A fork in the street, Rin's back to camera. Crowd left, empty alley right with a drone | Crowd: she vanishes in the umbrellas and comes out on the train platform | Alley: she runs deep in, he drops from a fire escape and pins her |
| D3 The Platform | Train with dark red-lit doors left, yellow ladder to the roof right | Roof: she climbs all the way up, the train moves, the van rises into frame alongside and its door opens | Board: she runs down the dark carriage and he grabs her |
| D4 The Drop | Train roof, van alongside on a parallel highway, exit ramp ahead. Timed: one target, the van | Tap the van: she dives in, the van rides with the train, then peels off the exit | No tap: the van can't wait and peels off the exit without her, the Hound comes up behind her on the roof |
| End | Van cab, Dex driving from the left. Then the Hound alone on the train roof as the van takes the exit | | DELIVERED / FLATLINED |

## Characters

Every frame that shows a character is drawn with that character's sheet as a reference image. Never redraw a character from a generated clip frame.

- **Rin:** black hair shaved on the left, long fringe on the right with acid-yellow tips, glowing cyan left eye, chrome left arm, black bomber with magenta lining and a cyan lightning bolt on the back, gray cargo pants, white sneakers.
- **The Hound:** lean, matte black bodysuit, faceless helmet with one red visor slit, crimson scarf, red forearm blade, white hexagon on the left shoulder. Never bulky.
- **Dex:** heavyset, bald, gray-streaked beard, orange goggles on his forehead, chrome jaw, teal bomber with patches. Drives from the left seat.
- **The van:** bright yellow, always.

## How frames and clips are made

1. **Keyframes** (Qwen Image 2.1 Turbo edit): every decision frame and every capture frame is drawn from the character sheets plus one approved frame as the style reference. A keyframe at the same place as another (the capture at the vent, the van leaving) uses that approved keyframe as its base.
2. **Clips** (LTX 2.5): every clip is pinned at both ends to keyframes. LTX has no character reference input, so a character it invents mid-clip drifts. Pinning both ends to sheet-drawn frames is what keeps faces and costumes on model. Where the place changes inside a clip, the prompt calls a hard cut.
3. **Loops** start and end on the decision frame, so the tap targets hold still.
4. **Dialogue** is captions, never spoken lines in the prompt (LTX burns spoken lines in as subtitles).
