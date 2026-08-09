# Schriften

Avenir Next (aus den Filmen) ist eine Apple-Systemschrift und darf nicht auf den Server.
Empfohlen wird stattdessen dieses Paar — beide unter **SIL Open Font License 1.1**, also frei
selbst hostbar, kommerziell wie privat.

## Display / UI: Schibsted Grotesk

Eine zeitgenössische Grotesk, gezeichnet für den norwegischen Medienkonzern Schibsted — die
Verbindung zum Thema ist also echt und nicht dekorativ. Etwas mehr Charakter als die üblichen
Verdächtigen: leicht verkürzte Versalien, offene Punzen, sehr gute Ziffern (auch tabellarisch).
Steht in großen Graden ruhig und in kleinen Labels präzise.

- Familie: Schibsted Grotesk (variabel, `wght` 400–900)
- Benötigte Schnitte: Regular 400, Medium 500, SemiBold 600, Bold 700
- Bezug: Google Fonts (`fonts.google.com/specimen/Schibsted+Grotesk`) oder direkt
  `github.com/Schibsted-Media-Group/schibsted-grotesk`
- Lizenz: SIL OFL 1.1

## Fließtext: Source Serif 4

Ruhige, gut ausgebaute Lesetype mit optischen Größen. Auf dunklem Grund trägt eine Serife den
längeren deutschen Fließtext deutlich angenehmer als eine weitere Grotesk — und setzt Text und
Interface sichtbar voneinander ab.

- Familie: Source Serif 4 (variabel, `wght` 300–700, `opsz`)
- Benötigte Schnitte: Regular 400, SemiBold 600 (kursiv optional)
- Bezug: Google Fonts (`fonts.google.com/specimen/Source+Serif+4`) oder
  `github.com/adobe-fonts/source-serif`
- Lizenz: SIL OFL 1.1

## Dateien, die ich brauche

Als **woff2** nach `site/assets/fonts/` — die `@font-face`-Regeln in
`site/assets/css/fonts.css` erwarten genau diese Namen:

```
SchibstedGrotesk-Variable.woff2          (Pflicht)
SchibstedGrotesk-VariableItalic.woff2    (optional)
SourceSerif4-Variable.woff2              (Pflicht)
SourceSerif4-VariableItalic.woff2        (optional)
```

Variable Schnitte reichen völlig aus und sparen Requests. Als Untergrenze mit statischen
Dateien: 400 und 600 je Familie. Solange die Dateien fehlen, greift der System-Fallback aus
`tokens.css` (Helvetica/Arial bzw. Georgia) — die Seite bleibt lesbar, sieht aber anders aus.

Bitte die Lizenztexte (`OFL.txt`) mit auf den Server legen und im Impressum verlinken.
