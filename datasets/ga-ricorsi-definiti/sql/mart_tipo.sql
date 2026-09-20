SELECT
    anno,
    classificazione_ricorso,
    esito_provvedimento,
    SUM(numero_ricorsi_definiti) AS totale
FROM clean_input
WHERE esito_provvedimento IS NOT NULL AND classificazione_ricorso IS NOT NULL
GROUP BY anno, classificazione_ricorso, esito_provvedimento
ORDER BY anno, classificazione_ricorso, totale DESC
