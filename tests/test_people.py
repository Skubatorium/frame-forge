"""Tests fuer Gesichtserkennung/Clustering.

`detect_faces` wird nur gegen die Negativ-Fixture getestet (Solid-Color-Foto ohne Gesicht) —
`cluster_people` ist reine Vektor-Arithmetik auf Encodings und wird mit synthetischen
128-d-Vektoren getestet, damit **keine echten Gesichtsfotos** im Repo landen muessen
(Datenschutz, siehe Modul-Docstring).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from frameforge.people import FaceDetectionError, cluster_people, detect_faces

FIXTURES = Path(__file__).parent / "fixtures"


def test_detect_faces_returns_empty_list_for_photo_without_face():
    assert detect_faces(FIXTURES / "photo.jpg") == []


def test_detect_faces_missing_file_raises():
    with pytest.raises(FaceDetectionError):
        detect_faces(FIXTURES / "does-not-exist.jpg")


def _synthetic_encoding(rng, base, noise=0.01):
    return (base + rng.normal(0, noise, 128)).tolist()


def test_cluster_people_groups_similar_encodings_together():
    rng = np.random.default_rng(1)
    person_a = rng.normal(0, 0.1, 128)
    person_b = rng.normal(5, 0.1, 128)

    faces_by_asset = {
        "a1": [_synthetic_encoding(rng, person_a)],
        "a2": [_synthetic_encoding(rng, person_a)],
        "a3": [_synthetic_encoding(rng, person_b)],
    }

    clusters = cluster_people(faces_by_asset)

    assert len(clusters) == 2
    grouped_assets = list(clusters.values())
    assert sorted(grouped_assets, key=len) == [["a3"], ["a1", "a2"]]


def test_cluster_people_empty_input_returns_empty_dict():
    assert cluster_people({}) == {}


def test_cluster_people_single_asset_multiple_faces_creates_multiple_clusters():
    rng = np.random.default_rng(2)
    person_a = rng.normal(0, 0.1, 128)
    person_b = rng.normal(5, 0.1, 128)

    faces_by_asset = {
        "group_photo": [_synthetic_encoding(rng, person_a), _synthetic_encoding(rng, person_b)],
    }

    clusters = cluster_people(faces_by_asset)

    assert len(clusters) == 2
    for asset_ids in clusters.values():
        assert asset_ids == ["group_photo"]


def test_cluster_people_respects_tolerance():
    rng = np.random.default_rng(3)
    person_a = rng.normal(0, 0.1, 128)
    # Leicht verschobene Variante derselben "Person" - je nach Toleranz gleicher oder
    # getrennter Cluster.
    similar_but_distinct = person_a + 0.5

    faces_by_asset = {
        "a1": [person_a.tolist()],
        "a2": [similar_but_distinct.tolist()],
    }

    strict = cluster_people(faces_by_asset, tolerance=0.1)
    loose = cluster_people(faces_by_asset, tolerance=10.0)

    assert len(strict) == 2
    assert len(loose) == 1
