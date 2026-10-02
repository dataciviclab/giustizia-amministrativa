-- Outlier per sede: mix di definizione anomalo rispetto alla media nazionale
-- Utile per individuare sedi ancora "decretiste" o con quota brevi estrema
WITH national AS (
    SELECT
        anno,
        ROUND(SUM(definiti_sentenza_breve) * 100.0 / NULLIF(SUM(totale_definiti), 0), 1) AS nat_sentenza_pct,
        ROUND(SUM(definiti_decreto_decisori) * 100.0 / NULLIF(SUM(totale_definiti), 0), 1) AS nat_decreto_pct
    FROM clean_input
    GROUP BY anno
)
SELECT
    c.anno,
    c.codice_sede,
    c.nome_sede,
    c.totale_definiti,
    c.sentenza_pct,
    c.decreto_pct,
    n.nat_sentenza_pct,
    n.nat_decreto_pct,
    ROUND(c.sentenza_pct - n.nat_sentenza_pct, 1) AS delta_sentenza_pct,
    ROUND(c.decreto_pct - n.nat_decreto_pct, 1) AS delta_decreto_pct,
    c.quota_brevi_pct,
    c.tasso_accoglimento
FROM clean_input c
JOIN national n ON c.anno = n.anno
WHERE c.totale_definiti >= 500
ORDER BY c.anno, delta_decreto_pct DESC
