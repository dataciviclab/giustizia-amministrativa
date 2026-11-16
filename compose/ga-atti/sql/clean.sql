-- Compose GA atti: un provvedimento pubblicato per riga.
-- Grano clean: anno × codice_sede × numero_provvedimento (atto).
--
-- Unione dei quattro dataset atti, che hanno schema identico. `tipo_atto`
-- distingue la famiglia di provvedimento.
--
-- DURATA: `durata_giorni` = pubblicazione dell'atto che definisce meno
-- deposito del ricorso. Calcolata solo per flg_definisce = 'D' e solo con
-- date coerenti (data_pubblicazione >= data_deposito_ricorso): le poche
-- righe con date invertite restano NULL invece di produrre durate negative
-- (144 ordinanze e 2.410 decreti sul totale 2017-2026).
WITH atti AS (
    SELECT *, 'sentenza' AS tipo_atto FROM raw_input
    UNION ALL
    SELECT *, 'ordinanza' AS tipo_atto FROM read_parquet('{support.ordinanze.clean}')
    UNION ALL
    SELECT *, 'decreto' AS tipo_atto FROM read_parquet('{support.decreti.clean}')
    UNION ALL
    SELECT *, 'parere' AS tipo_atto FROM read_parquet('{support.pareri.clean}')
)
SELECT
    anno,
    codice_sede,
    nome_sede,
    tipo_atto,
    codice_sezione,
    nome_sezione,
    numero_provvedimento,
    numero_ricorso,
    data_pubblicazione,
    mese_pubblicazione,
    esito_provvedimento,
    flg_definisce,
    data_deposito_ricorso,
    oggetto_ricorso,
    tipo_ricorso,
    tipo_udienza,
    num_membri_collegio,
    tipo_provvedimento,
    CASE
        WHEN flg_definisce = 'D'
            AND data_pubblicazione IS NOT NULL
            AND data_deposito_ricorso IS NOT NULL
            AND data_pubblicazione >= data_deposito_ricorso
        THEN date_diff('day', data_deposito_ricorso, data_pubblicazione)
    END AS durata_giorni
FROM atti
