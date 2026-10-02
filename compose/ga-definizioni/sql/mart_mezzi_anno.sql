-- Trend nazionale: mix mezzi di definizione per anno
SELECT
    anno,
    SUM(definiti_sentenza_breve) AS definiti_sentenza_breve,
    SUM(definiti_decreto_decisori) AS definiti_decreto_decisori,
    SUM(definiti_altri) AS definiti_altri,
    SUM(totale_definiti) AS totale_definiti,
    ROUND(SUM(definiti_sentenza_breve) * 100.0 / NULLIF(SUM(totale_definiti), 0), 1) AS sentenza_pct,
    ROUND(SUM(definiti_decreto_decisori) * 100.0 / NULLIF(SUM(totale_definiti), 0), 1) AS decreto_pct,
    ROUND(SUM(definiti_altri) * 100.0 / NULLIF(SUM(totale_definiti), 0), 1) AS altri_pct,
    SUM(sb_sentenze_brevi) AS sb_sentenze_brevi,
    SUM(sb_sentenze) AS sb_sentenze,
    ROUND(SUM(sb_sentenze_brevi) * 100.0 / NULLIF(SUM(sb_sentenze), 0), 1) AS quota_brevi_pct,
    SUM(rd_definiti) AS rd_definiti,
    ROUND(
        SUM(rd_accoglimenti) * 100.0
        / NULLIF(SUM(rd_accoglimenti) + SUM(rd_rigetti), 0),
        1
    ) AS tasso_accoglimento
FROM clean_input
GROUP BY anno
ORDER BY anno
