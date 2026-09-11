"""Runde-6-Feintuning von `exports/JGA/timeline.json` (editorial-notes-round6.md).

Transformiert die Runde-5-Timeline und schreibt zurueck nach `timeline.json`.

Kernpunkte:
* **Akt-1 -> Akt-2-Stille killen:** `music-01` laeuft bis knapp in den Akt-2-Anfang, `music-02`
  (Miserlou) setzt ~0,5 s vor dem `v069`-Cut ein -> kein stiller Spalt mehr. Dafuer werden
  `v007` (~0:23) und `v022` (~1:11) gestrichen (Christian: "5 Sekunden zu viel Zeit").
* **Kein Text ragt ins naechste Bild:** Host-Foto der genannten Overlays waechst, textfreie
  Nachbarfotos werden gekuerzt (Christian: "wo kein Text ist, ein bisschen schneller").
  Betroffen: `ov-crewupdate`, `ov-token`, `ov-natuerlich`, `ov-weiterziehen`, Gurken-Cluster.
* Intro-Karte `v001` +2,0 s. Schwarzblende `v160` +1,5 s (Musik danach). `ov-hydrated` /
  `ov-mok-detektor` -> nur PNG (party-fx-recipe.py Runde 6).

Aufruf:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/round6-timeline.py
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
# 2) Video: Streichungen + Dauern.
by_id = {c["id"]: c for c in V}


def set_dur(cid: str, seconds: float) -> None:
    c = by_id[cid]
    c["src_out"] = round(c["src_in"] + seconds * c.get("speed", 1.0), 4)


def trim_head(cid: str, seconds: float) -> None:
    """Video vorne kuerzen (src_in +): der Clip startet spaeter im Quellmaterial."""
    c = by_id[cid]
    c["src_in"] = round(c["src_in"] + seconds * c.get("speed", 1.0), 4)


DROP = {"v007", "v022"}
V = [c for c in V if c["id"] not in DROP]
by_id = {c["id"]: c for c in V}

# Intro-Karte laenger
set_dur("v001", clip_dur(by_id["v001"]) + 2.0)

# --- Text darf nicht ins naechste Bild ragen: Host waechst, textfreie Nachbarn schrumpfen ---
# ov-crewupdate (dur 3.5) auf v058
set_dur("v058", 3.9)
set_dur("v059", 1.9)
set_dur("v060", 1.7)
# ov-token (dur 3.0) auf v110
set_dur("v110", 3.5)
set_dur("v111", 1.0)
set_dur("v112", 1.5)
# ov-natuerlich auf v145 (Video, Asset-Dauer 185 s -> reichlich Reserve): hinten strecken
set_dur("v145", clip_dur(by_id["v145"]) + 1.8)
set_dur("v138", 1.0)
set_dur("v144", 1.2)  # Video: 1.5 -> 1.2 (Kopf), macht Platz
# ov-weiterziehen auf v153 (Foto vor dem Taxi-Video v154)
set_dur("v153", 3.6)
trim_head("v154", 1.6)   # Taxi-Video vorne kuerzen
set_dur("v152", 1.3)
# Gurken-Cluster: v159 (gurken + raetkeinkaese) und v158 (ich war es nicht) laenger
set_dur("v159", 4.3)
set_dur("v158", 3.0)
set_dur("v156", 1.5)
set_dur("v157", 1.9)
# Schwarzblende vor WIMM laenger
set_dur("v160", 3.7)

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
# 5) Overlay-Feintuning Runde 6 + Anti-Bleed-Klemme.
def get_ov(name: str) -> dict | None:
    for o in OV:
        if o.get("id") == name or o.get("png", "").endswith(name + ".png"):
            return o
    return None


og = get_ov("ov-gurken")
if og:
    og["dur"] = 4.0
ork = get_ov("ov-raetkeinkaese")
if og and ork:
    ork["tl_in"] = round(og["tl_in"] + 1.4, 4)
    ork["dur"] = 2.4
oin = get_ov("ov-ichwaresnicht")
if oin:
    oin["dur"] = 2.2
on = get_ov("ov-natuerlich")
if on:
    on["dur"] = 3.0
ow = get_ov("ov-weiterziehen")
if ow and "v153" in new_tl:
    ow["tl_in"] = round(new_tl["v153"] + 0.2, 4)
    ow["dur"] = 2.6

# Anti-Bleed-Sicherung — NUR die von Christian geruegten Lese-Texte, und nur KUERZEN
# (Host wurde oben schon gestreckt; das hier faengt Restueberhang ab). Nie unter 1,6 s.
# ov-wimm ist ausdruecklich ausgenommen (darf ueber zwei Fotos laufen).
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
# 6) Audio — Stille zwischen Akt 1 und Akt 2 schliessen.
amap = {a.get("id"): a for a in AU}
v069_tl = new_tl["v069"]
v160_tl = new_tl["v160"]

cl = amap.get("music-01-cltheme")
if cl:
    cl["tl_in"] = 0.0
    cl["src_in"] = 0.0
    cl["dur"] = round(min(181.4, v069_tl + 1.0), 3)   # laeuft ~1 s in Akt 2 hinein
    cl["fade_in_s"] = 0.6
    cl["fade_out_s"] = 2.5

mis = amap.get("music-02-miserlou")
if mis:
    mis["tl_in"] = round(v069_tl - 0.5, 3)            # setzt 0,5 s vor dem v069-Cut ein
    mis["src_in"] = 0.0
    mis["fade_in_s"] = 1.5
    mis["dur"] = round(v160_tl - (v069_tl - 0.5) - 0.2, 3)
    mis["fade_out_s"] = 2.0

wimm = amap.get("music-03-wimm")
if wimm:
    wimm["tl_in"] = round(v160_tl + 1.0, 3)           # ~1 s in die (laengere) Schwarzblende
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

print(f"timeline.json geschrieben. Dauer {video_end:.2f}s "
      f"({int(video_end // 60)}:{video_end % 60:05.2f}), "
      f"video {len(V)} / overlay {len(OV)} / audio {len(AU)}")
print(f"  v001 dur    = {clip_dur(by_id['v001']):.2f}s")
print(f"  v069 tl_in  = {v069_tl:.2f}s  ({int(v069_tl // 60)}:{v069_tl % 60:05.2f})")
print(f"  music-01 end= {cl['tl_in'] + cl['dur']:.2f}s  |  music-02 start = {mis['tl_in']:.2f}s"
      f"  -> Ueberlappung {cl['tl_in'] + cl['dur'] - mis['tl_in']:.2f}s (kein Loch)")
print(f"  v160 tl_in  = {v160_tl:.2f}s  dur {clip_dur(by_id['v160']):.2f}  "
      f"music-02 end {mis['tl_in'] + mis['dur']:.2f}  music-03 start {wimm['tl_in']:.2f}")
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
