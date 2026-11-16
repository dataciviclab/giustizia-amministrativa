-- OpenGA "ricorsi definiti per classificazione ed esito" conta i ricorsi
-- PER ESITO registrato: un ricorso che passa da un esito interlocutorio
-- (riunione, rinvio, nomina commissario ad acta, misura cautelare, ...) e poi
-- arriva a sentenza compare in piu' righe. Sommare `numero_ricorsi_definiti`
-- senza filtro da' un totale superiore ai ricorsi distinti definiti:
-- +15% nel 2017, +32% nel 2026 contro il tema ufficiale
-- "ricorsi definiti per tipo di decisione" (che resta la misura di livello).
--
-- Codelist: data/esiti_codelist.csv (esito_provvedimento -> definitorio 0/1).
-- Path risolto via template {base_dir_posix} del toolkit (dir del dataset.yml).
-- Il join canonicalizza le doppie virgolette dei refusi di fonte
-- ("DICHIARA L''INCOMPETENZA ..."); il valore pubblicato resta quello di fonte.
-- Un esito non mappato vale esito_definitorio = FALSE (fail-closed): il test
-- tests/test_esiti_codelist_contract.py fallisce finche' non entra in codelist.
WITH base AS (
    SELECT
        cast_bigint("ANNO_SENTENZA") AS anno,
        cast_bigint("MESE_SENTENZA") AS mese,
        cast_bigint("CODICE_SEDE") AS codice_sede,
        normalize_string("NOME_SEDE") AS nome_sede,
        normalize_string("CLASSIFICAZIONE_RICORSO") AS classificazione_ricorso,
        normalize_string("ESITO_PROVVEDIMENTO") AS esito_provvedimento,
        cast_bigint("NUMERO_RICORSI_DEFINITI") AS numero_ricorsi_definiti
    FROM raw_input
),
esiti AS (
    SELECT
        normalize_string("esito_provvedimento") AS esito_provvedimento,
        cast_bigint("definitorio") = 1 AS definitorio
    FROM read_csv_auto('{base_dir_posix}/data/esiti_codelist.csv')
)
SELECT
    b.anno,
    b.mese,
    b.codice_sede,
    b.nome_sede,
    b.classificazione_ricorso,
    b.esito_provvedimento,
    b.numero_ricorsi_definiti,
    COALESCE(e.definitorio, FALSE) AS esito_definitorio
FROM base b
LEFT JOIN esiti e
    ON replace(b.esito_provvedimento, chr(39) || chr(39), chr(39)) = e.esito_provvedimento
WHERE b.anno IS NOT NULL
