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


def _make_projector(track: list[dict], width: int, height: int, margin: int):
    """Liefert eine Funktion `(lat, lon) -> (x, y)`, die auf die Bounding-Box des Tracks abbildet.

    So landen Track-Punkte UND POIs (aus `locations.csv`) im selben Koordinatensystem.
    """
    lats = [p["lat"] for p in track]
    lons = [p["lon"] for p in track]
    lat_min, lon_min = min(lats), min(lons)
    lat_span = max(max(lats) - lat_min, 1e-9)
    lon_span = max(max(lons) - lon_min, 1e-9)
    usable_w = width - 2 * margin
    usable_h = height - 2 * margin

    def project(lat: float, lon: float) -> tuple[float, float]:
        x = margin + (lon - lon_min) / lon_span * usable_w
        y = margin + (1 - (lat - lat_min) / lat_span) * usable_h
        return x, y

    return project


def _project(track: list[dict], width: int, height: int, margin: int) -> list[tuple[float, float]]:
    """Equirectangular-Projektion der Track-Punkte auf Pixelkoordinaten der Bounding-Box."""
    project = _make_projector(track, width, height, margin)
    return [project(p["lat"], p["lon"]) for p in track]


def latlon_to_pixel(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    """Web-Mercator-Weltpixel bei `zoom` (Subpixel-genau, gleiche Basis wie XYZ-Kacheln).

    `latlon_to_tile` ist genau das hier, abgerundet auf ganze Kacheln. Route und Basiskarte
    im selben Koordinatensystem zu haben ist die Voraussetzung dafuer, dass eine Kachelkarte
    unter der Route pixelgenau stimmt (Plan 0003 §B2).
    """
    n = TILE_SIZE_PX * 2**zoom
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def pixel_to_latlon(x: float, y: float, zoom: int) -> tuple[float, float]:
    """Umkehrung von `latlon_to_pixel` — Weltpixel zurueck nach `(lat, lon)`."""
    n = TILE_SIZE_PX * 2**zoom
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n))))
    return lat, lon


def smooth_centers(
    points: list[tuple[float, float]], window: int
) -> list[tuple[float, float]]:
    """Gleitender Mittelwert ueber Mittelpunkte — sonst zittert der Follow-Ausschnitt.

    `window <= 1` gibt die Eingabe unveraendert zurueck.
    """
    if window <= 1 or not points:
        return list(points)
    half = window // 2
    out: list[tuple[float, float]] = []
    for i in range(len(points)):
        chunk = points[max(0, i - half) : i + half + 1]
        out.append(
            (sum(p[0] for p in chunk) / len(chunk), sum(p[1] for p in chunk) / len(chunk))
        )
    return out


def basemap_viewport(
    center_latlon: tuple[float, float],
    zoom: int,
    size: tuple[int, int],
    cache_dir: Path,
    *,
    tile_server_url: str = DEFAULT_TILE_SERVER,
    fetcher: TileFetcher | None = None,
) -> Image.Image:
    """Basiskarten-**Ausschnitt** beliebiger Pixelgroesse um einen Mittelpunkt.

    `render_basemap` liefert nur ganze Kachelraster (Vielfache von 256 px) — fuer den
    Follow-Modus braucht es einen frei positionierbaren Ausschnitt. Gelesen wird aus demselben
    Kachel-Cache; es werden nur die tatsaechlich sichtbaren Kacheln geholt.
    """
    width, height = size
    cx, cy = latlon_to_pixel(*center_latlon, zoom)
    left, top = cx - width / 2, cy - height / 2

    tile_x0, tile_y0 = int(left // TILE_SIZE_PX), int(top // TILE_SIZE_PX)
    tile_x1 = int((left + width) // TILE_SIZE_PX)
    tile_y1 = int((top + height) // TILE_SIZE_PX)

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    max_index = 2**zoom
    for tile_y in range(tile_y0, tile_y1 + 1):
        if not 0 <= tile_y < max_index:
            continue  # ausserhalb der Weltkarte (Pol) — bleibt transparent
        for tile_x in range(tile_x0, tile_x1 + 1):
            wrapped_x = tile_x % max_index  # Datumsgrenze: Kacheln laufen rundherum weiter
            tile_path = fetch_tile(
                zoom, wrapped_x, tile_y, cache_dir,
                tile_server_url=tile_server_url, fetcher=fetcher,
            )
            tile = Image.open(tile_path).convert("RGBA")
            canvas.alpha_composite(
                tile,
                (round(tile_x * TILE_SIZE_PX - left), round(tile_y * TILE_SIZE_PX - top)),
            )
    return canvas


def _dwell_schedule(
    track: list[dict], pois: list[dict], *, frame_count: int, fps: float, dwell_s: float
) -> list[int]:
    """Reveal-Index je Frame — mit Pause, sobald die Route einen POI erreicht.

    Ohne Haltezeit rauscht der Marker an einem Ort vorbei, bevor sein Name lesbar ist. Die
    Pause verlaengert den Clip **nicht**: die Gesamtdauer bleibt `dur`, die Bewegung dazwischen
    wird entsprechend zuegiger. So bleibt die Timeline-Zeitrechnung unangetastet.
    """
    if dwell_s <= 0 or not pois or not track:
        # Ohne Track gibt es keine Position, an der gehalten werden koennte — `min(range(0))`
        # waere hier ein ValueError statt einer sinnvollen Antwort.
        return [max(2, round(len(track) * (i + 1) / frame_count)) for i in range(frame_count)]

    stop_indices = sorted(
        {
            min(
                range(len(track)),
                key=lambda i: (track[i]["lat"] - poi["lat"]) ** 2
                + (track[i]["lon"] - poi["lon"]) ** 2,
            )
            for poi in pois
        }
    )
    dwell_frames = max(1, round(dwell_s * fps))
    moving_frames = max(1, frame_count - dwell_frames * len(stop_indices))

    schedule: list[int] = []
    index = 0.0
    step = len(track) / moving_frames
    remaining = set(stop_indices)
    while len(schedule) < frame_count:
        current = max(2, min(len(track), round(index)))
        schedule.append(current)
        hit = next((s for s in sorted(remaining) if s <= current), None)
        if hit is not None:
            remaining.discard(hit)
            schedule.extend([current] * min(dwell_frames, frame_count - len(schedule)))
        index += step
    return schedule[:frame_count]


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
    pois: list[dict] | None = None,
    viewport: str = "fit",
    zoom: int | None = None,
    ease_s: float = 1.0,
    dwell_s: float = 0.0,
    tile_cache_dir: Path | None = None,
    tile_server_url: str = DEFAULT_TILE_SERVER,
    fetcher: TileFetcher | None = None,
) -> list[Path]:
    """PNG-Sequenz mit Alpha: Route-Reveal (Linie waechst ueber die Dauer) + Positions-Marker.

    Ein Frame pro `1/fps` Sekunden ueber `dur` Sekunden. `track` braucht mindestens 2 Punkte
    (z.B. aus `frameforge.gpx.parse_gpx`).

    `marker_icon`: eigenes Icon (PNG mit Alpha, mittig auf die aktuelle Position gestempelt)
    statt des Default-Punkts — kein Auto-/Figur-Symbol ist hier fest eingebaut, jedes Projekt
    liefert sein eigenes (`design/assets/`).
    `basemap`: vorgerendertes Kartenbild (siehe `render_basemap`) als Hintergrund statt
    transparent — Grösse muss zu `(width, height)` passen.
    `pois`: feste Orte (aus `frameforge.gpx.parse_locations` / `locations.csv`) — auf jedem
    Frame als kleiner Punkt + Name eingezeichnet, im selben Koordinatensystem wie die Route.

    `viewport`:
    - `"fit"` (Default, **unveraendertes Verhalten**): fester Ausschnitt ueber die Bounding-Box
      des gesamten Tracks, nur der Marker bewegt sich.
    - `"follow"`: der Ausschnitt zentriert sich auf die aktuelle Position (Web-Mercator bei
      `zoom`), geglaettet ueber ein gleitendes Fenster von `ease_s` Sekunden, damit die Karte
      nicht zittert. Mit `tile_cache_dir` wird je Frame der passende Kartenausschnitt aus dem
      Kachel-Cache geholt (`basemap_viewport`); `basemap` ist in diesem Modus wirkungslos, weil
      ein festes Bild einen wandernden Ausschnitt nicht abbilden kann.

    `dwell_s`: Haltezeit, sobald die Route einen POI erreicht — ohne sie ist der Ortsname nicht
    lesbar. Die Gesamtdauer bleibt `dur`.
    """
    if len(track) < 2:
        raise ValueError("track braucht mindestens 2 Punkte fuer eine Route")
    if viewport not in {"fit", "follow"}:
        raise ValueError(f"viewport muss 'fit' oder 'follow' sein, nicht {viewport!r}")
    if viewport == "follow" and zoom is None:
        raise ValueError("viewport='follow' braucht ein zoom-Level (Web-Mercator)")
    if viewport == "fit" and basemap is not None and basemap.size != (width, height):
        raise ValueError(f"basemap-Groesse {basemap.size} passt nicht zu ({width}, {height})")

    out_dir.mkdir(parents=True, exist_ok=True)
    frame_count = max(1, round(fps * dur))
    icon = Image.open(marker_icon).convert("RGBA") if marker_icon else None
    pois = pois or []
    reveal_counts = _dwell_schedule(track, pois, frame_count=frame_count, fps=fps, dwell_s=dwell_s)

    if viewport == "fit":
        project = _make_projector(track, width, height, MARGIN_PX)
        points_px = [project(p["lat"], p["lon"]) for p in track]
        poi_px = [(project(p["lat"], p["lon"]), p.get("name", "")) for p in pois]
        centers = None
    else:
        world_px = [latlon_to_pixel(p["lat"], p["lon"], zoom) for p in track]
        poi_world = [(latlon_to_pixel(p["lat"], p["lon"], zoom), p.get("name", "")) for p in pois]
        raw_centers = [world_px[min(c, len(world_px)) - 1] for c in reveal_counts]
        centers = smooth_centers(raw_centers, max(1, round(ease_s * fps)))

    outputs: list[Path] = []
    for i in range(frame_count):
        reveal_count = min(reveal_counts[i], len(track))

        if viewport == "fit":
            visible = points_px[:reveal_count]
            frame_pois = poi_px
            image = (
                basemap.copy()
                if basemap is not None
                else Image.new("RGBA", (width, height), (0, 0, 0, 0))
            )
        else:
            center_x, center_y = centers[i]
            left, top = center_x - width / 2, center_y - height / 2
            visible = [(x - left, y - top) for x, y in world_px[:reveal_count]]
            frame_pois = [((x - left, y - top), name) for (x, y), name in poi_world]
            if tile_cache_dir is not None:
                image = basemap_viewport(
                    pixel_to_latlon(center_x, center_y, zoom),
                    zoom,
                    (width, height),
                    tile_cache_dir,
                    tile_server_url=tile_server_url,
                    fetcher=fetcher,
                )
            else:
                image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        draw = ImageDraw.Draw(image)
        for (px, py), name in frame_pois:
            if not (-MARGIN_PX <= px <= width + MARGIN_PX and -MARGIN_PX <= py <= height + MARGIN_PX):
                continue  # ausserhalb des Ausschnitts (nur im Follow-Modus moeglich)
            draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=MARKER_COLOR)
            if name:
                draw.text((px + 6, py - 6), name, fill=MARKER_COLOR)
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


# `→` und `↑` fehlen in den verfuegbaren Fonts — cairosvg rendert dafuer ein leeres Kaestchen
# (beides am gerenderten Bild geprueft, nicht vermutet). Fuer Bildtexte deshalb Ersatzzeichen;
# in `assets.json`, Reports und Logs bleiben die echten Zeichen stehen.
HUD_ARROW = "—"
HUD_ASCENT_PREFIX = "+"


def _profile_polyline(
    heights: list[float | None], box: tuple[int, int, int, int], upto: int
) -> tuple[str, tuple[float, float]]:
    """`(SVG-Polyline, Markerposition)` des Hoehenprofils innerhalb `box` = `(x, y, w, h)`."""
    x0, y0, w, h = box
    known = [(i, v) for i, v in enumerate(heights) if v is not None]
    if len(known) < 2:
        return "", (x0, y0 + h)
    lo = min(v for _, v in known)
    span = max(max(v for _, v in known) - lo, 1e-6)
    last = max(known[0][0], min(upto, known[-1][0]))

    def point(index: int, value: float) -> tuple[float, float]:
        x = x0 + w * index / max(len(heights) - 1, 1)
        y = y0 + h - h * (value - lo) / span
        return round(x, 1), round(y, 1)

    points = [point(i, v) for i, v in known]
    marker = min(points, key=lambda p: abs(p[0] - point(last, lo)[0]))
    return " ".join(f"{x},{y}" for x, y in points), marker


def render_hud_frames(
    out_dir: Path,
    *,
    template_path: Path,
    tokens: dict,
    fps: float,
    dur: float,
    width: int,
    height: int,
    track: list[dict],
    stage: dict | None = None,
    heights: list[float | None] | None = None,
    step_s: float = 1.0,
    dwell_s: float = 0.0,
    pois: list[dict] | None = None,
    arrow: str = HUD_ARROW,
) -> list[Path]:
    """Etappen-HUD als eigene Overlay-Sequenz (Plan 0003 §B3): Tag, Etappe, km, Hoehe, Profil.

    **Nicht pro Frame gerendert** — ein SVG→PNG je `step_s` Sekunden (Default 1 s) reicht
    voellig, die Zahlen aendern sich langsam. Die Frames dazwischen wiederholen dasselbe Bild
    (Hardlink-frei: dieselbe Datei wird mehrfach geschrieben, damit `frame_%04d.png` lueckenlos
    ist und `encode_alpha_video` unveraendert funktioniert).

    Die Reveal-Position folgt derselben Zeitrechnung wie `render_route_frames` (inklusive
    `dwell_s`), damit Karte und HUD synchron laufen.
    """
    from frameforge.design import build_svg_from_tokens, overlay_tokens, render_svg_to_png
    from frameforge.gpx import cumulative_km, stage_label, total_ascent_m

    out_dir.mkdir(parents=True, exist_ok=True)
    frame_count = max(1, round(fps * dur))
    reveal_counts = _dwell_schedule(
        track, pois or [], frame_count=frame_count, fps=fps, dwell_s=dwell_s
    )
    # Ohne Trackpunkte gibt es keine Position, keinen Kilometerstand und kein Profil — das HUD
    # zeigt dann nur Tag und Etappe. Ein leerer Track ist kein Fehler (eine Etappe ohne
    # aufgezeichnete Spur), aber ohne diesen Fallback lief `km_at[index]` in einen IndexError.
    km_at = cumulative_km(track) or [0.0]
    step_frames = max(1, round(step_s * fps))
    # Das Profil gehoert **in** das HUD-Panel, nicht irgendwohin ins Bild. Die Box wird deshalb
    # aus denselben Tokens abgeleitet, die das Template fuer das Panel nutzt (`overlay_tokens`)
    # — vorher standen hier eigene Konstanten (`height * 0.10`), sodass das Diagramm oben links
    # schwebte, waehrend das Panel unten lag (am echten Material gesehen, 2026-08-03).
    layout = overlay_tokens(tokens, width=width, height=height)
    inset = round(height * 0.02)
    profile_box = (
        layout["text_x"],
        layout["stats_y"] + inset,
        layout["panel_width"] - (layout["text_x"] - layout["margin"]) - inset,
        round(height * 0.09),
    )

    outputs: list[Path] = []
    cache: dict[int, str] = {}
    for i in range(frame_count):
        bucket = i // step_frames
        if bucket not in cache:
            index = max(0, min(reveal_counts[i], len(track)) - 1)
            polyline, (marker_x, marker_y) = _profile_polyline(
                heights or [], profile_box, index
            )
            elevation = heights[index] if heights and index < len(heights) else None
            km_label = f"{km_at[min(index, len(km_at) - 1)]:.0f} km" if track else ""
            # Kumulierte Hoehenmeter *bis zur aktuellen Position* (Plan 0003 §B1) — der Wert
            # waechst mit der Fahrt, deshalb je Stufe neu ueber den bereits gefahrenen Teil.
            ascent = total_ascent_m((heights or [])[: index + 1])
            content = {
                "day_label": f"TAG {stage['day']}" if stage else "",
                "stage_label": stage_label(stage, arrow=arrow) if stage else "",
                "date_label": stage["date"].isoformat() if stage else "",
                "km_label": km_label,
                "elevation_label": f"{elevation:.0f} m" if elevation is not None else "",
                "ascent_label": f"{HUD_ASCENT_PREFIX}{ascent:.0f} hm" if ascent > 0 else "",
                "profile_points": polyline,
                "marker_x": marker_x,
                "marker_y": marker_y,
            }
            cache[bucket] = build_svg_from_tokens(
                template_path, overlay_tokens(tokens, width=width, height=height, **content)
            )
        target = out_dir / f"frame_{i:04d}.png"
        render_svg_to_png(cache[bucket], target)
        outputs.append(target)
    return outputs


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
