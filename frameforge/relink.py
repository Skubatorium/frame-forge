"""Pfad-Reparatur nach Umsortieren von `media_root` (Plan 0003, Arbeitspaket E).

Der Analyse-Cache haengt am Datei-Hash (`ingest.hash_file`) und ueberlebt ein Verschieben —
der in `assets.json` gespeicherte **relative Pfad** wird dabei aber nicht nachgezogen. Der
Fehler faellt sonst erst beim Final-Render auf, weil `render_final` die Originale ueber genau
diesen Pfad aufloest.

`plan_relink` rechnet nur (kein Schreiben), `apply_relink` schreibt — damit `--dry-run` und der
echte Lauf garantiert dieselbe Entscheidung treffen. Beruehrt ausschliesslich das Feld `path`;
`content`, `rating`, `source`, `quality` und die Freitext-Notizen bleiben unangetastet, es
laeuft **keine** erneute Analyse und kein Vision-Call.

Grenze des Verfahrens: der Hash enthaelt `mtime` und `size` (Plan 0001 §3). Eine *kopierte*
Datei (ohne Erhalt der mtime) hat einen anderen Hash und erscheint deshalb als verwaister
Eintrag **plus** neue Datei, nicht als Verschiebung. Das ist gewollt — geraten wird hier
nichts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from frameforge import index as index_module
from frameforge import ingest as ingest_module
from frameforge.project import Project


@dataclass(frozen=True)
class PathChange:
    """Ein Asset, dessen Datei an einer anderen Stelle unter `media_root` liegt."""

    asset_id: str
    old_path: str
    new_path: str


@dataclass(frozen=True)
class Orphan:
    """Ein Asset, dessen Datei nirgends mehr unter `media_root` auffindbar ist."""

    asset_id: str
    path: str


@dataclass(frozen=True)
class Ambiguous:
    """Ein Asset-Hash, der auf mehrere Dateien passt (echte Duplikate im Fundus)."""

    asset_id: str
    candidates: list[str]


@dataclass
class RelinkResult:
    """Was ein Relink-Lauf tun wuerde bzw. getan hat."""

    changed: list[PathChange] = field(default_factory=list)
    unchanged: int = 0
    orphans: list[Orphan] = field(default_factory=list)
    ambiguous: list[Ambiguous] = field(default_factory=list)
    new_files: list[str] = field(default_factory=list)
    moved_proxies: int = 0  # von `apply_relink` gesetzt (Cache-Umbenennungen)

    @property
    def has_changes(self) -> bool:
        return bool(self.changed)


def _rel_path(path: Path, media_root: Path) -> str:
    """Relativer Pfad unter `media_root` — dieselbe Schreibweise wie in `preindex`."""
    return path.resolve().relative_to(media_root.resolve()).as_posix()


def plan_relink(project: Project) -> RelinkResult:
    """Vergleicht `assets.json` mit dem tatsaechlichen Inhalt von `media_root`. Schreibt nichts.

    Raises:
        FileNotFoundError: wenn `media_root` nicht erreichbar ist (externe Platte nicht
            gemountet) — dann waere *jedes* Asset ein Waise, und ein blindes Weiterlaufen
            wuerde eine leere Lueckenliste als Ergebnis verkaufen.
    """
    media_root = project.config.media_root
    found = ingest_module.scan_media(media_root)
    found_rel = {_rel_path(p, media_root): p for p in found}

    by_hash: dict[str, list[Path]] = {}
    for path in found:
        by_hash.setdefault(ingest_module.hash_file(path), []).append(path)

    result = RelinkResult()
    seen_hashes: set[str] = set()
    claimed_paths: set[str] = set()

    for asset in index_module.load_assets(project):
        digest = asset.get("hash")
        asset_id = asset.get("id", "?")
        old_path = asset.get("path", "")
        if digest:
            seen_hashes.add(digest)

        if old_path in found_rel:
            # **Der eingetragene Pfad existiert weiterhin — nichts zu reparieren.** Bewusst ohne
            # Hash-Vergleich: `hash_file` nimmt `mtime` mit auf, ein blosses Anfassen der Datei
            # (git-Checkout, `touch`, Kopie ohne mtime-Erhalt) aendert den Hash, ohne dass der
            # Pfad falsch waere. Relink repariert Pfade, nicht Hashes.
            result.unchanged += 1
            claimed_paths.add(old_path)
            continue

        candidates = by_hash.get(digest, []) if digest else []
        if not candidates:
            result.orphans.append(Orphan(asset_id=asset_id, path=old_path))
            continue

        rel_paths = sorted(_rel_path(p, media_root) for p in candidates)
        if len(rel_paths) > 1:
            result.ambiguous.append(Ambiguous(asset_id=asset_id, candidates=rel_paths))
            continue
        result.changed.append(
            PathChange(asset_id=asset_id, old_path=old_path, new_path=rel_paths[0])
        )
        claimed_paths.add(rel_paths[0])

    result.new_files = sorted(
        rel
        for rel, path in found_rel.items()
        if rel not in claimed_paths and ingest_module.hash_file(path) not in seen_hashes
    )
    return result


def _move_proxy(project: Project, change: PathChange) -> bool:
    """Benennt den Proxy einer verschobenen Datei mit um. True, wenn etwas verschoben wurde.

    `ingest.proxy_path` haengt den Hash des **relativen Pfads** an den Proxy-Namen (Audit-Fix K1
    gegen Namenskollisionen). Nach einem Verschieben zeigt der neue Pfad also auf einen anderen
    Proxy-Namen — der vorhandene Proxy waere verwaist und wuerde beim naechsten `ingest` neu
    transkodiert. Bei ~100 GB ist das der teuerste Teil der Pipeline, deshalb ziehen wir den
    Proxy hier mit um (Abweichung von Plan 0003 §E, siehe PROGRESS.md).
    """
    media_root = project.config.media_root
    proxies_dir = project.cache_dir / "proxies"
    old_proxy = ingest_module.proxy_path(media_root / change.old_path, proxies_dir, media_root=media_root)
    new_proxy = ingest_module.proxy_path(media_root / change.new_path, proxies_dir, media_root=media_root)
    if old_proxy == new_proxy or not old_proxy.exists() or new_proxy.exists():
        return False
    old_proxy.rename(new_proxy)
    return True


def apply_relink(project: Project, result: RelinkResult) -> int:
    """Schreibt die in `result.changed` geplanten Pfad-Korrekturen. Gibt die Anzahl zurueck.

    `assets.json` wird genau einmal geschrieben; die `.md`-Datei wird nur fuer geaenderte
    Assets neu erzeugt (Notizen bleiben erhalten, `index.write_asset_md` merged sie).
    Zusaetzlich wandert der zugehoerige Proxy im Cache mit (`_move_proxy`).
    """
    if not result.changed:
        return 0

    new_by_id = {c.asset_id: c.new_path for c in result.changed}
    assets = index_module.load_assets(project)
    touched = []
    for asset in assets:
        new_path = new_by_id.get(asset.get("id"))
        if new_path is not None:
            asset["path"] = new_path
            touched.append(asset)

    index_module.save_assets(project, assets)
    for asset in touched:
        index_module.write_asset_md(project, asset)
    result.moved_proxies = sum(_move_proxy(project, change) for change in result.changed)
    return len(touched)
