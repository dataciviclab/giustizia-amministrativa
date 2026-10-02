SELECT
    cast_bigint("ANNO_PUBBLICAZIONE") AS anno,
    cast_bigint("MESE_PUBBLICAZIONE") AS mese,
    cast_bigint("CODICE_SEDE") AS codice_sede,
    normalize_string("NOME_SEDE") AS nome_sede,
    cast_bigint("NUMERO_RICORSI_DEFINITI_SENTENZA_E_SENTENZA_BREVE") AS definiti_sentenza_breve,
    cast_bigint("NUMERO_RICORSI_DEFINITI_DECRETO_DECISORIO") AS definiti_decreto_decisori,
    cast_bigint("NUMERO_RICORSI_DEFINITI_ALTRI_PROVVEDIMENTI") AS definiti_altri,
    cast_bigint("NUMERO_RICORSI_DEFINITI") AS totale_definiti
FROM raw_input
WHERE cast_bigint("ANNO_PUBBLICAZIONE") IS NOT NULL
