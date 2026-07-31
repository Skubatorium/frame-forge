"""Vorbereitung des Index-Schritts: Keyframes + technische Analyse pro Asset.

Der `media-indexer`-Agent braucht Keyframes und technische Metadaten, um Beschreibung/Tags/
Rating zu vergeben — die eigentliche CV-/Probe-Arbeit gehört aber nicht ins Modell, sondern in
reproduzierbaren Code. Diese Schicht erzeugt für jedes noch nicht indizierte Asset:

- **Probe** auf dem **Original** (EXIF/Container-Tags → Quelle, Dauer, GPS bleiben erhalten;
  der re-encodete Proxy verlöre die Kamera-Herkunft).
- **CV-Analyse** (Schärfe/Belichtung/Stabilität/Szenen) und **Keyframe-Extraktion** auf dem
  **Proxy** (klein, schnell — Token-Disziplin, Plan §Token).

Das Ergebnis landet als `prep/<hash>.json` im Cache, **getrennt von `assets.json`**. So bleibt
die Pending-Logik (`hash in assets.json`) unberührt: ein Asset gilt erst als indiziert, wenn der
`media-indexer` seinen `assets.json`-Eintrag geschrieben hat. Idempotent: vorhandene Prep-Dateien
werden übersprungen, jede Datei genau einmal analysiert.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from frameforge import ingest as ingest_module
from frameforge import probe as probe_module
from frameforge.analyze import analyze_clip, analyze_photo
from frameforge.index import load_assets
from frameforge.keyframes import extract_keyframes
from frameforge.project import Project

_DATE_IN_NAME = re.compile(r"(20\d{6})")


@dataclass
class PrepFailure:
    asset: Path
    reason: str


@dataclass
class PrepResult:
    prepared: list[str] = field(default_factory=list)  # neu erzeugte Prep-Dateien (Asset-IDs)
    skipped_existing: int = 0  # bereits vorbereitet (Prep-Datei vorhanden)
    skipped_indexed: int = 0  # bereits in assets.json (nichts zu tun)
    failures: list[PrepFailure] = field(default_factory=list)


def _asset_date(path: Path, probe: dict) -> str:
    """`YYYYMMDD` aus captured_at (Foto), sonst Datum im Dateinamen, sonst mtime."""
    captured = probe.get("captured_at")
    if captured:
        try:
            return datetime.fromisoformat(captured).strftime("%Y%m%d")
        except ValueError:
            pass
    m = _DATE_IN_NAME.search(path.as_posix())  # Datum im Datei- oder Ordnernamen (z.B. DJI_20260720…)
    if m:
        return m.group(1)
    return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).strftime("%Y%m%d")


def _provisional_id(path: Path, probe: dict, digest: str) -> str:
    """Stabile, deterministische ID ohne Vision: `<datum>-<quelle>-<hash6>`.

    Der `media-indexer` darf sie behalten; sie ist eindeutig (Hash-Suffix) und sortierbar.
    """
    source = probe.get("source_guess", "unknown")
    hex_suffix = digest.split(":")[-1][:6]  # hash_file liefert "sha256:<hex>"
    return f"{_asset_date(path, probe)}-{source}-{hex_suffix}"


def _prepare_one(path: Path, *, project: Project, proxies_dir: Path, keyframes_dir: Path) -> dict:
    """Baut das Prep-Dict eines Assets (Probe auf Original, CV/Keyframes auf Proxy)."""
    digest = ingest_module.hash_file(path)
    suffix = path.suffix.lower()
    is_video = suffix in ingest_module.VIDEO_EXTENSIONS
    kind = "video" if is_video else "photo"
    proxy = ingest_module.proxy_path(path, proxies_dir, media_root=project.config.media_root)
    source_media = proxy if proxy.exists() else path  # Fallback: Original, falls kein Proxy

    rel = path.resolve().relative_to(project.config.media_root.resolve()).as_posix()
    prep: dict = {"hash": digest, "path": rel, "kind": kind}

    if is_video:
        probe = probe_module.probe_video(path)
        analysis = analyze_clip(source_media, probe)
        duration = float(probe.get("dur") or 0.0)
        scenes = [(s["start"], s["end"]) for s in analysis.get("scenes", [])]
        keyframes = extract_keyframes(
            source_media, kind="video", out_dir=keyframes_dir, duration=duration, scenes=scenes
        )
        prep.update(
            {
                "source_guess": probe.get("source_guess", "unknown"),
                "duration": duration,
                "probe": probe,
                "quality": analysis.get("quality"),
                "motion": analysis.get("motion"),
                "scenes": analysis.get("scenes", []),
            }
        )
    else:
        probe = probe_module.probe_photo_exif(path)
        analysis = analyze_photo(source_media)
        keyframes = extract_keyframes(source_media, kind="photo", out_dir=keyframes_dir)
        prep.update(
            {
                "source_guess": probe.get("source_guess", "unknown"),
                "captured_at": probe.get("captured_at"),
                "gps": probe.get("gps"),
                "probe": probe,
                "quality": analysis.get("quality"),
            }
        )

    prep["id"] = _provisional_id(path, probe, digest)
    prep["keyframes"] = [str(p) for p in keyframes]
    return prep


def prepare_index(
    project: Project, *, filter_substr: str | None = None, limit: int | None = None
) -> PrepResult:
    """Erzeugt Keyframes + Prep-Dateien für noch nicht indizierte Assets.

    `filter_substr` schränkt auf Assets ein, deren Pfad den Teilstring enthält (z.B. ein
    Tages-/Ordnername) — für etappenweises Indizieren. `limit` deckelt die Anzahl neu
    vorbereiteter Assets. Vorhandene Prep-Dateien und bereits indizierte Assets werden
    übersprungen (idempotent).
    """
    result = PrepResult()
    found = ingest_module.scan_media(project.config.media_root)
    indexed_hashes = {a.get("hash") for a in load_assets(project)}

    proxies_dir = project.cache_dir / "proxies"
    keyframes_dir = project.cache_dir / "keyframes"
    prep_dir = project.cache_dir / "prep"
    prep_dir.mkdir(parents=True, exist_ok=True)

    for path in found:
        if filter_substr and filter_substr not in path.as_posix():
            continue
        digest = ingest_module.hash_file(path)
        if digest in indexed_hashes:
            result.skipped_indexed += 1
            continue
        prep_path = prep_dir / f"{digest}.json"
        if prep_path.exists():
            result.skipped_existing += 1
            continue
        if limit is not None and len(result.prepared) >= limit:
            break
        try:
            prep = _prepare_one(
                path, project=project, proxies_dir=proxies_dir, keyframes_dir=keyframes_dir
            )
        except Exception as exc:  # noqa: BLE001 — ein defektes Asset darf den Batch nicht killen
            result.failures.append(PrepFailure(asset=path, reason=str(exc)))
            continue
        prep_path.write_text(json.dumps(prep, indent=2, ensure_ascii=False) + "\n")
        result.prepared.append(prep["id"])

    return result


def load_prep_by_hash(project: Project, digest: str) -> dict:
    """Ein einzelnes Prep-Dict laden (per Hash)."""
    prep_path = project.cache_dir / "prep" / f"{digest}.json"
    if not prep_path.exists():
        raise FileNotFoundError(f"Keine Prep-Datei für Hash {digest} — erst 'prepare-index'.")
    return json.loads(prep_path.read_text())


def index_prepared_asset(
    project: Project,
    digest: str,
    *,
    summary: str,
    tags: list[str],
    usable_as: list[str],
    rating: int,
    source: str,
    people: bool = False,
    place: str | None = None,
) -> dict:
    """Mergt die vom `media-indexer` vergebenen Inhaltsfelder in ein Prep-Dict und schreibt es.

    Deterministischer Schreibpfad: lädt `prep/<hash>.json` (technische Felder), ergänzt
    `content`, `rating`, `source` und ruft `index.write_asset`. So braucht der Agent pro Asset
    nur einen Befehl statt JSON-Bastelei. Gibt den geschriebenen Eintrag zurück.
    """
    if source not in probe_module.SOURCE_TYPES:
        raise ValueError(f"source '{source}' nicht in {probe_module.SOURCE_TYPES}")
    if not 1 <= rating <= 5:
        raise ValueError("rating muss 1..5 sein")

    asset = load_prep_by_hash(project, digest)
    asset["source"] = source
    asset["rating"] = rating
    asset["content"] = {
        "summary": summary,
        "tags": tags,
        "people": people,
        "usable_as": usable_as,
    }
    if place:
        gps = asset.get("gps") or {}
        gps["place"] = place
        asset["gps"] = gps

    from frameforge.index import write_asset

    write_asset(project, asset)
    return asset


def load_prep(project: Project) -> list[dict]:
    """Vorbereitete, **noch nicht indizierte** Assets — für den `media-indexer`.

    Filtert Prep-Dateien heraus, deren Hash bereits in `assets.json` steht (der media-indexer
    hat sie schon bearbeitet), damit ein zweiter Lauf nicht dieselben Assets erneut schickt.
    """
    prep_dir = project.cache_dir / "prep"
    if not prep_dir.is_dir():
        return []
    indexed_hashes = {a.get("hash") for a in load_assets(project)}
    preps = [json.loads(p.read_text()) for p in sorted(prep_dir.glob("*.json"))]
    return [p for p in preps if p.get("hash") not in indexed_hashes]
