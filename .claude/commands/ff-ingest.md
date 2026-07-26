---
description: Rohmaterial einlesen und Proxies erzeugen
argument-hint: <projekt-name>
---

Material für Projekt `$ARGUMENTS` einlesen.

Schritte:
1. `frameforge status $ARGUMENTS` — aktuelle Phase prüfen (informativ, `ingest` selbst hat
   kein Gate, aber ein bereits `INGESTED`+-Projekt erneut einzulesen ist meist ungewollt;
   im Zweifel nachfragen, ob neues Material dazugekommen ist).
2. `frameforge ingest $ARGUMENTS` ausführen (Scan + Proxy-Erzeugung; bis M1 ein Stub, der
   `NotImplementedError` wirft — das ist erwartetes Verhalten, kein Fehler in der Bedienung).
3. Nach erfolgreichem Lauf: `frameforge status $ARGUMENTS` sollte Phase `INGESTED` zeigen.
4. Kurz melden: Anzahl gefundener Assets, Proxy-Zielverzeichnis, Auffälligkeiten (z.B.
   unlesbare Dateien).

Diese Pipeline läuft potenziell auf ~100 GB Material — keine Einzeldatei-Pfade ins
Kontextfenster ziehen, nur Zusammenfassungen.
