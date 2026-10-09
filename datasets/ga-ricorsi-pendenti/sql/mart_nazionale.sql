-- Serie nazionale: somma delle sedi per mese, poi statistiche annuali
WITH pendenti_mese AS (
    SELECT
        anno,
        mese,
        SUM(numero_ricorsi_pendenti) AS pendenti_mese
    FROM clean_input
    GROUP BY anno, mese
)
SELECT
    anno,
    COUNT(*) AS n_mesi,
    ROUND(AVG(pendenti_mese), 0) AS pendenti_media,
    MIN(pendenti_mese) AS pendenti_min,
    MAX(pendenti_mese) AS pendenti_max,
    MAX(CASE WHEN mese = 12 THEN pendenti_mese END) AS pendenti_dicembre
FROM pendenti_mese
GROUP BY anno
ORDER BY anno
