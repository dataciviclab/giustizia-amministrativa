-- Compose GA: flusso pervenuti → definiti per sede/classificazione/anno
-- Grano clean: anno × codice_sede × classificazione_ricorso
-- raw_input = pervenuti (parquet clean)
-- support.definiti / support.sentenze_brevi via read_parquet('{support.X.clean}')
--
-- NOTA: le sentenze entrano SOLO da ga_sentenze_brevi (ha classificazione).
-- ga-sentenze non ha materia: in passato veniva broadcast per sede e le
-- somme risultavano inflate. Oggi sentenze/brevi/piene sono al grano materia.

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
        any_value(nome_sede) AS nome_sede,
        classificazione_ricorso,
        SUM(numero_ricorsi_definiti) AS definiti,
        SUM(CASE WHEN esito_provvedimento = 'ACCOGLIE' THEN numero_ricorsi_definiti ELSE 0 END) AS accoglimenti,
        SUM(CASE WHEN esito_provvedimento = 'RESPINGE' THEN numero_ricorsi_definiti ELSE 0 END) AS rigetti
    FROM read_parquet('{support.definiti.clean}')
    WHERE classificazione_ricorso IS NOT NULL
    GROUP BY anno, codice_sede, classificazione_ricorso
),
sentenze_agg AS (
    SELECT
        anno,
        codice_sede,
        any_value(nome_sede) AS nome_sede,
        classificazione_ricorso,
        SUM(CASE WHEN tipo_sentenza ILIKE '%BREVE%' THEN numero_sentenze ELSE 0 END) AS sentenze_brevi,
        SUM(CASE WHEN tipo_sentenza = 'SENTENZA' THEN numero_sentenze ELSE 0 END) AS sentenze_piene,
        SUM(numero_sentenze) AS sentenze
    FROM read_parquet('{support.sentenze_brevi.clean}')
    WHERE classificazione_ricorso IS NOT NULL
    GROUP BY anno, codice_sede, classificazione_ricorso
)
SELECT
    p.anno,
    p.codice_sede,
    -- nome_sede preferito da definiti/sentenze_brevi (contratto con spazi);
    -- il raw dei pervenuti da OpenGA omette i separatori " - "
    COALESCE(d.nome_sede, s.nome_sede, p.nome_sede) AS nome_sede,
    p.classificazione_ricorso,
    p.pervenuti,
    COALESCE(d.definiti, 0) AS definiti,
    COALESCE(s.sentenze, 0) AS sentenze,
    COALESCE(s.sentenze_brevi, 0) AS sentenze_brevi,
    COALESCE(s.sentenze_piene, 0) AS sentenze_piene,
    COALESCE(d.accoglimenti, 0) AS accoglimenti,
    COALESCE(d.rigetti, 0) AS rigetti,
    ROUND(COALESCE(d.definiti, 0) * 100.0 / NULLIF(p.pervenuti, 0), 1) AS tasso_definizione,
    ROUND(COALESCE(d.accoglimenti, 0) * 100.0 / NULLIF(COALESCE(d.accoglimenti, 0) + COALESCE(d.rigetti, 0), 0), 1) AS tasso_accoglimento,
    ROUND(COALESCE(s.sentenze_brevi, 0) * 100.0 / NULLIF(COALESCE(s.sentenze, 0), 0), 1) AS quota_sentenze_brevi
FROM pervenuti_agg p
LEFT JOIN definiti_agg d
    ON p.anno = d.anno
    AND p.codice_sede = d.codice_sede
    AND p.classificazione_ricorso = d.classificazione_ricorso
LEFT JOIN sentenze_agg s
    ON p.anno = s.anno
    AND p.codice_sede = s.codice_sede
    AND p.classificazione_ricorso = s.classificazione_ricorso
ORDER BY p.anno, p.pervenuti DESC
