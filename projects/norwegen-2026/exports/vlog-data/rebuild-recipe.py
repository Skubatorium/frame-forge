"""Rezept, das `timeline.json` fuer `vlog-data` neu aufbaut (Nutzer-Feedback Runde 3).

Warum ein Rezept und keine Handarbeit an 160 Clips: das Feedback aus Runde 3 war fast
vollstaendig **strukturell** (Reihenfolge, Doppelungen, Ausschnitt, Bauchbinden) statt punktuell.
Hier steht die Schnittentscheidung je Reisetag als Liste von Asset-IDs, alles andere (Timing,
Uebergaenge, Ken-Burns-Parameter, Bauchbinden-Timing, Audio) rechnet das Skript daraus aus.
Reproduzierbar und nachlesbar; `timeline.json` bleibt Single Source of Truth fuer den Render.

Aufruf von Repo-Root: `.venv/bin/python projects/norwegen-2026/exports/vlog-data/rebuild-recipe.py`

## Die drei Befunde, die den Umbau tragen

1. **Kamera-Zeitstempel sind UTC, Handy/Drohne lokal (+2h).** Verifiziert an drei unabhaengigen
   Tagen ueber Szenen, die von beiden Geraeten aufgenommen wurden (18.07. Kartenhaus:
   `camera` 16:39 vs `phone` 18:39 -- dieselbe Minute; 25.07. Bogenschiessen: `camera` 12:25 vs
   `phone` 14:24; 27.07. RIB-Tour: `camera` 13:06 vs `stages.csv` "RIB-Safari 15:00").
   Ohne diese Korrektur landen Kamera-Clips im Schnitt ~2h zu fruech -- genau die "Logikfehler"
   und "Spruenge", die der Nutzer beschrieben hat (Wikingerdorf-Aktivitaeten VOR der Ankunft
   ueber die Bruecke, Treppen- und RIB-Block ineinander verschraenkt).
   `CAMERA_UTC_OFFSET_H` macht die Korrektur explizit und nur fuer die Sortierung.

2. **Die Clips waren innerhalb der Tage praktisch unsortiert.** Beispiel 19.07.: 13:16, 09:32,
   15:04, 16:11, 13:04, 14:33, 18:58, 12:39, 18:14, 10:00, 06:40. Das Morgenbild in Flensburg
   (06:40) stand als letzter Clip des Tages -- der Nutzer hat das als eigenen Punkt gemeldet.
   Deshalb ist die Standard-Reihenfolge jetzt "nach korrigierter Aufnahmezeit"; `DAYS` listet
   die Assets in der Zielreihenfolge, damit die Abweichungen davon sichtbar sind.

3. **Hochkant-Material war der Grund fuer die angeschnittenen Personen UND die schwarzen
   Balken.** Fotos liefen ueber crop-to-fill (schnitt Koepfe ab, wenn die Gesichtserkennung eine
   Person nicht gefunden hatte -- bei Kindern mit Kappe/Sonnenbrille die Regel), Videos ueber
   Letterbox (die "dicken schwarzen Balken"). Beide Faelle bekommen jetzt `fit: "blur"`
   (ungeschnitten zentriert auf unscharfem Hintergrund, siehe `render._blur_fill_statements`).
   `PORTRAIT_MAX_ASPECT` entscheidet, ab wann ein Clip so behandelt wird.

## Was NICHT hier steht

- Die Titel-PNGs: `title-recipe.py`.
- Die Bauchbinden-PNGs: `stage-caption-recipe.py` (Text/Geometrie); das Timing rechnet dieses
  Skript und schreibt es in `tracks.overlay`.
- Der Karten-Track ist entfallen (Nutzer: "Ich muss leider die Entscheidung treffen, dass wir
  die Karte ausbauen") -- `tracks.map` bleibt leer, die Insets unter `map/` bleiben als
  Zwischenstand liegen, werden aber nicht mehr gerendert.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path("projects/norwegen-2026")
EXPORT = ROOT / "exports" / "vlog-data"
RES = (3840, 2160)
FPS = 30.0

# Kamera-Uhr laeuft auf UTC, Handy/Drohne auf Ortszeit (CEST). Nur fuer die Sortierung.
CAMERA_UTC_OFFSET_H = 2

# Ab hier gilt ein Clip als Hochkant/quadratisch und bekommt `fit: "blur"` statt crop/pad.
PORTRAIT_MAX_ASPECT = 1.05

# -- Schnittfassung je Reisetag -------------------------------------------------------------
# Reihenfolge = Zielreihenfolge im Film. Standard ist die korrigierte Aufnahmezeit; wo davon
# abgewichen wird, steht der Grund als Kommentar dahinter (immer Nutzer-Feedback Runde 3).
DAYS: dict[str, list[str]] = {
    # Tag 0 -- Beladen am Abend vor der Abreise.
    "2026-07-17": [
        "20260717-phone-0247f0",  # 18:13 Heck, Dachbox offen
        "20260717-phone-822c50",  # 18:17 beladener Kombi an der Strasse
    ],
    # Tag 1 -- Grevenbroich -> Flensburg. Nutzer wollte die Strecke deutlicher ("da kommt die
    # Strecke zu kurz"): Kaffee unterwegs + Hamburger Hafen dazu. Blumen/Moewe VOR der
    # Hafenpromenade ("da muesste zuerst was mit den Blumen oder der Moewe kommen"), danach
    # Ankunft mit dem Segler dahinter.
    "2026-07-18": [
        "20260718-phone-a788c9",  # 07:00 Oskar im Kindersitz, Aufbruch
        "20260718-phone-aed4c0",  # 09:29 Kaffee an der Raststaette -- NEU, "Kaffeebild"
        "20260718-phone-78974b",  # 13:13 Containerbruecken Hamburger Hafen -- NEU, Strecke
        "20260718-camera-d81da5",  # 14:59 Blumenbeet -- NEU, vor die Promenade gezogen
        "20260718-camera-b903eb",  # 14:58 Moewe auf dem Kopfsteinpflaster
        "20260718-camera-4a336b",  # 14:58 Schwenk Hafenpromenade Flensburg
        "20260718-phone-0ad093",  # 16:59 Familie am Kai vor dem Traditionssegler
        "20260718-camera-bacc27",  # 16:39 Kartenhaus aus Bierdeckeln (Video)
        "20260718-phone-83859a",  # 17:00 Hafenbecken, rotes Gebaeude -- NEU, "schoenes Rot"
        "20260718-phone-b0d0be",  # 17:06 Hafensteg mit Blumenampel
        # Raus: 20260718-phone-fa0f82 (Kartenhaus als Standbild direkt nach dem Kartenhaus-Video
        # -- "jetzt ist fuer mich eine Doppelung drin ... da muesste man was anderes nehmen").
    ],
    # Tag 2 -- Flensburg -> Skien. Morgenbild in Flensburg zuerst, dann Faehrterminal, erst
    # danach das Deck ("die Colourline muss getauscht werden ... danach macht es Sinn, die
    # Bilder von Oskar auf dem Deck zu zeigen"), Pizza vor der Flur-Szene.
    "2026-07-19": [
        "20260719-phone-0d87b4",  # 06:40 Morgensonne ueber dem Faehrterminal, Flensburg
        "20260719-camera-a37b5f",  # 09:32 Color-Line-Faehre am Terminal
        "20260719-phone-6f7371",  # 12:39 Familien-Selfie im Auto
        "20260719-phone-4a0970",  # 14:33 Brettspiel im Bordrestaurant
        "20260719-camera-21e343",  # 15:04 Oskar rennt ueber das Deck (Video, O-Ton/Ducking)
        "20260719-camera-3333c0",  # 15:16 Oskar posiert an der Kapuze
        "20260719-phone-b5868d",  # 16:11 Familien-Selfie auf dem Deck
        "20260719-phone-06c1ed",  # 18:14 Pizza bei den Freunden in Skien
        "20260719-phone-16d7f7",  # 18:58 Oskar wird auf der Decke durch den Flur gezogen
        # Raus: 20260719-phone-13fc22 (Standbild "spielt im Wind" direkt nach dem Deck-Video),
        #       20260719-phone-57e0de (Oskar im Auto am Tablet -- "das Bild soll raus").
    ],
    # Tag 3 -- Huette am See bei Skien. Grillen/Abendessen ans Tagesende ("jetzt ist der Ausflug
    # auseinandergerissen"), Beeren-Nahaufnahme und das angeschnittene Hochkantfoto raus.
    "2026-07-20": [
        "20260720-camera-669f06",  # 14:04 Waldsee mit Insel (Establisher)
        "20260720-camera-427a02",  # 14:07 weite Landschaft, Huegel und Seen
        "20260720-camera-01f68b",  # 14:09 Huettensiedlung am See von oben
        "20260720-phone-7c3e31",  # 14:43 Weidenroeschen-Feld
        "20260720-phone-01214e",  # 15:14 Familie auf dem Steg
        "20260720-camera-622c38",  # 15:22 Person auf dem Holzsteg, Wolkenspiegelung
        "20260720-camera-1058a9",  # 15:37 Ruderboot nah, Vater rudert ("richtig schoen paddeln")
        "20260720-camera-0ec48c",  # 15:38 Ruderboot mit Wolkenspiegelung
        "20260720-phone-0bd153",  # 16:01 Beeren pfluecken am Ufer
        "20260720-camera-3de2ef",  # 16:17 Paddleboards senkrecht von oben
        "20260720-phone-2308e5",  # 18:11 Grillen/Abendessen -- bewusst als Tagesabschluss
        # Raus: 20260720-camera-542e68 (erste Bootsfahrt, "die sieht so hilflos aus"),
        #       20260720-phone-ffc1ef (Hochkant, Gesicht + Beere weggeschnitten -- ersetzt durch
        #       den Beeren-pfluecken-Shot, den der Nutzer ausdruecklich mochte),
        #       20260720-phone-bcc3b5 (Beeren-Nahaufnahme, "die Beere finde ich unnoetig").
    ],
    # Tag 4 -- Ausflug ans Meer. Bauchbinde ist ein Aktivitaetstag ("Tag am Meer").
    "2026-07-21": [
        "20260721-phone-873dfd",  # 12:55 weiter Blick ueber die Badebucht
        "20260721-phone-ca46c2",  # 13:04 Felskueste, glitzerndes Meer
        "20260721-phone-33e8c5",  # 13:12 Badebucht mit Sandstrand
        "20260721-camera-cc5bd6",  # 14:17 Oskar isst auf dem Felsen (gekuerzt, s. TRIMS)
        # Raus: 20260721-phone-2c1992 ("komplett abgeschnitten oben, der halbe Oberkoerper").
    ],
    # Tag 5 -- Ruhetag in Skien. Vom Nutzer explizit vorgegebene Reihenfolge, NICHT chronologisch:
    # "Das Winkebild, was davor kam, das sollte ans Ende. Danach nach diesem Gitarren-Solo, dann
    # kann die noch mal winken und dann den Sonnenuntergang."
    "2026-07-22": [
        "20260722-phone-fdc96c",  # 16:10 Grillen, grosse Runde am Tisch
        "20260722-camera-7545fc",  # 15:28 Kitzeln/Gitarre im Wohnzimmer (O-Ton/Ducking)
        "20260722-phone-074074",  # 17:52 Winken von der Terrasse
        "20260722-drone-71e612",  # 21:54 Sonnenuntergang, orangerot
        "20260722-drone-a31495",  # 21:51 Sonne hinter dem Huegelkamm ("Lens-Flare")
        # Raus: 20260722-phone-d9b55c ("hier ist auch so viel abgeschnitten, macht keinen Sinn").
    ],
    # Tag 6 -- Skien -> Geilo. Unterkunft ans Tagesende ("diese Unterkunft ... muss spaeter
    # kommen, weil wir auf dem Weg dahin gewesen sind"), Totale direkt vor dem Bruecken-Durchflug
    # ("so ein bisschen Totale und dann auf die Brueckenszene gehen").
    "2026-07-23": [
        "20260723-camera-0df50b",  # 12:24L Heddal-Stabkirche
        "20260723-camera-49948e",  # 12:24L Stabkirche weitwinklig ueber den Friedhof
        "20260723-phone-3a599b",  # 12:35 Oskar vor der Aexte-Vitrine im Museum
        "20260723-phone-c42193",  # 12:45 Picknick auf der Wiese
        "20260723-drone-92fb1e",  # 14:07 Fjordsee mit Uferstrasse
        "20260723-drone-3db9c1",  # 14:07 See mit kleiner Marina
        "20260723-drone-61a62c",  # 14:08 Dorf im Flusstal mit Bruecke (Totale)
        "20260723-drone-c0be40",  # 14:09 Tiefflug unter der Strassenbruecke
        "20260723-phone-013f67",  # 15:17 Paar-Selfie mit Bergpanorama
        "20260723-phone-0fff0f",  # 17:42 Bergsee mit Ortsschild
        "20260723-drone-34c28f",  # 17:43 Hochgebirgssee mit Halbinsel
        "20260723-drone-07b1ef",  # 17:45 Hochebene bei Geilo, Grasdachhuetten
        "20260723-drone-40d97d",  # 17:45 Grasdachhuetten senkrecht von oben (Unterkunft)
        "20260723-drone-f9365c",  # 17:47 Landzunge mit Wanderwegen
        # Raus: 20260723-phone-2fed83 (Rosemaling-Teller -- "man sieht nur die Haelfte von
        # diesem Bild, das ist ein Artefakt, ein Museum, das macht keinen Sinn").
    ],
    # Tag 7 -- Geilo -> Aurland. Aussichtspunkte VOR der Flaamsbahn, Unterkunft (Winjum Cabins)
    # ans Tagesende, Kreuzfahrtschiff zuletzt und dabei von weit nach nah
    # ("ich wuerde zuerst die Szene von 8:42 nehmen und danach die von 8:36").
    "2026-07-24": [
        "20260724-camera-4c6ded",  # 11:53L Passstrasse am See
        "20260724-drone-0be02d",  # 12:11 Bergstrasse durch die Hochebene
        "20260724-phone-84ed90",  # 12:51 Aussichtspunkt ueber dem Fjord -- NEU
        "20260724-drone-094825",  # 12:53 tief eingeschnittener Fjord
        "20260724-camera-a690e2",  # 13:58L Fjordblick vom Aussichtspunkt, Nebel
        "20260724-drone-2f2cf4",  # 14:03 Stegastein-Plattform von oben
        "20260724-phone-e78577",  # 15:53 Vater und Sohn im historischen Waggon (Abfahrt 16:00)
        "20260724-camera-45e18d",  # 16:29L Zug faehrt vorbei -- NEU, macht die Flaamsbahn klar
        "20260724-camera-e1e3ae",  # 16:32L Blick aus dem Zugfenster ins Flusstal
        "20260807-camera-7c5d12",  # 15:00L Kjosfossen-Halt, Person in Rot -- Christinas iPhone
        # laeuft nochmal anders als Chris' Geraet, die Zeit passt nicht zum Halt um 17:20.
        # Bewusst neben das Kjosfossen-Foto gesetzt, wohin der Clip inhaltlich gehoert.
        "20260724-phone-5df3fd",  # 17:20 Kjosfossen in Kaskaden
        "20260724-camera-cc5cbc",  # 17:27L Zugbahn in Serpentinen den Hang hinauf
        "20260724-drone-c794de",  # 19:56 Winjum Cabins von oben (Unterkunft, Tagesende)
        "20260724-drone-0c5020",  # 19:56 Fjorddorf mit weissen Holzhaeusern
        "20260724-drone-7523dd",  # 20:01 Fjorddorf, tief haengende Wolken
        "20260724-drone-37d1f5",  # 22:05 Kreuzfahrtschiff aus der Vogelperspektive (weit)
        "20260724-drone-242fdd",  # 22:03 Kreuzfahrtschiff naeher, schmaler Fjord
        "20260724-drone-3f1f99",  # 22:10 beleuchtetes Schiff in der Abenddaemmerung
    ],
    # Tag 8 -- Aurland, Wikingerdorf. Mit der Zeitkorrektur ergibt die Chronologie exakt die vom
    # Nutzer gewuenschte Dramaturgie: erst die Fjordfahrt, dann die Ankunft ueber die Bruecke
    # ("erzaehlerisch deutlich besser"), dann das Dorf, auf der Rueckfahrt der Regenbogen und das
    # Elektroboot, zum Schluss das Abendessen.
    "2026-07-25": [
        "20260725-phone-9c1fcd",  # 09:03 Morgen an der Huette, Blick auf den Aurlandsfjord
        "20260725-camera-5a21c7",  # 10:20L 'Artania' am Kai (bevor wir aufs Boot gestiegen sind)
        "20260725-camera-4ab117",  # 11:09L ruhiger Fjord vom Boot aus
        "20260725-camera-ca97b0",  # 11:14L Wasserfall in zwei Stufen vom Fjord aus
        "20260725-phone-4f6759",  # 12:29 Wikingerschiff-Bruecke -- die Ankunft
        "20260725-phone-c04b91",  # 12:33 Uebersicht Wikingerdorf ("super Ankunftsbild")
        "20260725-phone-1625fd",  # 13:11 Grassoden-Huetten und Feuerstelle
        "20260725-phone-cce497",  # 13:25 Wollverarbeitung wird vorgefuehrt
        "20260725-camera-bbb451",  # 13:52L Wikinger-Darsteller zwischen den Holztotems
        "20260725-camera-91a441",  # 13:59L Schwertkampf Mutter gegen Sohn ("super, quer")
        "20260725-camera-b98ead",  # 14:24L Oskar zielt mit Pfeil und Bogen -- NEU als Ersatz
        "20260807-camera-e75da0",  # 16:00L Fjordfahrt bei Regen mit Regenbogen (GoPro-Datei)
        "20260725-camera-67ef35",  # 17:56L doppelter Regenbogen
        "20260725-camera-83f3bb",  # 18:24L baugleiches Elektro-Katamaranschiff faehrt vorbei
        "20260725-phone-f19e45",  # 20:27 Abendessen auf der Huettenveranda
        # Raus: 20260725-camera-4e8191 (Bogenschuss, bei dem der Pfeil aus der Hand faellt),
        #       20260725-camera-73d0ad (Hochkant-Schwertkampf, "kannst du komplett rausnehmen"),
        #       20260725-phone-2f5678 (Katamaran-Bug, "da ist nichts besonders drauf").
    ],
    # Tag 9 -- Aurland -> Geiranger. Die tuerkisen Olden-Shots liegen durch die Chronologie
    # gebuendelt ("die sollen ein bisschen mehr gebuendelt werden"), die Ankunft in Geiranger
    # bekommt den Establisher, den der Nutzer vermisst hat.
    "2026-07-26": [
        "20260726-camera-02a9d4",  # 09:39L Laerdalstunnel
        "20260726-camera-36033e",  # 10:12L Autofaehre 'Mannheller' legt an
        "20260726-camera-60238c",  # 10:27L Blick von der Faehre auf den Fjord
        "20260726-camera-117e4a",  # 13:22L reissender Gletscherfluss, tuerkis
        "20260726-camera-780f72",  # 13:23L Familienselfie vor dem Gletscherfluss (Hochkant)
        "20260726-drone-993daf",  # 13:30 Wasserfall mitten im Ort
        "20260726-drone-7206fd",  # 13:31 tuerkiser Gebirgsfluss mit Stromschnellen
        "20260726-drone-e9f050",  # 13:32 tuerkisfarbener Fjordsee
        "20260726-drone-a1945f",  # 14:06 tuerkisgruener Fjordsee von oben
        "20260726-drone-688dda",  # 14:14 Hubschrauberlandeplatz an der Fjordspitze
        "20260726-drone-44f27e",  # 15:11 enge Felsschlucht mit Gletscherfluss
        "20260726-drone-8d6634",  # 15:12 gruenes Bergtal mit kurviger Strasse
        "20260726-drone-cee8da",  # 15:14 Wasserfall in tief haengenden Wolken
        "20260726-drone-4a48a2",  # 15:15 Bergstrasse mit Tunnel am Wasserfall
        "20260726-drone-de30ac",  # 15:15 Wasserfall quert die Bergstrasse
        "20260726-camera-7be0c1",  # 15:54L Rastplatz am Bergpass mit Wasserfaellen
        "20260726-phone-0738b3",  # 16:15 Ausblick vom Balkon auf den Geirangerfjord -- NEU
        "20260726-drone-289830",  # 16:43 Geiranger mit Kreuzfahrtschiffen -- NEU, Ankunftsshot
        "20260726-phone-9d91fc",  # 17:11 Eltern kuessen Oskar, Fjord im Hintergrund
        "20260726-phone-0bd3b1",  # 20:20 alte Bergbauernhoefe mit Ziegen
    ],
    # Tag 10 -- Geiranger, Geburtstag. Mit der Zeitkorrektur liegen Treppenweg und RIB-Tour je
    # als geschlossener Block ("die Bilder muessen zusammengehalten werden") und die RIB-Tour
    # dort, wo sie laut stages.csv war (15:00).
    "2026-07-27": [
        "20260727-phone-2ed4af",  # 09:08 Geburtstagsfruehstueck mit Fjordblick
        "20260727-phone-42aeaa",  # 09:08 Kerzen und Karte nah
        "20260727-phone-6f2658",  # 09:10 Pop-up-Karte mit Sektglaesern
        "20260727-drone-50a966",  # 10:48 Besucherzentrum am Fluss
        "20260727-camera-448a45",  # 11:46L Wasserfall ueber bemooste Felsen
        "20260727-camera-e61b92",  # 11:48L Mutter und Kind steigen die Metalltreppe hinauf
        "20260727-phone-270b29",  # 11:48 Blick die Treppe hinunter zum Wildbach
        "20260727-phone-1d6624",  # 11:53 grosser Wasserfall mitten in Geiranger
        "20260727-camera-1b14b3",  # 13:31L Passagiere steigen in die RIB-Boote
        "20260727-phone-151c49",  # 14:19 Mutter und Sohn unter der norwegischen Flagge
        "20260727-phone-276d06",  # 14:47 Familienselfie im Ausruestungsschuppen
        "20260727-phone-27bf87",  # 15:00 Oskar mit Schwimmweste und Schutzbrille
        "20260727-camera-847bd7",  # 15:06L Familienselfie auf dem RIB (Hochkant)
        "20260727-camera-a7e386",  # 15:40L Wasserfall vom RIB aus
        # Raus: zweite Verwendung von 20260727-drone-50a966 (dasselbe Asset lief im alten
        # Schnitt zweimal, nur mit anderem Ausschnitt -- echte Doppelung).
    ],
    # Tag 11 -- Geiranger -> Lom ueber Trollstigen. Der Kern des Nutzer-Feedbacks: die Plattform
    # nach vorne ("das ist eine der wichtigsten Plattformen"), danach die Ausblicke, und dann der
    # Blick durchs Wolkenfenster ins Tal als Hoehepunkt ("die epischste ... die muss drin
    # bleiben, die darf nicht getoetet werden") -- lang und an der richtigen Stelle, nicht mehr
    # als Nachklapp am Ende. Danach erst der Fluss-Block und Lom.
    "2026-07-28": [
        "20260728-phone-1d62e5",  # 09:47 Panorama Geiranger (Abschied)
        "20260728-phone-058a38",  # 11:46 Erdbeeren am Strassenstand (vor dem Trollstigen)
        "20260728-drone-b307d9",  # 12:47 Aussichtsplattform mit Steg -- vorgezogen
        "20260728-drone-eb4ff3",  # 12:52 Plattform ueber dem Wasserfall -- vorgezogen
        "20260728-drone-eab4d9",  # 12:48 Serpentinen mit tief haengenden Wolken
        "20260728-drone-9f54f7",  # 12:46 Wasserfall in nebliger Bergwelt
        "20260728-drone-79c521",  # 12:49 ueber den Serpentinen ins nebelverhangene Tal
        "20260728-phone-17a594",  # 12:32 von der Serpentine tief ins gruene Tal -- NEU
        "20260728-phone-0b4712",  # 12:39 weit ins Tal mit Sonnenlichtflecken -- NEU
        "20260728-drone-c91b2a",  # 12:49 DURCH DIE WOLKEN INS TAL -- Hoehepunkt, laenger
        "20260728-drone-e42c63",  # 12:52 schmaler Wasserfall an dunkler Felswand
        "20260728-drone-17c8a4",  # 12:54 Bergtreppe mit Wanderern von oben
        "20260728-drone-1cc835",  # 12:48 Familie winkt am Steinmann-Rastplatz (gekuerzt)
        "20260728-phone-454596",  # 13:06 Oskar neben seinem Steinmaennchen
        "20260728-drone-c4f817",  # 14:55 tuerkisfarbener Gletscherfluss von oben
        "20260728-drone-e13194",  # 14:57 Kind watet am flachen Fluss entlang
        "20260728-drone-b550d2",  # 14:59 klarer tuerkiser Fluss im Kiefernwald
        "20260728-drone-5d3cd7",  # 15:00 tuerkiser Flusspool mit Felsinseln
        "20260728-drone-3feda7",  # 15:01 wilder Fluss in der Felsschlucht
        "20260728-drone-51fecd",  # 21:51 Stabkirche Lom von oben -- NEU ("Kirche umkreisen")
        "20260728-drone-4cae48",  # 21:57 Strassenbruecke ueber den Gletscherfluss
        "20260728-phone-4cbed2",  # 22:17 Stabkirche Lom, im Fluss gespiegelt
        "20260728-phone-7c5346",  # 22:18 Angler mit Fisch -- NEU ("wir haben den Angler")
        # Raus: 20260728-drone-0131d3 ("zu statisch, wirkt ein bisschen wie Bild, es passiert
        # nichts, keine Bewegung -- die wuerde ich rauslassen").
    ],
    # Tag 12 -- Lom -> Uvdal.
    "2026-07-29": [
        "20260729-drone-282819",  # 12:37 Hochebene mit Schneegipfeln (Valdresflye)
        "20260729-phone-992a22",  # 19:19 Camping-Huetten am Seeufer (Ankunft Uvdal)
    ],
    # Tag 13 -- Uvdal, Aktivitaetstag. Der gute Bogenschuss kommt hierher (der misslungene aus
    # dem Wikingerdorf ist raus), Pizza und Abendstimmung als Abschluss.
    "2026-07-30": [
        "20260730-phone-552cd8",  # 11:24 zwei Kinder waten durch den Fluss
        "20260730-drone-b7bed7",  # 11:54 Oskar angelt, senkrecht von oben -- NEU
        "20260730-phone-e85889",  # 18:47 Pizza am Picknicktisch an der Bruecke
        "20260730-unknown-e4dbc0",  # 20:56L Oskar schiesst mit Pfeil und Bogen -- NEU, der gute
        "20260730-unknown-cd9012",  # 20:56L Kinder werfen Steine in den Fluss (ohne Ducking)
        "20260730-phone-98df48",  # 21:52 Holzbruecke als Silhouette im Abendrot
    ],
    # Tag 15 -- Uvdal -> Skien. NEU als Kapitel: der Nutzer hat den fehlenden Uebergang zurueck
    # nach Skien ausdruecklich gemeldet ("jetzt fehlt aber der Uebergang von Uvdal zu Skien
    # zurueck ... da muss der Uebergang klarer sein").
    "2026-08-01": [
        "20260801-phone-83694e",  # 12:28 Triathleten auf der Fjordstrasse
        "20260801-drone-914211",  # 12:53 Rastplatz mit Motorradtreffen von oben
    ],
    # Tag 17 -- Angeln an der Schaerenkueste. Schlussszene des Tages ist bewusst NICHT
    # chronologisch: der Nutzer wollte die weite Schaerenaufnahme mit der Gruppe als Endbild.
    #
    # Die Moewe, die der Nutzer laenger sehen wollte, steckt in `20260803-drone-574c7c` (seg16,
    # 75s) -- der Index kannte sie nicht, weil bei drei Keyframes je Clip keiner in die
    # Moewen-Passage fiel. Ganzen Clip in Kontaktbogen gesichtet, zwei brauchbare Passagen:
    #   53,4-62,0s  Moewe gleitet ueber das glitzernde Wasser, Drohne folgt -- die
    #               "Verfolgungsjagd", laengstes ruhiges Stueck (8,6s)
    #   72,2-75,2s  zweiter Anflug ganz am Ende: die Moewe kreuzt von oben rechts diagonal
    #               durchs Bild und kommt sehr nah heran ("die eine schoene gegen Ende ... da
    #               war ich sehr nahe"), laeuft bis zum Clipende
    # Beide bewusst direkt hintereinander: sie sind in der Quelle auch aufeinanderfolgend, und
    # zusammen ergeben sie einen Bogen von der ruhigen Verfolgung zum nahen Vorbeiflug.
    "2026-08-03": [
        "20260803-camera-1d32ef",  # 15:12L Oskar jubelt ueber den gefangenen Fisch
        "20260803-phone-18fb6c",  # 15:34 Kiefer rahmt die tuerkise Badebucht -- NEU
        "20260803-drone-b015cc",  # 15:54 Drohne umkreist die Felszunge -- NEU
        "20260803-drone-574c7c@26.0-33.6",  # Anflug auf die Felseninsel mit der Kiefer
        "20260803-drone-08166f",  # 16:09 Badebucht mit Steg und rotem Bootshaus -- NEU
        "20260803-drone-574c7c@53.4-62.0",  # Moewen-Verfolgung -- NEU
        "20260803-drone-574c7c@71.6-75.25",  # naher Vorbeiflug am Ende -- NEU
        "20260803-drone-c51c2b",  # 17:05 Aufstieg ueber den Kiefernwald zur Schaerenkueste -- NEU
        "20260803-drone-d1eb17",  # 15:51 Gruppe auf den Felsen, Gegenlicht -- als Endbild
    ],
    # Tag 18 -- Skien -> Grevenbroich. Nutzer: "Ganz am Ende noch mal die Color Line reinnehmen
    # an dem Tag und als Letztes ein Ausfaden finde ich sehr, sehr gut."
    "2026-08-04": [
        "20260804-camera-0fc698",  # 07:22L Auffahrt auf das Faehrdeck -- NEU
        "20260804-camera-59ef0c",  # 11:07L offenes Meer, Sonnenstrahlen durch die Wolken
        "20260804-camera-80b8d0",  # 11:57L Color Line 'SuperSpeed' am Kai
    ],
}

# Durchschnittliche Clipdauer je Tag = die Pacing-Kurve des alten Schnitts (vorne ruhig, im
# Roadtrip schneller). Bewusst beibehalten, der Nutzer hat das Tempo nicht kritisiert.
DAY_AVG_S: dict[str, float] = {
    "2026-07-17": 8.8, "2026-07-18": 7.9, "2026-07-19": 7.9, "2026-07-20": 7.4,
    "2026-07-21": 7.7, "2026-07-22": 7.6, "2026-07-23": 7.3, "2026-07-24": 7.1,
    "2026-07-25": 6.8, "2026-07-26": 6.2, "2026-07-27": 6.1, "2026-07-28": 5.8,
    "2026-07-29": 9.0, "2026-07-30": 6.6, "2026-08-01": 7.4, "2026-08-03": 7.6,
    "2026-08-04": 8.4,
}

# Uebergangsdauer je Tag (dissolve). Kuerzer, wo schneller geschnitten wird.
DAY_XFADE_S: dict[str, float] = {
    "2026-07-17": 1.0, "2026-07-18": 0.8, "2026-07-19": 0.8, "2026-07-20": 0.8,
    "2026-07-21": 0.8, "2026-07-22": 0.8, "2026-07-23": 0.6, "2026-07-24": 0.6,
    "2026-07-25": 0.6, "2026-07-26": 0.5, "2026-07-27": 0.5, "2026-07-28": 0.5,
    "2026-07-29": 1.0, "2026-07-30": 0.7, "2026-08-01": 0.8, "2026-08-04": 1.0,
    "2026-08-03": 1.0,
}

# Rest-Drift der Titel-Layer nach dem Slide-in, in Pixeln der TIMELINE-Auflaesung (4K).
# Vorzeichen = Weiterlaufrichtung, also dieselbe wie beim Einlaufen ("die sollen schon in ihre
# Richtung weitergehen"). Betrag bewusst deutlich groesser als die 8px aus Runde 2 -- der Nutzer
# wollte MEHR Restbewegung, und unter ~30px (4K) rundet `overlay` die Position so grob, dass die
# Bewegung als Ruckeln statt als Drift gelesen wird.
TITLE_DRIFT_PX: dict[str, int] = {
    "ov-title-main": 56,  # "Norwegen" laeuft von links ein, driftet weiter nach rechts
    "ov-title-sub": -56,  # "2026" kommt von rechts, driftet weiter nach links
    "ov-title-caption": 42,  # "Roadtrip Edition" von links, etwas weniger Weg
}

# Abweichende Uebergangsdauer fuer einzelne Clips (Schluessel = Eintrag aus `DAYS`).
# 0 = harter Schnitt.
XFADE_OVERRIDE: dict[str, float] = {
    # Der nahe Moewen-Vorbeiflug wird ganz am Clipende am groessten. Eine 1s-Blende AUF dem
    # naechsten Clip wuerde genau diesen Moment wegblenden, also hart schneiden.
    "20260803-drone-c51c2b": 0.0,
    # Und rein kurz, damit der Vorbeiflug nicht halb im Uebergang liegt.
    "20260803-drone-574c7c@71.6-75.25": 0.4,
}

# Feste Dauern, die nicht aus dem Tagesbudget kommen (Nutzerwunsch bzw. Dramaturgie).
FIXED_DUR: dict[str, float] = {
    # "Auch schoen lange die Zeit. Die ist super. Die geht auch einige Zeit. Die muss drin
    # bleiben, die ist super wichtig, die darf nicht getoetet werden."
    "20260728-drone-c91b2a": 14.0,
}

# Quell-Ausschnitte, die aus dem Nutzer-Feedback kommen (Sekunden im Quellclip).
TRIMS: dict[str, tuple[float, float]] = {
    # "Der hebt die Hand hoch bei 5:07 ... bis 5:05 ist es okay." Der Griff nach oben liegt
    # ~5,6s nach Clipstart -- Fenster endet davor.
    "20260721-camera-cc5bd6": (4.9, 10.2),
    # "Die Szene sollte aber minimal vorher aufhoeren ... bei 15:46 Ende, 15:47 ist schon zu lang."
    "20260728-drone-1cc835": (0.1, 4.3),
}

# Startpunkte im Quellclip, die von der bestehenden `timeline.json` abweichen sollen.
# Fuer alles, was hier NICHT steht und kein `@`-Fenster in `DAYS` hat, uebernimmt das Skript den
# `src_in` aus der vorhandenen `timeline.json` -- dort hatte der timeline-builder pro Clip schon
# eine brauchbare Stelle gefunden, und die soll ein Umbau der Reihenfolge nicht wegwerfen.
# Das macht das Skript bewusst idempotent (es liest Werte, die es selbst geschrieben hat).
# Folge, die man kennen muss: ein NEU in `DAYS` aufgenommenes Video startet bei 0, solange es
# kein `@`-Fenster bekommt.
SRC_IN_HINTS: dict[str, float] = {}

# -- Ken-Burns-Varianten --------------------------------------------------------------------
# Nutzer: "mir sieht der Ken Burns immer so aus, als wuerde er ein bisschen nach rechts gehen
# und dann nach links wiederum und dabei ein bisschen zoomen. Kann es sein, dass es da keine
# Varianz gibt ... dass es ein bisschen weicher geht und man das nicht so direkt wiedererkennt?"
# Ursache: ALLE 59 Fotos hatten exakt dieselben Parameter (from [0.06,0.06,1.0] -> to
# [-0.02,-0.02,1.12]), linear. Jeder Schnitt setzte den Schwenk auf denselben Startpunkt
# zurueck -- das las sich als Hin-und-Her. Jetzt: sechs Varianten, jede in EINE Richtung, mit
# Smoothstep (`ease: "smooth"`), und nie zweimal dieselbe hintereinander.
KENBURNS_STYLES: list[tuple[str, list[float], list[float]]] = [
    ("zoom_in", [0.0, 0.0, 1.0], [0.0, 0.0, 1.13]),
    ("pan_right_soft", [-0.045, 0.0, 1.07], [0.045, 0.0, 1.09]),
    ("zoom_out", [0.0, 0.0, 1.13], [0.0, 0.0, 1.0]),
    ("push_up_left", [0.035, 0.03, 1.02], [-0.03, -0.025, 1.15]),
    ("pan_left_soft", [0.045, 0.0, 1.09], [-0.045, 0.0, 1.07]),
    ("push_down_right", [-0.035, -0.03, 1.02], [0.03, 0.025, 1.15]),
]
# Hochkant-Fotos liegen auf einem unscharfen Hintergrund (`fit: "blur"`); ein Schwenk wuerde das
# scharfe Bild sichtbar im Rahmen verschieben. Fuer sie nur ruhige Zooms.
KENBURNS_STYLES_BLUR: list[tuple[str, list[float], list[float]]] = [
    ("zoom_in_soft", [0.0, 0.0, 1.0], [0.0, 0.0, 1.07]),
    ("zoom_out_soft", [0.0, 0.0, 1.07], [0.0, 0.0, 1.0]),
]

PHOTO_KINDS = {"photo"}


def parse_entry(entry: str) -> tuple[str, tuple[float, float] | None]:
    """`"asset-id"` oder `"asset-id@<in>-<out>"` (Sekunden im Quellclip).

    Die `@`-Form erlaubt MEHRERE Ausschnitte aus derselben Datei in einem Tag -- gebraucht fuer
    lange Drohnen-Segmente, in denen mehr als eine brauchbare Szene steckt (der 75s-Shot
    `20260803-drone-574c7c` liefert die Felseninsel, den Moewenflug und den nahen Vorbeiflug
    am Ende). Ohne explizites Fenster gilt der `src_in` aus dem alten Schnitt und die
    Tagesdauer.
    """
    if "@" not in entry:
        return entry, None
    asset_id, window = entry.split("@", 1)
    start, end = window.split("-", 1)
    return asset_id, (float(start), float(end))


def load_assets() -> dict[str, dict]:
    return {a["id"]: a for a in json.loads((ROOT / "index" / "assets.json").read_text())}


IPHONE_VIDEO_SUFFIXES = {".mov", ".mp4"}


def needs_utc_offset(asset: dict) -> bool:
    """True fuer iPhone-VIDEOS -- nur die tragen ihre Zeit in UTC.

    QuickTime-Dateien vom iPhone speichern `creation_time` in UTC, die HEIC-Fotos derselben
    Kamera dagegen die Ortszeit. Deshalb laesst sich die Korrektur nicht am `source`- oder
    `source_guess`-Feld festmachen:

    - `source_guess == "camera"` sind hier zu ~80% `Chris-iPhone/*.MOV` bzw.
      `Christina-iPhone/*.MOV` (iPhone-Videos ohne EXIF-`make`, darum als "camera" geraten)
      -- die brauchen die Korrektur.
    - dieselbe Klasse enthaelt aber auch 37 `DJI_*.MP4` aus den Drohnen-Ordnern, deren
      Dateiname die Ortszeit traegt (`DJI_20260720140953` zu `captured_at` 14:09) -- die
      brauchen sie NICHT.
    - und `Christina-iPhone/*.MP4` steht teils unter `source_guess == "unknown"`, braucht sie
      aber genauso.

    Deshalb entscheidet der Pfad: iPhone-Ordner + Video-Endung.
    """
    path = asset.get("path") or ""
    top = path.split("/")[0]
    suffix = ("." + path.rsplit(".", 1)[-1].lower()) if "." in path else ""
    return top.endswith("-iPhone") and suffix in IPHONE_VIDEO_SUFFIXES


def sort_key(asset: dict) -> str:
    """Aufnahmezeit in Ortszeit -- Grundlage der Reihenfolge innerhalb eines Tages."""
    ca = asset.get("captured_at") or ""
    if needs_utc_offset(asset) and len(ca) >= 16:
        from datetime import datetime, timedelta

        try:
            return (datetime.fromisoformat(ca) + timedelta(hours=CAMERA_UTC_OFFSET_H)).isoformat()
        except ValueError:
            return ca
    return ca


def aspect_of(asset: dict) -> float | None:
    """Seitenverhaeltnis aus `probe` oder, bei Fotos, aus dem gecachten Keyframe."""
    probe = asset.get("probe") or {}
    w, h = probe.get("w"), probe.get("h")
    if w and h:
        return w / h
    for kf in asset.get("keyframes") or []:
        path = Path(kf)
        if not path.exists():
            continue
        try:
            from frameforge.imageio import open_image

            iw, ih = open_image(path).size
            return iw / ih
        except Exception:  # noqa: BLE001 -- Kein Seitenverhaeltnis => Default-Fit, kein Abbruch
            return None
    return None


def build() -> None:
    assets = load_assets()
    old = json.loads((EXPORT / "timeline.json").read_text())
    old_by_asset: dict[str, dict] = {}
    for clip in old["tracks"]["video"]:
        old_by_asset.setdefault(clip["asset"], clip)

    video: list[dict] = []
    captions: list[tuple[str, float]] = []  # (Tagesdatum, tl_in der Bauchbinde)
    warnings: list[str] = []
    counter = 0
    tl = 0.0
    kb_index = 0
    prev_style: str | None = None

    def add(
        entry: str,
        dur: float,
        xfade: float,
        *,
        xfade_type: str = "dissolve",
        note: str = "",
    ) -> dict:
        nonlocal counter, tl, kb_index, prev_style
        asset_id, window = parse_entry(entry)
        if window is not None:
            dur = window[1] - window[0]
        asset = assets.get(asset_id)
        if asset is None:
            raise SystemExit(f"Asset '{asset_id}' steht nicht in assets.json")
        clip: dict = {
            "id": f"c{counter:03d}",
            "asset": asset_id,
            "src_in": 0.0,
            "src_out": dur,
            "tl_in": max(0.0, tl - xfade),
            "speed": 1.0,
            "effects": [],
        }
        counter += 1
        if xfade > 0:
            clip["transition_in"] = {"type": xfade_type, "dur": xfade, "hold": 0.0}

        is_photo = asset.get("kind") in PHOTO_KINDS
        if not is_photo:
            if window is not None:
                src_in = window[0]
            else:
                src_in = SRC_IN_HINTS.get(asset_id)
                if src_in is None:
                    src_in = float((old_by_asset.get(asset_id) or {}).get("src_in", 0.0))
                trim = TRIMS.get(asset_id)
                if trim:
                    src_in = trim[0]
                    dur = min(dur, trim[1] - trim[0])
            clip["src_in"] = round(src_in, 3)
            clip["src_out"] = round(src_in + dur, 3)

        aspect = aspect_of(asset)
        if aspect is None:
            warnings.append(f"{asset_id}: kein Seitenverhaeltnis ermittelbar, Fit bleibt Default")
        elif aspect < PORTRAIT_MAX_ASPECT:
            clip["fit"] = "blur"

        if is_photo:
            styles = KENBURNS_STYLES_BLUR if clip.get("fit") == "blur" else KENBURNS_STYLES
            style = styles[kb_index % len(styles)]
            if style[0] == prev_style and len(styles) > 1:
                kb_index += 1
                style = styles[kb_index % len(styles)]
            kb_index += 1
            prev_style = style[0]
            clip["effects"] = [
                {"type": "kenburns", "from": style[1], "to": style[2], "ease": "smooth"}
            ]
        else:
            prev_style = None

        if window is not None:
            # `qc._check_clip_repetition` meldet mehr als zwei Verwendungen desselben Assets als
            # moegliches Versehen. Ein explizites `@`-Fenster ist genau der vorgesehene
            # Ausnahmefall (ein langer Quellclip, in mehrere eigenstaendige Szenen zerlegt), und
            # das Schema hat dafuer dieses Feld.
            clip["intentional_repeat"] = True
            note = f"{note} · Quellfenster {window[0]:.1f}-{window[1]:.1f}s".strip(" ·")
        if note:
            clip["note"] = note
        video.append(clip)
        tl = clip["tl_in"] + (clip["src_out"] - clip["src_in"])
        return clip

    # -- Cold-Open + Titelbett -------------------------------------------------------------
    # Nutzer: "Das Schwarzbild mit dem Wind und dem Start, das gefaellt mir schon mal gut."
    add("generated-cold-open-black", 10.0, 0.0, xfade_type="fade", note="Cold-Open, Wind-Audio")
    video[0]["transition_in"] = {"type": "fade", "dur": 3.0, "hold": 0.0}
    add("20260722-drone-e0e4c2", 24.0, 2.0, xfade_type="slow_dissolve", note="Titelbett K1")

    # -- Reisetage -------------------------------------------------------------------------
    for day in sorted(DAYS):
        ids = DAYS[day]
        xfade = DAY_XFADE_S[day]
        avg = DAY_AVG_S[day]
        fixed_total = sum(FIXED_DUR[i] for i in ids if i in FIXED_DUR)
        flexible = [i for i in ids if i not in FIXED_DUR and "@" not in i]
        # Tagesbudget aus der Pacing-Kurve; die festen Dauern gehen extra dazu, damit der
        # Hoehepunkt-Shot nicht auf Kosten des restlichen Tages laenger wird.
        per_clip = avg if not flexible else max(4.2, avg)

        # Kontrolle: weicht die gelistete Reihenfolge von der korrigierten Aufnahmezeit ab?
        # Zaehlt echte Inversionen (Paare, die gegen die Aufnahmezeit stehen), nicht
        # Positionsunterschiede -- ein einzelner verschobener Clip wuerde sonst als halber Tag
        # gemeldet und die Ausgabe waere als Kontrolle nutzlos.
        times = [sort_key(assets[parse_entry(i)[0]]) for i in ids]
        inversions = sum(
            1
            for a in range(len(times))
            for b in range(a + 1, len(times))
            if times[a] > times[b]
        )
        if inversions:
            warnings.append(
                f"{day}: {inversions} Paar(e) bewusst gegen die Aufnahmezeit (siehe Kommentare)"
            )

        first_of_day = True
        for asset_id in ids:
            dur = FIXED_DUR.get(asset_id, per_clip)
            add(
                asset_id,
                dur,
                XFADE_OVERRIDE.get(asset_id, xfade),
                xfade_type="slow_dissolve" if first_of_day else "dissolve",
                note=f"{day}",
            )
            if first_of_day:
                # Bauchbinde ~1,5s nach Kapitelbeginn, damit sie nicht in die Blende laeuft.
                captions.append((day, round(video[-1]["tl_in"] + 1.5, 3)))
                first_of_day = False
        _ = fixed_total  # nur zur Dokumentation des Budgets

    # -- Schlussschwarzbild ----------------------------------------------------------------
    # Nutzer: "die angesprochenen 15 Sekunden Schwarzbild braucht man nicht, da reichen drei
    # Sekunden." Die 17s im letzten Preview kamen aus dem Karten-Overhang (jetzt gefixt); ein
    # kurzes, gewolltes Schwarzbild als Abschluss bleibt.
    add("generated-cold-open-black", 3.0, 1.5, xfade_type="fade", note="Ausfaden, Schluss")

    duration = round(video[-1]["tl_in"] + (video[-1]["src_out"] - video[-1]["src_in"]), 3)

    # -- Bauchbinden (Overlays) ------------------------------------------------------------
    overlay = [o for o in old["tracks"]["overlay"] if o["id"].startswith("ov-title-")]
    for o in overlay:
        anim = dict(o.get("anim") or {})
        # Nutzer: die Drift soll "in ihre Richtung weitergehen", nicht pendeln, und deutlicher
        # sichtbar sein als bisher. Richtung = Slide-in-Richtung, Betrag ABSOLUT aus
        # `TITLE_DRIFT_PX`.
        #
        # Absolut und nicht als Faktor auf den Altwert, weil dieses Skript die vorhandene
        # `timeline.json` liest -- ein `* 7` haette bei jedem Lauf erneut multipliziert. Genau das
        # ist passiert: nach acht Laeufen stand `drift_px` bei 8 * 7^8 = 46.118.408 px, der Titel
        # schoss nach 1,5s aus dem Bild. Alles, was dieses Skript aus der alten Datei uebernimmt,
        # muss idempotent sein oder absolut gesetzt werden.
        drift = TITLE_DRIFT_PX.get(o["id"])
        if drift is not None:
            anim["drift_mode"] = "linear"
            anim["drift_px"] = str(drift)
        else:
            anim.pop("drift_px", None)
            anim.pop("drift_mode", None)
        anim.pop("drift_period_s", None)
        o["anim"] = anim
    for day, tl_in in captions:
        for kind in ("box", "text"):
            png = "overlays/stage-caption-box.png" if kind == "box" else f"overlays/stage-caption-{day}.png"
            overlay.append({
                "id": f"ov-stage-{kind}-{day}",
                "png": png,
                "tl_in": tl_in,
                "dur": 5.0,
                "anim": {"fade_in_s": "0.6", "fade_out_s": "1.2"},
            })

    # -- Audio -----------------------------------------------------------------------------
    music = [a for a in old["tracks"]["audio"] if a.get("src")]
    music[-1]["dur"] = round(duration - music[-1]["tl_in"], 3)
    # Nutzer zum Ducking: "Wir sollten Ducking vielleicht nur auf ein, zwei Sachen beschraenken"
    # -- Faehre (Oskar im Wind) und die Gitarren-/Kitzelszene. Und: "Es muss lauter sein, es muss
    # klarer sein. Nicht das eine leiser machen, sondern das andere ein bisschen hochziehen."
    # Also O-Ton von -18 auf -6 dB, Musikabsenkung von -12 auf -7 dB, beides mit weichen Rampen
    # ("das Absacken vom Sound muss smooth passieren, es muss einen kleinen Mini-Fade geben").
    atmo_specs = [
        ("atmo-faehre-wind", "20260719-camera-21e343"),
        ("atmo-gitarre-kitzeln", "20260722-camera-7545fc"),
    ]
    audio = list(music)
    for atmo_id, asset_id in atmo_specs:
        clip = next((c for c in video if c["asset"] == asset_id), None)
        if clip is None:
            warnings.append(f"{atmo_id}: Clip {asset_id} nicht im Schnitt, O-Ton entfaellt")
            continue
        dur = clip["src_out"] - clip["src_in"]
        audio.append({
            "id": atmo_id,
            "asset": asset_id,
            "tl_in": round(clip["tl_in"], 3),
            "dur": round(dur, 3),
            "src_in": round(clip["src_in"], 3),
            "gain_db": -6.0,
            "duck_music_db": -7.0,
            "duck_fade_s": 0.7,
            "fade_in_s": 0.3,
            "fade_out_s": 0.5,
        })

    timeline = {
        "version": 1,
        "export": "vlog-data",
        "fps": FPS,
        "resolution": list(RES),
        "duration": duration,
        "tracks": {
            "video": video,
            "overlay": overlay,
            # Nutzer: "Die Karte wird nicht angezeigt." Track bleibt leer statt entfernt, damit
            # das Schema stabil bleibt und die Entscheidung sichtbar ist.
            "map": [],
            "audio": audio,
        },
    }
    (EXPORT / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False) + "\n")

    photos = sum(1 for c in video if assets[c["asset"]].get("kind") in PHOTO_KINDS)
    blur = sum(1 for c in video if c.get("fit") == "blur")
    print(f"timeline.json: {len(video)} Clips ({photos} Fotos, {blur}x fit=blur), "
          f"{len(overlay)} Overlays, {len(audio)} Audiospuren")
    print(f"Dauer {duration:.3f}s = {int(duration // 60)}:{duration % 60:05.2f}")
    for w in warnings:
        print("  Hinweis:", w)


if __name__ == "__main__":
    build()
