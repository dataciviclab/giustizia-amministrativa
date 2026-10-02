-- Sintesi per sede×anno: mezzi di definizione + contesto esiti e brevi
SELECT
    anno,
    codice_sede,
    nome_sede,
    definiti_sentenza_breve,
    definiti_decreto_decisori,
    definiti_altri,
    totale_definiti,
    sentenza_pct,
    decreto_pct,
    altri_pct,
    rd_definiti,
    rd_accoglimenti,
    rd_rigetti,
    tasso_accoglimento,
    sb_sentenze_brevi,
    sb_sentenze_piene,
    sb_sentenze,
    quota_brevi_pct
FROM clean_input
ORDER BY anno, totale_definiti DESC
