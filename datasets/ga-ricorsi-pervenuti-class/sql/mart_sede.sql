SELECT
    anno,
    codice_sede,
    nome_sede,
    SUM(numero_ricorsi) AS totale
FROM clean_input
GROUP BY anno, codice_sede, nome_sede
ORDER BY anno, totale DESC
