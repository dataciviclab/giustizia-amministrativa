# ga-ricorsi-pervenuti-class — Note tecniche

## Architettura

Prefetch `--type ricorsi-pervenuti-class` concatena tutte le risorse CSV
delle 31 sedi (bulk `2017-2024` + `2025` + `2026`) in un unico `raw_input.csv`.

## Codelist sedi (contratto nome_sede)

OpenGA, per questa tipologia, emette `NOME_SEDE` **senza** i separatori
canonici del Lab (`TAR LAZIOROMA` invece di `TAR LAZIO - ROMA`).

- **Causa**: fonte, non `normalize_string`
- **Fix**: `data/sedi_canonici.csv` — mapping `codice_sede -> nome_sede_canonico` + `tipo_sede` (`giurisdizionale` / `consultivo`: 31 CdS CONSULTIVE e 33 CGA CONSULTIVE sono pareri, non ricorsi)
- **Consumo**: `sql/clean.sql` via template `{base_dir_posix}/data/sedi_canonici.csv`
- **Protezione**: `tests/test_sede_mapping_contract.py` (stesso CSV come source of truth)

Se OpenGA aggiunge una sede o cambia un codice:
1. aggiornare `data/sedi_canonici.csv`
2. i nuovi codici senza mapping ricadono sul raw (rotto) → il contract test fallisce

## Deriva tassonomia materia (2022)

OpenGA cambia la tassonomia `CLASSIFICAZIONE_RICORSO` dal 2022: ~1.000 valori
distinti fino al 2021, 1.329 nel 2022 (1.196-1.310 negli anni successivi).
Le etichette non sono stabili: la stessa materia compare con nomi diversi e
alcune spariscono.

Caso verificato: le quattro classificazioni `APPALTI PUBBLICI DI LAVORI,
SERVIZI E FORNITURE -> ...` valgono 127-290 ricorsi/anno dal 2017 al 2021,
**1 nel 2022 e zero dal 2023** — mentre il tema separato
`openga_ricorsi_appalto` resta stabile su ~3.000 ricorsi/anno. Il crollo è
di tassonomia, non di contenzioso.

Effetto sugli incroci per materia: nel `ga_cross` la quota di definiti
abbinati ai pervenuti per `(anno, sede, classificazione)` è 90-95% negli anni
2017-2021 e 2025, ma **66,5% nel 2022** (78,6% nel 2023, 85,1% nel 2024).

Regola: per volumi e trend per materia usare `ga_cross` sapendo di questa
frattura; per gli appalti usare `openga_ricorsi_appalto` /
`compose/ga-appalti-contenzioso`, che non dipendono dalla classificazione.

## Volumi

Serie storica completa nel clean anche con `years: [2026]` (prefetch multi-risorsa).

## Join

- `codice_sede` → tutti i dataset GA
- `classificazione_ricorso` → `ga_ricorsi_definiti`, `ga_cross`, `ga_sentenze_brevi`
