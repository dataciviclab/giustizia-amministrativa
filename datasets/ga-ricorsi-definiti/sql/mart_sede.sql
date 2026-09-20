SELECT
    anno,
    codice_sede,
    nome_sede,
    esito_provvedimento,
    SUM(numero_ricorsi_definiti) AS totale
FROM clean_input
WHERE esito_provvedimento IS NOT NULL
GROUP BY anno, codice_sede, nome_sede, esito_provvedimento
ORDER BY anno, nome_sede, totale DESC
