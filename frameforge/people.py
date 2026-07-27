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

from pathlib import Path

import face_recognition
import numpy as np


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


def cluster_people(
    faces_by_asset: dict[str, list[list[float]]], *, tolerance: float = 0.6
) -> dict[str, list[str]]:
    """Gruppiert Gesichts-Encodings ueber Assets hinweg zu Personen.

    Greedy-Clustering: jedes Encoding wird mit den bisherigen Cluster-Centroiden verglichen
    (`face_recognition.face_distance`) und dem naechsten unter `tolerance` zugeordnet, sonst
    startet ein neuer Cluster. `tolerance` ist der `face_recognition`-Standardwert (0.6) —
    kleiner = strenger (weniger Falsch-Positive, mehr Falsch-Negative).

    Rueckgabe: `{"person_1": [asset_id, ...], "person_2": [...], ...}` — sortiert nach
    Cluster-Reihenfolge, nicht nach Personenidentitaet (die Zuordnung "person_1 = Oskar"
    liefert der Nutzer/Orchestrator, nicht dieses Modul).
    """
    clusters: list[dict] = []  # je Cluster: {"encodings": [np.ndarray], "assets": set[str]}

    for asset_id, encodings in faces_by_asset.items():
        for raw_encoding in encodings:
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
                clusters.append({"encodings": [encoding], "assets": {asset_id}})
            else:
                clusters[best_index]["encodings"].append(encoding)
                clusters[best_index]["assets"].add(asset_id)

    return {
        f"person_{i + 1}": sorted(cluster["assets"]) for i, cluster in enumerate(clusters)
    }
