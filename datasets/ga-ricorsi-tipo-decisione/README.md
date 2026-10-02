# ga-ricorsi-tipo-decisione — Come si definiscono i ricorsi (OpenGA)

Ricorsi definiti per meccanismo decisionale: sentenza/sentenza breve, decreto
decisorio, altri provvedimenti. Complementare a `ga_ricorsi_definiti` (esito)
e `ga_sentenze_brevi` (mix breve/pieno per materia).

## Copertura

- **31 sedi**: CdS (giurisdizionale + consultive), CGA Sicilia, 27 TAR, 2 TRGA
- **Serie**: 2017-2026 (risorse `2017-2024` + `2025` + `2026`)
- **Granularità**: aggregato (sede × mese)

## Cosa risponde

1. Quale quota di definizioni arriva da sentenza rispetto a decreti/altri atti?
2. Le sedi "celeri" (più decreti decisori) sono le stesse che hanno più esiti favorevoli?
3. Come cambia il mix meccanismi di definizione nel tempo?

## Schema clean

| Colonna | Tipo | Note |
|---|---|---|
| `anno` | BIGINT | Anno pubblicazione |
| `mese` | BIGINT | Mese pubblicazione (YYYYMM) |
| `codice_sede` | BIGINT | Codice sede |
| `nome_sede` | VARCHAR | Nome sede |
| `definiti_sentenza_breve` | BIGINT | Definiti con sentenza o sentenza breve |
| `definiti_decreto_decisori` | BIGINT | Definiti con decreto decisorio |
| `definiti_altri` | BIGINT | Definiti con altri provvedimenti |
| `totale_definiti` | BIGINT | Totale ricorsi definiti |

## Mart

| Tabella | Descrizione |
|---|---|
| `mart_mezzi_sede` | Mix meccanismi per sede/anno + quota sentenza |
| `mart_trend` | Mix nazionale per anno |

## Fonte

31 package CKAN OpenGA (`*-ricorsi-definiti-per-tipo-di-decisione`).

## Nota CdS

Il package CdS include sia la sezione **giurisdizionale** sia le **consultive**:
le consultive hanno `definiti_sentenza_breve = 0` e prevalenza di "altri"
(pareri). Utile per non confondere volume consultivo con contenzioso.
