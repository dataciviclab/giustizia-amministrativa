# ga-pareri — Pareri delle sezioni consultive (OpenGA)

Pareri del Consiglio di Stato e del CGA Sicilia — lato consultivo della
Giustizia Amministrativa, non il contenzioso.

## Copertura

- **2 sedi**: CdS (sezioni consultive, Roma) + CGA Sicilia
- **Serie**: 2017-2026 (risorse `2017-2024` + `2025` + `2026`)
- **Aggiornamento**: mensile

## Cosa risponde

1. Quanti pareri emettono le sezioni consultive e come variano nel tempo?
2. Quali esiti prevalgono (parere favorevole, sospensivo, inammissibile…)?
3. Come si distribuiscono per sezione e per materia (tipo_ricorso)?

## Schema clean

Stesso schema record-level di `ga-sentenze` (17 colonne). Colonne chiave:

| Colonna | Note |
|---|---|
| `tipo_provvedimento` | PARERE DEFINITIVO / PARERE SOSPENSIVO / … |
| `esito_provvedimento` | ACCOGLIE, RESPINGE, INAMMISSIBILE, LICENZIATO, … |
| `numero_ricorso` | Chiave di join cross-sede |
| `nome_sede` | es. `CdS CONSULTIVE - ROMA`, `CGA SICILIA` |

## Fonte

2 package CKAN OpenGA (`cds-pareri`, `cga-sicilia-pareri`). Prefetch con
`--type pareri` scarica solo queste due sedi.

## Mart

| Tabella | Descrizione |
|---|---|
| `mart_esiti_per_sede` | Pareri per sede/anno/esito |
| `mart_esiti_per_tipo` | Pareri per tipo provvedimento/esito |
