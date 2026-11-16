-- Durata del ricorso per sede × anno × tipo di atto.
-- Grano: anno × codice_sede × tipo_atto.
-- Un ricorso definito da piu' atti conta una volta (MIN della durata per ricorso).
WITH definitori AS (
    SELECT
        anno,
        codice_sede,
        nome_sede,
        tipo_atto,
        numero_ricorso,
        MIN(durata_giorni) AS durata_giorni
    FROM clean_input
    WHERE durata_giorni IS NOT NULL
    GROUP BY anno, codice_sede, nome_sede, tipo_atto, numero_ricorso
)
SELECT
    anno,
    codice_sede,
    nome_sede,
    tipo_atto,
    COUNT(*) AS n_ricorsi_definiti,
    ROUND(MEDIAN(durata_giorni), 0) AS durata_mediana_giorni,
    ROUND(QUANTILE_CONT(durata_giorni, 0.9), 0) AS durata_p90_giorni,
    ROUND(AVG(durata_giorni), 0) AS durata_media_giorni
FROM definitori
GROUP BY anno, codice_sede, nome_sede, tipo_atto
ORDER BY anno, n_ricorsi_definiti DESC
