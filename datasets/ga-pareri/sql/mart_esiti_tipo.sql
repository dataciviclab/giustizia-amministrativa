SELECT
    anno,
    tipo_provvedimento,
    esito_provvedimento,
    COUNT(*) AS totale,
    COUNT(DISTINCT numero_ricorso) AS ricorsi_distinti
FROM clean_input
WHERE esito_provvedimento IS NOT NULL
  AND tipo_provvedimento IS NOT NULL
GROUP BY anno, tipo_provvedimento, esito_provvedimento
ORDER BY anno, tipo_provvedimento, totale DESC
