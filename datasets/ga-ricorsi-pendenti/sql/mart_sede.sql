-- Stock pendenti per sede/anno: media, min, max e valore a dicembre
-- (dicembre mancante sui parziali → NULL, non 0)
SELECT
    anno,
    codice_sede,
    any_value(nome_sede) AS nome_sede,
    COUNT(*) AS n_mesi,
    ROUND(AVG(numero_ricorsi_pendenti), 0) AS pendenti_media,
    MIN(numero_ricorsi_pendenti) AS pendenti_min,
    MAX(numero_ricorsi_pendenti) AS pendenti_max,
    MAX(CASE WHEN mese = 12 THEN numero_ricorsi_pendenti END) AS pendenti_dicembre
FROM clean_input
GROUP BY anno, codice_sede
ORDER BY anno, pendenti_media DESC
