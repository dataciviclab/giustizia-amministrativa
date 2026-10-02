-- OpenGA emette NOME_SEDE per i pervenuti SENZA separatori
-- (es. "TAR LAZIOROMA" invece di "TAR LAZIO - ROMA").
-- Causa: fonte, non normalize_string. Il contratto del Lab è il nome
-- canonico con " - ", allineato a ga_ricorsi_definiti / ga_sentenze.
-- Fix: override per codice_sede (chiave stabile della sede).
WITH base AS (
    SELECT
        cast_bigint(floor(cast("ANNO_DEPOSITO" AS double) / 100)) AS anno,
        cast_bigint("ANNO_DEPOSITO") AS anno_mese,
        cast_bigint("CODICE_SEDE") AS codice_sede,
        normalize_string("NOME_SEDE") AS nome_sede_raw,
        normalize_string("CLASSIFICAZIONE_RICORSO") AS classificazione_ricorso,
        cast_bigint("NUMERO_RICORSI_PERVENUTI") AS numero_ricorsi
    FROM raw_input
),
sedi AS (
    SELECT * FROM (VALUES
        (1,  'TAR LAZIO - LATINA'),
        (2,  'CdS GIURISDIZIONALE - ROMA'),
        (3,  'TAR LAZIO - ROMA'),
        (4,  'TAR ABRUZZO - L''AQUILA'),
        (5,  'TAR ABRUZZO - PESCARA'),
        (6,  'TAR TRENTINO ALTO ADIGE - BOLZANO'),
        (7,  'TAR BASILICATA - POTENZA'),
        (8,  'TAR CALABRIA - CATANZARO'),
        (9,  'TAR CALABRIA - REGGIO CALABRIA'),
        (10, 'TAR CAMPANIA - NAPOLI'),
        (11, 'TAR CAMPANIA - SALERNO'),
        (12, 'TAR EMILIA-ROMAGNA - BOLOGNA'),
        (13, 'TAR EMILIA-ROMAGNA - PARMA'),
        (14, 'TAR FRIULI VENEZIA GIULIA - TRIESTE'),
        (15, 'TAR LIGURIA - GENOVA'),
        (16, 'TAR LOMBARDIA - MILANO'),
        (17, 'TAR LOMBARDIA - BRESCIA'),
        (18, 'TAR MARCHE - ANCONA'),
        (19, 'TAR MOLISE - CAMPOBASSO'),
        (20, 'TAR PIEMONTE - TORINO'),
        (21, 'TAR PUGLIA - BARI'),
        (22, 'TAR PUGLIA - LECCE'),
        (23, 'TAR SARDEGNA - CAGLIARI'),
        (24, 'TAR SICILIA - PALERMO'),
        (25, 'TAR SICILIA - CATANIA'),
        (26, 'TAR TOSCANA - FIRENZE'),
        (27, 'TAR TRENTINO ALTO ADIGE - TRENTO'),
        (28, 'TAR UMBRIA - PERUGIA'),
        (29, 'TAR VALLE D''AOSTA - AOSTA'),
        (30, 'TAR VENETO - VENEZIA'),
        (31, 'CdS CONSULTIVE - ROMA'),
        (32, 'CGA GIURISDIZIONALE - PALERMO'),
        (33, 'CGA CONSULTIVE - PALERMO')
    ) AS t(codice_sede, nome_sede_canonico)
)
SELECT
    b.anno,
    b.anno_mese,
    b.codice_sede,
    COALESCE(s.nome_sede_canonico, b.nome_sede_raw) AS nome_sede,
    b.classificazione_ricorso,
    b.numero_ricorsi
FROM base b
LEFT JOIN sedi s
    ON b.codice_sede = s.codice_sede
WHERE b.anno IS NOT NULL
