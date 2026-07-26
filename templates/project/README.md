# Projekt-Skeleton

Referenz für die Ordnerstruktur, die `frameforge new` unter `projects/<name>/` anlegt
(siehe `Project`-Pfade in `frameforge/project.py` und Plan §1). Kein Template-Engine-Input —
`frameforge new` erzeugt die Struktur direkt, dieser Ordner dokumentiert sie nur:

```
projects/<name>/
├── project.yaml
├── .state.json
├── design/
│   ├── tokens.yaml
│   ├── fonts/
│   ├── assets/
│   └── prompts.md
├── index/
│   ├── assets.json
│   ├── assets/
│   └── days/
├── route/
│   ├── roadtrip.gpx
│   └── locations.csv
├── music/
│   └── analysis/
└── exports/
    └── <export>/
        ├── brief.yaml
        ├── beatsheet.md
        ├── timeline.json
        ├── overlays/
        ├── map/
        ├── preview/
        ├── final/
        └── nle/
```
