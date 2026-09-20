SELECT
    anno,
    SUM(totale_provvedimenti) AS totale_provvedimenti,
    SUM(provvedimenti_definiscono) AS provvedimenti_definiscono,
    SUM(provvedimenti_non_definiscono) AS provvedimenti_non_definiscono,
    ROUND(SUM(provvedimenti_definiscono) * 100.0 / NULLIF(SUM(totale_provvedimenti), 0), 1) AS definiscono_pct,
    SUM(totale_ricorsi) AS totale_ricorsi
FROM clean_input
GROUP BY anno
ORDER BY anno
