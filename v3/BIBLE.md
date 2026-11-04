# Split Second v3: bible

Locked before anything is drawn. Every frame and take is checked against this page and `RUBRIC.md` (v2, unchanged).

## The one rule of the world

The Hound sees through his red drones. Wherever a red drone light points, he is already on his way. Every decision shows one red drone on the wrong choice, so a viewer who learns the rule can win, and the rule is readable with the sound off.

## Cast

| Who | Look (from the references) | Sides | Locks in every take |
|---|---|---|---|
| Rin, 19, courier | Black hair shaved on her left, long fringe on her right with acid-yellow tips; glowing cyan LEFT eye; chrome robotic LEFT arm; black bomber with magenta lining and one big glowing cyan lightning bolt across the back; black crop top; charcoal cargo pants; plain white chunky sneakers. Nothing on her back. | Facing camera: chrome arm and glowing eye on screen-right, fringe on screen-left. From behind: chrome arm screen-left, fringe screen-right. | Her chrome left arm stays chrome; only her left eye glows; the bolt on her jacket stays cyan. |
| The Hound, corp hunter | Tall and lean, matte black bodysuit, smooth faceless helmet with one thin red visor slit, crimson scarf, red blade along his RIGHT forearm, small white hexagon on his LEFT shoulder. Never bulky. | Facing camera: blade screen-left. From behind: blade screen-right. | His blade stays on his right forearm; his visor stays one thin red line. |
| Dex, Rin's fixer | Heavyset, bald, gray-streaked beard, orange goggles on his forehead, chrome jaw, teal bomber with patches. Only ever in the van. | | |

References: one front view and one back view each (Dex front only), plain background, no turnarounds, no brand marks.

## Hero props

- **The chip:** a small flat chip that glows cyan, carried in her chrome left hand. When she opens her hand, a small cyan DNA hologram floats above it.
- **Red drones:** small black quad drones, one red light each, a red cone of light where they look. They are the clue.
- **The van:** one boxy bright-yellow panel van, two rear doors, driver's window on its LEFT side. It drives the same way as the train, away from camera. Seen from behind in every shot outside the cab. Once it leaves, it never comes back.
- **The ladder:** fixed yellow steel. It never moves.

## Places (one empty plate each)

| Place | Plate | Camera |
|---|---|---|
| roof_run | Wide flat rooftop at night, water tank on the right, a taller rooftop across a gap in the far background | Low, looking back the way she came |
| roof_edge | Rooftop edge; billboard with a wordless glowing-can ad and a fixed yellow ladder on the left; open square vent on the right | Behind her, at shoulder height |
| alley | Narrow back alley behind the market, fire escape on the right wall, a vent grate low on the left wall, puddles | Down the alley |
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
