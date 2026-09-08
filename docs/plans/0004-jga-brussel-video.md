# Plan 0004 — JGA Brüssel: neues FrameForge-Projekt + neue Fähigkeiten (v3)

*v2, 2026-09-07: überarbeitet nach Rückfragen. Änderungen ggü. v1 am Ende jedes betroffenen
Abschnitts als „**Update v2**" markiert. Größte Korrektur: die Aussage, dass „alle Assets
zeigen" rechnerisch unmöglich sei, war zu pauschal — siehe §5.*

*v3, 2026-09-07 (gleicher Tag, zweite Runde): Ziellänge ist ab jetzt ein offener Richtwert
(circa 6-7 statt starrer 5,5 Minuten), Cast-Intro-Position korrigiert (Karaoke-Bar „Red",
mitten in Akt 2, nicht am Akt-Übergang), Intro-/Outro-Bild + Abspann-Karte ergänzt,
Designsystem-Vorschlag anhand eines von Christian bereitgestellten Stilreferenz-Bilds
präzisiert (§4) — Bild liegt jetzt unter
`web/sites/michael-jga-2026/design/reference/style-reference-jga-poster.png`.*

## Kontext

Christian will aus Fotos/Videos seines Junggesellenabschieds (Brüssel, Wochenende) einen
~5,5-Minuten-Film bauen: zwei Songs, zwei komplett unterschiedliche Stimmungen (gediegener
Freitag/Samstagvormittag → eskalierende Partynacht), dazu eine passende, passwortgeschützte
Website unter `micha-jga.skubus.de` — nach demselben Muster wie `norwegen.skubus.de`. Fotos
und Videos werden gerade noch zusammengetragen (fertig vermutlich morgen); Projekt-Grundgerüst,
Designsystem und Musik lassen sich aber schon jetzt vorbereiten.

Recherchegrundlage wie v1, ergänzt um: `frameforge/relink.py`, `templates/project/*`,
`templates/prompts/graphics.md`, `templates/prompts/music.md`, eine Prüfung der
Ausführungsumgebung (siehe §0) und eine Websuche zu freien Sound-Effekt-Quellen (§6).

---

## 0. Wichtig — was ich aus dieser Session heraus wirklich ausführen kann

**Neu in v2, weil es dein „lass uns jetzt loslegen" direkt betrifft:** Ich habe versucht,
`frameforge doctor` über die Ordner-Anbindung auszuführen. Ergebnis: **das geht von hier aus
nicht.** `.venv/bin/python` in deinem Repo ist ein Symlink auf einen Python-Interpreter unter
`/Users/christianskubatz/.local/share/uv/...` — das liegt auf deinem Mac, aber außerhalb des
Ordners, den ich über die Geräte-Anbindung sehen kann (nur `frame-forge` selbst ist gemountet).
Dasselbe gilt für die Homebrew-Werkzeuge (`ffmpeg`, `cairo`, `exiftool`), die `frameforge`
braucht. Ich kann also **Dateien** in deinem Repo lesen und schreiben (das mache ich unten),
aber **`frameforge`-Befehle selbst nicht ausführen** — kein `frameforge new`, kein `doctor`,
kein `ingest`.

**Was das praktisch bedeutet:** Alles, was reine Dateien sind (Doku, Prompts, Presets als
YAML, die Website als statisches HTML/CSS), erledige ich jetzt direkt. Alles, was echten
`frameforge`-Code braucht (Projekt anlegen inkl. `.state.json`, Ingest, Index, Build, Render),
musst du entweder selbst mit einem Befehl anstoßen (dauert Sekunden), oder wir machen es in
einer nativen Claude-Code-Session auf deinem Mac (genau das Muster aus `HANDOVER.md`: `cd
~/Workspace/Repos/frame-forge && claude`). Der eine Befehl für den Projekt-Start:

```
cd ~/Workspace/Repos/frame-forge
.venv/bin/python -m frameforge new michael-jga-2026 \
  --media-root ~/Workspace/Daten/Medien/JGA-Bruessel-Platzhalter \
  --timezone Europe/Brussels --language de
```

Der `--media-root`-Pfad muss **noch nicht existieren** (siehe `/ff-new`-Doku) — du trägst den
echten Pfad ein, sobald die Fotos/Videos sortiert sind, einfach indem du die Zeile
`media_root:` in `projects/michael-jga-2026/project.yaml` von Hand editierst. Das ist die
Antwort auf deine Frage „wie verknüpfe ich später den echten Medienordner": **ein Zeile in
einer YAML-Datei ändern**, kein Sonderbefehl nötig, solange `ingest` noch nicht gelaufen ist.
(`frameforge relink` ist für einen anderen Fall gedacht — Dateien, die *nach* dem ersten
Ingest umsortiert wurden; hier brauchst du es noch nicht.)

---

## 1. Designsystem-Frage — direkte Antwort (unverändert aus v1)

**Das Designsystem ist bereits pro Projekt, nicht global.** `tokens.yaml`, Fonts und Assets
liegen unter `projects/<projekt>/design/`, komplett getrennt je Projekt — ein neues Projekt
bekommt automatisch sein eigenes leeres Designsystem. Hier ist nichts umzubauen. Einzige
Einschränkung: Die Website übernimmt Tokens bisher nur manuell, nicht automatisch (§9).

---

## 2. Phasenmodell — was wann passiert

**Neu in v2**, weil du explizit nach der Reihenfolge gefragt hast.

**Phase 0 — jetzt, ohne Material nötig.**
Designsystem-Vorschlag inkl. konkreter `tokens.yaml` und fertiger Bild-Prompts (§4, liefere
ich in diesem Dokument), Font-Empfehlungen zum Herunterladen (§4), Custom-Preset
`jga-zweiteiler` als YAML (§7, kann ich als Datei anlegen, sobald das Projekt existiert),
Website-Grundgerüst (§9, kann ich jetzt schon als Dateien anlegen — reines HTML/CSS, keine
`frameforge`-Abhängigkeit), Beat-Sheet-Grundgerüst als Diskussionsbasis (§3, steht schon unten).

**Phase 1 — wartet auf dich (blockierend).**
`frameforge new` ausführen (§0) → dann: `media_root` final eintragen, die drei Musik-Dateien
nach `music/` legen, generierte Design-Grafiken nach `design/assets/` legen, den exakten
Pulp-Fiction-Songtitel nennen, die Muss/Nice-Liste per Dateiname durchgeben (§5).

**Phase 2 — sobald Material + Phase 1 stehen.**
Normale Pipeline (`ingest → index → design fertig → brief → build → preview → freigeben →
render`) plus ein **kreatives Skript-Gespräch**: gemeinsam durch die Bilder/Clips gehen und
konkret festlegen, wo ein Herzchen, ein Heiligenschein, eine Denkblase oder eine Cast-Karte
hinkommt (dein Wunsch, „nochmal ein Skript vorgeben"). Das fließt direkt in `beatsheet.md`
und die `fx`-Spur der `timeline.json` (§6).

---

## 3. Dramaturgie — Grundgerüst (Update v3: Cast-Intro-Position korrigiert, Timing offen)

**Zur Länge (Update v3):** ~5,5 Minuten war nie ein hartes Ziel. Die Musik allein (Vivaldi +
Pulp-Fiction-Stück) kommt auf ~5:45, dazu kommt noch der eigene Outro-Track. Realistisch
eher **circa 6-7 Minuten** — als Richtwert für Brief/Preset, kein fixer Deadline-Wert. Wo
„Ziellänge" in diesem Plan sonst auftaucht, ist das gemeint.

**Intro-Bild (neu):** ein eigenes, von Christian bereits erstelltes Standbild, mit dem der
Film öffnet. Kommt als fertige Grafik nach `design/assets/` — kein Ausschnitt aus dem
Rohmaterial, sondern ein separates Design-Asset (wie ein Logo).

**Akt 1 — „Gediegen"** (Freitag + Samstag bis zur ersten Kneipe), Musik: Vivaldi „L'inverno".
Ankunft/Auto → Haus in Brüssel → Pizza + Bier + Schnaps, ruhig ins Bett → Frühstück →
Stadtbummel → Waffeln + Schokolade → Pommes. Langsamer Schnitt, warm, leiser Humor.

**Akt 2 — „Eskalation"** (ab erster Kneipe, jetzt mit der ganzen Gruppe), Musik:
Pulp-Fiction-Soundtrack-Stück. Kneipe zu Kneipe → Essen/Trinken → **Karaoke-Bar „Red"** →
weiter in die Nacht → Junggeselle „abgeschossen" im Bett. Schneller, lauter Schnitt, Comic-FX
aktiv (§6).

**Cast-Intro — korrigierte Position (Update v3):** **nicht** am Akt-Übergang wie in v2
angenommen, sondern **mitten in Akt 2, konkret in der Karaoke-Bar „Red"** — dort sind die
Sonnenbrillen-Fotos entstanden, die den Anstoß für die Idee gegeben haben. Sonnenbrillen-Foto
pro Person, Bild friert ein, Name kommt in cooler Schrift reingestempelt, kurzer
Sound-Effekt — wie die Team-Vorstellung in einem Heist-Film. Braucht **Einzelfotos pro
Person** (nicht nur das Gruppenfoto) — die Namenszuordnung bereitet Christian noch vor (Phase 1).

**Outro** — eigener dritter, ruhiger Track (getragen/violinenartig). Bilder vom nächsten
Morgen, „alle sind erledigt", plus die zwei Auto-Schlaf-Fotos.

**Outro-Bild + Abspann-Karte (neu):** ein zweites fertiges Standbild fürs Ende (analog zum
Intro-Bild), danach eine kurze „Danke"-Karte mit Text — dafür reicht das ohnehin vorhandene
`credits`-SVG-Template, keine neue Technik nötig.

## 4. Designsystem-Vorschlag — jetzt anhand eines echten Stilbilds (Update v3)

Christian hat ein Referenzbild geliefert (Gruppenfoto, Sonnenbrillen, Neon-Optik, mit
Titel-Schriftzug „JGA 2026 — Micha im Delirium — Brüssel"). Liegt jetzt im Repo unter
`web/sites/michael-jga-2026/design/reference/style-reference-jga-poster.png` — die
**zentrale Stilreferenz** für Video-Tokens *und* Website. Analyse davon, was den Stil
ausmacht (Bildbeschreibung, nicht Bild-Interpretation durch Dritte):

- **Grundfarbe:** sehr dunkles Indigo-Purpur, leicht ins Blaue (Nachthimmel/Brüssel-Kulisse
  bei Nacht), kein reines Schwarz.
- **Hero-Farbe: Gold.** Der Haupt-Schriftzug „JGA"/„2026" ist in warmem Gold mit
  Verlauf/Glanz gehalten — das ist optisch die dominanteste Farbe, nicht Pink. Verdient den
  `accent_color`-Slot.
- **Zweitfarbe: Neon-Pink/Magenta** — Umgebungslicht, der leuchtende „Delirium"-Schriftzug/
  Elefant im Hintergrund (Anspielung auf die reale Brüsseler Kneipe/Biermarke), diffuses
  Glühen über der ganzen Szene.
- **Ein blauer Achzent** taucht gezielt auf (die leuchtende blaue Punkte-Schleife des
  Bräutigams) — eher ein persönliches Erkennungsmerkmal als ein durchgängiges Systemfarbe,
  siehe Vorschlag unten.
- **Typografische Zweiteilung, die zufällig genau zum Film passt:** der raue, „JGA"/„MICHA IM
  DELIRIUM"-Schriftzug wirkt wie mit dickem Pinsel/Graffiti-Spray gemalt (unregelmäßige
  Kanten, Störungen, Leuchten) — passend zu Akt 2. „BRÜSSEL" darunter dagegen in einer
  ruhigen, sauberen Versalienschrift mit dünnen Trennlinien — passend zur zurückhaltenderen
  Akt-1-Optik. Diese Zweiteilung sollten die Templates aufgreifen, nicht nur die Farben.
- **Deko-Elemente:** leuchtend-weiße/goldene Doodle-Kronen über den Köpfen, kleine
  Glitzer-/Herz-Akzente — als **leuchtende Neon-Doodles**, nicht als flache Comic-Cartoon-
  Symbole. Das ändert den technischen Zuschnitt der Sticker-Bausteine in §6.3 (siehe dort).
- Handschriftliche Rand-Captions („GOOD FRIENDS, BAD DECISIONS" / „SAME MEN, DIFFERENT
  CITY") in grobem Marker-/Brush-Stil, seitlich, leicht schräg.

**Praktische Konsequenz für Intro-/Outro-Bild und Hero-Grafiken:** Ein Bild wie dieses mit
eingebranntem Text in diesem Pinsel-/Foliendruck-Look lässt sich mit Live-Text über SVG kaum
nachbauen (Web-/Systemschriften liefern diesen Verlauf/diese Störung/dieses Leuchten nicht).
Für **einmalige Hero-Grafiken** (Intro-Bild, Outro-Bild, ggf. `title-bg.png`) ist es deshalb
richtig, sie — wie Christian es mit dem Intro-Bild bereits macht — als **fertige Bilder mit
eingebranntem Text** zu behandeln, genau wie ein Logo: einmal erzeugen/liefern, unter
`design/assets/` ablegen. Die SVG-Overlay-Vorlagen (Cast-Karten-Namen, Bauchbinden,
Denkblasen) bleiben **live Text**, weil sich deren Inhalt ändert (Namen, Uhrzeiten) — dafür
gilt weiterhin die Font-Empfehlung aus §4.3.

### 4.1 Überarbeiteter Vorschlag für `design/tokens.yaml`

```yaml
primary_color: "#1e1640"     # dunkles Indigo-Purpur, leicht blau — Nachtgrundton aus dem Referenzbild
secondary_color: "#ff2e8a"   # Neon-Pink/Magenta — Umgebungsglühen, Delirium-Neon
accent_color: "#d9a441"      # warmes Gold — Haupt-Schriftzug-Farbe, dominantester Farbton
text_color: "#fdf6ec"        # warmes Cremeweiß statt reinem Weiß, wie die Handschrift-Captions
motion:
  fade_in_s: 0.4
  fade_out_s: 0.5
  overlay_hold_min_s: 1.5
type_scale:
  title: 110
  subtitle: 40
  caption: 30
```

Gegenüber v2 getauscht: Gold ist jetzt `accent_color` (vorher Pink) — im Referenzbild ist Gold
die auffälligste Farbe, nicht Pink. Pink rutscht auf `secondary_color`.

**Der blaue Bräutigam-Akzent** (`#4fd8ff` o.ä.) wird bewusst **nicht** ins globale Token-Set
aufgenommen — er würde als vierte Systemfarbe verwässern. Stattdessen als kleiner,
wiederkehrender Sonderfarbwert nur dort, wo es um Micha persönlich geht (z. B. sein
Namens-Tag in der Cast-Intro, siehe §6.3) — eine hübsche Randnotiz, kein globales System.

### 4.2 Bild-Prompts — aktualisiert auf die neuen Farbwerte

Gleiche Prompts wie in v2, Farbcodes ersetzt (`#1b1035`/`#ff2e63` → `#1e1640`/`#d9a441`
Gold als Hauptfarbe, `#ff2e8a` als Zweitakzent), plus expliziter Verweis aufs Referenzbild:

```
Minimalistisches Logo-Emblem für einen Junggesellenabschied-Film "JGA — Micha im Delirium
2026", im Stil von design/reference/style-reference-jga-poster.png: warmes Gold als
Hauptfarbe (Verlauf, leichtes Leuchten), dunkles Indigo-Purpur (#1e1640) im Hintergrund,
Neon-Pink (#ff2e8a) als Umgebungsglühen. Kein Fotorealismus, funktioniert klein UND groß.
Hintergrund: transparent (PNG mit Alpha).
```

Die übrigen Prompts aus v2 (Titelkarten-Hintergrund, Comic-Burst-Textur) analog anpassen,
sobald sie gebraucht werden — Hero-Bilder mit eingebranntem Text laufen ohnehin über
Christians eigenen Weg (siehe oben), nicht über diese Prompts.

### 4.3 Schrift-Empfehlung (unverändert aus v2, jetzt begründet durch das Referenzbild)

**Bangers** für Titel/Denkblasen/Cast-Karten-Namen (Comic-Lettering, verträgt sich mit der
Energie des Referenzbilds, auch wenn es dessen Pinsel-Textur nicht 1:1 nachbildet — dafür
sind Hero-Bilder da, s. o.). **Poppins** für Fließtext/Bauchbinden — kann in Versalien mit
Buchstabenabstand auch die ruhigere „BRÜSSEL"-Anmutung für Akt-1-Textelemente übernehmen,
ohne eine dritte Schriftart einführen zu müssen (das Tokens-Schema hat nur zwei Font-Felder).
Optional, falls gewünscht: **Permanent Marker** für einzelne handschriftliche
Spontan-Kommentare, näher am Rand-Caption-Stil des Referenzbilds.

## 5. Prioritätsstufen für Assets — korrigiert (Update v2)

**Korrektur meinerseits:** In v1 hatte ich geschrieben, „alle Assets zeigen" sei bei 5,5
Minuten rechnerisch unmöglich. Das war zu pauschal und dein Einwand ist berechtigt — bei z.B.
50 Fotos (~2s Ken-Burns-Schnitt je Bild ≈ 100s) plus 3 Videoclips à 20s (60s) sind das
zusammen ~2:40 min, passt locker in 5,5 Minuten. Ob „alles" reinpasst, hängt schlicht davon
ab, wie groß deine finale Vorauswahl am Ende wird — das weiß heute noch keiner von uns beiden.
Die Prioritätsstufen (§ unten) bleiben trotzdem sinnvoll: als Absicherung *falls* die
Vorauswahl doch größer wird als der Film Zeit hat, und weil du ohnehin explizit gestufte
Kontrolle wolltest (nicht nur binär must/nicht-must).

**Mechanismus — überarbeitet (Update v2), jetzt dateinamen-basiert statt hash-basiert:**
Ein Hash oder eine interne Asset-ID (`20260714-drone-fjord-001`) kannst du beim Sichten nicht
kennen — du kennst nur die Original-Dateinamen. Deshalb:

- `frameforge set-priority <projekt> --filename "IMG_1234" --priority must` — matcht per
  Teilstring gegen den gespeicherten Original-Pfad (`assets.json`-Feld `path`), unabhängig von
  Groß/Kleinschreibung. Meldet Klartext zurück, welche Datei(en) getroffen wurden — bei 0 oder
  mehreren Treffern bricht der Befehl ab und listet die Kandidaten, statt zu raten.
- **Bulk-Variante** für mehrere Dateien auf einmal: `frameforge set-priority <projekt>
  --from-file prioritaeten.csv`, Datei mit zwei Spalten `dateiname,prioritaet`
  (`must`/`nice`/`ok`) — du kannst mir einfach eine Liste von Dateinamen mit Einstufung
  schicken, ich baue daraus die CSV.
- Stufen: `must` (hart eingeplant, Konflikt wird gemeldet statt stillschweigend verworfen),
  `nice`/„wenn möglich" (bevorzugt vor `ok`, wenn Zeit reicht), `ok` (Default, Lückenfüller).
- `timeline-builder`: pro Kapitel zuerst `must`, dann `nice` vor `ok` aus der Restzeit.
- Datenblatt (`<export>_vN.report.md`) bekommt eine Zeile: wie viele `must`/`nice`/`ok`, wie
  viele davon tatsächlich im Schnitt gelandet sind.

---

## 6. Comic/Party-FX — Baukasten, jetzt mit echter Tool-Prüfung (Update v2)

Du hast zu Recht nochmal nachgefragt, ob es nicht doch externe Tools/Plugins/MCPs gibt, die
helfen. Ich habe das jetzt geprüft (MCP-Registry durchsucht, Web-Recherche zu Sound-Effekten):

### 6.1 Typografie/Optik — gefundenes Tool: Canva (MCP), bereits in deinem Account

In der MCP-Registry deines Accounts taucht **Canva** auf (Status: verbunden gewesen, aktuell
„needs_reconnect" — du müsstest es einmal neu verbinden). Das ist genau die Antwort auf „muss
wirklich gut aussehen, nicht wie die schwachen Norwegen-Bauchbinden": statt Titel/Cast-Karten
nur als schlichtes SVG zu bauen, kannst du (oder ich über die Canva-Anbindung) hochwertigere
Grafiken mit echten Effekten (3D, Prägung, gemalt wirkende Texturen) in Canva gestalten, als
PNG exportieren und wie jede andere generierte Grafik nach `design/assets/` legen — der
bestehende Mechanismus (Nutzer legt Bild ab, Pipeline bindet es ein) bleibt unverändert, nur
die Bildquelle ist hochwertiger als reines SVG. Kein After-Effects, kein Node — Canva läuft im
Browser. Zusätzlich baue ich in die neuen Templates selbst schon einen fetteren Look ein
(dicke Kontur, Schatten-Versatz, leichter Bevel über SVG-Filter) statt Norwegens flacher
Textfläche — das behebt den Norwegen-Kritikpunkt strukturell, nicht nur im Einzelfall.

### 6.2 Sound-Effekte — kein Tool nötig, zwei geprüfte kostenlose Quellen

Für die Whoosh-/Stempel-Sounds bei der Cast-Intro und vereinzelte Comic-SFX braucht es kein
neues Werkzeug, nur Audiodateien zum Herunterladen. Geprüft (frei nutzbar, keine
Herkunftsnennung nötig):

- [Pixabay – Whoosh-Sound-Effekte](https://pixabay.com/sound-effects/search/whoosh%20sound%20effect/)
- [Pixabay – Comic-Sound-Effekte](https://pixabay.com/sound-effects/search/comic/)
- [Mixkit – Whoosh-Sound-Effekte](https://mixkit.co/free-sound-effects/whoosh/)

Ein bis zwei Dateien reichen (z. B. ein Whoosh fürs Einfrieren des Bildes, ein Stempel-/
Klick-Sound fürs Einblenden des Namens) — legst du wie Musik unter `music/` ab (oder einen
neuen Unterordner `music/sfx/`, macht die Trennung von den drei Haupttracks sauberer).

### 6.3 Technische Umsetzung — unverändert zu v1, plus neue Cast-Intro-Mechanik

Kein externes Tool für die eigentliche Compositing-Arbeit — das bleibt beim bestehenden
Stack (FFmpeg, OpenCV, Pillow, cairosvg):

| Baustein | Ansatz |
|---|---|
| Denkblase mit Text | Neues SVG-Template `thought-bubble`, wie `lower-third`/`caption` |
| Speedlines/Sticker (Herzchen, Krone, Glitzer) | Vorgerenderte Alpha-PNG-Sequenzen, prozedural erzeugt und gecacht — **Update v3: Leucht-Doodle-Optik** (dünne weiße/goldene Konturlinie + weicher Glow-Schatten darunter) statt flacher Comic-Cartoon-Fläche, siehe Referenzbild §4 |
| Heiligenschein/Krone um den Kopf | Kleines animiertes Ring-/Kronen-Overlay im selben Leucht-Doodle-Stil, positionierbar — technisch wie ein Sticker |
| Farb-Pop/Blitz | Zeitlich begrenzter Filter direkt auf dem Clip (`eq`/`hue`) |
| Cartoon-/Kritzel-Outline | Bilateral-Filter + Kantenerkennung (OpenCV, „Cartoonizer"-Technik) |
| **Cast-Intro (neu)** | Standbild aus Video/Foto (Freeze), Text „stampft" rein (Scale-Overshoot-Animation), SFX-Einschuss |

**Neue Timeline-Bausteine, die das braucht:**
1. Neue Spur `fx` in `timeline.json` (Denkblasen, Sticker, Cast-Karten-Text).
2. Freeze-Unterstützung im `video`-Track (ein Frame als Standbild halten).
3. Ein neuer Audio-Eintragstyp `kind: "sfx"` (kurzer Einschuss-Sound, keine Ducking-Kurve
   nötig, anders als Musik/O-Ton).

**Technische Notiz zum Glow-Look (Update v3):** kein neues Werkzeug nötig — ein dünner
Pfad plus eine weichgezeichnete Kopie darunter (Gaussian Blur, per SVG-Filter oder
`Pillow`) ergibt den Leucht-Effekt aus dem Referenzbild. Die dicke Comic-Outline-Technik
aus §6.1/OpenCV bleibt für andere Zwecke (Cartoon-Konturen auf dem Bild selbst) bestehen —
beide Stile ergänzen sich, sind aber nicht dasselbe.

Neuer Agent `party-fx` bleibt wie in v1 vorgesehen: baut die FX-Bausteine, schlägt Stellen im
Beat-Sheet vor (Akt 2 + Cast-Intro aktiv, Akt 1 bewusst zurückhaltend), schreibt die
FX-Einträge in die Timeline.

**Ehrlichkeitspunkt unverändert:** Echte Meme-Bilder mit geschützten Figuren (Pepe, Forrest
Gump etc.) kann ich nicht generieren — die legst du selbst als PNG ab. Für alles andere
(Denkblasen, Sticker, Cast-Karten, Comic-Texturen) brauchst du niemanden extra.

---

## 7. Custom-Preset `jga-zweiteiler`

Unverändert aus v1: Akt 1 nah an **Diary/Handheld**/**Calm/Meditative**, Akt 2 nah an **Beat
Music Video**/**Action-Adrenalin**, dreiteiliger `arc` (ruhig → eskalierend → Ausklang). Sobald
das Projekt existiert, lege ich `presets/jga-zweiteiler.yaml` direkt an (reine YAML-Datei,
keine `frameforge`-Ausführung nötig) — das kann schon in Phase 0 passieren.

---

## 8. Musik & Audio

Unverändert aus v1: drei Tracks (Vivaldi, Pulp-Fiction-Stück, neuer Outro-Track), Ducking für
O-Ton (Karaoke etc.), Lizenz-Hinweis fürs Pulp-Fiction-Stück bleibt offener Punkt für privaten
Gebrauch. Neu (§6.2): plus 1-2 kurze SFX-Dateien für die Cast-Intro.

---

## 9. Website

Unverändert aus v1, Subdomain jetzt bestätigt: **`micha-jga.skubus.de`**. Neu in v2: das
Website-Grundgerüst (`web/sites/michael-jga-2026/{content,design,public,deploy}`) ist reines
HTML/CSS/Shell, hängt nicht an `frameforge`/Python — das kann ich **jetzt schon** als
Datei-Skelett anlegen (Phase 0), analog zu `web/sites/norwegen-2026/`. DNS-Eintrag +
Basic-Auth in traefik bleiben manuelle Server-Schritte außerhalb des Repos.

---

## 10. Technik-Ziele / Deliverables

Mind. Full HD, 4K-Final + 1080p-Streaming (unverändert). **Ziellänge (Update v3): circa
6-7 Minuten, offener Richtwert** — nicht die starren 5-5,5 Minuten aus v1/v2 (siehe §3).
EBU-R128-Normalisierung, FCPXML/OTIO-Export automatisch verfügbar.

---

## 11. Risiken & offene Punkte

1. Ausführungsumgebung (§0) — `frameforge`-Befehle brauchen deinen Mac-Terminal oder eine
   native Claude-Code-Session dort, nicht diese Geräte-Anbindung.
2. Priorität-Tagging-Aufwand — realistisch nur die ~12-15 harten Anker aus §3 als `must`.
3. Musik-Lizenz (Pulp-Fiction-Stück) — kein Blocker für privaten, passwortgeschützten Gebrauch.
4. iPhone-Zeitzonen-Fallstrick — beim Ingest wie bei Norwegen prüfen.
5. Comic-FX + Cast-Intro sind echte Neuentwicklung (neues Timeline-Schema, neuer Agent, neue
   Render-Codepfade, neue Tests) — realistisch Zeit einplanen.
6. Welches Pulp-Fiction-Stück genau (Titel + gewünschter Ausschnitt) noch offen.
7. Canva-Verbindung muss neu autorisiert werden, falls genutzt (§6.1).

---

## 12. Arbeitspakete

| # | Paket | Phase | Kurzbeschreibung |
|---|---|---|---|
| J1 | Projekt anlegen | 1 (du/native Session) | `frameforge new michael-jga-2026 …` (§0) |
| J2 | Prioritätsstufen | Dev, vor Phase 2 nutzbar | `content.priority`, dateinamen-basiertes CLI + Bulk-Import (§5) |
| J3 | Ingest + Index | 2 | inkl. iPhone-Zeitzonen-Check |
| J4 | Designsystem | 0 (Vorschlag steht) / 2 (final) | `tokens.yaml`-Vorschlag §4.1, Bild-Prompts §4.2, Fonts §4.3 |
| J5 | Custom Preset `jga-zweiteiler` | 0 | dreiteiliger Arc (§7) |
| J6 | Comic/Party-FX-Baukasten | Dev | neuer Agent, neue `fx`-Spur, Freeze-Support, SFX-Audiotyp (§6.3) |
| J7 | Brief + Beat-Sheet | 0 (Entwurf) / 2 (final) | Muss-Shot-Liste, drei Akte + Cast-Intro (§3) |
| J8 | Audio | 1 (Dateien) / 2 (Build) | 3 Musik-Tracks + 1-2 SFX, Ducking |
| J9 | Build → Preview → Freigabe → Render | 2 | Standard-Pipeline |
| J10 | Website | 0 (Grundgerüst) / 2 (Inhalte) | `web/sites/michael-jga-2026/`, `micha-jga.skubus.de` |

---

## 13. Nächste konkrete Schritte

1. Ich lege jetzt an (Phase 0, reine Dateien, kein `frameforge` nötig): Website-Grundgerüst,
   `jga-zweiteiler`-Preset-Entwurf als Referenzdatei, diesen Plan aktualisiert.
2. Du führst `frameforge new …` aus (§0) — dann kann ich wieder direkt in `design/`,
   `music/`, `presets/` weiterarbeiten.
3. Sobald Fotos/Videos + Musik da sind: Phase 1 abschließen, dann Phase 2 (Ingest → Index →
   gemeinsames FX-/Skript-Gespräch → Build).

---

## 14. Nachtrag — bereits angelegte Phase-0-Dateien (2026-09-07)

Beim Schreiben dieses Plans direkt mit erledigt (reine Dateien, kein `frameforge` nötig):

- `presets/jga-zweiteiler.yaml` — Entwurf des Custom-Presets aus §7 (Kommentar im Kopf: noch
  nicht gegen den echten Preset-Loader geprüft, vor Nutzung im `/ff-brief`-Wizard gegenlesen).
- `web/sites/michael-jga-2026/design/PROMPT-designsystem.md` — der Website-Design-Prompt, den
  du angefordert hast. Folgt demselben Verfahren wie
  `web/sites/norwegen-2026/design/PROMPT-designsystem.md`: vollständig in eine neue
  Design-Session geben, Export zurück in denselben Ordner legen, danach wird `public/`
  daraus gebaut. Enthält bewusste Platzhalter für das genaue Datum, die zehn Namen/Fotos der
  Crew und die Musik-Credits — die kennt heute noch niemand.
- `web/sites/michael-jga-2026/design/README.md` — kurzer Ablauf-Hinweis, Analogie zu
  Norwegen.
- Leere Grundordner `web/sites/michael-jga-2026/{content,public,deploy}` für die spätere
  Site-Fertigstellung (Phase 2).

Der `tokens.yaml`-Vorschlag für das **Video** selbst (§4.1) ist bewusst *nicht* schon als
Datei angelegt, weil dafür erst `projects/michael-jga-2026/` existieren muss (§0) — der
Vorschlag steht aber fertig in diesem Dokument, sobald du `frameforge new` ausgeführt hast,
trage ich ihn direkt ein.

---

## 15. Nachtrag v3 (2026-09-07, zweite Runde)

- Stilreferenz-Bild von Christian übernommen:
  `web/sites/michael-jga-2026/design/reference/style-reference-jga-poster.png`.
- `presets/jga-zweiteiler.yaml` — Arc-Text korrigiert (Cast-Intro jetzt in der
  Karaoke-Bar „Red" verankert statt am Akt-Übergang).
- `web/sites/michael-jga-2026/design/PROMPT-designsystem.md` — Farbwerte, Font-Begründung
  und Sticker-Optik auf Basis des Referenzbilds aktualisiert, Verweis auf die Bilddatei
  ergänzt.
- Ziellänge überall auf „circa 6-7 Minuten, offener Richtwert" korrigiert (§3, §10).

---

## 16. Klarstellung: Design-Tokens sind keine Farbkorrektur der Aufnahmen (2026-09-07, dritte Runde)

Wichtige Präzisierung, damit hier kein Missverständnis entsteht: `tokens.yaml`
(`primary_color`/`secondary_color`/`accent_color`/`text_color`) speist **ausschließlich**
SVG-Overlays (Titel, Bauchbinden, Cast-Karten) und die Website. Diese Werte werden **nicht**
als Farbkorrektur/LUT auf die eigentlichen Foto-/Videoaufnahmen angewendet — dafür gibt es
einen komplett getrennten Mechanismus:

- **`color_grade` im Preset** (`presets/jga-zweiteiler.yaml`, aktuell `mood: warm_then_vivid,
  contrast: medium`) — ein bewusst gewählter, moderater "Look" (etwas kräftigere Farben),
  kein Zwang zur Token-Palette. Wird beim `/ff-brief`/`/ff-build` mit echtem Material verfeinert.
- **`render.match_filter` / `color_match`** (Plan 0003 H2) — gleicht nur unterschiedliche
  Kamera-/Handyquellen farblich aneinander an, erfindet keine neue Farbwelt.

Die Aufnahmen selbst bleiben also, wie sie sind — mit optional einem dezenten,
separat einstellbaren Grad an Kräftigkeit, nicht dem Gold/Pink-Farbschema der Grafiken.

**Zum genannten Norwegen-Problem** (QuickTime zeigte Farben korrekt, ein Web-Player nicht,
Bilder wirkten "verrutscht"): das ist exakt der Fall, der im Norwegen-Projekt bereits
root-caused und behoben wurde — unterschiedliche Farbraum-/Range-Tags (HLG-Drohnenmaterial,
Full-Range-Fotos, Display-P3-HEIC) wurden von verschiedenen Playern unterschiedlich
interpretiert. Fix liegt in `frameforge/color.py` (`normalize_chain`, bringt jedes Segment an
der Quelle auf BT.709/TV) und `ingest._write_heif_proxy` (HEIC jetzt farbverwaltet nach sRGB
statt P3-Werte unverändert als sRGB zu interpretieren) — beides **generische
Pipeline-Module**, nicht Norwegen-spezifisch, greifen also automatisch auch für
`michael-jga-2026`. Relevant für JGA vor allem die HEIC/P3-Seite (iPhone-Fotos), die
HLG-Seite eher nicht (kein Drohnenmaterial diesmal). Trotzdem sinnvoll, wie in
`HANDOVER.md` empfohlen: vor dem ersten Vollrender einen kleinen Ausschnitt (2-3 Clips)
smoke-testen statt blind zu vertrauen.

## 17. Konkreter Ablauf jetzt (2026-09-07, dritte Runde)

**A. Website-Designsystem (kann sofort passieren, unabhängig von B):**
1. Eine neue, separate Design-Session öffnen (z. B. neuer Chat) — die hat **keinen** Zugriff
   auf dieses Repo.
2. Kompletten Inhalt von `web/sites/michael-jga-2026/design/PROMPT-designsystem.md`
   hineingeben **und das Bild `design/reference/style-reference-jga-poster.png` als Datei
   an dieselbe Nachricht anhängen** (die Session kann nicht selbst in den Ordner schauen).
3. Ergebnis (tokens.css, theme-jga-2026.css, base.css, components.css, HTML-Entwürfe,
   Font-Hinweis) unverändert zurück in genau diesen Ordner `web/sites/michael-jga-2026/design/`
   legen (siehe `design/README.md`).
4. `public/` wird daraus erst in Phase 2 gebaut — jetzt reicht die Ablage.

**B. Video-Projekt (Mac-Terminal oder native Claude-Code-Session dort):**
1. Projekt anlegen:
   ```
   cd ~/Workspace/Repos/frame-forge
   .venv/bin/python -m frameforge new michael-jga-2026 \
     --media-root ~/Workspace/Daten/Medien/JGA-Bruessel-Platzhalter \
     --timezone Europe/Brussels --language de
   ```
   Legt automatisch u. a. `design/`, `design/assets/`, `design/fonts/`, `music/` leer an —
   dafür ist **kein manuelles Vorbereiten von Ordnern nötig**.
2. `projects/michael-jga-2026/design/tokens.yaml` von Hand mit dem Vorschlag aus §4.1 dieses
   Plans befüllen (einfache Textdatei, kein Gate). Kurzauftrag an die native Session: „Lies
   `docs/plans/0004-jga-brussel-video.md` §4.1 und schreib das als
   `projects/michael-jga-2026/design/tokens.yaml`."
3. Fonts (Bangers, Poppins, beide Google Fonts) herunterladen: `.ttf`/`.otf` nach
   `projects/michael-jga-2026/design/fonts/` (fürs Video), `.woff2` nach
   `web/sites/michael-jga-2026/design/fonts/` bzw. wohin die Design-Session aus Teil A sie
   legt (fürs Web) — zwei getrennte Dateiformate, gleiche Schriftfamilie.
4. **`frameforge design michael-jga-2026`** (der Befehl, der die Phase offiziell auf
   `DESIGNED` setzt) wird laut State-Machine erst **nach** `ingest`+`index` funktionieren —
   das ist normal und kein Fehler. Die Tokens/Fonts liegen bis dahin einfach schon bereit.
5. Feste Dateinamen für die zwei Standbilder aus §3, damit später nichts geraten werden muss:
   `design/assets/intro-still.png` und `design/assets/outro-still.png`.
6. Musik: die drei Tracks (Vivaldi, Pulp-Fiction-Stück, Outro-Track) nach `music/` legen,
   sobald heruntergeladen.

**Danach:** Fotos/Videos landen im echten `media_root`-Pfad (Zeile in `project.yaml`
anpassen), dann normale Pipeline (`ingest → index → …`).

---

## 18. Umsetzung J2 + J6 als Code (2026-09-07, vierte Runde)

Nutzer-Entscheidung: Website (J10) und die beiden Kern-Feature-Pakete (J2 Prioritätsstufen,
J6 Comic/Party-FX-Baukasten) sollten sofort als echter Code umgesetzt werden, statt auf
Ingest/Index von echtem Material zu warten — beides hängt an keinem Footage. Umgesetzt,
**aber ungetestet in diesem Sinne**: von dieser Session aus lässt sich `frameforge` nicht
ausführen (§0, Linux-VM vs. macOS-venv/-Homebrew) — die Kernlogik wurde stattdessen mit einem
separat installierten Python 3.10 + den reinen Python-Abhängigkeiten (pydantic, pyyaml,
numpy, pillow) direkt importiert und funktional gegengetestet (echte Funktionsaufrufe, keine
reinen Syntax-Checks) — siehe unten, was das abdeckt und was nicht.

### J2 — Prioritätsstufen (`must`/`nice`/`ok`), dateinamen-basiert

- `frameforge/index.py`: `PRIORITY_LEVELS = ("must","nice","ok")`, `query_assets(...,
  priority=...)`-Filter, neue Funktion `find_assets_by_filename()` (Teilstring-Match auf
  `path`, case-insensitive).
- `frameforge/preindex.py`: `index_prepared_asset(..., priority="ok")` — Default beim
  Indizieren, `media-indexer` kann optional `nice` mitgeben.
- `frameforge/cli.py`: neuer Befehl `set-priority` (`--filename`/`--priority`,
  `--from-file prioritaeten.csv` für Bulk, `--all-matches` bei mehrdeutigem Dateinamen-Match),
  `query --priority`, `index-asset --priority`.
- `frameforge/stats.py`: `build_report()` zeigt jetzt must/nice/ok-Nutzung und meldet fehlende
  `must`-Assets explizit statt sie stillschweigend zu übergehen.
- `.claude/agents/timeline-builder.md`: Schritt 2 neu — platziert `must` garantiert, füllt mit
  `nice` vor `ok`, meldet Konflikte statt sie zu verschlucken.
- **Funktional getestet:** `query_assets(priority=...)`, `find_assets_by_filename()`,
  Default-„ok"-Verhalten fehlender Prioritäten — mit echten Funktionsaufrufen gegen eine
  Fake-`assets.json`, nicht nur `py_compile`.
- **Nicht testbar von hier:** `set-priority`-CLI end-to-end (Typer/Click-Aufruf), `--from-file`
  mit echter CSV, Zusammenspiel mit dem `timeline-builder`-Agenten am echten Fundus.

### J6 — Comic/Party-FX, mit einer echten Architektur-Korrektur

Beim genaueren Hinsehen brauchte es **keine neue `fx`-Spur** in `timeline.json`, wie ursprünglich
in §6 skizziert — das bestehende Schema deckt alles ab, ohne neuen, ungetesteten
Compositing-Code:

- Denkblasen/Sticker/Speedlines sind normale **`OverlayClip`**-Einträge (drei neue Templates:
  `templates/svg/thought-bubble.svg`, `sticker.svg`, `speedlines.svg`, plus die zugehörigen
  Layout-Tokens in `frameforge/design.py::overlay_tokens`) — dieselbe Mechanik wie
  Titel/Bauchbinden, Bewegung über die schon vorhandenen `anim`-Schlüssel.
- Farb-Pop und Cartoon-Outline sind **`Effect`**-Einträge in `VideoClip.effects` (wie
  `kenburns`): `frameforge/render.py` hat zwei neue Funktionen `_color_pop_expr`/
  `_cartoon_outline_expr`, die bei `type: "color_pop"`/`"cartoon_outline"` greifen.
  Cartoon-Outline ist bewusst ein FFmpeg-natives Äquivalent (`gblur` + `edgedetect=
  mode=colormix`) zum ursprünglich skizzierten OpenCV-Cartoonizer — bleibt im bestehenden
  Ein-Pass-Filtergraphen statt eine zweite Video-Vorverarbeitungsstufe einzuführen. Schwächerer
  Look als eine echte Bilateral-Kantenerkennung; falls das am echten Bild zu dünn aussieht, ist
  eine OpenCV-Vorstufe der naheliegende Ausbau, aber kein Blocker für einen ersten Versuch.
- Ein kurzer Soundeffekt ist ein ganz normaler **`AudioClip`** mit `type: "sfx"` — das Feld
  existierte schon (frei, `render.py` behandelt `type` an keiner Stelle funktional anders),
  `stats.py`'s Report bucketet `sfx`-Clips jetzt separat von „Musik" statt sie zu vermischen.
- **Freeze-Frame-Unterstützung war eine falsche Annahme meinerseits** — nochmal eine Korrektur
  wie schon bei §5/Prioritäten: eine "Freeze-Frame"-Cast-Intro-Aufnahme ist in der Praxis ein
  ganz normales **Foto** (die Sonnenbrillen-Fotos aus der Karaoke-Bar sind laut Christian
  bereits als Fotos aufgenommen, keine Video-Frames), und Fotos werden von `frameforge.render`
  schon als gehaltenes Standbild behandelt. Keine neue Timeline-/Render-Mechanik nötig.
- Neuer Agent `.claude/agents/party-fx.md`: baut die FX-Schicht auf einer schon vom
  `timeline-builder` gebauten `timeline.json` auf (Rezept-Skript-Muster wie
  `stage-caption-recipe.py`), inkl. konkreter Cast-Intro-Anleitung (Foto-Clip + Namensstempel
  über bestehendes `title-only.svg`/`subtitle-only.svg` + optionaler `color_pop`/SFX).
- **Funktional getestet** (echte Objektaufrufe, nicht nur Syntax): `_color_pop_expr`/
  `_cartoon_outline_expr` gegen echte `VideoClip`/`Effect`-Instanzen (inkl. Zeitfenster-Gate),
  alle drei neuen SVG-Templates über `build_svg_from_tokens`/`overlay_tokens` (löst vollständig
  auf, keine übrig gebliebenen Platzhalter), `AudioClip(type="sfx")` inkl.
  `Timeline.validate_semantics()`. Bestehende Templates (title-card, infocard, lower-third,
  stage-caption, stat-badge, subtitle-only, title-only, box-only) laufen nach den Änderungen an
  `overlay_tokens`/`_OPTIONAL_TOKENS` weiterhin durch — keine Regression an den gemeinsamen
  Layout-Tokens.
- **Nicht testbar von hier:** wie es tatsächlich aussieht (kein `ffmpeg`/`cairosvg`-Rendering
  in dieser Session möglich), das eigentliche `party-fx`-Agentenverhalten am echten Beat-Sheet,
  Zusammenspiel mit `_join_video_segments`/Farbnormalisierung im echten Render.

### Offen / nächster Schritt für Christian

Alles oben ist Code + Doku, kein Ersatz für einen echten Testlauf. Sobald `ingest`/`index`
mit echtem Material gelaufen sind, lohnt sich einmal ein kurzer Preview-Export mit ein bis
zwei `color_pop`/`cartoon_outline`-Effekten und einer Denkblase, um zu sehen, ob Stärke/Optik
passen, bevor der `party-fx`-Agent das für den ganzen Akt 2 einsetzt.

---

## 19. Kleine Korrektur (2026-09-08): Akt-1-FX nicht komplett verboten

Christian: Comic-FX (Herzchen, Krone etc.) müssen nicht strikt auf Akt 2 beschränkt sein —
ein einzelner netter Akzent vorher ist okay, solange Akt 1 in Summe ruhig bleibt. Der
Kontrast-Witz aus §3 bezieht sich auf die **Dichte**, nicht auf ein hartes Verbot in Akt 1.
`.claude/agents/party-fx.md` entsprechend angepasst (Schritt 1 + Constraints). Außerdem
bestätigt: vor einem flächigen Einsatz der Effekte erst an ein bis zwei Clips ausprobieren,
sobald ein echter Preview-Export möglich ist — dafür war bislang schon ein Hinweis in §18
vorgesehen, jetzt nochmal explizit als Agenten-Regel festgehalten.
