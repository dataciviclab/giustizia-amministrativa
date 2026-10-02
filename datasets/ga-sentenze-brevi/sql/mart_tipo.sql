SELECT
    anno,
    classificazione_ricorso,
    tipo_sentenza,
    SUM(numero_sentenze) AS totale
FROM clean_input
WHERE tipo_sentenza IS NOT NULL
  AND classificazione_ricorso IS NOT NULL
GROUP BY anno, classificazione_ricorso, tipo_sentenza
ORDER BY anno, classificazione_ricorso, totale DESC
