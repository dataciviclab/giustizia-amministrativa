-- Compose ponte appalti ↔ contenzioso.
-- Grano clean: ricorso = codice_sede × numero_ricorso.
--
-- Sorgente ricorsi: openga_ricorsi_appalto, dove lo stesso ricorso puo'
-- comparire su piu' righe (piu' gare/CIG impugnati): si aggrega al ricorso,
-- tenendo il numero di CIG distinti e l'importo della gara piu' rilevante
-- (max, non somma: importo_complessivo_gara e' ripetuto su ogni lotto).
--
-- Sorgente decisioni: atti pubblicati (sentenze, decreti, ordinanze) joinati
-- su (codice_sede, numero_ricorso). `esito_decisione` privilegia
-- ACCOGLIE/RESPINGE; gli altri esiti restano 'ALTRO'.
-- `durata_giorni` = prima decisione che definisce meno deposito del ricorso,
-- scartata se negativa (poche date incoerenti di fonte).
WITH gara AS (
    SELECT
        codice_sede,
        numero_ricorso,
        MIN(anno) AS anno,
        any_value(nome_sede) AS nome_sede,
        any_value(classificazione_ricorso) AS classificazione_ricorso,
        COUNT(DISTINCT codice_cig) AS n_cig,
        COUNT(DISTINCT numero_gara) AS n_gare,
        MAX(importo_complessivo_gara) AS importo_gara,
        SUM(importo_lotto) AS importo_lotti,
        COUNT(*) AS n_lotti,
        any_value(settore) AS settore,
        any_value(provincia) AS provincia,
        any_value(cf_amministrazione_appaltante) AS cf_amministrazione_appaltante,
        any_value(denominazione_amministrazione_appaltante) AS denominazione_amministrazione_appaltante,
        MIN(data_deposito_ricorso) AS data_deposito_ricorso
    FROM raw_input
    GROUP BY codice_sede, numero_ricorso
),
atti AS (
    SELECT codice_sede, numero_ricorso, data_pubblicazione, esito_provvedimento, flg_definisce
    FROM read_parquet('{support.sentenze.clean}')
    UNION ALL
    SELECT codice_sede, numero_ricorso, data_pubblicazione, esito_provvedimento, flg_definisce
    FROM read_parquet('{support.decreti.clean}')
    UNION ALL
    SELECT codice_sede, numero_ricorso, data_pubblicazione, esito_provvedimento, flg_definisce
    FROM read_parquet('{support.ordinanze.clean}')
),
atti_ric AS (
    SELECT
        codice_sede,
        numero_ricorso,
        COUNT(*) AS n_atti,
        COUNT(*) FILTER (WHERE flg_definisce = 'D') AS n_atti_definitori,
        MIN(data_pubblicazione) FILTER (WHERE flg_definisce = 'D') AS data_decisione,
        CASE
            WHEN COUNT(*) FILTER (WHERE esito_provvedimento = 'ACCOGLIE') > 0 THEN 'ACCOGLIE'
            WHEN COUNT(*) FILTER (WHERE esito_provvedimento = 'RESPINGE') > 0 THEN 'RESPINGE'
            ELSE 'ALTRO'
        END AS esito_decisione
    FROM atti
    GROUP BY codice_sede, numero_ricorso
)
SELECT
    g.anno,
    g.codice_sede,
    g.nome_sede,
    g.numero_ricorso,
    g.classificazione_ricorso,
    g.n_cig,
    g.n_gare,
    g.n_lotti,
    g.importo_gara,
    g.importo_lotti,
    COALESCE(g.settore, 'NON DISPONIBILE') AS settore,
    COALESCE(g.provincia, 'NON DISPONIBILE') AS provincia,
    g.cf_amministrazione_appaltante,
    g.denominazione_amministrazione_appaltante,
    g.data_deposito_ricorso,
    COALESCE(a.n_atti, 0) AS n_atti,
    COALESCE(a.n_atti_definitori, 0) AS n_atti_definitori,
    COALESCE(a.n_atti, 0) > 0 AS ha_decisione,
    COALESCE(a.esito_decisione, 'SENZA DECISIONE') AS esito_decisione,
    a.data_decisione,
    CASE
        WHEN g.data_deposito_ricorso IS NOT NULL
            AND a.data_decisione IS NOT NULL
            AND a.data_decisione >= g.data_deposito_ricorso
        THEN date_diff('day', g.data_deposito_ricorso, a.data_decisione)
    END AS durata_giorni
FROM gara g
LEFT JOIN atti_ric a
    ON g.codice_sede = a.codice_sede
    AND g.numero_ricorso = a.numero_ricorso
