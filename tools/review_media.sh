#!/usr/bin/env bash
# Pulls every hosted clip and still in v2/media.json and writes small review copies:
# a 270x480 preview mp4 plus first and last frames for clips, a jpg for stills.
set -euo pipefail
out=review
mkdir -p "$out" /tmp/src
python3 - <<'PY' > /tmp/list.txt
import json
for k, u in json.load(open("v2/media.json")).items():
    print(k, u)
PY
while read -r key url; do
  ext="${url##*.}"
  src="/tmp/src/$key.$ext"
  curl -sSfL "$url" -o "$src"
  if [ "$ext" = "mp4" ]; then
    ffmpeg -loglevel error -y -i "$src" -vf scale=270:480 -c:v libx264 -preset veryfast -crf 30 -c:a aac -b:a 64k -movflags +faststart "$out/$key.mp4"
    ffmpeg -loglevel error -y -i "$src" -vf "select=eq(n\,0),scale=270:480" -frames:v 1 -q:v 4 "$out/${key}_first.jpg"
    ffmpeg -loglevel error -y -sseof -0.1 -i "$src" -vf scale=270:480 -frames:v 1 -update 1 -q:v 4 "$out/${key}_last.jpg"
  else
    ffmpeg -loglevel error -y -i "$src" -vf "scale=270:-2" -q:v 4 "$out/$key.jpg"
  fi
done < /tmp/list.txt
ls -la "$out" | head -80
