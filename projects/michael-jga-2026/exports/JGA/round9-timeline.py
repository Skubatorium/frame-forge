"""Runde-9-Feintuning (Christians 8. Preview-Feedback, editorial-notes-round9.md).

Zwei Text-Korrekturen (party-fx-recipe.py, separat gelaufen) + eine Streichung:
* `v056` ("Frietland"-Terrasse) raus -- Christian: Bilder ruecken vor, Schwarzblende +
  Stille am Akt-1/2-Uebergang passen dann besser.

Transformiert die Runde-8-Timeline und schreibt zurueck nach `timeline.json`.

Aufruf:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/round9-timeline.py
"""
from __future__ import annotations

import json
import re as _re
from pathlib import Path

ROOT = Path("projects/michael-jga-2026")
TL_PATH = ROOT / "exports" / "JGA" / "timeline.json"
BRIEF_PATH = ROOT / "exports" / "JGA" / "brief.yaml"

XF = {"dissolve", "fade", "crossfade", "slow_dissolve"}

tl = json.loads(TL_PATH.read_text())
V = sorted(tl["tracks"]["video"], key=lambda c: c["tl_in"])
OV = sorted(tl["tracks"]["overlay"], key=lambda c: c["tl_in"])
AU = tl["tracks"]["audio"]
ORIG_ORDER = [c["id"] for c in V]


def clip_dur(clip: dict) -> float:
    return (clip["src_out"] - clip["src_in"]) / clip.get("speed", 1.0)


# ---------------------------------------------------------------------------
# 1) Overlays + Cast-SFX + otons an ihren Video-Anker binden (VOR jeder Aenderung).
def anchor_of(t: float) -> tuple[str, float]:
    cur = V[0]
    for c in V:
        if c["tl_in"] <= t + 1e-6:
            cur = c
        else:
            break
    return cur["id"], round(t - cur["tl_in"], 4)


anchors: dict[int, tuple[str, float]] = {id(o): anchor_of(o["tl_in"]) for o in OV}
for s in AU:
    if s.get("id", "").startswith(("sfx-cast", "oton-")):
        anchors[id(s)] = anchor_of(s["tl_in"])

# ---------------------------------------------------------------------------
# 2) Video: v056 ("Frietland"-Terrasse) raus.
DROP = {"v056"}
V = [c for c in V if c["id"] not in DROP]
by_id = {c["id"]: c for c in V}

# ---------------------------------------------------------------------------
# 3) Video-Spur sequentiell neu auslegen.
t = 0.0
new_tl: dict[str, float] = {}
for i, c in enumerate(V):
    ti = c.get("transition_in") or {}
    ov = ti.get("dur", 0.0) if ti.get("type") in XF else 0.0
    if i == 0:
        ov = 0.0
    start = round(t - ov, 4)
    if start < 0:
        start = 0.0
    c["tl_in"] = start
    new_tl[c["id"]] = start
    t = start + clip_dur(c)

video_end = round(t, 4)
alive = {c["id"] for c in V}


def resolve_anchor(aid: str) -> str:
    if aid in alive:
        return aid
    j = ORIG_ORDER.index(aid) if aid in ORIG_ORDER else 0
    for k in range(j - 1, -1, -1):
        if ORIG_ORDER[k] in alive:
            return ORIG_ORDER[k]
    return next(iter(alive))


# ---------------------------------------------------------------------------
# 4) Overlays + SFX/oton generisch via Anker neu platzieren.
for o in OV:
    aid, off = anchors[id(o)]
    o["tl_in"] = round(new_tl[resolve_anchor(aid)] + off, 4)
for s in AU:
    if id(s) in anchors:
        aid, off = anchors[id(s)]
        s["tl_in"] = round(new_tl[resolve_anchor(aid)] + off, 4)

# ---------------------------------------------------------------------------
# 5) Audio — Akt-1/2-Uebergang (Schwarzblende v057b, Musikluecke) auf die neue Geometrie
# nachziehen, WIMM (music-03) auf das neue video_end.
amap = {a.get("id"): a for a in AU}
v069_tl = new_tl["v069"]
black_tl = new_tl["v057b"]
v160_tl = new_tl["v160"]

cl = amap.get("music-01-cltheme")
if cl:
    cl["dur"] = round(black_tl, 3)

mis = amap.get("music-02-miserlou")
if mis:
    mis["tl_in"] = round(v069_tl, 3)
    mis["dur"] = round(v160_tl - v069_tl - 0.2, 3)

wimm = amap.get("music-03-wimm")
if wimm:
    wimm["dur"] = round(video_end - wimm["tl_in"] - 0.9, 3)

# ---------------------------------------------------------------------------
tl["duration"] = video_end
tl["tracks"]["video"] = V
tl["tracks"]["overlay"] = sorted(OV, key=lambda c: c["tl_in"])
tl["tracks"]["audio"] = AU
TL_PATH.write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")

gap = mis["tl_in"] - (cl["tl_in"] + cl["dur"]) if cl and mis else None
print(f"timeline.json geschrieben. Dauer {video_end:.2f}s "
      f"({int(video_end // 60)}:{video_end % 60:05.2f}), "
      f"video {len(V)} / overlay {len(OV)} / audio {len(AU)}")
print(f"  v057b (Black) tl_in={black_tl:.2f}")
print(f"  v069 tl_in   = {v069_tl:.2f}s  ({int(v069_tl // 60)}:{v069_tl % 60:05.2f})")
if gap is not None:
    print(f"  music-01 end = {cl['tl_in'] + cl['dur']:.2f}s  |  music-02 start = "
          f"{mis['tl_in']:.2f}s  -> Stille {gap:.2f}s")
if wimm:
    print(f"  music-03-wimm dur={wimm['dur']:.2f} -> Ende "
          f"{wimm['tl_in'] + wimm['dur']:.2f} (video_end {video_end:.2f})")

bt = BRIEF_PATH.read_text()
bt2 = _re.sub(r"target_duration_s:\s*[0-9.]+", f"target_duration_s: {video_end:.1f}", bt)
if bt2 != bt:
    BRIEF_PATH.write_text(bt2)
    print(f"brief.yaml target_duration_s -> {video_end:.1f}")
