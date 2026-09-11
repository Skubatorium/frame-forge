"""Runde-8-Korrektur von `exports/JGA/timeline.json` (editorial-notes-round8.md).

Behebt ein Missverstaendnis aus Runde 7: `v092` (IMG_1543, Zunge raus neben Corona-Flasche)
wurde faelschlich gestrichen -- das war das Bild, das mit `ov-hydrated` zusammengehoert.
Christian wollte stattdessen `v091` (Dachterrasse-Anstoss, redundant zu `v090`) draussen haben.

Transformiert die Runde-7-Timeline und schreibt zurueck nach `timeline.json`.

Aufruf:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/round8-timeline.py
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
# 2) Video: v091 raus, v092 (IMG_1543, "Text Stay hydrated") wieder rein.
by_id = {c["id"]: c for c in V}


def set_dur(cid: str, seconds: float) -> None:
    c = by_id[cid]
    c["src_out"] = round(c["src_in"] + seconds * c.get("speed", 1.0), 4)


DROP = {"v091"}
V = [c for c in V if c["id"] not in DROP]
by_id = {c["id"]: c for c in V}

# Original-Definition (Runde <=6, vor dem faelschlichen Streichen in R7). Etwas laenger
# (2.2 -> 2.6 s) als Puffer fuer das ov-hydrated-Placement.
v092 = {
    "id": "v092", "asset": "20260905-phone-a05520", "src_in": 0.0, "src_out": 2.6,
    "tl_in": 0.0, "speed": 1.0,
    "effects": [{"type": "kenburns", "from": [0.0, 0.0, 1.08],
                 "to": [-0.0127, 0.0127, 1.035], "ease": "in"}],
    "note": "R8: wieder rein (war in R7 faelschlich gestrichen) -- Text Stay hydrated",
    "fit": "blur",
}
i090 = next(i for i, c in enumerate(V) if c["id"] == "v090")
V.insert(i090 + 1, v092)
by_id["v092"] = v092

# Gurken-Cluster: v159 (Host von ov-gurken + ov-raetkeinkaese) minimal strecken, damit
# ov-raetkeinkaese laenger stehen kann; v158 (kein Text mehr, ov-ichwaresnicht faellt weg)
# schrumpft dafuer.
set_dur("v159", clip_dur(by_id["v159"]) + 0.6)
set_dur("v158", clip_dur(by_id["v158"]) - 0.6)

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
# 5) Overlay-Aenderungen Runde 8.
def get_ov(name: str) -> dict | None:
    for o in OV:
        if o.get("id") == name or o.get("png", "").endswith(name + ".png"):
            return o
    return None


# ov-christoph + ov-ichwaresnicht komplett raus.
DROP_OV = {"ov-christoph", "ov-ichwaresnicht"}
OV = [o for o in OV if o.get("id") not in DROP_OV]

# ov-hydrated auf v092 verankern (statt v091, das jetzt weg ist).
oh = get_ov("ov-hydrated")
if oh and "v092" in new_tl:
    oh["tl_in"] = round(new_tl["v092"] + 0.15, 4)
    oh["dur"] = 2.0

# ov-raetkeinkaese etwas laenger stehen lassen.
ork = get_ov("ov-raetkeinkaese")
if ork:
    ork["dur"] = round(ork["dur"] + 0.8, 4)

# Anti-Bleed-Sicherung — Lese-Texte, nur KUERZEN, nie unter 1,6 s.
ANTIBLEED = {"ov-crewupdate", "ov-token", "ov-natuerlich", "ov-weiterziehen",
             "ov-gurken", "ov-raetkeinkaese", "ov-hydrated"}
Vsorted = sorted(V, key=lambda c: c["tl_in"])
bleed_report = []
for o in OV:
    if o.get("id") not in ANTIBLEED:
        continue
    o_start = o["tl_in"]
    host = None
    for c in Vsorted:
        if c["tl_in"] <= o_start + 1e-6:
            host = c
    if host is None:
        continue
    host_end = host["tl_in"] + clip_dur(host)
    max_dur = round(host_end - 0.1 - o_start, 4)
    if max_dur < o["dur"] - 0.05 and max_dur >= 1.6:
        bleed_report.append(f"{o['id']}: dur {o['dur']} -> {max_dur} (Host {host['id']})")
        o["dur"] = max_dur
    elif max_dur < 1.6:
        bleed_report.append(f"{o['id']}: RESTUEBERHANG, Host {host['id']} zu kurz "
                            f"(max_dur {max_dur}) — an Preview pruefen")

# ---------------------------------------------------------------------------
# 6) Audio — WIMM (music-03) muss bis nah ans neue Filmende reichen (v092 wieder rein hat
# den Film um ~1,4 s verlaengert, WIMM-Dauer war noch auf den alten video_end berechnet).
amap = {a.get("id"): a for a in AU}
wimm = amap.get("music-03-wimm")
if wimm:
    wimm["dur"] = round(video_end - wimm["tl_in"] - 0.9, 3)

# ---------------------------------------------------------------------------
tl["duration"] = video_end
tl["tracks"]["video"] = V
tl["tracks"]["overlay"] = sorted(OV, key=lambda c: c["tl_in"])
tl["tracks"]["audio"] = AU
TL_PATH.write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")

print(f"timeline.json geschrieben. Dauer {video_end:.2f}s "
      f"({int(video_end // 60)}:{video_end % 60:05.2f}), "
      f"video {len(V)} / overlay {len(OV)} / audio {len(AU)}")
print(f"  v092 (IMG_1543) tl_in={new_tl['v092']:.2f}  dur={clip_dur(by_id['v092']):.2f}")
print(f"  ov-hydrated tl_in={oh['tl_in']:.2f} dur={oh['dur']:.2f}" if oh else "  ov-hydrated fehlt!")
print(f"  ov-raetkeinkaese dur={ork['dur']:.2f}" if ork else "  ov-raetkeinkaese fehlt!")
print(f"  music-03-wimm dur={wimm['dur']:.2f} -> Ende {wimm['tl_in']+wimm['dur']:.2f}"
      f" (video_end {video_end:.2f})" if wimm else "  music-03-wimm fehlt!")
if bleed_report:
    print("  Anti-Bleed-Klemme:")
    for r in bleed_report:
        print("   ", r)
else:
    print("  Anti-Bleed: nichts zu klemmen")

bt = BRIEF_PATH.read_text()
bt2 = _re.sub(r"target_duration_s:\s*[0-9.]+", f"target_duration_s: {video_end:.1f}", bt)
if bt2 != bt:
    BRIEF_PATH.write_text(bt2)
    print(f"brief.yaml target_duration_s -> {video_end:.1f}")
