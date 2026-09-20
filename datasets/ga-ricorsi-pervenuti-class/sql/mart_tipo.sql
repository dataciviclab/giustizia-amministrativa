SELECT
    anno,
    classificazione_ricorso,
    SUM(numero_ricorsi) AS totale
FROM clean_input
WHERE classificazione_ricorso IS NOT NULL
GROUP BY anno, classificazione_ricorso
ORDER BY anno, totale DESC
