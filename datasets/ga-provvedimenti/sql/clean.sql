SELECT
    cast_bigint("ANNO_PUBBLICAZIONE") AS anno,
    cast_bigint("MESE_PUBBLICAZIONE") AS mese,
    cast_bigint("CODICE_SEDE") AS codice_sede,
    normalize_string("NOME_SEDE") AS nome_sede,
    normalize_string("TIPO_PROVVEDIMENTO") AS tipo_provvedimento,
    cast_bigint("NUMERO_PROVVEDIMENTI_DEFINISCONO") AS provvedimenti_definiscono,
    cast_bigint("NUMERO_PROVVEDIMENTI_NON_DEFINISCONO") AS provvedimenti_non_definiscono,
    cast_bigint("NUMERO_TOTALE_PROVVEDIMENTI") AS totale_provvedimenti,
    cast_bigint("NUMERO_RICORSI_DEFINITI") AS ricorsi_definiti,
    cast_bigint("NUMERO_RICORSI_NON_DEFINITI") AS ricorsi_non_definiti,
    cast_bigint("NUMERO_TOTALE_RICORSI") AS totale_ricorsi
FROM raw_input
WHERE anno IS NOT NULL
