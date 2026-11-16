-- Trend nazionale della durata per anno × tipo di atto.
-- Anno = anno di pubblicazione dell'atto che definisce (non anno di deposito):
-- la durata e' per coorte di definizione, non di ingresso.
WITH definitori AS (
    SELECT
        anno,
        tipo_atto,
        codice_sede,
        numero_ricorso,
        MIN(durata_giorni) AS durata_giorni
    FROM clean_input
    WHERE durata_giorni IS NOT NULL
    GROUP BY anno, tipo_atto, codice_sede, numero_ricorso
)
SELECT
    anno,
    tipo_atto,
    COUNT(*) AS n_ricorsi_definiti,
    ROUND(MEDIAN(durata_giorni), 0) AS durata_mediana_giorni,
    ROUND(QUANTILE_CONT(durata_giorni, 0.75), 0) AS durata_p75_giorni,
    ROUND(QUANTILE_CONT(durata_giorni, 0.9), 0) AS durata_p90_giorni,
    COUNT(DISTINCT codice_sede) AS n_sedi
FROM definitori
GROUP BY anno, tipo_atto
ORDER BY anno, tipo_atto
