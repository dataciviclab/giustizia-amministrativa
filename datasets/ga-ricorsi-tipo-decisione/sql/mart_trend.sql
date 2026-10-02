SELECT
    anno,
    SUM(definiti_sentenza_breve) AS definiti_sentenza_breve,
    SUM(definiti_decreto_decisori) AS definiti_decreto_decisori,
    SUM(definiti_altri) AS definiti_altri,
    SUM(totale_definiti) AS totale_definiti,
    ROUND(SUM(definiti_sentenza_breve) * 100.0 / NULLIF(SUM(totale_definiti), 0), 1) AS sentenza_pct
FROM clean_input
GROUP BY anno
ORDER BY anno
