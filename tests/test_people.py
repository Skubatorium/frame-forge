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


# -- detailliertes Clustering + Crops -----------------------------------------


def test_cluster_people_detailed_keeps_members():
    rng = np.random.default_rng(7)
    a = rng.normal(0, 0.1, 128)
    b = rng.normal(5, 0.1, 128)
    faces = {
        "img1": [_synthetic_encoding(rng, a), _synthetic_encoding(rng, b)],  # Gruppenfoto
        "img2": [_synthetic_encoding(rng, a)],
    }
    from frameforge.people import cluster_people_detailed

    detailed = cluster_people_detailed(faces)
    assert len(detailed) == 2
    # person mit a: img1(face 0) + img2(face 0)
    a_cluster = next(m for m in detailed.values() if ("img2", 0) in m)
    assert ("img1", 0) in a_cluster


def test_crop_face_writes_jpeg(tmp_path):
    from frameforge.people import crop_face

    out = crop_face(
        FIXTURES / "photo.jpg",
        {"top": 5, "right": 40, "bottom": 30, "left": 10},
        tmp_path / "crop.jpg",
    )
    assert out.exists()
    from PIL import Image

    assert Image.open(out).format == "JPEG"


# -- Namensverwaltung ----------------------------------------------------------


@pytest.fixture
def proj(tmp_path, monkeypatch):
    from frameforge import project as project_module
    from frameforge.project import ProjectConfig, resolve_project

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=tmp_path / "media").save(root / "project.yaml")
    project = resolve_project("p")
    project.index_dir.mkdir(parents=True)
    (project.index_dir / "people_clusters.json").write_text(
        __import__("json").dumps({"person_1": ["a1", "a2"], "person_2": ["a2", "a3"]})
    )
    return project


def test_set_and_resolve_person_name(proj):
    from frameforge.people import assets_for_person, load_people_names, set_person_name

    key = set_person_name(proj, "person_1", "Oskar")
    assert key == "person_1"
    assert load_people_names(proj) == {"person_1": "Oskar"}
    assert assets_for_person(proj, "Oskar") == ["a1", "a2"]
    assert assets_for_person(proj, "oskar") == ["a1", "a2"]  # case-insensitiv


def test_rename_by_existing_name(proj):
    from frameforge.people import load_people_names, set_person_name

    set_person_name(proj, "person_1", "Oskar")
    set_person_name(proj, "Oskar", "Oscar")  # umbenennen ueber alten Namen
    assert load_people_names(proj) == {"person_1": "Oscar"}


def test_set_person_name_unknown_cluster_raises(proj):
    from frameforge.people import set_person_name

    with pytest.raises(KeyError):
        set_person_name(proj, "person_99", "X")


def test_assets_for_person_unknown_returns_empty(proj):
    from frameforge.people import assets_for_person

    assert assets_for_person(proj, "niemand") == []
