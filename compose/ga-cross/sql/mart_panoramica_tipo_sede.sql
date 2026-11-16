-- Panoramica annuale per tipo di sede: giurisdizionale vs consultivo.
-- Le sedi 31 (CdS CONSULTIVE) e 33 (CGA CONSULTIVE) esprimono pareri, non
-- ricorsi: nei totali nazionali di mart_panoramica valgono il 2-4% dei
-- pervenuti annui e vanno lette a parte quando si parla di contenzioso.
SELECT
    anno,
    tipo_sede,
    SUM(pervenuti) AS totale_pervenuti,
    SUM(definiti) AS totale_definiti,
    SUM(esiti_interlocutori) AS totale_esiti_interlocutori,
    SUM(sentenze) AS totale_sentenze,
    SUM(accoglimenti) AS totale_accoglimenti,
    SUM(rigetti) AS totale_rigetti,
    ROUND(SUM(definiti) * 100.0 / NULLIF(SUM(pervenuti), 0), 1) AS tasso_definizione,
    ROUND(SUM(accoglimenti) * 100.0 / NULLIF(SUM(accoglimenti) + SUM(rigetti), 0), 1) AS tasso_accoglimento,
    COUNT(DISTINCT codice_sede) AS n_sedi
FROM clean_input
GROUP BY anno, tipo_sede
ORDER BY anno, tipo_sede
