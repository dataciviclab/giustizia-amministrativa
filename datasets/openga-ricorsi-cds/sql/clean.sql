-- Clean: Ricorsi Pendenti Consiglio di Stato (OpenGA)
-- Colonna ANNO_MESE_RIFERIMENTO: YYYYMM (es. 202401) — mese = ultime 2 cifre

SELECT
    cast_bigint(floor(cast("ANNO_MESE_RIFERIMENTO" as double) / 100)) AS anno,
    cast_bigint("ANNO_MESE_RIFERIMENTO") AS anno_mese_riferimento,
    cast_bigint("ANNO_MESE_RIFERIMENTO" % 100) AS mese,
    cast_bigint("CODICE_SEDE") AS codice_sede,
    normalize_string("NOME_SEDE") AS nome_sede,
    cast_bigint("NUMERO_RICORSI_PENDENTI") AS numero_ricorsi_pendenti
FROM raw_input
