"""Gesichtserkennung fuer "zeig mehr von <Person>" (Plan §11).

**Datenschutz-Hinweis, bewusst kein Default-Verhalten:** Gesichtserkennung verarbeitet
biometrische Daten. Dieses Modul wird **nicht** automatisch von `frameforge index`
aufgerufen — es ist ein expliziter Opt-in pro Projekt (`frameforge faces <projekt>`,
Task-Nummer M-Extra in `docs/plans/PROGRESS.md`). Wer es nutzt, ist selbst dafuer
verantwortlich, dass die Verarbeitung der abgebildeten Personen rechtlich gedeckt ist
(z.B. eigene Familie/Freunde mit Einverstaendnis, nicht fremde Personen im Hintergrund).

Erkennung (`detect_faces`) laeuft auf `face_recognition`/`dlib` (HOG-Detektor + 128-d
Encodings) — echt, kein Mock. Das Gruppieren mehrerer Gesichter zu "das ist dieselbe Person"
(`cluster_people`) ist reine Vektor-Arithmetik auf den Encodings und braucht keine echten
Fotos zum Testen (siehe `tests/test_people.py`).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import face_recognition
import numpy as np
from PIL import Image

if TYPE_CHECKING:
    from frameforge.project import Project


class FaceDetectionError(RuntimeError):
    """Ein Bild konnte nicht gelesen werden."""


def detect_faces(path: Path) -> list[dict]:
    """Gesichter + 128-d Encodings in einem Foto/Keyframe.

    Rueckgabe: `[{"location": {"top", "right", "bottom", "left"}, "encoding": [128 floats]}, ...]`.
    Leere Liste, wenn kein Gesicht erkannt wurde — kein Fehler.
    """
    try:
        image = face_recognition.load_image_file(str(path))
    except (OSError, ValueError) as exc:
        raise FaceDetectionError(f"{path}: nicht lesbar ({exc})") from exc

    locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, locations)
    return [
        {
            "location": {"top": top, "right": right, "bottom": bottom, "left": left},
            "encoding": encoding.tolist(),
        }
        for (top, right, bottom, left), encoding in zip(locations, encodings, strict=True)
    ]


def cluster_people_detailed(
    faces_by_asset: dict[str, list[list[float]]], *, tolerance: float = 0.6
) -> dict[str, list[tuple[str, int]]]:
    """Wie `cluster_people`, behaelt aber pro Cluster die genauen Mitglieder.

    Rueckgabe: `{"person_1": [(asset_id, face_index), ...], ...}` — `face_index` ist der
    Index des Gesichts innerhalb des Assets (fuer den repraesentativen Ausschnitt beim
    Benennen wichtig, damit bei Gruppenfotos das richtige Gesicht gecroppt wird).
    """
    clusters: list[dict] = []  # {"encodings": [np.ndarray], "members": [(asset_id, face_idx)]}

    for asset_id, encodings in faces_by_asset.items():
        for face_index, raw_encoding in enumerate(encodings):
            encoding = np.array(raw_encoding)
            best_index: int | None = None
            best_distance = tolerance
            for index, cluster in enumerate(clusters):
                centroid = np.mean(cluster["encodings"], axis=0)
                distance = face_recognition.face_distance([centroid], encoding)[0]
                if distance < best_distance:
                    best_distance = distance
                    best_index = index

            if best_index is None:
                clusters.append({"encodings": [encoding], "members": [(asset_id, face_index)]})
            else:
                clusters[best_index]["encodings"].append(encoding)
                clusters[best_index]["members"].append((asset_id, face_index))

    return {f"person_{i + 1}": c["members"] for i, c in enumerate(clusters)}


def cluster_people(
    faces_by_asset: dict[str, list[list[float]]], *, tolerance: float = 0.6
) -> dict[str, list[str]]:
    """Gruppiert Gesichts-Encodings ueber Assets hinweg zu Personen.

    Rueckgabe: `{"person_1": [asset_id, ...], ...}` (eindeutige, sortierte Asset-IDs je
    Cluster). Die Zuordnung "person_1 = Oskar" liefert der Nutzer/Orchestrator, nicht dieses
    Modul — dafuer gibt es `set_person_name`.
    """
    detailed = cluster_people_detailed(faces_by_asset, tolerance=tolerance)
    return {key: sorted({asset_id for asset_id, _ in members}) for key, members in detailed.items()}


def crop_face(image_path: Path, location: dict, out_path: Path, *, margin: float = 0.4) -> Path:
    """Schneidet ein Gesicht (mit Rand) aus einem Bild aus und speichert es als JPEG.

    `location` = `{"top", "right", "bottom", "left"}` (Pixel), wie von `detect_faces` geliefert.
    """
    image = Image.open(image_path).convert("RGB")
    top, right = location["top"], location["right"]
    bottom, left = location["bottom"], location["left"]
    dy = int((bottom - top) * margin)
    dx = int((right - left) * margin)
    box = (
        max(0, left - dx),
        max(0, top - dy),
        min(image.width, right + dx),
        min(image.height, bottom + dy),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.crop(box).save(out_path, format="JPEG", quality=85)
    return out_path


def write_representative_crops(
    people_json: dict[str, list[dict]],
    detailed_clusters: dict[str, list[tuple[str, int]]],
    resolve_path,
    out_dir: Path,
) -> dict[str, Path]:
    """Schreibt pro Cluster einen repraesentativen Gesichts-Ausschnitt.

    `people_json` = `{asset_id: [{"location", "encoding"}, ...]}` (voller `detect_faces`-Output).
    `resolve_path(asset_id) -> Path` liefert das Quellbild. Rueckgabe: `{cluster_key: crop_path}`.
    Cluster ohne lesbares Bild werden uebersprungen.
    """
    crops: dict[str, Path] = {}
    for key, members in detailed_clusters.items():
        if not members:
            continue
        asset_id, face_index = members[0]
        faces = people_json.get(asset_id, [])
        if face_index >= len(faces):
            continue
        try:
            src = resolve_path(asset_id)
            crops[key] = crop_face(src, faces[face_index]["location"], out_dir / f"{key}.jpg")
        except (OSError, ValueError, KeyError):
            continue  # ein unlesbares Bild darf den Rest nicht kippen
    return crops


# -- Namensverwaltung (projektweit) ------------------------------------------


def _names_path(project: Project) -> Path:
    return project.index_dir / "people_names.json"


def _clusters_path(project: Project) -> Path:
    return project.index_dir / "people_clusters.json"


def load_people_names(project: Project) -> dict[str, str]:
    """Cluster-Key -> Name (z.B. `{"person_1": "Oskar"}`); leeres Dict, falls noch nichts benannt."""
    path = _names_path(project)
    return json.loads(path.read_text()) if path.exists() else {}


def load_clusters(project: Project) -> dict[str, list[str]]:
    """Cluster-Key -> Asset-IDs (aus `people_clusters.json`); leer, falls `faces` nie lief."""
    path = _clusters_path(project)
    return json.loads(path.read_text()) if path.exists() else {}


def set_person_name(project: Project, cluster_or_name: str, name: str) -> str:
    """Benennt einen Cluster. `cluster_or_name` ist ein Cluster-Key (`person_1`) oder ein

    bereits vergebener Name (dann wird umbenannt). Gibt den betroffenen Cluster-Key zurueck.
    """
    clusters = load_clusters(project)
    names = load_people_names(project)

    key = cluster_or_name
    if key not in clusters:
        # Vielleicht ein bereits vergebener Name -> zugehoerigen Key finden.
        matches = [k for k, n in names.items() if n.lower() == cluster_or_name.lower()]
        if not matches:
            raise KeyError(
                f"Cluster '{cluster_or_name}' nicht gefunden — bekannte Cluster: {sorted(clusters)}"
            )
        key = matches[0]

    names[key] = name
    _names_path(project).parent.mkdir(parents=True, exist_ok=True)
    _names_path(project).write_text(json.dumps(names, indent=2, ensure_ascii=False))
    return key


def assets_for_person(project: Project, name: str) -> list[str]:
    """Alle Asset-IDs, in denen die benannte Person vorkommt (case-insensitiv).

    `name` darf auch ein Cluster-Key (`person_1`) sein. Leere Liste, wenn unbekannt.
    """
    clusters = load_clusters(project)
    names = load_people_names(project)
    keys = {k for k, n in names.items() if n.lower() == name.lower()}
    if name in clusters:
        keys.add(name)
    asset_ids: set[str] = set()
    for key in keys:
        asset_ids.update(clusters.get(key, []))
    return sorted(asset_ids)
