"""Timeline-Schema als Pydantic-Modell.

Single Source of Truth fuer `timeline.json` (siehe Plan Abschnitt 4 und 9).
`frameforge.render` baut daraus den FFmpeg-Filtergraph, `frameforge.nle`
schreibt dieselbe Struktur als FCPXML/OTIO — beide lesen ausschliesslich
dieses Schema.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TimelineValidationError(ValueError):
    """Semantischer Fehler in einer Timeline, der ueber Pydantic-Feldvalidierung hinausgeht."""


class Transition(BaseModel):
    """Übergang am Clip-Anfang. `type` steuert die Umsetzung im Renderer.

    `fade`/`dissolve`/`slow_dissolve`/`crossfade` blenden die beiden Clips ineinander (`xfade`)
    und **verkürzen** die Gesamtlänge um `dur`. `black` blendet nach Schwarz, hält optional
    `hold` Sekunden und blendet wieder auf — das **verlängert** die Timeline um `dur + hold`
    (Plan 0003 §C). Alles andere ist ein harter Schnitt.
    """

    type: str
    dur: float = Field(gt=0)
    hold: float = Field(default=0.0, ge=0)  # nur bei `black`: Standzeit auf Schwarz


class Effect(BaseModel):
    """Generischer Effekt (z.B. Ken-Burns). Zusaetzliche Parameter (`from`, `to`, ...) sind erlaubt."""

    model_config = ConfigDict(extra="allow")

    type: str


class ColorMatch(BaseModel):
    """Milde Angleichung eines Clips an die gemeinsame Referenz (Plan 0003 §H2).

    Steht **pro Clip in der Timeline**, nicht als versteckte Renderer-Logik: nachvollziehbar,
    von Hand überschreibbar, reproduzierbar und im NLE-Export mit dabei.
    """

    brightness: float = Field(default=0.0, ge=-1.0, le=1.0)  # eq-Parameter
    saturation: float = Field(default=1.0, ge=0.0, le=3.0)
    temperature: float = Field(default=0.0, ge=-1.0, le=1.0)  # >0 waermer, <0 kuehler


class VideoClip(BaseModel):
    # extra="allow": handgepflegte Zusatzfelder (Notizen, Herkunftsvermerke) ueberleben
    # jedes Zurueckschreiben der Datei. Siehe Kommentar an `Timeline`.
    model_config = ConfigDict(extra="allow")

    id: str
    asset: str
    src_in: float = Field(ge=0)
    src_out: float
    tl_in: float = Field(ge=0)
    speed: float = Field(default=1.0, gt=0)
    transition_in: Transition | None = None
    transition_out: Transition | None = None
    effects: list[Effect] = Field(default_factory=list)
    color_match: ColorMatch | None = None  # None = keine Angleichung (Default, wie bisher)

    @model_validator(mode="after")
    def _check_in_out(self) -> VideoClip:
        if self.src_out <= self.src_in:
            raise ValueError(f"Clip '{self.id}': src_out muss groesser sein als src_in")
        return self

    @property
    def duration(self) -> float:
        return (self.src_out - self.src_in) / self.speed


class OverlayClip(BaseModel):
    # extra="allow": handgepflegte Zusatzfelder (Notizen, Herkunftsvermerke) ueberleben
    # jedes Zurueckschreiben der Datei. Siehe Kommentar an `Timeline`.
    model_config = ConfigDict(extra="allow")

    id: str
    png: str
    tl_in: float = Field(ge=0)
    dur: float = Field(gt=0)
    # Freies String-Dict (kein eigenes Feld je Animationsart) -- `frameforge.render` interpretiert
    # die Schluessel, unbekannte werden ignoriert. Bekannt: `fade_in_s`/`fade_out_s` (Alpha-Fade,
    # bestehend) sowie `slide_from_px`/`slide_in_s`/`drift_px`/`drift_period_s` (horizontale
    # Slide-in-/Drift-Bewegung, siehe `render._overlay_x_expr`). Fehlen alle Slide/Drift-Schluessel
    # (0/None), bleibt die Overlay-Position exakt beim bisherigen statischen `x=0`.
    anim: dict[str, str] | None = None


class MapClip(BaseModel):
    # extra="allow": handgepflegte Zusatzfelder (Notizen, Herkunftsvermerke) ueberleben
    # jedes Zurueckschreiben der Datei. Siehe Kommentar an `Timeline`.
    model_config = ConfigDict(extra="allow")

    id: str
    clip: str
    tl_in: float = Field(ge=0)
    dur: float = Field(gt=0)
    blend: str = "over"


class AudioClip(BaseModel):
    # extra="allow": handgepflegte Zusatzfelder (Notizen, Herkunftsvermerke) ueberleben
    # jedes Zurueckschreiben der Datei. Siehe Kommentar an `Timeline`.
    model_config = ConfigDict(extra="allow")

    id: str
    src: str | None = None
    asset: str | None = None
    type: str | None = None
    tl_in: float = Field(ge=0)
    dur: float | None = None
    # Source-Offset: wo im Quelltrack der Clip beginnt (analog zu VideoClip.src_in).
    # Default 0 = Trackanfang, wie bisher — bestehende Timelines rendern unveraendert.
    src_in: float = Field(default=0.0, ge=0)
    gain_db: float | None = None
    duck_music_db: float | None = None
    # Ein-/Ausblendung dieses Clips (Plan 0003 §F). Default 0 = harter Einsatz wie bisher.
    fade_in_s: float = Field(default=0.0, ge=0)
    fade_out_s: float = Field(default=0.0, ge=0)

    @model_validator(mode="after")
    def _check_source(self) -> AudioClip:
        if not self.src and not self.asset:
            raise ValueError(f"Audio-Clip '{self.id}': entweder 'src' oder 'asset' erforderlich")
        return self


class Tracks(BaseModel):
    # extra="allow": handgepflegte Zusatzfelder (Notizen, Herkunftsvermerke) ueberleben
    # jedes Zurueckschreiben der Datei. Siehe Kommentar an `Timeline`.
    model_config = ConfigDict(extra="allow")

    video: list[VideoClip] = Field(default_factory=list)
    overlay: list[OverlayClip] = Field(default_factory=list)
    map: list[MapClip] = Field(default_factory=list)
    audio: list[AudioClip] = Field(default_factory=list)

    def all_ids(self) -> list[str]:
        return [c.id for c in (*self.video, *self.overlay, *self.map, *self.audio)]


class Timeline(BaseModel):
    # `extra="allow"`: `timeline.json` ist Single Source of Truth und wird von Agenten und von
    # Hand gepflegt. Ohne das verlieren wir alle Felder, die das Schema (noch) nicht kennt — z.B.
    # Notizen des timeline-builders — sobald ein Kommando die Datei zurueckschreibt
    # (`frameforge color-match`, `Timeline.save`). Stiller Datenverlust in der wichtigsten
    # Datei des Projekts; Audit-Befund F4.
    model_config = ConfigDict(extra="allow")

    version: int = 1
    export: str
    fps: float = Field(gt=0)
    resolution: tuple[int, int]
    duration: float = Field(gt=0)
    tracks: Tracks = Field(default_factory=Tracks)

    # -- IO ---------------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> Timeline:
        return cls.model_validate_json(path.read_text())

    def save(self, path: Path) -> None:
        path.write_text(self.model_dump_json(indent=2, exclude_none=True))

    # -- Semantische Validierung, ueber Feld-Constraints hinaus -----------

    def validate_semantics(self) -> None:
        """Prueft Invarianten, die einzelne Felder allein nicht abdecken.

        Raises:
            TimelineValidationError: bei doppelten IDs oder Clips ausserhalb
                der Timeline-Dauer.
        """
        ids = self.tracks.all_ids()
        duplicates = {i for i in ids if ids.count(i) > 1}
        if duplicates:
            raise TimelineValidationError(f"Doppelte Clip-IDs: {sorted(duplicates)}")

        for clip in self.tracks.video:
            end = clip.tl_in + clip.duration
            if end > self.duration + 1e-6:
                raise TimelineValidationError(
                    f"Video-Clip '{clip.id}' endet bei {end:.2f}s, "
                    f"Timeline-Dauer ist nur {self.duration:.2f}s"
                )
        for clip in (*self.tracks.overlay, *self.tracks.map, *self.tracks.audio):
            dur = clip.dur or 0.0
            end = clip.tl_in + dur
            if end > self.duration + 1e-6:
                raise TimelineValidationError(
                    f"Clip '{clip.id}' endet bei {end:.2f}s, "
                    f"Timeline-Dauer ist nur {self.duration:.2f}s"
                )
