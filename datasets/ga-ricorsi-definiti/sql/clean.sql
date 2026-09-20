SELECT
    cast_bigint("ANNO_SENTENZA") AS anno,
    cast_bigint("MESE_SENTENZA") AS mese,
    cast_bigint("CODICE_SEDE") AS codice_sede,
    normalize_string("NOME_SEDE") AS nome_sede,
    normalize_string("CLASSIFICAZIONE_RICORSO") AS classificazione_ricorso,
    normalize_string("ESITO_PROVVEDIMENTO") AS esito_provvedimento,
    cast_bigint("NUMERO_RICORSI_DEFINITI") AS numero_ricorsi_definiti
FROM raw_input
WHERE anno IS NOT NULL
