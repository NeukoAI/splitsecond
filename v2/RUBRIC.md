# Split Second: clip rubric

Grade every keyframe and clip against this page before Austin sees it. It is built from every review note he left on the review board during the build. Read `v2/BIBLE.md` first for the story, the cast and how frames are made.

## How to grade

1. **Look, don't assume.** For every clip, pull 8 evenly spaced frames, including the true first and last frame, and look at them. Look at the seams too: the last frame of each clip next to the first frame of every clip it can cut to. A prompt saying something happened is not evidence.
2. **Score each clip on the eight checks below:** 2 = right, 1 = noticeable flaw a viewer would still follow, 0 = wrong or broken. A 0 on a gate check (marked **gate**) fails the clip whatever the total.
3. **Clip grade:** A = 15 to 16 with no gate failure, B = 12 to 14, C = 9 to 11, F = 8 or below, or any gate failure.
4. **Run grade:** the lowest grade on the winning path, then note every capture below B. A run is ready to publish only when every clip is B or better.
5. **Adversarial pass:** a second grader who did not make the clips grades them from the frames alone, without the prompts. Any check where the two graders disagree by more than a point is re-examined at full size before shipping.
6. **Write the fix with the grade.** Each clip below A gets one line: what is wrong, the cause (keyframe, clip, or seam) and the fix (redraw which frame from which references, or regenerate which clip pinned to which frames).

## The eight checks

### 1. Character on model (gate)
Every visible character matches their sheet in every frame, not just the first and last.
- **Rin:** black hair shaved on the left with a long fringe on the right with acid-yellow tips, glowing cyan left eye, chrome left arm, black bomber with magenta lining and a cyan lightning bolt on the back, gray cargo pants, chunky white sneakers.
- **The Hound:** tall and lean, matte black bodysuit, smooth faceless helmet with one thin red visor slit, crimson scarf, red forearm blade. Never bulky, never a generic robot.
- **Dex:** heavyset, bald, gray-streaked beard, orange goggles on his forehead, teal bomber. Only ever inside the yellow van: at the wheel or leaning out of the driver's side window. Never on the train, never in the cargo bay, never melting through the van's siding.
- **Left and right:** Rin's chrome arm and glowing eye are her left. When she faces camera they sit on camera right; from behind, camera left. Only one arm is chrome.
- **Fails:** the face or hair changes mid-clip (yellow tips or eye glow fading out counts), liquid dripping off a hand or face, a character melts or warps, a character appears twice, a character the shot needs is missing, or a sheet's text or turnaround leaks into the frame.

### 2. One art style (gate)
Flat cel-shaded neon anime: thick black ink lines, hard-edged shadows, magenta, cyan and acid yellow on blue-black night. Every person in frame, crowds and extras included, is drawn in that same crisp style as Rin.
- **One palette:** blue-black night with magenta and cyan neon in every clip. A green or orange sky in one clip is a style break.
- **Fails:** photoreal or semi-real rendering, muddy or washed-out color, painterly or blurry crowds that look pasted behind a crisp Rin, or the style drifting from one clip to the next.

### 3. Seams
A clip's first frame is the last frame of the clip that cuts to it. A decision loop starts and ends on its decision frame, so the tap targets hold still. Where the place changes, the clip uses a clean hard cut.
- **Fails:** a black frame or a frozen gap inside a clip, a pop in pose, color or framing at a cut, a loop that drifts away from its frame, or a morph where one place melts into another.

### 4. Story reads
A viewer who has never seen the script can say what happened. The beat matches the bible.
- Captures are real grabs: the Hound grabs her, pins her or puts a hand on her shoulder. Never a handshake, never sitting down next to her.
- The Hound appears at the moment of the capture, not earlier.
- The safe route ends on the next decision frame. The timeout capture plays out the miss, so on decision 4 the van leaves without her.

### 5. Direction and blocking
Everything moves the way the story says.
- Rin has her back to the camera at the decision frames and when she runs away from camera. She does not turn around unless the beat calls for it.
- The van drives the same way as the train, away from camera, seen from behind, and takes the exit ramp up and to the right. It never faces the camera, never drives in reverse, and never comes back once it has left.
- Escapes head away from the threat; the camera follows behind her.

### 6. Physics and motion
What should move moves; what should stay still stays still.
- The crowd walks, umbrellas bob, rain falls. The train and the van keep moving forward together, so a loop never reads as forward-then-back.
- Fixed things stay fixed: the ladder never moves with her, the train only starts once she is on the roof.
- Jumps are short and plausible. She slides down the ladder and never climbs up it.
- **Fails:** frozen crowds, oscillating loops, objects that bend or swim, impossible leaps, a character who vanishes mid-action, or one who pops in at a sudden size jump.

### 7. Decision frame reads
At each decision the two choices are obvious at a glance, and the glow outline sits on the right object.
- D1: the billboard ladder on the left, the vent on the right, drones sweeping the vents (the clue).
- D2: a clear fork, crowd on the left, empty alley on the right with a red drone.
- D3: dark red-lit doors, the ladder to the roof.
- D4: the van right beside her with its rear doors open, Dex waving her in from the driver's window, the exit ramp ahead.

### 8. Picture and sound clean
- No burned-in subtitles or captions in the picture. Dialogue lives in captions, and voice lines fit inside their clip.
- No garbled text. Ads show invented products, never Rin's face and never a real brand or a lookalike of one.
- The score runs under every story clip without a gap or a jump on the winning path.
- No other speech or narration.

## Known model behavior to plan around

- LTX 2.5 and H3 Max get no character sheet. A character they invent mid-clip drifts, so pin both ends to sheet-drawn frames.
- Image edits that use a scene frame as the base keep its composition and its mistakes. Draw from a location plate plus the sheets when the composition must change.
- Passing an approved scene as a "style reference" makes the model copy that scene's layout.
- Scene-to-scene first/last frame clips morph. Use a hard cut, or end on a frame in the same place.
- Quoted dialogue in a video prompt brings burned-in subtitles. Put lines in captions or the off-screen audio sentence.
- Rin's backpack hides the bolt from behind, and the models move the bolt onto the backpack, then drop one or the other. Draw her without the backpack.
- A clip that has to cover two places morphs, pans or goes black between them. One place per clip; join two places with a hard cut between two clips.
- Anything the story needs held in place (the van beside her, the van on the ramp) needs its own pinned frame. Prompts alone do not hold it.
- An edit that moves a character keeps the old one too: two Rins. "Remove her" is ignored. "Redraw the scene with exactly one person, Rin, now at X" works, but it can move the camera.
- An edit that adds a vehicle keeps the old vehicle. Draw the frame fresh from the empty location plate with exact counts of people and vehicles.
- Pins at very different sizes make a jump: a start frame much closer than the end makes her teleport in the first second, or run past the camera and snap back. Keep the two pins at the same scale, and say the camera moves with her so she stays the same size.
- Two pins with the same composition and a run in between make the model run her away, then snap her back. Trim the take to the good stretch.
- Neon light turns the cyan bolt magenta for a beat. Say the bolt stays cyan.
- "Red emergency light pulses" makes the whole carriage flash red and teal. Ask for a steady red light.
- Takes default to the same seed. Pass a new seed on a retake.

- (v3) The Hound's blade lands on screen-right whichever way he faces. A small edit asking to move it to his other forearm is ignored. Accept it on capture frames or redraw with the blade named as "on the left side of the picture, near the left edge".
- (v3) A take that starts halfway up a ladder climbs up first before it slides down. Start the pin at the top of the ladder, or trim the climb in the mix.
- (v3) A follow-cam take on a running character can jump to a close-up for a frame and lose fixed props for a second. Trim to the stretch after it settles.
- (v3) The grab Action skips files whose name is already on the branch. A retake pulled under the same name comes back as the old picture. Put the media id in every pulled file name.
- (v3) Hand-traced glow outlines (a polygon per object on the decision frame, drawn with PIL) are fine when SAM3 is not run. Draw them on the final decision frame, never an earlier version.
