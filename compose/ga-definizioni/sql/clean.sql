-- Compose GA definizioni: mezzi di definizione per sede×anno
-- Grano clean: anno × codice_sede × nome_sede
-- raw_input = ga_ricorsi_tipo_decisione (clean)
-- support.definiti / support.sentenze_brevi per contesto esiti e mix brevi
--
-- Attenzione: non unire a ga_cross per materia — questo compose non ha
-- classificazione_ricorso. È il grano giusto per "come lavora ogni sede".

WITH td AS (
    SELECT
        anno,
        codice_sede,
        any_value(nome_sede) AS nome_sede,
        SUM(definiti_sentenza_breve) AS definiti_sentenza_breve,
        SUM(definiti_decreto_decisori) AS definiti_decreto_decisori,
        SUM(definiti_altri) AS definiti_altri,
        SUM(totale_definiti) AS totale_definiti
    FROM raw_input
    GROUP BY anno, codice_sede
),
rd AS (
    SELECT
        anno,
        codice_sede,
        any_value(nome_sede) AS nome_sede,
        SUM(numero_ricorsi_definiti) AS rd_definiti,
        SUM(CASE WHEN esito_provvedimento = 'ACCOGLIE' THEN numero_ricorsi_definiti ELSE 0 END) AS rd_accoglimenti,
        SUM(CASE WHEN esito_provvedimento = 'RESPINGE' THEN numero_ricorsi_definiti ELSE 0 END) AS rd_rigetti
    FROM read_parquet('{support.definiti.clean}')
    GROUP BY anno, codice_sede
),
sb AS (
    SELECT
        anno,
        codice_sede,
        any_value(nome_sede) AS nome_sede,
        SUM(CASE WHEN tipo_sentenza ILIKE '%BREVE%' THEN numero_sentenze ELSE 0 END) AS sb_sentenze_brevi,
        SUM(CASE WHEN tipo_sentenza = 'SENTENZA' THEN numero_sentenze ELSE 0 END) AS sb_sentenze_piene,
        SUM(numero_sentenze) AS sb_sentenze
    FROM read_parquet('{support.sentenze_brevi.clean}')
    GROUP BY anno, codice_sede
)
SELECT
    t.anno,
    t.codice_sede,
    t.nome_sede,
    t.definiti_sentenza_breve,
    t.definiti_decreto_decisori,
    t.definiti_altri,
    t.totale_definiti,
    ROUND(t.definiti_sentenza_breve * 100.0 / NULLIF(t.totale_definiti, 0), 1) AS sentenza_pct,
    ROUND(t.definiti_decreto_decisori * 100.0 / NULLIF(t.totale_definiti, 0), 1) AS decreto_pct,
    ROUND(t.definiti_altri * 100.0 / NULLIF(t.totale_definiti, 0), 1) AS altri_pct,
    COALESCE(r.rd_definiti, 0) AS rd_definiti,
    COALESCE(r.rd_accoglimenti, 0) AS rd_accoglimenti,
    COALESCE(r.rd_rigetti, 0) AS rd_rigetti,
    ROUND(
        COALESCE(r.rd_accoglimenti, 0) * 100.0
        / NULLIF(COALESCE(r.rd_accoglimenti, 0) + COALESCE(r.rd_rigetti, 0), 0),
        1
    ) AS tasso_accoglimento,
    COALESCE(s.sb_sentenze_brevi, 0) AS sb_sentenze_brevi,
    COALESCE(s.sb_sentenze_piene, 0) AS sb_sentenze_piene,
    COALESCE(s.sb_sentenze, 0) AS sb_sentenze,
    ROUND(
        COALESCE(s.sb_sentenze_brevi, 0) * 100.0 / NULLIF(COALESCE(s.sb_sentenze, 0), 0),
        1
    ) AS quota_brevi_pct
FROM td t
LEFT JOIN rd r
    ON t.anno = r.anno AND t.codice_sede = r.codice_sede
LEFT JOIN sb s
    ON t.anno = s.anno AND t.codice_sede = s.codice_sede
ORDER BY t.anno, t.totale_definiti DESC
