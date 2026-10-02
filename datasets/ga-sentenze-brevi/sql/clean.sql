SELECT
    cast_bigint("ANNO_SENTENZA") AS anno,
    cast_bigint("MESE_SENTENZA") AS mese,
    cast_bigint("CODICE_SEDE") AS codice_sede,
    normalize_string("NOME_SEDE") AS nome_sede,
    normalize_string("CLASSIFICAZIONE_RICORSO") AS classificazione_ricorso,
    normalize_string("TIPO_SENTENZA") AS tipo_sentenza,
    cast_bigint("NUMERO_SENTENZE") AS numero_sentenze
FROM raw_input
WHERE cast_bigint("ANNO_SENTENZA") IS NOT NULL
