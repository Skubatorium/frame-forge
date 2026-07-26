"""Regressionstest: alle noch nicht implementierten Modul-Funktionen werfen

`NotImplementedError` statt stillschweigend `None` zurueckzugeben oder
abzustuerzen. Verhindert, dass ein Stub versehentlich "erfolgreich" durchlaeuft.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from frameforge import audio, nle, render


@pytest.mark.parametrize(
    "call",
    [
        lambda: audio.analyze_track(Path("x.wav")),
        lambda: audio.duck_curve({}, [], duck_db=-14),
        lambda: render.build_filtergraph(None),
        lambda: nle.export_fcpxml(None, Path("x.fcpxml")),
        lambda: nle.export_otio(None, Path("x.otio")),
    ],
)
def test_stub_raises_not_implemented(call):
    with pytest.raises(NotImplementedError):
        call()
