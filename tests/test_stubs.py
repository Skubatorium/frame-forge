"""Regressionstest: alle noch nicht implementierten Modul-Funktionen werfen

`NotImplementedError` statt stillschweigend `None` zurueckzugeben oder
abzustuerzen. Verhindert, dass ein Stub versehentlich "erfolgreich" durchlaeuft.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from frameforge import nle
from frameforge import render as render_module


@pytest.mark.parametrize(
    "call",
    [
        lambda: render_module.render_final(None, None, None),
        lambda: nle.export_fcpxml(None, Path("x.fcpxml")),
        lambda: nle.export_otio(None, Path("x.otio")),
    ],
)
def test_stub_raises_not_implemented(call):
    with pytest.raises(NotImplementedError):
        call()
