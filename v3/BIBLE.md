# Split Second v3: bible

Locked before anything is drawn. Every frame and take is checked against this page and `RUBRIC.md` (v2, unchanged).

## The one rule of the game

You get a split second. Every decision runs on a visible timer, and the timer is the pressure: hesitate and the Hound has you. No tap plays the capture.

| Decision | Timer |
|---|---|
| D1 The Edge | 5 s |
| D2 The Market | 4 s |
| D3 The Platform | 3 s |
| D4 The Drop | 2 s |

Nothing on screen marks the right choice. The pattern a viewer can feel by D3, never stated: the Hound corners Rin in tight spaces (the vent, the alley, the carriage), and open ground keeps her alive. Every capture makes sense afterward.

## Cast

| Who | Look (from the references) | Sides | Locks in every take |
|---|---|---|---|
| Rin, a woman in her mid-twenties, courier | Black hair shaved on her left, long fringe on her right with acid-yellow tips; glowing cyan LEFT eye; chrome robotic LEFT arm; black bomber with magenta lining and one big glowing cyan lightning bolt across the back; black crop top; charcoal cargo pants; plain white chunky sneakers. Nothing on her back. | Facing camera: chrome arm and glowing eye on screen-right, fringe on screen-left. From behind: chrome arm screen-left, fringe screen-right. | Her chrome left arm stays chrome; only her left eye glows; the bolt on her jacket stays cyan. |
| The Hound, corp hunter | Tall and lean, matte black bodysuit, smooth faceless helmet with one thin red visor slit, crimson scarf, red blade along his RIGHT forearm, small white hexagon on his LEFT shoulder. Never bulky. | Facing camera: blade screen-left. From behind: blade screen-right. | His blade stays on his right forearm; his visor stays one thin red line. |
| Dex, Rin's fixer | Heavyset, bald, gray-streaked beard, orange goggles on his forehead, chrome jaw, teal bomber with patches. Only ever in the van. | | |

References: one front view and one back view each (Dex front only), plain background, no turnarounds, no brand marks.

## Hero props

- **The chip:** a small flat chip that glows cyan, carried in her chrome left hand. When she opens her hand, a small cyan DNA hologram floats above it.
- **The van:** one boxy bright-yellow panel van, two rear doors, driver's window on its LEFT side. It drives the same way as the train, away from camera. Seen from behind in every shot outside the cab. Once it leaves, it never comes back.
- **The ladder:** fixed yellow steel, bolted flat to the billboard's side panel and running the full height of the building to the market street. It never moves.

## Places (one empty plate each)

| Place | Plate | Camera |
|---|---|---|
| roof_run | Wide flat rooftop at night, water tank on the right, a square vent jutting out of the right-hand wall, a taller rooftop across a gap in the far background | Low, looking back the way she came |
| roof_edge | Rooftop edge; billboard with a wordless glowing-can ad on the left, the fixed yellow ladder flush against its side panel; open square vent on the right | Behind her, at shoulder height |
| alley | Narrow back alley behind the market, fire escape on the right wall, a vent low on the left wall with its grate hanging open, puddles | Down the alley |
| ladder_side | The full height of the billboard building from across the market street, the ladder running from the billboard to the street | Low across the street, looking up |
| market | Market street fork: umbrella crowd on the left, dark alley mouth on the right | Behind her, raised |
| platform | Elevated platform, train on the left with one open red-lit door, fixed yellow ladder up the side of the car on the right | Behind her |
| carriage | Inside the dark empty carriage, aisle straight away from camera, seats both sides, red emergency light | Down the aisle |
| train_roof | Top of the moving train from behind, parallel highway on the right, exit ramp curving up and to the right far ahead | Behind her, above the roof |
| cab | Inside the van cab from behind the two front seats, windshield and the city ahead; driver's seat on the left | Behind the seats, at head height |

## Look

- **Style block, word for word in every prompt:** "Flat cel-shaded neon anime, thick black ink lines, hard-edged shadows, every person and crowd drawn in the same crisp style."
- **Sky line:** "Blue-black night sky, magenta and cyan neon, steady light."
- **Ambient:** rain falls in the background; characters stay dry.
- One palette for the whole episode. No green or orange skies.
- Text in the picture: only the title card. Ads are wordless invented products.

## Sound

- One score under the whole run (the v2 Stable Audio track), mixed by `tools/mix_music.py`.
- Voice: Dex's off-screen line in the setup, kept from the audited v2 stakes take. Everything else is captions.
- Every take: "Nobody speaks."

## Build

Follow the `build-interactive-episode` skill: script, shot spec, keyframe board, takes, mix, grade, ship. H3 Max, 768P, 5 s takes, expansion off, pinned at both ends, one place per take.
