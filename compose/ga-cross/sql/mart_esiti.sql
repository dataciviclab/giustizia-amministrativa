-- Esiti per classificazione: tasso accoglimento per materia
SELECT
    anno,
    classificazione_ricorso,
    SUM(pervenuti) AS pervenuti,
    SUM(definiti) AS definiti,
    SUM(accoglimenti) AS accoglimenti,
    SUM(rigetti) AS rigetti,
    ROUND(SUM(definiti) * 100.0 / NULLIF(SUM(pervenuti), 0), 1) AS tasso_definizione,
    ROUND(SUM(accoglimenti) * 100.0 / NULLIF(SUM(accoglimenti) + SUM(rigetti), 0), 1) AS tasso_accoglimento
FROM clean_input
WHERE classificazione_ricorso IS NOT NULL
GROUP BY anno, classificazione_ricorso
ORDER BY anno, pervenuti DESC
