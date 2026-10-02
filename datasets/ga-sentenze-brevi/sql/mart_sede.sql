SELECT
    anno,
    codice_sede,
    nome_sede,
    tipo_sentenza,
    SUM(numero_sentenze) AS totale
FROM clean_input
WHERE tipo_sentenza IS NOT NULL
GROUP BY anno, codice_sede, nome_sede, tipo_sentenza
ORDER BY anno, nome_sede, totale DESC
