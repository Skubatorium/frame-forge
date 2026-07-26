"""Karten-Frames, Marker, Route-Reveal aus GPX-Tracks.

M1-Scope: reine Routen-Linie + Marker auf transparentem Grund, projiziert per einfacher
Equirectangular-Projektion auf die Bounding-Box des Tracks — kein Tile-Fetch. Gecachte
OSM-Tiles als Basiskarte sind laut Plan Abschnitt 8 explizit M3-Scope ("Tile-Cache"), nicht
Teil des Mini-Prototyps.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 360
MARGIN_PX = 40
ROUTE_COLOR = (224, 164, 88, 255)
ROUTE_WIDTH_PX = 4
MARKER_COLOR = (255, 255, 255, 255)
MARKER_RADIUS_PX = 8


def _project(track: list[dict], width: int, height: int, margin: int) -> list[tuple[float, float]]:
    """Equirectangular-Projektion der Track-Punkte auf Pixelkoordinaten der Bounding-Box."""
    lats = [p["lat"] for p in track]
    lons = [p["lon"] for p in track]
    lat_span = max(max(lats) - min(lats), 1e-9)
    lon_span = max(max(lons) - min(lons), 1e-9)
    usable_w = width - 2 * margin
    usable_h = height - 2 * margin

    points = []
    for p in track:
        x = margin + (p["lon"] - min(lons)) / lon_span * usable_w
        y = margin + (1 - (p["lat"] - min(lats)) / lat_span) * usable_h
        points.append((x, y))
    return points


def render_route_frames(
    track: list[dict],
    out_dir: Path,
    *,
    fps: float,
    dur: float,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> list[Path]:
    """PNG-Sequenz mit Alpha: Route-Reveal (Linie waechst ueber die Dauer) + Positions-Marker.

    Ein Frame pro `1/fps` Sekunden ueber `dur` Sekunden. `track` braucht mindestens 2 Punkte
    (z.B. aus `frameforge.gpx.parse_gpx`).
    """
    if len(track) < 2:
        raise ValueError("track braucht mindestens 2 Punkte fuer eine Route")

    out_dir.mkdir(parents=True, exist_ok=True)
    points_px = _project(track, width, height, MARGIN_PX)
    frame_count = max(1, round(fps * dur))

    outputs: list[Path] = []
    for i in range(frame_count):
        progress = (i + 1) / frame_count
        reveal_count = max(2, round(len(points_px) * progress))
        visible = points_px[:reveal_count]

        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.line(visible, fill=ROUTE_COLOR, width=ROUTE_WIDTH_PX, joint="curve")
        cx, cy = visible[-1]
        r = MARKER_RADIUS_PX
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=MARKER_COLOR)

        target = out_dir / f"frame_{i:04d}.png"
        image.save(target)
        outputs.append(target)

    return outputs


def encode_alpha_video(frames_dir: Path, out_path: Path, *, fps: float) -> Path:
    """Kodiert eine `frame_%04d.png`-Sequenz zu einem `.mov` mit Alphakanal (QuickTime Animation).

    `render.build_filtergraph` erwartet `MapClip.clip` als fertigen Videoclip (Plan §4:
    `"clip": "map/leg-01.mov"`) — dieser Schritt macht aus `render_route_frames`-Output genau das.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "frame_%04d.png"),
            "-c:v",
            "qtrle",
            "-loglevel",
            "error",
            str(out_path),
        ],
        check=True,
    )
    return out_path
