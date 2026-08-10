#!/usr/bin/env python
"""Haengt an jeden Asset-Verweis in den HTML-Dateien einen Inhalts-Hash an.

Hintergrund: Vor Cloudflare liefert der Edge-Cache Stylesheets und Bilder mit
`max-age=14400` aus. Die HTML kommt frisch durch (`cf-cache-status: DYNAMIC`),
die Assets nicht — nach einem Deploy zeigt also neues HTML stundenlang auf
alte CSS. Genau so verschwand der Sprachumschalter: die Kuerzel waren im HTML
schon weg, die Flaggen-Regeln in der ausgelieferten CSS noch nicht da.

Loesung ohne Server-Konfiguration: `…/styles.css` wird zu `…/styles.css?v=ab12cd34`.
Aendert sich die Datei, aendert sich die URL, und der Cache muss neu laden.
Aendert sie sich nicht, bleibt die URL stabil und der Cache greift weiter.

Arbeitet **in-place auf einem Build-Verzeichnis**, nie auf `public/` selbst.

    python cache-bust.py <build-verzeichnis>
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

# Verweise auf /assets/… in href, src, poster und url(). Der Query-String wird
# nur an Dateien mit diesen Endungen gehaengt — Schriften referenziert die CSS
# selbst, die bekommt ihren Hash ueber die CSS-URL mit. Lizenztexte (.txt) sind
# bewusst aussen vor: sie aendern sich nie.
PATTERN = re.compile(
    r'(?P<pre>(?:href|src|poster)="|url\(\'|url\()'
    r'(?P<path>/assets/[^"\')?]+\.(?:css|js|jpg|jpeg|png|svg|webp))'
)


def short_hash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"Kein Verzeichnis: {root}")
        return 1

    hashes: dict[str, str] = {}
    missing: set[str] = set()

    def repl(m: re.Match) -> str:
        rel = m.group("path")
        if rel not in hashes:
            target = root / rel.lstrip("/")
            if not target.exists():
                missing.add(rel)
                return m.group(0)
            hashes[rel] = short_hash(target)
        return f'{m.group("pre")}{rel}?v={hashes[rel]}'

    touched = 0
    for html in sorted(root.rglob("*.html")):
        text = html.read_text()
        new = PATTERN.sub(repl, text)
        if new != text:
            html.write_text(new)
            touched += 1

    print(f"cache-bust: {touched} HTML-Dateien, {len(hashes)} Assets versioniert")
    for rel in sorted(missing):
        print(f"  ! nicht gefunden, unveraendert gelassen: {rel}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
