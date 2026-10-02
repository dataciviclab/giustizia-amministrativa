-- Panoramica annuale: totals per anno
-- sentenze/brevi/piene sono al grano materia: le somme sono valide
SELECT
    anno,
    SUM(pervenuti) AS totale_pervenuti,
    SUM(definiti) AS totale_definiti,
    SUM(sentenze) AS totale_sentenze,
    SUM(sentenze_brevi) AS totale_sentenze_brevi,
    SUM(sentenze_piene) AS totale_sentenze_piene,
    ROUND(SUM(sentenze_brevi) * 100.0 / NULLIF(SUM(sentenze), 0), 1) AS quota_brevi_pct,
    SUM(accoglimenti) AS totale_accoglimenti,
    SUM(rigetti) AS totale_rigetti,
    ROUND(SUM(definiti) * 100.0 / NULLIF(SUM(pervenuti), 0), 1) AS tasso_definizione,
    ROUND(SUM(accoglimenti) * 100.0 / NULLIF(SUM(accoglimenti) + SUM(rigetti), 0), 1) AS tasso_accoglimento,
    COUNT(DISTINCT codice_sede) AS n_sedi,
    COUNT(DISTINCT classificazione_ricorso) AS n_classificazioni
FROM clean_input
GROUP BY anno
ORDER BY anno
