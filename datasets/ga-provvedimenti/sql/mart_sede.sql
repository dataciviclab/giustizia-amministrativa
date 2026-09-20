SELECT
    anno,
    codice_sede,
    nome_sede,
    SUM(totale_provvedimenti) AS totale_provvedimenti,
    SUM(provvedimenti_definiscono) AS provvedimenti_definiscono,
    SUM(provvedimenti_non_definiscono) AS provvedimenti_non_definiscono,
    SUM(totale_ricorsi) AS totale_ricorsi
FROM clean_input
GROUP BY anno, codice_sede, nome_sede
ORDER BY anno, totale_provvedimenti DESC
