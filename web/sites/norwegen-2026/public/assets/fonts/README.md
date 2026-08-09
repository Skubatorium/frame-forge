# Schriften — fehlen noch

`assets/css/fonts.css` erwartet genau zwei Dateien in diesem Ordner:

| Datei | Familie | Bezug | Lizenz |
|---|---|---|---|
| `SchibstedGrotesk-Variable.woff2` | Schibsted Grotesk (wght 400–900) | fonts.google.com/specimen/Schibsted+Grotesk | SIL OFL 1.1 |
| `SourceSerif4-Variable.woff2` | Source Serif 4 (wght 300–700) | fonts.google.com/specimen/Source+Serif+4 | SIL OFL 1.1 |

Solange sie fehlen, greift der System-Fallback aus `tokens.css` — die Seite funktioniert,
sieht aber deutlich generischer aus.

Google Fonts liefert TTF-Archive. Umwandeln nach woff2 z. B. mit
[`fonttools`](https://pypi.org/project/fonttools/):

```bash
pip install "fonttools[woff]" brotli
fonttools ttLib.woff2 compress -o SchibstedGrotesk-Variable.woff2 SchibstedGrotesk[wght].ttf
fonttools ttLib.woff2 compress -o SourceSerif4-Variable.woff2 SourceSerif4[opsz,wght].ttf
```

Alternativ direkt woff2 von `gwfh.mranftl.com` oder aus den GitHub-Repos der Familien laden.

**Nicht** über `fonts.googleapis.com` einbinden — die Seite darf keine externen Requests
machen.
