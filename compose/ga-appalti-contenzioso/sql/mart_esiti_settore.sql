-- Esiti dei ricorsi in materia di appalti per settore × anno.
-- Grano: anno × settore.
SELECT
    anno,
    settore,
    COUNT(*) AS n_ricorsi,
    COUNT(*) FILTER (WHERE ha_decisione) AS n_con_decisione,
    COUNT(*) FILTER (WHERE esito_decisione = 'ACCOGLIE') AS n_accoglie,
    COUNT(*) FILTER (WHERE esito_decisione = 'RESPINGE') AS n_respinge,
    ROUND(COUNT(*) FILTER (WHERE ha_decisione) * 100.0 / NULLIF(COUNT(*), 0), 1) AS tasso_decisione_pct,
    ROUND(
        COUNT(*) FILTER (WHERE esito_decisione = 'ACCOGLIE') * 100.0
        / NULLIF(
            COUNT(*) FILTER (WHERE esito_decisione IN ('ACCOGLIE', 'RESPINGE')),
            0
        ),
        1
    ) AS tasso_accoglimento_pct,
    ROUND(MEDIAN(durata_giorni), 0) AS durata_mediana_giorni,
    ROUND(MEDIAN(importo_gara), 0) AS importo_mediano_gara
FROM clean_input
GROUP BY anno, settore
ORDER BY anno, n_ricorsi DESC
