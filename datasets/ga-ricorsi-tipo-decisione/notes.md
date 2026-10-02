# ga-ricorsi-tipo-decisione — Note tecniche

## Architettura

31 package CKAN paralleli. Prefetch `--type ricorsi-tipo-decisione` concatena
tutte le risorse CSV (`2017-2024` bulk + `2025` + `2026`).

## Tipo di dato

Tabella **aggregata** mensile per sede. I mart fanno `SUM(...)` sui contatori.

## Colonne di origine → clean

| Raw | Clean |
|---|---|
| `NUMERO_RICORSI_DEFINITI_SENTENZA_E_SENTENZA_BREVE` | `definiti_sentenza_breve` |
| `NUMERO_RICORSI_DEFINITI_DECRETO_DECISORIO` | `definiti_decreto_decisori` |
| `NUMERO_RICORSI_DEFINITI_ALTRI_PROVVEDIMENTI` | `definiti_altri` |
| `NUMERO_RICORSI_DEFINITI` | `totale_definiti` |

## Join utili

- `codice_sede` ↔ `ga_ricorsi_definiti` (esiti per stessa sede)
- `ga_sentenze_brevi` (mix breve/pieno per materia — questo dataset è per sede)
- `ga_provvedimenti` (produttività: definiscono vs non definiscono)

## Cautele

- CdS = giurisdizionale + consultive nella stessa tabella: filtrare per
  `nome_sede` se si vuole solo il contenzioso
- I contatori sono già aggregati dalla fonte — mai contare righe raw
- Config runna `years: [2026]` ma il clean contiene la serie completa
