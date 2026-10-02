# ga-ricorsi-pervenuti-class — Note tecniche

## Architettura

Prefetch `--type ricorsi-pervenuti-class` concatena tutte le risorse CSV
delle 31 sedi (bulk `2017-2024` + `2025` + `2026`) in un unico `raw_input.csv`.

## Codelist sedi (contratto nome_sede)

OpenGA, per questa tipologia, emette `NOME_SEDE` **senza** i separatori
canonici del Lab (`TAR LAZIOROMA` invece di `TAR LAZIO - ROMA`).

- **Causa**: fonte, non `normalize_string`
- **Fix**: `data/sedi_canonici.csv` — mapping `codice_sede -> nome_sede_canonico`
- **Consumo**: `sql/clean.sql` via template `{base_dir_posix}/data/sedi_canonici.csv`
- **Protezione**: `tests/test_sede_mapping_contract.py` (stesso CSV come source of truth)

Se OpenGA aggiunge una sede o cambia un codice:
1. aggiornare `data/sedi_canonici.csv`
2. i nuovi codici senza mapping ricadono sul raw (rotto) → il contract test fallisce

## Volumi

Serie storica completa nel clean anche con `years: [2026]` (prefetch multi-risorsa).

## Join

- `codice_sede` → tutti i dataset GA
- `classificazione_ricorso` → `ga_ricorsi_definiti`, `ga_cross`, `ga_sentenze_brevi`
