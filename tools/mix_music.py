"""Mixes one score under every story clip, cut to where that clip sits in a run.

    python3 tools/mix_music.py      (needs ffmpeg and ffprobe)

The player has no story-wide music track, so the score is baked into each clip.
Clips on the main path take the score from where the run reaches them; a capture
takes it from the same point as the escape it replaces. The result in mixed/
is the clip with the score under its own sound (dialogue clips duck it more).

A source can be a list of parts (a URL, or {"url", "start", "end"} to keep only
the good stretch of a take): they are joined with hard cuts first, so one
place per generated clip still plays as one scene. "audio_from" keeps a clip's
sound (a voice line) from another file, and "clip_db" turns a clip's own sound
up or down before the score goes under it.
"""
import json
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "v2" / "mix.json").read_text())
media = cfg["sources"]  # the unmixed clips, so a re-run never mixes twice
out = ROOT / "mixed"
src = Path("/tmp/mix-src")
out.mkdir(exist_ok=True)
src.mkdir(exist_ok=True)


def fetch(url, name):
    path = src / name
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    return path


def run(args):
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *args], check=True)


# every take's own sound is brought to one loudness, so cuts and joins don't jump
LEVEL = f"loudnorm=I={cfg.get('own_lufs', -26)}:TP=-2:LRA=11,"


def prepare(key):
    """One local file per clip: parts joined by hard cuts, sound swapped if asked."""
    entry = media[key]
    parts = [p if isinstance(p, dict) else {"url": p} for p in (entry if isinstance(entry, list) else [entry])]
    files = []
    for i, part in enumerate(parts):
        f = fetch(part["url"], f"{key}_{i}.mp4")
        if "start" in part or "end" in part:  # keep only the good stretch of a take
            cut = src / f"{key}_{i}_cut.mp4"
            span = ["-ss", str(part.get("start", 0))]
            if "end" in part:
                span += ["-t", str(part["end"] - part.get("start", 0))]
            run(["-i", str(f), *span, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                 "-c:a", "aac", "-b:a", "160k", str(cut)])
            f = cut
        files.append(f)
    clip = files[0]
    if len(files) > 1:
        w, h = (probe(files[0], "stream=width,height")["streams"][0][k] for k in ("width", "height"))
        ins, chains = [], []
        for i, f in enumerate(files):
            ins += ["-i", str(f)]
            chains.append(f"[{i}:v]scale={w}:{h},setsar=1,fps=24,format=yuv420p[v{i}]")
            if has_audio(f):
                chains.append(f"[{i}:a]{LEVEL}aresample=44100,aformat=channel_layouts=stereo[a{i}]")
            else:
                d = duration(f)
                chains.append(f"anullsrc=r=44100:cl=stereo,atrim=duration={d:.3f}[a{i}]")
        joined = "".join(f"[v{i}][a{i}]" for i in range(len(files)))
        graph = ";".join(chains) + f";{joined}concat=n={len(files)}:v=1:a=1[v][a]"
        clip = src / f"{key}_joined.mp4"
        run([*ins, "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
             "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "160k", str(clip)])
    if key in cfg.get("audio_from", {}):
        voice = fetch(cfg["audio_from"][key], f"{key}_voice.mp4")
        swapped = src / f"{key}_voiced.mp4"
        run(["-i", str(clip), "-i", str(voice), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "160k", "-shortest", str(swapped)])
        clip = swapped
    return clip


def probe(path, entries):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def duration(path):
    return float(probe(path, "format=duration")["format"]["duration"])


def has_audio(path):
    return any(s.get("codec_type") == "audio" for s in probe(path, "stream=codec_type").get("streams", []))


score = fetch(cfg["score"], "score" + Path(cfg["score"]).suffix)

# where each clip sits on the score
at, t = {}, 0.0
for key in cfg["path"]:
    clip = prepare(key)
    at[key] = t
    t += duration(clip)
for capture, escape in cfg["captures"].items():
    at[capture] = at[escape]

report = {}
for key, start in at.items():
    clip = prepare(key)
    db = cfg["voice_db"] if key in cfg["voice"] else cfg["music_db"]
    music = f"[1:a]atrim=start={start:.3f},asetpts=PTS-STARTPTS,volume={db}dB,afade=t=in:d=0.08[m]"
    own = cfg.get("clip_db", {}).get(key, 0)
    if has_audio(clip):
        level = "" if key in cfg["voice"] else LEVEL
        graph = f"{music};[0:a]{level}aresample=44100,volume={own}dB[c];[c][m]amix=inputs=2:duration=first:normalize=0[a]"
    else:
        graph = f"{music};[m]anull[a]"
    target = out / f"{key}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(clip), "-i", str(score),
                    "-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(target)],
                   check=True)
    report[key] = {"at": round(start, 2), "own_audio": has_audio(clip)}
(out / "report.json").write_text(json.dumps(report, indent=1))
print(json.dumps(report, indent=1))
