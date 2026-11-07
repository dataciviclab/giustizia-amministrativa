# ga-sentenze — Note tecniche

## Architettura

31 source CKAN native, una per sede (`download_all: true`, `prefer_datastore: false`). Il RAW produce un CSV per sede; `clean.read.mode: all` + `union_by_name=true` fondono i file nella vista `raw_input`.

## Dataset id

Le source usano `dataset_id: "{sede}-sentenze"`: ogni sede è un package CKAN separato con le risorse `2017-2024`, `2025`, `2026`.

## Drop colonne raw

- `ANNO_PUBBLICAZIONE` → rinominato in `anno` nel clean

## Run

```
toolkit run --config datasets/ga-sentenze/dataset.yml
```

## Copertura mensile

OpenGA aggiorna i dataset ogni mese. Per l'aggiornamento schedulato, rieseguire il run full su tutti gli anni.

## Performance

31 sedi × 3 risorse CSV ≈ 170 MB, ~1-2 minuti (dipende dalla rete). Il merge multi-file nel clean è istantaneo una volta che i raw sono disponibili.
