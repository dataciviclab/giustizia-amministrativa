-- Stock mensile ricorsi pendenti per sede (OpenGA)
-- ANNO_MESE_RIFERIMENTO: YYYYMM (es. 202507 = luglio 2025)
-- Grano clean: anno × mese × codice_sede
SELECT
    cast_bigint("ANNO_MESE_RIFERIMENTO") // 100 AS anno,
    cast_bigint("ANNO_MESE_RIFERIMENTO") % 100 AS mese,
    cast_bigint("CODICE_SEDE") AS codice_sede,
    normalize_string("NOME_SEDE") AS nome_sede,
    cast_bigint("NUMERO_RICORSI_PENDENTI") AS numero_ricorsi_pendenti
FROM raw_input
WHERE anno IS NOT NULL
  AND mese BETWEEN 1 AND 12
  AND numero_ricorsi_pendenti >= 0
