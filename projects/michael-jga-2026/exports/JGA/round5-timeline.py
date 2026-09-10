"""Runde-5-Umbau von `exports/JGA/timeline.json` (editorial-notes-round5.md).

Transformiert die Runde-4-Timeline und schreibt zurueck nach `timeline.json`.

Video:
* `v003` (erstes Bild) auf 8,0 s (doppelt). `v008` (0:21) streichen. `v004`-`v007` je 0,2 s
  trimmen, damit der 30-Sekunden-Anker (`v011`) ~30,0 s landet.
* Akt-1-Tail (`v053`-`v057`) leicht schrumpfen, damit `v069` frueh genug fuer <=1 s Stille
  vor dem 3:03-Cut liegt.
* Reihenfolge: Schoko-Block `v041b->v041->v043->v044->v045->v046`; Swap `v097<->v100`;
  Swap `v157<->v156`; Swap `v158<->v159`; `v117` direkt vor `v122` (Cast).
* Ken Burns: Near-static-Set (Mini-Zoom, kein Pan); `v039` -> Zoom raus; nie zwei Fotos
  hintereinander beide Zoom-raus; `v040` unangetastet.
* Outro: `jga-outro-card` +1,5 s; neue schwarze Schluss-Karte `v172` (+`ov-thanks`), der
  Film endet dort (nicht auf Schwarz).

Overlays: Standzeiten/Placement/Anker laut editorial-notes-round5.md §5. Speedlines bei 5:15
und 5:21 raus, neu auf `v143` (5:29). Neu `ov-thanks`.

Audio: `music-01` bis ~0,8 s vor 3:03; `music-02` (Miserlou) Stopp kurz vor der 6:03-
Schwarzblende (`v160`); `music-03` (WIMM) setzt im Schwarz ein (~1 s vor `v161`).

Aufruf:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/round5-timeline.py
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
assets = {a["id"]: a for a in json.loads((ROOT / "index" / "assets.json").read_text())}

ORIG_ORDER = [c["id"] for c in V]


def is_photo(clip: dict) -> bool:
    if clip["asset"] in CARD_ASSETS:
        return False
    a = assets.get(clip["asset"])
    if a is None:
        return not clip["asset"].startswith("generated")
    return a.get("kind") == "photo"


def clip_dur(clip: dict) -> float:
    return (clip["src_out"] - clip["src_in"]) / clip.get("speed", 1.0)


# ---------------------------------------------------------------------------
# 1) Overlays + Cast-SFX + otons an ihren Video-Anker binden (VOR jeder Video-Aenderung).
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
    sid = s.get("id", "")
    if sid.startswith(("sfx-cast", "oton-")):
        anchors[id(s)] = anchor_of(s["tl_in"])

# ---------------------------------------------------------------------------
# 2) Video: Streichung + Dauern + Reihenfolge.
V = [c for c in V if c["id"] != "v008"]
by_id = {c["id"]: c for c in V}


def set_src_dur(cid: str, seconds: float) -> None:
    c = by_id[cid]
    c["src_out"] = round(c["src_in"] + seconds * c.get("speed", 1.0), 4)


def trim_src(cid: str, cut_s: float) -> None:
    c = by_id[cid]
    c["src_out"] = round(c["src_out"] - cut_s * c.get("speed", 1.0), 4)


# erstes Bild doppelt
set_src_dur("v003", 8.0)
# 30-Sekunden-Anker halten: v003 +4,0 s / v008 -3,2 s -> ~0,8 s zu viel -> v004..v007 kuerzen
for cid in ("v004", "v005", "v006", "v007"):
    trim_src(cid, 0.2)
# Akt-1-Tail schrumpfen (~1,3 s), damit v069 frueh genug liegt
for cid, cut in (("v053", 0.3), ("v054", 0.3), ("v055", 0.3), ("v056", 0.2), ("v057", 0.2)):
    trim_src(cid, cut)
# Outro-Karte laenger
by_id["v170"]["src_out"] = round(by_id["v170"]["src_out"] + 1.5, 4)


def set_order(ids: list[str]) -> None:
    """Die genannten Clips belegen — in genau dieser Reihenfolge — die sortierte Menge ihrer
    aktuellen Listenplaetze. Fuer Swaps/Umsortierungen innerhalb eines zusammenhaengenden
    Laufs."""
    slots = sorted(V.index(by_id[i]) for i in ids)
    picked = [by_id[i] for i in ids]
    for slot, clip in zip(slots, picked):
        V[slot] = clip


set_order(["v041b", "v041", "v043", "v044", "v045", "v046"])  # Schoko-Block
set_order(["v100", "v097"])                                   # 4:02 <-> 4:05
set_order(["v156", "v157"])                                   # 5:56 <-> 5:57
set_order(["v159", "v158"])                                   # Gurkenbild vor "Ich war es nicht"
set_order(["v118", "v119", "v120", "v117", "v122"])           # v117 vor den Cast

# ---------------------------------------------------------------------------
# 3) Ken Burns: Near-static + v039 + kein doppeltes Zoom-raus.
NEAR_STATIC = {"v006", "v013", "v020", "v028", "v029", "v034", "v049", "v135", "v150", "v167"}
KEEP = {"v040"}  # Christian-Referenz, unangetastet


def kb_of(c: dict) -> dict | None:
    return next((e for e in c.get("effects", []) if e.get("type") == "kenburns"), None)


for c in V:
    if c["id"] in NEAR_STATIC and is_photo(c):
        kb = {"type": "kenburns", "from": [0.0, 0.0, 1.0], "to": [0.0, 0.0, 1.022],
              "ease": "linear"}
        c["effects"] = [kb, *[e for e in c.get("effects", []) if e.get("type") != "kenburns"]]

# v039: Zoom raus + minimaler Schwenk nach rechts
_c = by_id["v039"]
_c["effects"] = [
    {"type": "kenburns", "from": [0.0, 0.0, 1.10], "to": [0.022, 0.0, 1.035], "ease": "in"},
    *[e for e in _c.get("effects", []) if e.get("type") != "kenburns"],
]

# kein doppeltes Zoom-raus in Folge
prev_out: bool | None = None
for c in V:
    if not is_photo(c):
        prev_out = None
        continue
    if c["id"] in KEEP:
        prev_out = None
        continue
    kb = kb_of(c)
    if kb is None:
        prev_out = None
        continue
    zf, zt = float(kb["from"][2]), float(kb["to"][2])
    is_out = zt < zf - 1e-6
    if is_out and prev_out:
        kb["from"][2], kb["to"][2] = zt, zf  # zu Zoom-rein umkehren
        is_out = False
    prev_out = is_out

# ---------------------------------------------------------------------------
# 4) Schluss-Karte v172 (schwarz) hinter v171 — Film endet hier.
v172 = {
    "id": "v172", "asset": "generated-black",
    "src_in": 0.0, "src_out": 3.6, "tl_in": 0.0,
    "intentional_repeat": True,
    "note": "Runde 5: Hintergrund fuer die Schluss-Karte ov-thanks; Film endet hier, "
            "nicht auf Schwarz.",
}
V.insert(V.index(by_id["v171"]) + 1, v172)

# ---------------------------------------------------------------------------
# 5) Video-Spur sequentiell neu auslegen.
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
    # nur v008 kann fehlen -> naechster Ueberlebender davor in der alten Reihenfolge
    j = ORIG_ORDER.index(aid) if aid in ORIG_ORDER else 0
    for k in range(j - 1, -1, -1):
        if ORIG_ORDER[k] in alive:
            return ORIG_ORDER[k]
    return next(iter(alive))


# ---------------------------------------------------------------------------
# 6) Overlays + SFX/oton generisch via Anker neu platzieren.
for o in OV:
    aid, off = anchors[id(o)]
    o["tl_in"] = round(new_tl[resolve_anchor(aid)] + off, 4)

for s in AU:
    if id(s) in anchors:
        aid, off = anchors[id(s)]
        s["tl_in"] = round(new_tl[resolve_anchor(aid)] + off, 4)

# ---------------------------------------------------------------------------
# 7) Overlay-Feintuning Runde 5.
def get_ov(needle: str) -> dict | None:
    for o in OV:
        if o.get("id") == needle or o.get("png", "").endswith(needle + ".png"):
            return o
    return None


for name, dur in (
    ("ov-sulemann-a", 4.0), ("ov-sulemann-b", 4.0), ("ov-crewupdate", 3.5),
    ("ov-token", 3.0), ("ov-lampen", 2.6), ("ov-natuerlich", 3.2), ("ov-gurken", 3.6),
):
    o = get_ov(name)
    if o:
        o["dur"] = dur

o = get_ov("ov-token")
if o:
    o["placement"] = "bottom-right"

o = get_ov("ov-hydrated")
if o:
    o["placement"] = "bottom"

# Gurkenbild-Text zuerst, dann "Red kein Kaese!" oben rechts ~1 s spaeter
og = get_ov("ov-gurken")
ork = get_ov("ov-raetkeinkaese")
if og and ork:
    ork["tl_in"] = round(og["tl_in"] + 1.0, 4)
    ork["dur"] = 2.0

# ov-weiterziehen -> Bild v153 (5:47)
o = get_ov("ov-weiterziehen")
if o and "v153" in new_tl:
    o["tl_in"] = round(new_tl["v153"] + 0.2, 4)
    o["dur"] = 2.4
    o["placement"] = "bottom"

# ov-wimm -> Bild v162, laenger (bis in v163, gemeinsamer Ausblend)
o = get_ov("ov-wimm")
if o and "v162" in new_tl:
    o["tl_in"] = round(new_tl["v162"] + 0.8, 4)
    o["dur"] = 7.0

# Speedlines: 5:15 + 5:21 raus, neu auf v143 (5:29)
OV = [o for o in OV if o.get("id") not in {"ov-fx-speedlines-v144", "ov-fx-speedlines-v139"}]
if "v143" in new_tl:
    OV.append({
        "id": "ov-fx-speedlines-v143", "png": "overlays/ov-fx-speedlines.png",
        "tl_in": round(new_tl["v143"] + 0.1, 4), "dur": 1.3,
        "anim": {"fade_in_s": "0.1", "fade_out_s": "0.3"},
        "placement": "center",
    })

# ov-thanks — Schluss-Karte auf v172, bleibt bis zum Cut stehen
OV.append({
    "id": "ov-thanks", "png": "overlays/ov-thanks.png",
    "tl_in": round(new_tl["v172"] + 0.15, 4),
    "dur": round(clip_dur(v172) - 0.15, 4),
    "anim": {"fade_in_s": "0.4", "fade_out_s": "0.0"},
    "placement": "center", "text": "THANKS FOR WATCHING",
})

# ---------------------------------------------------------------------------
# 8) Audio.
amap = {a.get("id"): a for a in AU}
v069_tl = new_tl["v069"]
v160_tl = new_tl["v160"]

cl = amap.get("music-01-cltheme")
if cl:
    cl["tl_in"] = 0.0
    cl["src_in"] = 0.0
    cl["dur"] = round(min(181.4, v069_tl - 0.8), 3)
    cl["fade_in_s"] = 0.6
    cl["fade_out_s"] = 1.5

mis = amap.get("music-02-miserlou")
if mis:
    mis["tl_in"] = round(v069_tl, 3)
    mis["src_in"] = 0.0
    mis["fade_in_s"] = 0.3
    mis["dur"] = round(v160_tl - v069_tl - 0.2, 3)   # endet knapp vor der Schwarzblende
    mis["fade_out_s"] = 2.0

wimm = amap.get("music-03-wimm")
if wimm:
    wimm["tl_in"] = round(v160_tl + 1.0, 3)          # ~1 s in die Schwarzpause, vor v161
    wimm["src_in"] = 17.0
    wimm["fade_in_s"] = 1.5
    wimm["dur"] = round(video_end - wimm["tl_in"] - 0.9, 3)
    wimm["fade_out_s"] = 6.0

# ---------------------------------------------------------------------------
tl["duration"] = video_end
tl["tracks"]["video"] = V
tl["tracks"]["overlay"] = sorted(OV, key=lambda c: c["tl_in"])
tl["tracks"]["audio"] = AU

TL_PATH.write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")
print(f"timeline.json geschrieben. Dauer {video_end:.2f}s "
      f"({int(video_end // 60)}:{video_end % 60:05.2f}), "
      f"video {len(V)} / overlay {len(OV)} / audio {len(AU)}")
print(f"  v003 dur    = {clip_dur(by_id['v003']):.2f}s")
print(f"  v011 tl_in  = {new_tl['v011']:.2f}s  (Ziel ~30,0)")
print(f"  v069 tl_in  = {v069_tl:.2f}s  (Ziel ~183 / 3:03)")
print(f"  music-01 end= {cl['tl_in'] + cl['dur']:.2f}s  (Stille bis v069: "
      f"{v069_tl - (cl['tl_in'] + cl['dur']):.2f}s)")
print(f"  v160 tl_in  = {v160_tl:.2f}s   music-02 end = {mis['tl_in'] + mis['dur']:.2f}s")
print(f"  music-03    = {wimm['tl_in']:.2f}..{wimm['tl_in'] + wimm['dur']:.2f}s  "
      f"(video_end {video_end:.2f})")

bt = BRIEF_PATH.read_text()
bt2 = _re.sub(r"target_duration_s:\s*[0-9.]+", f"target_duration_s: {video_end:.1f}", bt)
if bt2 != bt:
    BRIEF_PATH.write_text(bt2)
    print(f"brief.yaml target_duration_s -> {video_end:.1f}")
