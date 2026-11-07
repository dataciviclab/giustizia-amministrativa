# ga-pareri — Note tecniche

## Architettura

2 source CKAN (CdS + CGA Sicilia), non le 31 sedi. `download_all: true`
scarica tutte le risorse CSV di ciascun package: `2017-2024` (bulk) + `2025` + `2026`.

## Sedi diverse dal lato giurisdizionale

- `NOME_SEDE` = `CdS CONSULTIVE - ROMA` (codice 031), non `CdS GIURISDIZIONALE - ROMA`
- Il CGA Sicilia compare con le sezioni consultive siciliane
- Non confondere con `ga_sentenze`: stessa struttura CSV, ma unità = parere

## Copertura storica

La risorsa multi-anno `2017-2024` è un unico CSV bulk (~16k righe CdS).
Il clean legge i 2 file RAW (uno per sede); l'anno analitico è
`ANNO_PUBBLICAZIONE` (colonna `anno`).

## Volumi indicativi (CdS)

| Risorsa | Righe ~ |
|---|---|
| 2017-2024 | 16.494 |
| 2025 | 1.341 |
| 2026 (parziale) | 1.592 |

## Cautele

- `ESITO_PROVVEDIMENTO` per i pareri usa un vocabolario più ampio del contenzioso
  (es. `LICENZIATO`, `RESPINGE ISTANZA DI SOSPENSIVA`)
- `TIPO_PROVVEDIMENTO` distingue parere definitivo vs sospensivo — mart dedicato
- La serie è storica 2017-2026 anche se il config runna `years: [2026]`
  (stesso pattern di ga-sentenze: `download_all` concatena le risorse del package)
