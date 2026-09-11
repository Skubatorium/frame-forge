"""Runde-7-Feintuning (final) von `exports/JGA/timeline.json` (editorial-notes-round7.md).

Transformiert die Runde-6-Timeline und schreibt zurueck nach `timeline.json`.

Kernpunkte:
* Intro-Schwarz `v000` +1,0 s.
* Ken-Burns-Diversifizierung: jeder 4. "echte" Zoom-Effekt (from-zoom != to-zoom) wird auf
  reinen diagonalen Pan (Zoom konstant) umgestellt -> bricht das sture Rein/Raus-Muster auf.
* `v092` (3:51, Zungen-Nahaufnahme, "doppelt gemoppelt") streichen.
* Akt-1->Akt-2-Uebergang: Kurskorrektur ggue. Runde 6 -- statt 3-s-Crossfade jetzt eine kurze
  Schwarzblende (~1,5 s) zwischen `v057` und `v069`, `music-01` endet dort, `music-02` startet
  exakt mit `v069` -> 1,0-1,5 s echte Stille dazwischen (bewusste Trennung statt Verschmelzung).
* `ov-weiterziehen` von `v153` auf `v152` umgehaengt (das eigentliche "zwei Personen"-Bild),
  Standzeit hoch; Taxi-Video `v154` danach deutlich kuerzer.
* `ov-gurken` Text gekuerzt (party-fx-recipe.py) -> Standzeit runter.

Aufruf:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/round7-timeline.py
"""
from __future__ import annotations

import json
import re as _re
from pathlib import Path

ROOT = Path("projects/michael-jga-2026")
TL_PATH = ROOT / "exports" / "JGA" / "timeline.json"
BRIEF_PATH = ROOT / "exports" / "JGA" / "brief.yaml"

CARD_ASSETS = {"generated-black", "jga-intro-card", "jga-outro-card"}
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
# 2) Video: Streichung, Dauern, neue Schwarzblende einfuegen.
by_id = {c["id"]: c for c in V}


def set_dur(cid: str, seconds: float) -> None:
    c = by_id[cid]
    c["src_out"] = round(c["src_in"] + seconds * c.get("speed", 1.0), 4)


def trim_head(cid: str, seconds: float) -> None:
    c = by_id[cid]
    c["src_in"] = round(c["src_in"] + seconds * c.get("speed", 1.0), 4)


DROP = {"v092"}
V = [c for c in V if c["id"] not in DROP]
by_id = {c["id"]: c for c in V}

# Intro-Schwarz laenger, bevor die Titelkarte kommt.
set_dur("v000", clip_dur(by_id["v000"]) + 1.0)

# --- Akt-1->Akt-2: kurze Schwarzblende statt Crossfade-Ueberlapp ---
BLACK_DUR = 1.5
black = {
    "id": "v057b", "asset": "generated-black", "src_in": 0.0, "src_out": BLACK_DUR,
    "tl_in": 0.0, "speed": 1.0,
    "transition_in": {"type": "fade", "dur": 0.5, "hold": 0.0},
    "effects": [], "note": "R7: kurze Trennung Akt 1/Akt 2 statt Crossfade-Ueberlapp",
    "intentional_repeat": True,
}
i057 = next(i for i, c in enumerate(V) if c["id"] == "v057")
V.insert(i057 + 1, black)
by_id["v057b"] = black

# --- ov-weiterziehen gehoert auf v152 (die "zwei Personen"-Aufnahme), nicht v153 (Auto-POV) ---
set_dur("v152", 3.4)      # war 1.3 -- Host fuer den Text
set_dur("v153", 1.8)      # war 3.6 -- traegt keinen Text mehr, zurueck auf Verbindungslaenge
trim_head("v154", 0.8)    # Taxi-Video zusaetzlich vorne kuerzen (R6 hatte schon 1.6 s getrimmt)

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
# 5) Overlay-Feintuning Runde 7 + Anti-Bleed-Klemme.
def get_ov(name: str) -> dict | None:
    for o in OV:
        if o.get("id") == name or o.get("png", "").endswith(name + ".png"):
            return o
    return None


og = get_ov("ov-gurken")
if og:
    og["dur"] = 2.4   # Text gekuerzt (party-fx-recipe.py Runde 7) -> kuerzer stehen

ow = get_ov("ov-weiterziehen")
if ow and "v152" in new_tl:
    ow["tl_in"] = round(new_tl["v152"] + 0.15, 4)
    ow["dur"] = 3.0

# Anti-Bleed-Sicherung — Lese-Texte, nur KUERZEN, nie unter 1,6 s.
ANTIBLEED = {"ov-crewupdate", "ov-token", "ov-natuerlich", "ov-weiterziehen",
             "ov-gurken", "ov-raetkeinkaese", "ov-ichwaresnicht"}
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
# 6) Ken-Burns-Diversifizierung: jeder 4. "echte" Zoom-Effekt -> reiner diagonaler Pan.
kb_clips = []
for c in Vsorted:
    for eff in c.get("effects", []):
        if eff.get("type") == "kenburns":
            fz, tz = eff["from"][2], eff["to"][2]
            if abs(fz - tz) > 0.005:   # "echter" Zoom-Effekt (kein Near-static-Set)
                kb_clips.append((c["id"], eff))

kb_converted = []
for idx, (cid, eff) in enumerate(kb_clips):
    if idx % 4 != 0:
        continue
    z = round(min(eff["from"][2], eff["to"][2]), 4)   # kleinerer Zoom = Basis, kein Sprung
    sign_x = 1.0 if (idx // 4) % 2 == 0 else -1.0
    sign_y = 1.0 if (idx // 4) % 3 == 0 else -1.0
    px, py = round(0.026 * sign_x, 4), round(0.017 * sign_y, 4)
    eff["from"] = [0.0, 0.0, z]
    eff["to"] = [px, py, z]
    eff["ease"] = "linear"
    kb_converted.append(cid)

# ---------------------------------------------------------------------------
# 7) Audio — Akt-1/Akt-2: kurze Schwarzblende statt Crossfade, 1-1,5 s echte Stille.
amap = {a.get("id"): a for a in AU}
v069_tl = new_tl["v069"]
black_tl = new_tl["v057b"]
v160_tl = new_tl["v160"]

cl = amap.get("music-01-cltheme")
if cl:
    cl["tl_in"] = 0.0
    cl["src_in"] = 0.0
    cl["dur"] = round(black_tl, 3)          # endet an der neuen Schwarzblende
    cl["fade_in_s"] = 0.6
    cl["fade_out_s"] = 1.0

mis = amap.get("music-02-miserlou")
if mis:
    mis["tl_in"] = round(v069_tl, 3)        # startet exakt mit dem Akt-2-Bild, kein Vorlauf
    mis["src_in"] = 0.0
    mis["fade_in_s"] = 1.0
    mis["dur"] = round(v160_tl - v069_tl - 0.2, 3)
    mis["fade_out_s"] = 2.0

wimm = amap.get("music-03-wimm")
if wimm:
    wimm["tl_in"] = round(v160_tl + 1.0, 3)
    wimm["src_in"] = 17.0
    wimm["fade_in_s"] = 1.5
    wimm["dur"] = round(video_end - (v160_tl + 1.0) - 0.9, 3)
    wimm["fade_out_s"] = 6.0

# ---------------------------------------------------------------------------
tl["duration"] = video_end
tl["tracks"]["video"] = V
tl["tracks"]["overlay"] = sorted(OV, key=lambda c: c["tl_in"])
tl["tracks"]["audio"] = AU
TL_PATH.write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")

gap = mis["tl_in"] - (cl["tl_in"] + cl["dur"])
print(f"timeline.json geschrieben. Dauer {video_end:.2f}s "
      f"({int(video_end // 60)}:{video_end % 60:05.2f}), "
      f"video {len(V)} / overlay {len(OV)} / audio {len(AU)}")
print(f"  v000 dur     = {clip_dur(by_id['v000']):.2f}s")
print(f"  v057b (Black) tl_in={black_tl:.2f} dur={BLACK_DUR}")
print(f"  v069 tl_in   = {v069_tl:.2f}s  ({int(v069_tl // 60)}:{v069_tl % 60:05.2f})")
print(f"  music-01 end = {cl['tl_in'] + cl['dur']:.2f}s  |  music-02 start = {mis['tl_in']:.2f}s"
      f"  -> Stille {gap:.2f}s")
print(f"  v152 dur={clip_dur(by_id['v152']):.2f}  v153 dur={clip_dur(by_id['v153']):.2f}  "
      f"v154 dur={clip_dur(by_id['v154']):.2f}")
print(f"  KB diversifiziert: {len(kb_converted)}/{len(kb_clips)} echte Zoom-Effekte -> "
      f"reiner diagonaler Pan")
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
