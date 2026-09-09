# Detail-Regie Export "JGA" — RUNDE 2 (Preview-Feedback)

Quelle: Christians Sichtung des ersten Previews `preview/JGA_preview.mp4` (8:53), Voice-Transkript
2026-09-09. **Ergänzt und überschreibt punktuell `editorial-notes.md` (Runde 1).** Wo Runde 2 und
Runde 1 sich widersprechen, gilt Runde 2.

`story-architect`, `timeline-builder`, `audio-designer` und `party-fx` lesen **beide** Dateien.

Zeitangaben `M:SS` beziehen sich auf das **alte** Preview (8:53), nur zur Identifikation der
gemeinten Bilder. Bildnummern ohne Präfix = `IMG_XXXX`; UUID-JPGs mit den letzten 4 Zeichen.

---

## 0. Globale Regeln (gelten für den ganzen Film)

### 0.1 Musik — komplett neu
| Track | Rolle | Datei (`music/`) | Länge | Nutzung |
|---|---|---|---|---|
| **Champions League Theme** | Intro + AKT 1 | `01 Champions League Theme (Champions League Theme).m4a` | 181,5 s | ganz, `fade_in_s: 2` unter dem Intro-Standbild, hartes Ende → Cut auf Akt 2 |
| **Miserlou** (Dick Dale, Pulp-Fiction-Titel) | AKT 2 | `01 Miserlou.m4a` → **loop-verlängerte Variante** | 136,1 s → **~196 s** | Loop-Datei bauen (§0.2), harter Cut an beiden Enden |
| **Where Is My Mind** (2007 Remaster) | Aftermath / Outro | `07 Where Is My Mind_ (2007 Remaster).m4a` | 235 s | **unverändert wie Runde 1**: `src_in 17.0`, ~45 s, `fade_out_s: 4`, Danke-Karte in Stille |

- Vivaldi „Der Winter" und Galvanize [Edit] fallen **raus** (Dateien bleiben in `music/` liegen,
  werden nicht mehr referenziert).
- Neue Gesamtlänge grob: 181,5 (Akt 1) + ~196 (Akt 2) + ~45 (Aftermath) + ~6 Stille ≈ **~7:08**.
  Der alte Film war 8:53 — es müssen ~1:45 raus. Kürzung fährt über `priorities.csv`
  (`must` > `nice` > `ok`) plus die Streichungen in §2 unten. `ok`-Bilder fallen zuerst,
  danach `nice`; `must` bleibt.
- `target_duration_s` in `brief.yaml` auf die real gebaute Länge nachziehen (sonst bricht die
  QC-Längenprüfung ab — HANDOVER).

### 0.2 Miserlou-Loop-Datei (audio-designer)
Miserlou ist nur 2:16, Akt 2 braucht ~3:16. Eine **nahtlose interne Wiederholung** einbauen:
einen vollen Phrasenblock (Downbeat → Downbeat, per librosa-Beatgrid bestimmt) etwa in der
Mitte des Tracks doppeln, am Beat schneiden, 20–40 ms Equal-Power-Crossfade an der Nahtstelle.
Nicht zeitdehnen (kein Pitch-/Tempo-Artefakt). Ziel-Länge ~196 s (±4 s, muss auf einem
Downbeat enden). Ergebnis als neue Datei `music/01 Miserlou (loop-196).m4a`, Analyse frisch
cachen. Naht darf beim Drüberhören nicht auffallen.

### 0.3 Ducking — überall raus
Christian explizit: „du kannst überall das Ducking rausnehmen." **Keine `duck_music_db`- /
`duck_fade_s`-Werte mehr**, keine Duck-`AudioClip`s. O-Ton-Stellen, die hörbar bleiben sollen,
laufen nur über `gain_db` am O-Ton-Clip unter durchlaufender Musik — die Musik wird an keiner
Stelle abgesenkt. Für die Akt-2-Party-Videos gilt: **nur Musik**, O-Ton der Clips still oder
sehr leise (kein Anheben).
- Wo Runde 1 noch weiche Ducking-Rampen forderte (Schoko-Unboxing 1395, 4835-Tequila u.a.):
  gestrichen. Wenn irgendwo doch O-Ton kurz durchkommen soll, dann als sauberer Ein-/Ausblend
  am O-Ton-Clip selbst, „smoother" — kein Musik-Ducking.

### 0.4 Ken-Burns-Bewegung — variieren, nicht monoton
Das alte Preview zoomte auf **jedem** Bild gleich langsam rein. Das ist der Haupt-Kritikpunkt.
Pro Clip die Bewegung wechseln: mal Pan links→rechts, mal rechts→links, mal unten→oben, mal
oben→unten, mal leicht rein, mal leicht **raus**. Amplitude spürbar, aber ruhig (Akt 1) bzw.
knapp (Akt 2). Manche Bilder dürfen auch **ganz ohne** Ken Burns stehen — der Effekt ist ein
Gewürz, keine Pflicht. `timeline-builder`: `effects[].kenburns` pro Clip mit wechselnder
Richtung/Start-End-Box setzen, nicht den Preset-Default durchlaufen lassen.

### 0.5 Hochkantbilder — Blur-Extend statt Überskalieren
Mehrfach gerügt: Hochkantfotos wurden vollflächig gefüllt → Köpfe abgeschnitten, Bild matschig.
Regel (wie im Norwegen-Video): Hochkant = **volle Bildhöhe zeigen**, links/rechts mit
weichgezeichneter, gestreckter Kopie desselben Bildes füllen — `fit: "blur"` am Clip
(render.py kann das, HANDOVER Runde 3). Leichtes Ken Burns erlaubt, aber das Motiv **nicht**
wegzoomen/wegskalieren. Betrifft u.a. Sülemann-Bild, das „skalierte Gruppenbild" (~0:33),
Pizzakarton, Pizza-Nahaufnahme, Becher-Bilder, Brüssel-Duck, Mannequin-Pis, Delirium-Glas,
Rooftop-Hochkant-Gruppe (1515), Reit-/Bär-Aufsteller.

### 0.6 Text-Einblendungen — Stil & Timing
Aktuell nur nackter Text mittig. Soll:
- **Nicht** Mitte-Mitte. **Nie** über Gesichtern. Regel: unten rechts oder unten links (Akt 2),
  bzw. am Rand (Akt 1), mit Abstand zum Bildrand. Einzelne Stellen mit Vorgabe (s. §1).
- Coole Schrift, groß, **bold**, leicht **schräg** gestellt, mit **Schatten** — „funky".
  Font: Bangers (Display) für Akt 2, Poppins SemiBold/Bold für Akt 1.
- **Auftritt animiert**: Buchstaben einzeln / kurz nacheinander rein, oder Wortteile
  gegeneinander laufend, oder Größe ändern beim Erscheinen. Nicht hart aufblenden.
- **Muss weg sein, bevor der Fade zum nächsten Bild beginnt** — kein Text, der über den
  Schnitt/Fade hinweg stehenbleibt und sich mit dem nächsten Bild überlagert.
- Zweizeiler / Dreizeiler bewusst umbrechen (z.B. „Ein bisschen / genießt er es / ja schon").

### 0.7 Speed-Ramps in Akt-2-Videos
Gelegentlich (nicht durchgängig): ein paar Frames schnell auf eine markante Stelle zu, dort
dann normal/langsam weiterlaufen lassen. Bringt Dynamik **und** spart Laufzeit. Sparsam, an
2–4 Clips, nicht als Dauereffekt. `VideoClip.speed` + kurze Rampe.

### 0.8 Schnitt-Tempo Akt 2
Darf **deutlich schneller** geschnitten sein als im alten Preview — aber nicht 1-Frame-hektisch.
Kurze Clips (0,4–1,5 s) sind ok, gerade um Streichbilder als schnelle Blitze noch unterzubringen.

### 0.9 André
Namensstempel: **konsistent** schreiben. Wenn „André" mit Akzent im Bangers-Rendering sauber
kommt → überall „André". Wenn der é-Glyph fehlt/tofu → überall „Andre" (ohne Akzent), auch im
Dateinamen-Key. Kein Mischen. `party-fx` prüft das Rendering und entscheidet einmal.

---

## 1. Intro & Akt-1-Durchgang (Champions League Theme)

- **Intro**: Schwarz → weiche Blende in `JGA_INTRO.png`. Erste Blende darf **gestreckt** sein
  (langsam rein, gut so). Die **zweite** Schwarzblende (raus aus dem Standbild) ist im alten
  Preview **zu lang** → deutlich kürzen. Kurz ausblenden reicht.
- Erstes echtes Bild ist richtig gewählt (bleibt).
- **~0:14 (Bild 3, zwei Personen Daumen hoch)**: **nach hinten** schieben. Erst das Bild
  danach zeigen (Couch, ~0:17 — gut). Dann die „Daumen hoch"-Leute. Danach normal weiter.
- **Haus zeigen**: das zweite Haus-Bild ist zu viel → eins reicht.
- **~0:28 (nur das Bett)**: **raus**.
- **~0:29 Treppenhaus**: bleibt. **~0:33**: bleibt, aber das ist ein Blur-Extend-Fall
  (Gruppenbild, überskaliert, halbe Gesichter weg) → §0.5.
- **„Let's go" / Intro-Text**: Position und Auftritt besser (§0.6). Text z.B. „Let's go" oder
  „Los geht's!" / „Let the party start!" — groß, bold, schräg, unten rechts, Schatten,
  „Let's" und „go" nacheinander rein.
- **Sülemann**: Text **„Der Mann des Abends: Süleman Pizza-Star"** o.ä. (Christian schwankte —
  „Es lebe Sülemann" / „Lang lebe Süleman"). Schreibweise **„Süleman"**. Bild ist Blur-Extend
  (Hochkant, halber Kopf weg) → §0.5. Text animiert, nicht nur reinblenden.
- **Pizzakarton** → Blur-Extend. **Pizza-Nahaufnahme**: sehr nah, hochkant wäre besser →
  Blur-Extend, ggf. etwas rauszoomen.
- **Frühstück / nächster Morgen**: Reihenfolge gut. **Tausch**: das Bild bei **~0:56** soll
  **vor** das Bild bei **~0:53** — also 0:56 zuerst (Frühstücksstart), dann 0:53.
- **Reit-/Pferde-Bilder**: gut, bleiben.
- **~1:33**: bleibt.
- **Einfamilienhaus-Bild**: bleibt („mega toll").
- **~1:48 Bier-Logo mit belgischer Fahne (1381)**: **raus** (statt Sprechblase). — Achtung:
  Runde 1 wollte hier die Sprechblase „Design Award 2026". Runde 2 streicht das Bild. Der
  „eine erlaubte Akt-1-FX-Akzent" wandert damit auf **1390** (kleiner Sticker am Pappbären).
- **~1:50 Kranbild**: eher raus.
- **~1:56 Doppelung** (Architektur von oben, zweite Version = Kranbild): das Kranbild raus.
- **Waffeln von vorn (~2:02/2:03)**: jetzt nur noch `nice`/`ok`. Das Bild **von oben danach**
  ist schöner → das bevorzugen.
- **Bär-Pappaufsteller**: Hochkant, halber Kopf → Blur-Extend; ist `ok`-Bild, nur wenn Platz.
- **Schokoladen-Bilder**: sind etwas **zu viele** → ausdünnen. Schoko-**Video** (Praliniere
  1395) muss nicht zwingend rein.
- **~2:20**: **raus** (nicht schön).
- **~2:22**: bleibt („der steht so geil") — gut.
- **Becher-Hochkant (Schokomousse 4793)** → Blur-Extend.
- **Brüssel-Duck-Store-Bild** → Blur-Extend (Hochkant).
- **Mannequin-Pis ~2:42 (auf den Penis zentriert)**: wenn Hochkant → drin lassen als
  `ok`/`kann`; sonst eher raus.
- **Präsente für den Junggesellen (1403)**: bleibt. Text animiert/stylish (§0.6).
- **1406 „ein bisschen genießt er es ja schon"**: Text in **drei Zeilen**
  („Ein bisschen / genießt er es / ja schon"), Position **links oben**, coole Schrift.
- **~3:02**: `kann`-Bild. **~3:05**: `muss`. **~3:08**: bleibt.
- **MOK Coffee**: Bild gut. Trio-Sitzbild gut. Schaufenster „100 Best Coffee Shops" (1435):
  **muss** rein. **~3:21**: `kann`-Bild. Kipferl: gut. Pommes: gut.

---

## 2. Akt-1 → Akt-2 Übergang & Musik-Sync (Miserlou-Loop)

- Nach dem **Pommes-Schwenk** endet Champions League Theme. Der **Cut auf Akt 2 / Start
  Miserlou** liegt auf dem Bild, das im alten Preview bei **~3:28** lag: **drei Personen,
  Daumen hoch** (die neu Dazugestoßenen). Miserlou setzt **~0,5 s vorher** ein (auf dem
  Pommes-Bild kann er anfangen), sodass der Beat exakt auf dem „3 Personen Daumen hoch"-Cut
  sitzt.
- Text an dieser Stelle: **„Crew-Update"** o.ä. — Christian-Vorschläge: „Die verlorenen Söhne
  stoßen dazu". `party-fx` darf finalisieren.
- Danach sind **zu viele Bilder** im Block — ausdünnen. Bei den „Jungs" **muss** die Musik
  schon laufen.

---

## 3. Akt 2 — per-Bild (Miserlou-Loop)

### Burlesque / erste Kneipe
- **~3:31 Eingangsbild (à la Bécasse Eingang)**: **raus** (kein schönes Bild). Stattdessen
  gleich das **Bild danach** als Einstieg. — überschreibt Runde 1 (dort war 1445 der Einleiter).
- Danach: Tränke-Bild → Linse → Demoschritte. **Schnellerer Schnitt hier: gut.**
- **~3:47 kurzes Bild, 90° falsch gedreht**: **muss drin bleiben**, aber **um 90° drehen**.
- **Timmermans-mit-Witte (1455)**: `kann` — ggf. raus. (Runde 1 wollte hier den „Nebengewerbe"-
  Wortwitz — nur wenn das Bild bleibt.)
- **~3:51**: das eine Bild **raus**; **kein Ducking** dort.
- Kurzer Videoschnipsel danach: **Anfang 1–2 s wegschneiden**, direkt aufs Lächeln/Smiley
  rein. Nächstes Bild (Trinken/Cocktail) gut.
- **Delirium-Bier**: muss zur Höhe / voll zu sehen sein → Blur-Extend (Hochkant-Regel).
- **~4:11**: **raus**. **~4:12 (Runde-1-TC „5:12")**: `kann`. **~4:14 Delirium-Bild**: bleibt,
  sehr schön.

### Rooftop Bar 58
- **~4:17 / „Rooftop war 58 — auf geht's / wir kommen"**: Text links oben, geile Schrift, cooler
  Auftritt, Farben (§0.6).
- Sehr viele Sonnenuntergangsbilder → **ausdünnen**. **~4:36 überladen** → eins raus.
- **~4:41 (zwei Personen, schon dunkel)**: an **spätere** Position schieben (zwei sehr ähnliche
  Bilder lagen hintereinander).
- **~4:44**: Bild, das eigentlich in die **Karaoke-Sektion** gehört → **hier raus**, dort
  einsortieren.
- **~4:48 kleiner Videoschnipsel**: kein `muss` → eher raus.
- **~4:51 Corona-Flaschen (1524-Umfeld)**: **muss**. Zweites Corona-Bild danach: `kann`.
- **~4:56 „Stay hydrated" (1543)**: bleibt, aber **Werbecharakter**, coole Schrift oben rechts,
  „stay" + „hydrated" als **zwei Elemente**, ggf. gegeneinander laufend, halb übereinander,
  dann langsam ausfaden. **~4:57**: Bild danach eher **raus**.
- **„Wo ist Christoph?" (1514)**: schönes Bild, Text **unten rechts**, kleiner, nette Schrift,
  drei Fragezeichen. **Nicht** mittig.
- **~5:01 zwei fast gleiche Bilder hintereinander**: auf **eins** reduzieren (das mit weniger
  Skalierungsbedarf).

### Zeit-Vermischung Rooftop ↔ Karaoke — HART TRENNEN
Im alten Preview sind Karaoke-Bilder (kräftiges Blau-Lila) mitten in der Rooftop-Sequenz und
umgekehrt. Das ist ein Fehler. `timeline-builder`: Rooftop-/Blaue-Stunde-Block und
Karaoke-Bar-Block **sauber nacheinander**, keine Sprünge zurück.
- **~5:04–5:07**: mehrere Karaoke-Bilder liegen zu früh (noch Rooftop) → in den Karaoke-Block.
- **~5:13–5:18**: Weg zur Karaoke-Bar (Uhrzeit/Architektur) — `kann`/`muss` gemischt, ok.
- **~5:20 Video (Karaoke) dann ~5:21 Sonnenuntergang**: der **Sonnenuntergang (1508/1518-Klasse)**
  gehört **in die Mitte** der Rooftop-Sequenz, nicht ans Ende und nicht neben Karaoke.
- **~5:25**: **raus** (zu dunkel).
- **~5:27 / ~5:29**: Weg zur Karaoke-Bar.
- **~5:33 Downtown**: `kann`.

### Burger-Stop (vor Karaoke)
- Vor der Karaoke-Bar der **Burger-Stop** — bringt die Zeit besser rüber. Zwei Burger-Bilder
  gut, Brücke/Burger-Truppe (1597) gut.
- **Claude-Schild „Frische Token" (1598)**: Text „**wolle** Token **kaufen** ???" — „wolle"
  klein, „Token" groß, „kaufen" klein, drei Fragezeichen, nett animiert. Skalierung des Bildes
  prüfen (wirkt komisch).

### Red Karaoke-Bar (+ Cast-Intro)
- **~5:49 „Red Karaoke" (1611/1619-Klasse)**: **Einleitungsbild** für die Karaoke-Sektion.
  Danach die blauen Bilder.
- **Tequila (1608)**: **kein Ducking** (§0.3).
- **~6:00 Video mit Knutscher**: „einfach perfekt" — nur **etwas kürzen**.
- **Larrette-Bild**: kann zwischendrin.
- **~6:11 „I wandered that way"**: **raus**. **~6:12 Mini-Video**: **raus**.
- **~6:15**: „super mega Bild" — bleibt.

#### Cast-Intro (9 Personen, party-fx §5)
- Im alten Preview lagen die Namen **Mitte-Mitte über den Gesichtern**, überblendeten sich,
  zu schnell. Neu:
  - Name **unten links / unten rechts**, **schräg**, coole Schrift, **einzelne Buchstaben**
    nacheinander rein, etwas mehr Standzeit pro Person.
  - Bevor der Fade zum nächsten Foto beginnt, ist der Name **komplett ausgeblendet**.
  - Ansonsten Mechanik wie geplant (Standbild 0,6–1,0 s, Bangers, kurzer SFX, `color_pop`
    beim Cut). Reihenfolge unverändert: Witte · Christoph · Matti · Bartosz · Hagi · Bernhard ·
    André · Skuub · **Micha zuletzt** (Stempel „Micha im Delirium", Sonderblau `#4fd8ff`).
  - SFX: 9× Whoosh + Stamp aus `music/sfx/` (liegt bereit, siehe unten), Micha größerer
    Stamp. Zeiten an die realen Cast-Cuts auf dem Miserlou-Beatgrid binden.

**SFX-Dateien (Task T3, liegen in `projects/michael-jga-2026/music/sfx/`, gitignoriert wie
alle `music/*`):**
| Datei | Länge | Peak | Quelle / Lizenz |
|---|---|---|---|
| `sfx-cast-whoosh.wav` | 0,42 s | −12 dBFS | Mixkit SFX #1485 „Fast whoosh transition", **Mixkit Free License** (kommerziell frei, keine Attribution, nicht als Stock weiterverbreiten) |
| `sfx-cast-stamp.wav` | 0,40 s | −10 dBFS | Mixkit SFX #752 (Kategorie „thud"), Mixkit Free License |
| `sfx-cast-stamp-micha.wav` | 0,55 s | −9 dBFS | wie #752, −5 Halbtöne + kurzer Raum (für den Bräutigam) |
Aufbereitet mit `soundfile`/`librosa` (48 kHz, Stereo, PCM16), Skript im Scratchpad
(`mk_sfx.py`). Whoosh+Stamp im Render pro Person **überlappend** legen (Whoosh −6 dB, Stamp
0 dB), Micha-Cut nutzt `sfx-cast-stamp-micha.wav`.

### Weiterziehen / Tanz / Gesang
- **Ducking überall raus** (§0.3). „Einfach nur Musik."
- **Speed-Ramps** (§0.7) an 1621 / 1635 / 1637 einstreuen — Dynamik + Zeitgewinn.
- **~6:xx Video mit dem Knutscher**: s.o., etwas kürzen.
- **1635 Dance**: `FX:` Farb-Pop / Speedlines auf den Beat.
- **1637 Karaoke-Gesang, Hauptstelle „dreht sich um" (2:22–2:37 im Clip)**: unbedingt drin,
  **O-Ton nur leise** unter der Musik, kein Ducking.
- **Micha im Delirium** (Lampen-Szene, Video): „einfach super" — bleibt, wie es ist.
- **„Gehen hier etwa schon die Lampen aus?" (1634)**: Text **unten rechts**, mit Abstand,
  **nicht** über Gesichter.
- Nächste Szene (Video, „der mit dem Video reinkommt"): Text **unten rechts**
  „Natürlich … (noch nicht)" — „noch nicht" in Klammern.
- Party-Videos danach: viele, **Laufzeit knapp** → über Miserlou-Loop + Speed-Ramps Zeit
  holen, `ok`/`nice`-Fotos dazwischen streichen, Videos eher behalten.
- **Bräutigam singt** (Video): schön, ggf. etwas schneiden.
- **~7:23 Video**: optional. **~7:25 Foto**: optional. **~7:26 Video von ihm**: **muss** drin.
- **~7:34 Tequila-Hangar oben**: super, bleibt. Danach: „nach Hause".
- **Delirium-Valley-Hochkant** → Blur-Extend, mit Ecken/Seiten. **Berliner/Dattler** beide
  nochmal. **Taxi** ein bisschen (nicht wichtig, aber cool).

### Taxi / abgeschossen / Gurken — Ende Akt 2 neu ordnen
Das alte Ende ab hier „nicht gelungen", Texte sitzen schlecht, Audio schon aus. Neu:
1. Nach dem **Video ~7:51** (nach Hause gelaufen): zuerst das **Gurken-„What the fuck"-Bild
   (1660)**, Text **nur „WTF?"**.
2. Danach die **zwei Nachthaus-Bilder ~7:54 / ~7:55** (die beiden im Bett, 1656/1658).
3. Bei **~7:58**: Text „**Ich war es nicht.**" (Christoph-Gag, 1659).
4. Dann das **zweite Gurkenbild (1661)** (~8:02), Text
   „**Der Michael mag Gurken. Gib mir Gurken. Der Michael braucht Gurken.**" — skurril.
5. Danach **Schwarz-Fade**. Audio (Miserlou) ist hier **weg**. Nur noch das **Video von den
   Names** vorher — d.h. Miserlou endet **vor** dem Gurken-Block, der Gurken-Block läuft in
   Stille bzw. auf dem auslaufenden Track, dann Schwarz.

---

## 4. Aftermath / Outro (Where Is My Mind)

- Aus dem Schwarz heraus: **Mitte der Schwarzblende** setzt Where Is My Mind ein (src_in 17 s),
  zieht in den **nächsten Morgen**.
- **~8:07 zwei fast gleiche Bilder**: eins **raus** (das erste, 8:07).
- **Michael-Bild ~8:11**: **später** — nicht so früh im Abspann. Gehört vor das Bild ~8:26.
- **~8:13**: **muss** drin.
- **~8:16 (Bild aus der Bar, letzte Nacht)**: **raus** (passt zeitlich nicht). Ggf. als
  schneller Blitz woanders.
- **~8:19 / ~8:20**: **raus**.
- Weiter mit **~8:22** — die zwei **Michael-„zerstört"-Bilder** müssen rein.
- **~8:30 (vor der Tür)**: **super wichtiges Bild**, aber **nicht in den Abspann** — gehört zur
  **Rooftop-Sequenz** (danach, als sie runtergegangen sind / vor dem Burgerladen). Dort
  einbauen.
- **~8:54 Bild**: braucht man, bleibt.

### Aftermath — feste Bild-Reihenfolge (Christian diktiert)
1. **~8:37** — Christoph liegt da. **Erstes** Bild, in dieses blenden wir rein → Text
   „**Where is my mind?**".
2. **~8:14** — Michael.
3. **~8:24** — Michael.
4. **~8:04** — die Gruppe.
5. **~8:11** — Michael (nochmal, jetzt hier).
6. **~8:27** — jemand übergibt sich (dezent).
7. **~8:34**.
8. **~8:40** und **~8:45** — die letzten beiden Bilder.
9. Dann **kein harter Schnitt**: Musik läuft aus, **Schwarzblende**, dann letzter Part.

### Schluss
- Der „extrem KI"-wirkende, unsaubere Schwarzblenden-Übergang am Ende: aufräumen, sauberer
  Cross-Fade.
- **Text** (bleibt inhaltlich, sitzt aber besser): „Drink responsibly" · „Danke, Jungs" ·
  „Super Crew, tolle Erinnerung" · „Genug Käse" · „Ein unvergesslicher Abend" ·
  „Micha im Delirium". — animiert, sauber, nicht über Gesichter.
- Dann Audio weg, dann Schwarzblende vom Bild. Ende.

---

## 5. FX-Sammelliste Runde 2 (party-fx) — Delta zu Runde 1

Runde-1-FX-Liste (`editorial-notes.md` §"FX-Sammelliste") bleibt Grundlage. Änderungen:
- **1381 gestrichen** → Sprechblase „Design Award 2026" entfällt. Einziger Akt-1-Akzent = **1390**
  Sticker am Pappbären.
- **Denkblasen / Sticker / Kronen / Herzchen jetzt umsetzen** (Runde 1 hatte sie auf „Runde 2"
  geschoben, weil `thought-bubble.svg` / `sticker.svg` / `speedlines.svg` rote Tests hatten —
  die werden in Task T1 grün gemacht):
  - **1706 / 1707** Herzchen + goldene Kronen (Aftermath / Rooftop).
  - **1464 „Delirium"** als zittrig nachgemalte Leuchtschrift.
  - **1544** Corona-Extra „Werbe"-Look, Flüssigkeitslinie = Horizont.
  - **1621 / 1635 / 1637 / 4835** Speedlines/Farb-Pop an den lautesten Beats, sparsam.
  - Cast-Intro: `color_pop` auf allen 9 Cuts + 9 SFX (nicht nur auf Michas Cut).
- Alle Text-FX nach den Stil-/Positions-/Timing-Regeln aus §0.6.
- **André**-Schreibweise einmal final festlegen (§0.9).

---

## 6. Was NICHT ändern (aus dem Preview ausdrücklich gelobt)

- Intro: Schwarz → Blende ins Standbild (erste, gestreckte Blende).
- Erste Bildauswahl/-reihenfolge Akt 1 bis auf die genannten Ausnahmen.
- Reit-/Pferde-Bilder, Einfamilienhaus-Bild, „~2:22 der steht so geil".
- Frühstücks-/nächster-Morgen-Reihenfolge (bis auf den 0:53/0:56-Tausch).
- „Micha im Delirium"-Lampen-Video.
- MOK-Coffee-Auswahl.
- Aftermath-Textinhalte (Drink responsibly / Danke Jungs …).
