"""`python -m frameforge <cmd>` — die in Plan und CLAUDE.md dokumentierte Aufrufform.

Ohne diese Datei bricht der Aufruf mit "No module named frameforge.__main__" ab, obwohl er
an ~10 Stellen der Doku so steht (gefunden 2026-08-09 beim Start des Chunk-Renders). Der
Gate-Hook erkennt genau diese Form, deshalb wird sie hier nachgereicht statt die Doku auf
`frameforge.cli` bzw. das Konsolenskript umzuschreiben.
"""

from frameforge.cli import app

if __name__ == "__main__":
    app()
