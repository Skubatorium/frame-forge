"""Index-Statistik und Export-Datenblatt.

Reine Ableitung aus dem, was die Pipeline ohnehin geschrieben hat (`assets.json`,
`timeline.json`, `brief.yaml`, `tokens.yaml`, `beatsheet.md`) — keine Neuanalyse. Liefert
eine Uebersicht ueber den Fundus (`index_stats`), die Nutzung ueber alle Exporte
(`usage_stats`) und einen menschenlesbaren Markdown-Report pro Export (`build_report`), der
neben dem Final-Render abgelegt wird.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime

import yaml

from frameforge.index import load_assets
from frameforge.ingest import scan_media
from frameforge.project import Export, Project
from frameforge.timeline import Timeline


@dataclass
class IndexStats:
    on_disk: int | None  # Mediendateien im media_root (None = nicht erreichbar)
    indexed: int
    videos: int
    photos: int
    total_video_seconds: float
    avg_quality: dict[str, float]  # sharpness/stability/exposure (Video-Mittel)
    rating_hist: dict[int, int]  # Rating -> Anzahl
    resolutions: dict[str, int]  # "3840x2160" -> Anzahl
    codecs: dict[str, int]
    places: dict[str, int]  # gps.place -> Anzahl
    with_people: int  # Assets mit content.people == True

    @property
    def indexed_coverage(self) -> float | None:
        """Anteil der Dateien auf der Platte, die schon indiziert sind (0..1)."""
        if not self.on_disk:
            return None
        return self.indexed / self.on_disk


def index_stats(project: Project, *, scan_disk: bool = True) -> IndexStats:
    """Statistik ueber den indizierten Fundus eines Projekts."""
    assets = load_assets(project)
    videos = [a for a in assets if a.get("kind") == "video"]
    photos = [a for a in assets if a.get("kind") == "photo"]

    on_disk: int | None = None
    if scan_disk:
        try:
            on_disk = len(scan_media(project.config.media_root))
        except (FileNotFoundError, OSError):
            on_disk = None  # externe Platte nicht gemountet o.ae. — kein Fehler

    quality_keys = ("sharpness", "stability", "exposure")
    sums = {k: 0.0 for k in quality_keys}
    counts = {k: 0 for k in quality_keys}
    for a in videos:
        q = a.get("quality", {})
        for k in quality_keys:
            if k in q:
                sums[k] += float(q[k])
                counts[k] += 1
    avg_quality = {k: round(sums[k] / counts[k], 3) for k in quality_keys if counts[k]}

    resolutions = Counter()
    codecs = Counter()
    total_video_seconds = 0.0
    for a in videos:
        tech = a.get("tech", {})
        if "w" in tech and "h" in tech:
            resolutions[f"{tech['w']}x{tech['h']}"] += 1
        if "codec" in tech:
            codecs[tech["codec"]] += 1
        total_video_seconds += float(tech.get("dur", 0.0))

    rating_hist = Counter(a["rating"] for a in assets if isinstance(a.get("rating"), int))
    places = Counter(
        a["gps"]["place"] for a in assets if a.get("gps") and a["gps"].get("place")
    )
    with_people = sum(1 for a in assets if a.get("content", {}).get("people") is True)

    return IndexStats(
        on_disk=on_disk,
        indexed=len(assets),
        videos=len(videos),
        photos=len(photos),
        total_video_seconds=round(total_video_seconds, 1),
        avg_quality=avg_quality,
        rating_hist=dict(sorted(rating_hist.items())),
        resolutions=dict(resolutions.most_common()),
        codecs=dict(codecs.most_common()),
        places=dict(places.most_common()),
        with_people=with_people,
    )


def used_asset_ids(timeline: Timeline) -> set[str]:
    """Alle Asset-IDs, die eine Timeline tatsaechlich verwendet (Video + Asset-Audio)."""
    ids = {c.asset for c in timeline.tracks.video}
    ids |= {c.asset for c in timeline.tracks.audio if c.asset is not None}
    return ids


@dataclass
class UsageStats:
    total_assets: int
    per_export: dict[str, int] = field(default_factory=dict)  # export -> genutzte Assets
    used_union: set[str] = field(default_factory=set)  # ueber alle Exporte genutzt

    @property
    def union_coverage(self) -> float | None:
        if not self.total_assets:
            return None
        return len(self.used_union) / self.total_assets


def usage_stats(project: Project) -> UsageStats:
    """Wie viel des Fundus über alle Exporte hinweg (und je Export) verwendet wird."""
    total = len(load_assets(project))
    usage = UsageStats(total_assets=total)
    for name in project.list_exports():
        tl_path = project.export(name).timeline_path
        if not tl_path.exists():
            continue
        used = used_asset_ids(Timeline.load(tl_path))
        usage.per_export[name] = len(used)
        usage.used_union |= used
    return usage


def _pct(part: int, whole: int) -> str:
    return f"{(100 * part / whole):.0f} %" if whole else "—"


def build_report(project: Project, export: Export, timeline: Timeline) -> str:
    """Menschenlesbares Markdown-Datenblatt zu einem Export.

    Beschreibt Quelle, Umfang, Nutzung, Dramaturgie, Audio, Design und Technik — das, was
    beim Erstellen dieses Films tatsaechlich passiert ist. Wird neben den Final-Render gelegt.
    """
    assets = load_assets(project)
    assets_by_id = {a["id"]: a for a in assets}
    used = sorted(used_asset_ids(timeline))
    stats = index_stats(project, scan_disk=True)

    brief = (
        yaml.safe_load(export.brief_path.read_text())
        if export.brief_path.exists()
        else {}
    ) or {}
    tokens = (
        yaml.safe_load(project.design_tokens_path.read_text())
        if project.design_tokens_path.exists()
        else {}
    ) or {}

    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    w, h = timeline.resolution

    lines: list[str] = []
    lines.append(f"# Report — {project.name} / {export.name}")
    lines.append("")
    lines.append(f"*Erstellt {now}*")
    lines.append("")

    lines.append("## Quelle & Umfang")
    lines.append(f"- **Projekt:** {project.name}")
    lines.append(f"- **Quellordner (media_root):** `{project.config.media_root}`")
    on_disk = "unbekannt (nicht erreichbar)" if stats.on_disk is None else str(stats.on_disk)
    lines.append(f"- **Dateien im Quellordner:** {on_disk}")
    lines.append(
        f"- **Indiziert:** {stats.indexed} Assets ({stats.videos} Video, {stats.photos} Foto), "
        f"Rohmaterial gesamt ~{stats.total_video_seconds:.0f} s Video"
    )
    lines.append("")

    lines.append("## Verwendung in diesem Export")
    lines.append(
        f"- **Genutzte Assets:** {len(used)} von {stats.indexed} "
        f"({_pct(len(used), stats.indexed)} des Fundus)"
    )
    lines.append("")
    lines.append("| Clip | Asset | In–Out (s) | Beschreibung |")
    lines.append("|---|---|---|---|")
    for clip in timeline.tracks.video:
        asset = assets_by_id.get(clip.asset, {})
        summary = asset.get("content", {}).get("summary", "—")
        lines.append(
            f"| {clip.id} | {clip.asset} | {clip.src_in:.1f}–{clip.src_out:.1f} | {summary} |"
        )
    lines.append("")

    lines.append("## Dramaturgie")
    lines.append(f"- **Stil-Preset:** {brief.get('preset', '—')}")
    target = brief.get("target_duration_s")
    lines.append(
        f"- **Länge:** {timeline.duration:.1f} s"
        + (f" (Ziel {target} s)" if target is not None else "")
    )
    if export.beatsheet_path.exists():
        lines.append(f"- **Beat-Sheet:** `{export.beatsheet_path.name}` (Dramaturgie im Detail)")
    lines.append("")

    lines.append("## Audio")
    music = [a for a in timeline.tracks.audio if a.src is not None]
    oton = [a for a in timeline.tracks.audio if a.asset is not None]
    if music:
        for a in music:
            gain = f", {a.gain_db:+.0f} dB" if a.gain_db is not None else ""
            lines.append(f"- **Musik:** `{a.src}`{gain}")
    else:
        lines.append("- **Musik:** keine")
    for a in oton:
        duck = f", Musik geduckt {a.duck_music_db:+.0f} dB" if a.duck_music_db is not None else ""
        lines.append(f"- **O-Ton:** Asset `{a.asset}` bei {a.tl_in:.1f} s{duck}")
    lines.append("")

    lines.append("## Design")
    lines.append(f"- **Display-Schrift:** {tokens.get('font_display', '—')}")
    lines.append(f"- **Text-Schrift:** {tokens.get('font_text', '—')}")
    palette = ", ".join(
        f"{k}={tokens[k]}" for k in ("primary_color", "accent_color", "text_color") if k in tokens
    )
    lines.append(f"- **Farben:** {palette or '—'}")
    n_overlays = len(timeline.tracks.overlay)
    n_maps = len(timeline.tracks.map)
    lines.append(f"- **Overlays:** {n_overlays} · **Karten-Clips:** {n_maps}")
    lines.append("")

    lines.append("## Technik")
    lines.append(f"- **Auflösung:** {w}×{h} @ {timeline.fps:g} fps")
    lines.append(
        f"- **Spuren:** {len(timeline.tracks.video)} Video-Clips, {n_overlays} Overlays, "
        f"{n_maps} Karten-Clips, {len(timeline.tracks.audio)} Audio-Spuren"
    )
    if stats.avg_quality:
        q = stats.avg_quality
        lines.append(
            "- **Fundus-Qualität (Ø Video):** "
            f"Schärfe {q.get('sharpness', 0):.2f}, Stabilität {q.get('stability', 0):.2f}, "
            f"Belichtung {q.get('exposure', 0):.2f}"
        )
    lines.append("")

    return "\n".join(lines)
