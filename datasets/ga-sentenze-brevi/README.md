# ga-sentenze-brevi — Sentenze brevi per classificazione (OpenGA)

Ricorsi definiti con sentenze e sentenze brevi, aggregati per sede e materia.
Chiude il gap su **come** si chiudono i ricorsi (breve vs piena), non solo su
quanti e con quale esito.

## Copertura

- **31 sedi**: CdS, CGA Sicilia, 27 TAR, 2 TRGA
- **Serie**: 2017-2026 (risorse `2017-2024` + `2025` + `2026`)
- **Granularità**: aggregato (sede × classificazione × tipo sentenza × mese)

## Cosa risponde

1. Quale quota di definizioni arriva da sentenza breve vs sentenza piena?
2. Quali materie usano più sentenze brevi (istruttoria snella, materie standardizzate)?
3. Come varia il mix breve/pieno per sede nel tempo?

## Schema clean

| Colonna | Tipo | Note |
|---|---|---|
| `anno` | BIGINT | Anno sentenza |
| `mese` | BIGINT | Mese sentenza (YYYYMM) |
| `codice_sede` | BIGINT | Codice sede |
| `nome_sede` | VARCHAR | Nome sede |
| `classificazione_ricorso` | VARCHAR | Materia (tassonomia OpenGA) |
| `tipo_sentenza` | VARCHAR | `SENTENZA` / `SENTENZA BREVE` |
| `numero_sentenze` | BIGINT | Conteggio (metrica da sommare) |

## Mart

| Tabella | Descrizione |
|---|---|
| `mart_brevi_per_sede` | Mix breve/pieno per sede e anno |
| `mart_brevi_per_tipo` | Mix breve/pieno per materia e anno |

## Fonte

31 package CKAN OpenGA (`*-ricorsi-definiti-con-sentenze-e-sentenze-brevi-per-classificazione`).
