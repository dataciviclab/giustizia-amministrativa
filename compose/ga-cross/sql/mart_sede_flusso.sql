-- Flusso per sede: pervenuti vs definiti per sede/anno
SELECT
    anno,
    codice_sede,
    nome_sede,
    SUM(pervenuti) AS pervenuti,
    SUM(definiti) AS definiti,
    SUM(sentenze) AS sentenze,
    SUM(accoglimenti) AS accoglimenti,
    SUM(rigetti) AS rigetti,
    ROUND(SUM(definiti) * 100.0 / NULLIF(SUM(pervenuti), 0), 1) AS tasso_definizione,
    ROUND(SUM(accoglimenti) * 100.0 / NULLIF(SUM(accoglimenti) + SUM(rigetti), 0), 1) AS tasso_accoglimento
FROM clean_input
GROUP BY anno, codice_sede, nome_sede
ORDER BY anno, pervenuti DESC
