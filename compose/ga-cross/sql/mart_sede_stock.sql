-- Flusso × stock per sede/anno: pendente medio affiancato ai flussi
-- Flusso: aggregato dal clean (sede × classificazione → sede × anno)
-- Stock: mart_pendenti_per_sede del support ga-ricorsi-pendenti
--
-- Gap fonte pendenti: assente 2017-2019 e 2024 → righe con
-- pendenti_media NULL (non 0). Usare pendenti_n_mesi come controllo
-- di copertura (2020 e 2026 sono parziali).
WITH flusso AS (
    SELECT
        anno,
        codice_sede,
        any_value(nome_sede) AS nome_sede,
        SUM(pervenuti) AS pervenuti,
        SUM(definiti) AS definiti,
        SUM(sentenze) AS sentenze,
        ROUND(SUM(definiti) * 100.0 / NULLIF(SUM(pervenuti), 0), 1) AS tasso_definizione
    FROM clean_input
    GROUP BY anno, codice_sede
)
SELECT
    f.anno,
    f.codice_sede,
    f.nome_sede,
    f.pervenuti,
    f.definiti,
    f.sentenze,
    f.tasso_definizione,
    p.n_mesi AS pendenti_n_mesi,
    p.pendenti_media,
    p.pendenti_min,
    p.pendenti_max,
    -- Definiti per unita' di stock medio: ~1 = si assorbe l'arretrato
    -- alla velocita' con cui si forma (solo dove il stock e' disponibile)
    ROUND(f.definiti * 1.0 / NULLIF(p.pendenti_media, 0), 2) AS definisci_su_pendente
FROM flusso f
LEFT JOIN read_parquet('{support.pendenti.mart.mart_pendenti_per_sede}') p
    ON f.anno = p.anno
    AND f.codice_sede = p.codice_sede
ORDER BY f.anno, f.pervenuti DESC
