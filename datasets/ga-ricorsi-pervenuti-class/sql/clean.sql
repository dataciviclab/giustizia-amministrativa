-- OpenGA emette NOME_SEDE per i pervenuti SENZA separatori
-- (es. "TAR LAZIOROMA" invece di "TAR LAZIO - ROMA").
-- Causa: fonte, non normalize_string. Contratto Lab: nome canonico con " - ",
-- allineato a ga_ricorsi_definiti / ga_sentenze.
--
-- Codelist: data/sedi_canonici.csv (codice_sede -> nome_sede_canonico).
-- Il path e' risolto via template {base_dir_posix} del toolkit (dir del dataset.yml).
-- Protezione: tests/test_sede_mapping_contract.py legge lo stesso CSV.
WITH base AS (
    SELECT
        cast_bigint(floor(cast("ANNO_DEPOSITO" AS double) / 100)) AS anno,
        cast_bigint("ANNO_DEPOSITO") AS anno_mese,
        cast_bigint("CODICE_SEDE") AS codice_sede,
        normalize_string("NOME_SEDE") AS nome_sede_raw,
        normalize_string("CLASSIFICAZIONE_RICORSO") AS classificazione_ricorso,
        cast_bigint("NUMERO_RICORSI_PERVENUTI") AS numero_ricorsi
    FROM raw_input
),
sedi AS (
    SELECT
        cast_bigint("codice_sede") AS codice_sede,
        normalize_string("nome_sede_canonico") AS nome_sede_canonico
    FROM read_csv_auto('{base_dir_posix}/data/sedi_canonici.csv')
)
SELECT
    b.anno,
    b.anno_mese,
    b.codice_sede,
    COALESCE(s.nome_sede_canonico, b.nome_sede_raw) AS nome_sede,
    b.classificazione_ricorso,
    b.numero_ricorsi
FROM base b
LEFT JOIN sedi s
    ON b.codice_sede = s.codice_sede
WHERE b.anno IS NOT NULL
