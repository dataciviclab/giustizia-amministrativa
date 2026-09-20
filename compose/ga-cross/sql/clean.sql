-- Compose GA: unisce pervenuti e definiti per sede/classificazione/anno
-- clean_input = pervenuti (dal raw parquet)
-- Le tabelle support si leggono con read_parquet('{support.X.clean}')

WITH pervenuti_agg AS (
    SELECT
        anno,
        codice_sede,
        nome_sede,
        classificazione_ricorso,
        SUM(numero_ricorsi) AS pervenuti
    FROM raw_input
    WHERE classificazione_ricorso IS NOT NULL
    GROUP BY anno, codice_sede, nome_sede, classificazione_ricorso
),
definiti_agg AS (
    SELECT
        anno,
        codice_sede,
        nome_sede,
        classificazione_ricorso,
        SUM(numero_ricorsi_definiti) AS definiti,
        SUM(CASE WHEN esito_provvedimento = 'ACCOGLIE' THEN numero_ricorsi_definiti ELSE 0 END) AS accoglimenti,
        SUM(CASE WHEN esito_provvedimento = 'RESPINGE' THEN numero_ricorsi_definiti ELSE 0 END) AS rigetti
    FROM read_parquet('{support.definiti.clean}')
    WHERE classificazione_ricorso IS NOT NULL
    GROUP BY anno, codice_sede, nome_sede, classificazione_ricorso
),
sentenze_agg AS (
    SELECT
        anno,
        codice_sede,
        nome_sede,
        COUNT(*) AS sentenze
    FROM read_parquet('{support.sentenze.clean}')
    GROUP BY anno, codice_sede, nome_sede
)
SELECT
    p.anno,
    p.codice_sede,
    p.nome_sede,
    p.classificazione_ricorso,
    p.pervenuti,
    COALESCE(d.definiti, 0) AS definiti,
    COALESCE(s.sentenze, 0) AS sentenze,
    COALESCE(d.accoglimenti, 0) AS accoglimenti,
    COALESCE(d.rigetti, 0) AS rigetti,
    ROUND(COALESCE(d.definiti, 0) * 100.0 / NULLIF(p.pervenuti, 0), 1) AS tasso_definizione,
    ROUND(COALESCE(d.accoglimenti, 0) * 100.0 / NULLIF(COALESCE(d.accoglimenti, 0) + COALESCE(d.rigetti, 0), 0), 1) AS tasso_accoglimento
FROM pervenuti_agg p
LEFT JOIN definiti_agg d
    ON p.anno = d.anno
    AND p.codice_sede = d.codice_sede
    AND p.classificazione_ricorso = d.classificazione_ricorso
LEFT JOIN sentenze_agg s
    ON p.anno = s.anno
    AND p.codice_sede = s.codice_sede
ORDER BY p.anno, p.pervenuti DESC
