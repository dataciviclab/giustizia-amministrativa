-- Esiti per tipo di atto: un solo posto per il confronto tra famiglie.
-- Grano: anno × tipo_atto × esito_provvedimento.
SELECT
    anno,
    tipo_atto,
    esito_provvedimento,
    COUNT(*) AS n_atti,
    COUNT(*) FILTER (WHERE flg_definisce = 'D') AS n_atti_che_definiscono
FROM clean_input
WHERE esito_provvedimento IS NOT NULL
GROUP BY anno, tipo_atto, esito_provvedimento
ORDER BY anno, tipo_atto, n_atti DESC
