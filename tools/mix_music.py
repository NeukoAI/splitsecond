"""Mixes one score under every story clip, cut to where that clip sits in a run.

    python3 tools/mix_music.py      (needs ffmpeg and ffprobe)

The player has no story-wide music track, so the score is baked into each clip.
Clips on the main path take the score from where the run reaches them; a capture
takes it from the same point as the escape it replaces. The result in mixed/
is the clip with the score under its own sound (dialogue clips duck it more).
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
    clip = fetch(media[key], key + ".mp4")
    at[key] = t
    t += duration(clip)
for capture, escape in cfg["captures"].items():
    at[capture] = at[escape]

report = {}
for key, start in at.items():
    clip = fetch(media[key], key + ".mp4")
    db = cfg["voice_db"] if key in cfg["voice"] else cfg["music_db"]
    music = f"[1:a]atrim=start={start:.3f},asetpts=PTS-STARTPTS,volume={db}dB,afade=t=in:d=0.08[m]"
    if has_audio(clip):
        graph = f"{music};[0:a][m]amix=inputs=2:duration=first:normalize=0[a]"
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
