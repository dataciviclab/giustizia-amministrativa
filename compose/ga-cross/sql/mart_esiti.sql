-- Esiti per classificazione: tasso accoglimento + mix sentenze brevi
SELECT
    anno,
    classificazione_ricorso,
    SUM(pervenuti) AS pervenuti,
    SUM(definiti) AS definiti,
    SUM(sentenze) AS sentenze,
    SUM(sentenze_brevi) AS sentenze_brevi,
    SUM(sentenze_piene) AS sentenze_piene,
    ROUND(SUM(sentenze_brevi) * 100.0 / NULLIF(SUM(sentenze), 0), 1) AS quota_brevi_pct,
    SUM(accoglimenti) AS accoglimenti,
    SUM(rigetti) AS rigetti,
    ROUND(SUM(definiti) * 100.0 / NULLIF(SUM(pervenuti), 0), 1) AS tasso_definizione,
    ROUND(SUM(accoglimenti) * 100.0 / NULLIF(SUM(accoglimenti) + SUM(rigetti), 0), 1) AS tasso_accoglimento
FROM clean_input
WHERE classificazione_ricorso IS NOT NULL
GROUP BY anno, classificazione_ricorso
ORDER BY anno, pervenuti DESC
