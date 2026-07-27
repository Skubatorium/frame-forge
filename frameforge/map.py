"""Karten-Frames, Marker, Route-Reveal aus GPX-Tracks.

Generische Fähigkeit, keine projektspezifische Gestaltung: Farben/Icons/Kartenstil sind
Parameter, nichts davon ist hier hart codiert (siehe `docs/plans/PROGRESS.md` M3 — bewusste
Scope-Entscheidung, dass "wie es aussieht" Sache des jeweiligen Projekts/Designsystems ist,
nicht dieses Moduls). `render_route_frames` funktioniert ohne Basemap (reine Linie auf
transparentem Grund, M1-Verhalten) und mit Basemap (`render_basemap` aus gecachten XYZ-Kacheln).
Marker sind per Default ein Punkt, oder ein beliebiges Icon-Bild (`marker_icon`) — kein
festes Auto-/Figur-Symbol im Code, das liefert das Projekt selbst.
"""

from __future__ import annotations

import math
import subprocess
import urllib.request
from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 360
MARGIN_PX = 40
ROUTE_COLOR = (224, 164, 88, 255)
ROUTE_WIDTH_PX = 4
MARKER_COLOR = (255, 255, 255, 255)
MARKER_RADIUS_PX = 8

TILE_SIZE_PX = 256
DEFAULT_TILE_SERVER = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
DEFAULT_TILE_USER_AGENT = "frameforge/0.1 (+https://github.com/Skubatorium/frame-forge)"

TileFetcher = Callable[[str], bytes]


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
    marker_icon: Path | None = None,
    basemap: Image.Image | None = None,
    route_color: tuple[int, int, int, int] = ROUTE_COLOR,
    route_width_px: int = ROUTE_WIDTH_PX,
) -> list[Path]:
    """PNG-Sequenz mit Alpha: Route-Reveal (Linie waechst ueber die Dauer) + Positions-Marker.

    Ein Frame pro `1/fps` Sekunden ueber `dur` Sekunden. `track` braucht mindestens 2 Punkte
    (z.B. aus `frameforge.gpx.parse_gpx`).

    `marker_icon`: eigenes Icon (PNG mit Alpha, mittig auf die aktuelle Position gestempelt)
    statt des Default-Punkts — kein Auto-/Figur-Symbol ist hier fest eingebaut, jedes Projekt
    liefert sein eigenes (`design/assets/`).
    `basemap`: vorgerendertes Kartenbild (siehe `render_basemap`) als Hintergrund statt
    transparent — Grösse muss zu `(width, height)` passen.
    """
    if len(track) < 2:
        raise ValueError("track braucht mindestens 2 Punkte fuer eine Route")
    if basemap is not None and basemap.size != (width, height):
        raise ValueError(f"basemap-Groesse {basemap.size} passt nicht zu ({width}, {height})")

    out_dir.mkdir(parents=True, exist_ok=True)
    points_px = _project(track, width, height, MARGIN_PX)
    frame_count = max(1, round(fps * dur))
    icon = Image.open(marker_icon).convert("RGBA") if marker_icon else None

    outputs: list[Path] = []
    for i in range(frame_count):
        progress = (i + 1) / frame_count
        reveal_count = max(2, round(len(points_px) * progress))
        visible = points_px[:reveal_count]

        image = basemap.copy() if basemap is not None else Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.line(visible, fill=route_color, width=route_width_px, joint="curve")
        cx, cy = visible[-1]
        if icon is not None:
            image.alpha_composite(icon, (round(cx - icon.width / 2), round(cy - icon.height / 2)))
        else:
            r = MARKER_RADIUS_PX
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=MARKER_COLOR)

        target = out_dir / f"frame_{i:04d}.png"
        image.save(target)
        outputs.append(target)

    return outputs


def _default_tile_fetcher(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": DEFAULT_TILE_USER_AGENT})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read()


def latlon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    """Standard-Slippy-Map-Formel (Web-Mercator) — Lat/Lon zu Kachel-Index bei `zoom`."""
    lat_rad = math.radians(lat)
    n = 2**zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def fetch_tile(
    z: int,
    x: int,
    y: int,
    cache_dir: Path,
    *,
    tile_server_url: str = DEFAULT_TILE_SERVER,
    fetcher: TileFetcher | None = None,
) -> Path:
    """Laedt eine XYZ-Kachel, gecacht unter `cache_dir/<z>/<x>/<y>.png`.

    `fetcher(url) -> bytes` ist injizierbar — Tests/Offline-Betrieb muessen nicht echt gegen
    einen Tile-Server gehen. Ohne eigenen `fetcher` wird per `urllib` gegen `tile_server_url`
    geladen (Default: OpenStreetMap — bei produktivem Einsatz Nutzungsbedingungen/eigenen
    Tile-Server beachten, siehe Modul-Docstring).
    """
    target = cache_dir / str(z) / str(x) / f"{y}.png"
    if target.exists():
        return target

    fetch = fetcher or _default_tile_fetcher
    data = fetch(tile_server_url.format(z=z, x=x, y=y))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def render_basemap(
    bbox: tuple[float, float, float, float],
    zoom: int,
    cache_dir: Path,
    *,
    tile_server_url: str = DEFAULT_TILE_SERVER,
    fetcher: TileFetcher | None = None,
) -> Image.Image:
    """Setzt eine Basiskarte aus gecachten XYZ-Kacheln fuer eine Bounding-Box zusammen.

    `bbox` = `(lat_min, lon_min, lat_max, lon_max)`. Liefert ein RGBA-Bild, dessen Groesse
    sich aus der Anzahl abgedeckter Kacheln ergibt (Vielfaches von `TILE_SIZE_PX`) — fuer
    `render_route_frames(..., basemap=...)` ggf. vorher zuschneiden/skalieren.
    """
    lat_min, lon_min, lat_max, lon_max = bbox
    x_min, y_min = latlon_to_tile(lat_max, lon_min, zoom)  # Norden/Westen -> kleinere x/y
    x_max, y_max = latlon_to_tile(lat_min, lon_max, zoom)  # Sueden/Osten -> groessere x/y
    x_min, x_max = sorted((x_min, x_max))
    y_min, y_max = sorted((y_min, y_max))

    cols = x_max - x_min + 1
    rows = y_max - y_min + 1
    canvas = Image.new("RGBA", (cols * TILE_SIZE_PX, rows * TILE_SIZE_PX), (0, 0, 0, 0))

    for row, y in enumerate(range(y_min, y_max + 1)):
        for col, x in enumerate(range(x_min, x_max + 1)):
            tile_path = fetch_tile(
                zoom, x, y, cache_dir, tile_server_url=tile_server_url, fetcher=fetcher
            )
            tile = Image.open(tile_path).convert("RGBA")
            canvas.paste(tile, (col * TILE_SIZE_PX, row * TILE_SIZE_PX))

    return canvas


def encode_alpha_video(
    frames_dir: Path, out_path: Path, *, fps: float, timeout_s: float = 300.0
) -> Path:
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
        timeout=timeout_s,
    )
    return out_path
