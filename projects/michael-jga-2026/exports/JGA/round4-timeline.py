"""Runde-4-Umbau von `exports/JGA/timeline.json` (editorial-notes-round4.md).

Transformiert die Runde-3-Timeline in-place-artig (schreibt zurueck nach timeline.json):

R4-T4 (Bild):
* Ken Burns pro Foto neu: EINE Aktion (rein ODER raus), EINE Richtung, kleine Amplitude,
  Mix aus `ease:"linear"` (konstant) und `ease:"in"`; Richtung wechselt, nie 3x gleich.
  `v040` unangetastet (Christian-Referenz), `v021`/`v036`/`v037` erzwungen Zoom RAUS,
  `v030` Schwenk nach oben. Fotos ohne KB bekommen einen Mini-Zoom.
* `fit:"blur"` auf ALLEN Foto-Clips (4:3 + Hochkant) — killt "Kopf angeschnitten" +
  schwarze Balken global. Videos bleiben unangetastet (Hochkant-Videos hatten schon blur).
* Streichungen: v089 (Dach-Doppelung ~3:53), v094 (2. Bild nach ov-christoph), v106 (Downtown).
* Swaps (tl-Position): v041b<->v043, v044<->v045, v158<->v159.
* v069 (IMG_1460.MOV) + oton-01 an den Titelwechsel ~3:03 vorziehen.

R4-T2-Anschluss (Overlays):
* ov-sulemann -> ov-sulemann-a (o.l.) + ov-sulemann-b (u.r.).
* ov-fx-sterne raus. ov-mok-detektor neu (~2:48). ov-wimm auf Bild ~6:17. ov-weiterziehen
  auf Bild ~5:52 (Mitte). ov-crewupdate ~3:04. ov-hydrated Jitter ab Start.

R4-T5 (Audio):
* music-01 (CL): fade_in 2.0->0.6 (erster Ausschlag auf Bild-Einblenden), laeuft bis ~3:01.
* music-02 (Miserlou): tl_in ~183 (3:03), ~1,6 s Stille davor, dur so dass ~6:15 aus.
* music-03 (WIMM): weich rein ~6:04, Outro +2,5 s laenger; Timeline-Dauer + brief.yaml nach.

Aufruf:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/round4-timeline.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("projects/michael-jga-2026")
TL_PATH = ROOT / "exports" / "JGA" / "timeline.json"
BRIEF_PATH = ROOT / "exports" / "JGA" / "brief.yaml"

CARD_ASSETS = {"generated-black", "jga-intro-card", "jga-outro-card"}

# ---------------------------------------------------------------------------
tl = json.loads(TL_PATH.read_text())
V = sorted(tl["tracks"]["video"], key=lambda c: c["tl_in"])
OV = sorted(tl["tracks"]["overlay"], key=lambda c: c["tl_in"])
AU = tl["tracks"]["audio"]

# Asset -> kind (photo/video) aus assets.json
assets = {a["id"]: a for a in json.loads((ROOT / "index" / "assets.json").read_text())}


def is_photo(clip: dict) -> bool:
    if clip["asset"] in CARD_ASSETS:
        return False
    a = assets.get(clip["asset"])
    if a is None:  # generierte/lose jpgs ohne Index -> wie Foto behandeln (Standbild)
        return not clip["asset"].startswith("generated")
    return a.get("kind") == "photo"


def clip_dur(clip: dict) -> float:
    return (clip["src_out"] - clip["src_in"]) / clip.get("speed", 1.0)


# ---------------------------------------------------------------------------
# 1) Overlays + Audio an ihren Video-Anker binden (VOR jeder Video-Aenderung).
def anchor_of(t: float) -> tuple[str, float]:
    """(video-clip-id, offset) fuer einen Zeitpunkt t."""
    cur = V[0]
    for c in V:
        if c["tl_in"] <= t + 1e-6:
            cur = c
        else:
            break
    return cur["id"], round(t - cur["tl_in"], 4)


anchors: dict[int, tuple[str, float]] = {}
for o in OV:
    anchors[id(o)] = anchor_of(o["tl_in"])
# nur die Cast-SFX + otons an Video ankern; Musik setzen wir explizit.
for s in AU:
    sid = s.get("id", "")
    if sid.startswith("sfx-cast") or sid.startswith("oton-"):
        anchors[id(s)] = anchor_of(s["tl_in"])

# ---------------------------------------------------------------------------
# 2) Video: Streichungen + Swaps + Move.
DROP = {"v089", "v094", "v106"}
V = [c for c in V if c["id"] not in DROP]

by_id = {c["id"]: c for c in V}


def swap_positions(a: str, b: str) -> None:
    """Tauscht zwei Clips in der Reihenfolge (ueber ihre Listen-Indizes)."""
    ia = next(i for i, c in enumerate(V) if c["id"] == a)
    ib = next(i for i, c in enumerate(V) if c["id"] == b)
    V[ia], V[ib] = V[ib], V[ia]


# Hinweis: v158/v159 NICHT tauschen — Christians Ziel-Reihenfolge ist v158 (Christoph,
# "Ich war es nicht") VOR v159 (2. Gurkenbild, Gurken-Text) = die Runde-3-Reihenfolge.
for a, b in [("v041b", "v043"), ("v044", "v045")]:
    if a in by_id and b in by_id:
        swap_positions(a, b)

# v069 (+ Anker-Umzug von oton-01) direkt hinter v057 (Pommes) einsortieren.
if "v069" in by_id:
    V.remove(by_id["v069"])
    idx = next(i for i, c in enumerate(V) if c["id"] == "v057")
    V.insert(idx + 1, by_id["v069"])

# ---------------------------------------------------------------------------
# 3) Ken Burns neu.  Richtungen: 8er-Rose, nicht 3x gleich hintereinander.
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
PAN = 0.030          # Amplitude Pan (Bruchteil Bildkante)
PAN_MINI = 0.018     # fuer vorher statische Fotos
ZD = 0.075           # Zoom-Delta regulaer
ZD_MINI = 0.045
Z_LO = 1.035         # Basiszoom, damit Pan immer Schwenkraum hat


def norm(d):
    import math
    x, y = d
    m = math.hypot(x, y) or 1.0
    return x / m, y / m


FORCE_OUT = {"v021", "v036", "v037"}
FORCE_UP = {"v030"}
SKIP = {"v040"}

photo_idx = 0
last_dir = None
for c in V:
    if not is_photo(c) or c["id"] in SKIP:
        continue
    had_kb = any(e.get("type") == "kenburns" for e in c.get("effects", []))
    # Richtung waehlen: rotieren, aber != last_dir
    d = DIRS[(photo_idx * 3) % len(DIRS)]
    if d == last_dir:
        d = DIRS[(photo_idx * 3 + 1) % len(DIRS)]
    last_dir = d
    ux, uy = norm(d)
    if c["id"] in FORCE_UP:
        ux, uy = 0.0, -1.0
    pan = PAN if had_kb else PAN_MINI
    zd = ZD if had_kb else ZD_MINI
    zoom_in = (photo_idx % 2 == 0)
    if c["id"] in FORCE_OUT:
        zoom_in = False
    if zoom_in:
        z0, z1 = Z_LO, Z_LO + zd
    else:
        z0, z1 = Z_LO + zd, Z_LO
    # Pan monoton in EINE Richtung: Start zentriert, Ende `pan` in Richtung d.
    frm = [0.0, 0.0, round(z0, 4)]
    to = [round(ux * pan, 4), round(uy * pan, 4), round(z1, 4)]
    ease = "in" if (photo_idx % 3 == 0) else "linear"
    kb = {"type": "kenburns", "from": frm, "to": to, "ease": ease}
    other = [e for e in c.get("effects", []) if e.get("type") != "kenburns"]
    c["effects"] = [kb, *other]
    photo_idx += 1

# ---------------------------------------------------------------------------
# 4) fit:"blur" auf allen Foto-Clips.
for c in V:
    if is_photo(c):
        c["fit"] = "blur"

# ---------------------------------------------------------------------------
# 5) Video-Track sequentiell neu auslegen (tl_in aus Dauer + Crossfade-Overlap).
XF = {"dissolve", "fade", "crossfade", "slow_dissolve"}
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

# ---------------------------------------------------------------------------
# 6) Overlays + SFX/oton via Anker neu platzieren.
#    Anker-Clip evtl. geloescht -> auf den zeitlich davor liegenden Ueberlebenden.
alive = {c["id"] for c in V}
order = [c["id"] for c in V]


def resolve_anchor(aid: str) -> str:
    if aid in alive:
        return aid
    # DROP/oton-Anker: naechster ueberlebender Clip davor in der ALTEN Reihenfolge
    old_order = ["v089", "v094", "v106"]  # nur Info; nutze einfache Heuristik
    return order[0]


for o in OV:
    aid, off = anchors[id(o)]
    if aid not in alive:
        aid = {"v089": "v088", "v094": "v093", "v106": "v105"}.get(aid, aid)
    base = new_tl.get(aid, 0.0)
    o["tl_in"] = round(base + off, 4)

for s in AU:
    if id(s) in anchors:
        aid, off = anchors[id(s)]
        if aid not in alive:
            aid = {"v089": "v088", "v094": "v093", "v106": "v105"}.get(aid, aid)
        # oton-01 haengt an v069 (verschoben) -> folgt automatisch mit
        s["tl_in"] = round(new_tl.get(aid, 0.0) + off, 4)

# ---------------------------------------------------------------------------
# 7) Overlay-Track: Splits / Neu / Weg / Retime.
OV = [o for o in OV if "ov-fx-sterne" not in o["png"]]

sule = next((o for o in OV if o["png"].endswith("ov-sulemann.png")), None)
if sule is not None:
    OV.remove(sule)
    a = dict(sule); a["id"] = "ov-sulemann-a"; a["png"] = "overlays/ov-sulemann-a.png"
    a["placement"] = "top-left"
    b = dict(sule); b["id"] = "ov-sulemann-b"; b["png"] = "overlays/ov-sulemann-b.png"
    b["placement"] = "bottom-right"
    OV += [a, b]

# ov-mok-detektor auf v052 (IMG_1423, ~2:48), 2,0 s
v052 = new_tl.get("v052")
if v052 is not None:
    OV.append({
        "id": "ov-mok-detektor", "png": "overlays/ov-mok-detektor.png",
        "tl_in": round(v052 + 1.0, 4), "dur": 2.0,
        "anim": {"fade_in_s": "0.25", "fade_out_s": "0.35"},
        "placement": "top-left", "text": "MOK Detektor",
    })


def get_ov(name: str):
    return next((o for o in OV if o["png"].endswith(name)), None)


# ov-crewupdate -> rechte Seite, auf erstes Akt-2-Bild (~3:04)
o = get_ov("ov-crewupdate.png")
if o:
    v058 = new_tl.get("v058")
    if v058 is not None:
        o["tl_in"] = round(v058 + 0.1, 4)
    o["dur"] = 2.2
    o["placement"] = "top-right"

# ov-weiterziehen -> Bild ~5:52 (v154 Taxi-Nacht), Mitte/unten
o = get_ov("ov-weiterziehen.png")
if o:
    anchor = new_tl.get("v154") or new_tl.get("v153")
    if anchor is not None:
        o["tl_in"] = round(anchor + 0.4, 4)
    o["dur"] = 2.2
    o["placement"] = "bottom"

# Gurken-Ende: feste Reihenfolge der 4 Overlays (v155 WTF ... v158 ichwaresnicht ... v159 gurken)
_v155, _v158, _v159 = new_tl.get("v155"), new_tl.get("v158"), new_tl.get("v159")
o = get_ov("ov-wtf.png")
if o and _v155 is not None:
    o["tl_in"] = round(_v155 + 0.15, 4); o["dur"] = 2.1; o["placement"] = "top-left"
o = get_ov("ov-ichwaresnicht.png")
if o and _v158 is not None:
    o["tl_in"] = round(_v158 + 0.2, 4); o["dur"] = 1.8; o["placement"] = "bottom-right"
o = get_ov("ov-gurken.png")
if o and _v159 is not None:
    o["tl_in"] = round(_v159 + 0.2, 4); o["dur"] = 2.6; o["placement"] = "bottom-left"
o = get_ov("ov-raetkeinkaese.png")
if o and _v159 is not None:
    o["tl_in"] = round(_v159 + 0.5, 4); o["dur"] = 2.0; o["placement"] = "top-right"

# ov-wimm -> Bild ~6:17 (v162)
o = get_ov("ov-wimm.png")
if o:
    v162 = new_tl.get("v162")
    if v162 is not None:
        o["tl_in"] = round(v162 + 1.2, 4)
    o["dur"] = 4.5
    o["placement"] = "top-left"

# ov-hydrated -> Jitter ab Start (drift sine, kurze Periode), rechts
o = get_ov("ov-hydrated.png")
if o:
    o["placement"] = "right"
    o["anim"] = {
        "fade_in_s": "0.2", "fade_out_s": "0.3",
        "slide_in_s": "0.15",
        "drift_px": "9", "drift_py": "7",
        "drift_mode": "sine", "drift_period_s": "0.45",
    }

# ov-letsgo -> etwas laenger stehen
o = get_ov("ov-letsgo.png")
if o:
    o["dur"] = max(o.get("dur", 3.0), 3.4)
    o["placement"] = "bottom-right"

# ---------------------------------------------------------------------------
# 8) Audio.
OUTRO_EXTRA = 2.5
amap = {a.get("id"): a for a in AU}

cl = amap.get("music-01-cltheme")
if cl:
    cl["fade_in_s"] = 0.6
    cl["dur"] = 181.4          # natuerliches Ende ~3:01.4
    cl["fade_out_s"] = 2.0

mis = amap.get("music-02-miserlou")
if mis:
    mis["tl_in"] = 183.0       # 3:03 — neuer Titel exakt hier
    mis["fade_in_s"] = 0.3
    mis["dur"] = 192.0         # Ende ~375 s (6:15)
    mis["fade_out_s"] = 6.0

wimm = amap.get("music-03-wimm")
if wimm:
    wimm["tl_in"] = 366.0      # ~6:06 weich rein
    wimm["fade_in_s"] = 4.0
    wimm["dur"] = round(video_end + OUTRO_EXTRA - 366.0, 3)
    wimm["fade_out_s"] = 10.0

# ---------------------------------------------------------------------------
# 9) Outro-Karte + Timeline-Dauer verlaengern.
outro = next((c for c in V if c["asset"] == "jga-outro-card"), None)
blk = None
if outro is not None:
    # letzten schwarzen Clip nach der Outro-Karte finden
    oi = V.index(outro)
    for c in V[oi + 1:]:
        if c["asset"] == "generated-black":
            blk = c
            break
    outro["src_out"] = round(outro["src_out"] + OUTRO_EXTRA, 4)

# tl_in ab Outro neu ziehen (Outro-Karte wurde laenger)
t = outro["tl_in"] if outro else video_end
if outro:
    t = outro["tl_in"]
    for c in V[V.index(outro):]:
        ti = c.get("transition_in") or {}
        ov = ti.get("dur", 0.0) if ti.get("type") in XF else 0.0
        c["tl_in"] = round(t - ov, 4) if c is not outro else round(t, 4)
        t = c["tl_in"] + clip_dur(c)
video_end = round(t, 4)

tl["duration"] = video_end
tl["tracks"]["video"] = V
tl["tracks"]["overlay"] = sorted(OV, key=lambda c: c["tl_in"])

TL_PATH.write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")
print(f"timeline.json geschrieben. Dauer {video_end:.2f}s  "
      f"({int(video_end//60)}:{video_end%60:05.2f}), "
      f"video {len(V)} / overlay {len(OV)} / audio {len(AU)}")

# brief.yaml target_duration_s nachziehen (einfache Textersetzung)
bt = BRIEF_PATH.read_text()
import re as _re
bt2 = _re.sub(r"target_duration_s:\s*[0-9.]+", f"target_duration_s: {video_end:.1f}", bt)
if bt2 != bt:
    BRIEF_PATH.write_text(bt2)
    print(f"brief.yaml target_duration_s -> {video_end:.1f}")
