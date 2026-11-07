# ga-ordinanze — Note tecniche

## Architettura

31 source CKAN native, una per sede (`download_all: true`, `prefer_datastore: false`). Il RAW produce un CSV per sede; `clean.read.mode: all` + `union_by_name=true` fondono i file nella vista `raw_input`.

## Dataset id

Le source usano `dataset_id: "{sede}-ordinanze"`: ogni sede è un package CKAN separato con le risorse `2017-2024`, `2025`, `2026`.

## Run

```
toolkit run --config datasets/ga-ordinanze/dataset.yml
```

## Volumi

| Anno | Ordinanze | Sedi |
|---|---|---|
| 2023 | 4.796 | 31 |
| 2024 | 4.327 | 31 |
| 2025 | 3.970 | 31 |
| 2026 | 1.961 | 31 |

## Copertura mensile

OpenGA aggiorna i dataset ogni mese. Per l'aggiornamento schedulato, rieseguire il run full su tutti gli anni.
