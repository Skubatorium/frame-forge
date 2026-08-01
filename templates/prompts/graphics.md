# Grafik-Prompt-Vorlage

Vorlage für die Prompts, die der `design-system`-Agent nach `projects/<projekt>/design/prompts.md`
schreibt, wenn Grafiken fehlen. Du kopierst den fertigen Prompt in einen Bildgenerator
(Midjourney, DALL·E, Ideogram …) oder gibst ihn einem Designer, lädst das Ergebnis herunter und
legst es unter `projects/<projekt>/design/assets/<dateiname>` ab.

## Konventionen (immer einhalten)

- **Format:** PNG. Freisteller/Logo/Marker **mit transparentem Hintergrund** (Alpha).
- **Auflösung:** so groß wie im Film gebraucht, mindestens 1024 px lange Kante; Marker-Icons
  512×512 px, quadratisch.
- **Stil an die Projekt-Tokens koppeln:** Farben aus `design/tokens.yaml`
  (`primary_color`/`accent_color`/`text_color`) und die Stimmung des Projekts nennen, damit die
  Grafik zur visuellen Familie passt.
- **Kein Text in generierten Bildern** (Text macht das SVG-Overlay-System sauberer und
  lesbarer) — außer es ist explizit ein Logo-Schriftzug.
- **Dateiname = Verwendungszweck**, klein, mit Bindestrich (`logo.png`, `marker-icon.png`,
  `freisteller-familie.png`, `textur-papier.png`).

## Prompt-Skelett (pro fehlender Grafik ausfüllen)

```
<Was> für <Projekt>, Stil: <3–5 Adjektive aus dem Designsystem>.
Farbwelt: <primary/accent/text aus tokens.yaml>.
Hintergrund: transparent (PNG mit Alpha).  Kein Text.
Auflösung: <z. B. 512×512 quadratisch für Marker>.
<Zusätzliche Vorgaben je Typ, siehe unten>.
```

## Bausteine je Grafik-Typ

- **Logo / Titelmarke:** minimal, funktioniert klein und auf hellem wie dunklem Bild;
  einfarbig oder in Akzentfarbe; als Vektor gedacht (klare Kanten, keine Fotorealistik).
- **Kartenmarker / Positions-Icon:** einfaches, gut erkennbares Symbol, 512×512, mittig,
  transparente Ränder — wird per `map.render_route_frames(marker_icon=…)` auf die Karte
  gestempelt.
- **Freisteller (Person/Auto):** sauber freigestellte Silhouette/Figur vor transparentem
  Grund; von der Seite oder in Bewegungsrichtung, falls entlang einer Route animiert.
- **Textur / Hintergrund:** dezent, gekachelt/nahtlos wenn wiederholt; niedriger Kontrast,
  damit Text darüber lesbar bleibt.

## Bausteine für die neuen Overlay-Typen (Plan 0003 §D2)

Diese Grafiken sind **optional** — alle Templates rendern auch ohne sie (dann Farbfläche statt
Bild). Sie werten Titel, Kapitelmarken und Karte auf, wo reine Typo zu nüchtern wirkt.

- **Titelkarten-Hintergrund** (`title-bg.png`): formatfüllend, ruhige Fläche mit Tiefe —
  Verlauf, Struktur oder abstrahierte Landschaftsform in der Projektfarbwelt. **Mitte und
  unteres Drittel bewusst ruhig halten**, dort steht der Titel. Kein Text, kein hoher Kontrast
  in der Textzone. Wird über `background_layer` in `title-card.svg` eingesetzt.
- **Kapitelmarke** (`chapter-bg.png`): dasselbe Prinzip, kleiner eingesetzt und dezenter —
  sie taucht mehrfach im Film auf und darf nicht jedes Mal die Aufmerksamkeit stehlen.
- **Landes-/Regions-Motiv** (`motif-<region>.png`): stilisiertes Wappen-, Flaggen- oder
  Landschaftsmotiv als Akzent, einfarbig oder zweifarbig, freigestellt. Keine realen Hoheits-
  zeichen nachbauen, wenn eine Abstraktion reicht.
- **Karten-Rahmen** (`map-frame.png`): Rahmen/Vignette für die eingeblendete Karte, innen
  transparent, außen weich auslaufend — trennt die Karte vom Videobild, ohne sie zu erdrücken.
  Exakt in der Pixelgröße des Karten-Clips.
- **Fahrzeug-/Positions-Icon** (`marker-vehicle.png`): 512×512, transparent, Blickrichtung
  nach rechts (Fahrtrichtung), einfache Silhouette. Wird per
  `map.render_route_frames(marker_icon=…)` auf die aktuelle Position gestempelt.

**Größenregel:** Hintergründe in der Zielauflösung des Films liefern (also 3840×2160, wenn 4K
gerendert wird) — Overlay-Templates skalieren Text relativ zur Bildhöhe, Bitmaps nicht.
