"""Turns v2/split_second_v2.json into bitebox document_apply batches.

    python3 v2/to_commands.py v2/split_second_v2.json old_node_ids.json > v2/commands.json

bitebox builds a File only through commands: create each node, patch its
content, then connect wires (exits, overlays, glow markers, choice options).
The last batch sets the new start and deletes the old nodes.
"""
import json
import sys

DEF = {"video": "video", "image": "image"}


def defid(n):
    if n["type"] == "trigger":
        return "choice-overlay" if n["props"]["kind"] == "choiceOverlay" else "hotspot"
    return DEF[n["type"]]


def commands(doc, old_ids):
    nodes = doc["nodes"]
    build, wire = [], []
    for nid, n in nodes.items():
        d = defid(n)
        build.append({"type": "create-node-at-position", "nodeId": nid, "definitionId": d,
                      "x": n["ui"]["x"], "y": n["ui"]["y"] + 4000})
        build.append({"type": "rename-node", "nodeId": nid, "title": n["title"]})
        p = n["props"]
        edits = []
        if d == "video":
            for k in ("src", "width", "height", "durationMs", "displayInExperience", "captions"):
                if k in p:
                    edits.append({"operation": "set", "path": f"/props/{k}", "value": p[k]})
        elif d == "image":
            for k in ("src", "alt", "displayInExperience"):
                edits.append({"operation": "set", "path": f"/props/{k}", "value": p[k]})
        elif d == "hotspot":
            edits += [{"operation": "set", "path": "/props/position/x", "value": p["position"]["x"]},
                      {"operation": "set", "path": "/props/position/y", "value": p["position"]["y"]},
                      {"operation": "set", "path": "/props/rect/width", "value": p["rect"]["width"]},
                      {"operation": "set", "path": "/props/rect/height", "value": p["rect"]["height"]},
                      {"operation": "set", "path": "/props/size", "value": p["size"]},
                      {"operation": "set", "path": "/props/displayInExperience", "value": True}]
        else:
            edits += [{"operation": "set", "path": "/props/active/startMs", "value": p["active"]["startMs"]}]
            for i, o in enumerate(p["options"]):
                edits.append({"operation": "set", "path": f"/props/options/{i}/label", "value": o["label"]})
        build.append({"type": "patch-node-content", "patch": {"nodeId": nid, "expectedDefinitionId": d, "edits": edits}})

        def conn(src, sep, dst, dep):
            wire.append({"type": "connect", "connection": {"source": {"nodeId": src, "endpointId": sep},
                                                           "target": {"nodeId": dst, "endpointId": dep}}})

        if d == "video":
            ex = f"exit:exit.{nid}.autoplay"
            nxt = p["exits"][0]["next"]
            if nxt:
                conn(nid, ex, nxt, "story-in")
            for ov in p.get("overlays", []):
                conn(nid, ex, ov, "owner")
        elif d == "hotspot":
            conn(p["image"], "file", nid, "file")
            conn(nid, "branch", n["next"], "story-in")
        elif d == "choice-overlay":
            for o in p["options"]:
                if o["next"]:
                    conn(nid, f"option:{o['id']}", o["next"], "story-in")
    finish = [{"type": "set-start", "nodeId": doc["start"]}]
    finish += [{"type": "delete-node", "deletion": {"nodeId": o}} for o in old_ids]
    return {"build": build, "wire": wire, "finish": finish}


if __name__ == "__main__":
    doc = json.load(open(sys.argv[1]))
    old = json.load(open(sys.argv[2]))
    json.dump(commands(doc, old), sys.stdout, indent=1)
