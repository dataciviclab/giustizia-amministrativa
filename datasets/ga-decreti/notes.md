# ga-decreti — Note tecniche

## Architettura

31 source CKAN native, una per sede (`download_all: true`, `prefer_datastore: false`). Il RAW produce un CSV per sede; `clean.read.mode: all` + `union_by_name=true` fondono i file nella vista `raw_input`.

## Dataset id

Le source usano `dataset_id: "{sede}-decreti"`: ogni sede è un package CKAN separato con le risorse `2017-2024`, `2025`, `2026`.

## Run

```
toolkit run --config datasets/ga-decreti/dataset.yml
```

## Volumi

| Anno | Decreti | Sedi |
|---|---|---|
| 2023 | 2.601 | 31 |
| 2024 | 2.230 | 31 |
| 2025 | 1.727 | 31 |
| 2026 | 926 | 31 |

## Copertura mensile

OpenGA aggiorna i dataset ogni mese. Per l'aggiornamento schedulato, rieseguire il run full su tutti gli anni.
