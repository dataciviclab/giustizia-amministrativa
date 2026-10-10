# ga-ricorsi-pendenti — Stock pendenti GA per sede

## Grano

`anno × mese × codice_sede` (clean) — stock dichiarato di ricorsi pendenti in giudizio.

## Fonte

OpenGA CKAN: `{sede}-ricorsi-pendenti-per-periodo` per tutte le 33 sedi
(CdS ×2 codici — giurisdizionale/consultivo —, CGA ×2, TAR, TRGA).

**Copertura reale della fonte: 2020-2023 + 2025-2026** — le risorse
"2017-2024" in CKAN contengono di fatto solo 2020-2023; **il 2024 manca
del tutto** (gap di pubblicazione OpenGA, non di ingestione). 2020 e 2026
sono parziali (n_mesi < 12 nel mart).

## Colonne clean

| Colonna | Note |
|---|---|
| `anno` / `mese` | da `ANNO_MESE_RIFERIMENTO` (YYYYMM) |
| `codice_sede` / `nome_sede` | sede OpenGA (contratto spazi nei nomi) |
| `numero_ricorsi_pendenti` | stock a fine mese di riferimento |

## Marts

| Tabella | Grano | Note |
|---|---|---|
| `mart_pendenti_per_sede` | anno × sede | media/min/max + `pendenti_dicembre` (NULL se dicembre assente) |
| `mart_pendenti_nazionale` | anno | somma mensile delle sedi, poi stats annuali |

## Caveat

1. **Stock, non flusso**: va affiancato a `ga_ricorsi_pervenuti_class` / `ga_ricorsi_definiti`, non sostituito — pendenti a fine mese ≠ cumulata (pervenuti − definiti) per via di rientri, consolidamenti e correzioni di stock.
2. **Copertura variabile**: 2020 e 2026 parziali, 2024 assente — usare sempre `n_mesi` prima di confronti inter-anno/sede.
3. **Aggiornamento**: risorse fresh per l'anno in corso (mensile); i blocchi storici sono statici.

Issue di riferimento: #10
