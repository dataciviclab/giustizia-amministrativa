SELECT
    cast_bigint(floor(cast("ANNO_DEPOSITO" as double) / 100)) AS anno,
    cast_bigint("ANNO_DEPOSITO") AS anno_mese,
    cast_bigint("CODICE_SEDE") AS codice_sede,
    normalize_string("NOME_SEDE") AS nome_sede,
    normalize_string("CLASSIFICAZIONE_RICORSO") AS classificazione_ricorso,
    cast_bigint("NUMERO_RICORSI_PERVENUTI") AS numero_ricorsi
FROM raw_input
WHERE anno IS NOT NULL
