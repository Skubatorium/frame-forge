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
    type: str
    dur: float = Field(gt=0)


class Effect(BaseModel):
    """Generischer Effekt (z.B. Ken-Burns). Zusaetzliche Parameter (`from`, `to`, ...) sind erlaubt."""

    model_config = ConfigDict(extra="allow")

    type: str


class VideoClip(BaseModel):
    id: str
    asset: str
    src_in: float = Field(ge=0)
    src_out: float
    tl_in: float = Field(ge=0)
    speed: float = Field(default=1.0, gt=0)
    transition_in: Transition | None = None
    transition_out: Transition | None = None
    effects: list[Effect] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_in_out(self) -> VideoClip:
        if self.src_out <= self.src_in:
            raise ValueError(f"Clip '{self.id}': src_out muss groesser sein als src_in")
        return self

    @property
    def duration(self) -> float:
        return (self.src_out - self.src_in) / self.speed


class OverlayClip(BaseModel):
    id: str
    png: str
    tl_in: float = Field(ge=0)
    dur: float = Field(gt=0)
    anim: dict[str, str] | None = None


class MapClip(BaseModel):
    id: str
    clip: str
    tl_in: float = Field(ge=0)
    dur: float = Field(gt=0)
    blend: str = "over"


class AudioClip(BaseModel):
    id: str
    src: str | None = None
    asset: str | None = None
    type: str | None = None
    tl_in: float = Field(ge=0)
    dur: float | None = None
    gain_db: float | None = None
    duck_music_db: float | None = None

    @model_validator(mode="after")
    def _check_source(self) -> AudioClip:
        if not self.src and not self.asset:
            raise ValueError(f"Audio-Clip '{self.id}': entweder 'src' oder 'asset' erforderlich")
        return self


class Tracks(BaseModel):
    video: list[VideoClip] = Field(default_factory=list)
    overlay: list[OverlayClip] = Field(default_factory=list)
    map: list[MapClip] = Field(default_factory=list)
    audio: list[AudioClip] = Field(default_factory=list)

    def all_ids(self) -> list[str]:
        return [c.id for c in (*self.video, *self.overlay, *self.map, *self.audio)]


class Timeline(BaseModel):
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
