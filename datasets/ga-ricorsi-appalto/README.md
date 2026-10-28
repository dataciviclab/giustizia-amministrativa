# ga-ricorsi-appalto

Ricorsi pervenuti in materia d'appalto presso tutte le sedi della Giustizia Amministrativa — Consiglio di Stato, CGA Sicilia, 27 TAR e 2 TRGA. Integrati con dati ANAC (CIG).

**Fonte**: OpenGA (Giustizia Amministrativa) — `https://openga.giustizia-amministrativa.it`
**Protocollo**: CKAN (31 dataset)
**Frequenza**: mensile
**Licenza**: CC-BY 4.0

## Domanda

Quali sono i volumi e la distribuzione del contenzioso sugli appalti pubblici in Italia? Quali settori, territori e stazioni appaltanti sono più coinvolti?

## Dataset

24 colonne. Granularità: ricorso × CIG (un ricorso può avere più CIG). La chiave del ricorso è `numero_ricorso`. 100% dei record con `CODICE_CIG` — joinabile con dataset ANAC.

**Copertura**: 2023–2026 (4 anni), **31 sedi** unificate, aggiornamento mensile.

**Totale**: ~11.500 ricorsi appalto con CIG.

## Perché vale la pena

- **Tema civico**: il contenzioso sugli appalti pubblici è un indicatore di salute del sistema degli acquisti pubblici
- **31 sedi**: primo grado (TAR) e appello (CdS) nello stesso dataset
- **CODICE_CIG al 100%**: join diretto con ANAC bandi/aggiudicazioni
- **Collegabile**: via `numero_ricorso` a `ga_sentenze` per l'esito giudiziario

## Output minimo atteso

- `mart_ricorsi_sede_classificazione`: ricorsi e gare per anno/sede/classificazione
- `mart_ricorsi_territorio_settore`: ricorsi e gare per provincia/anno/settore

## Criterio di promozione

- Run completo su tutti gli anni (2023-2026) con validazioni green
- Mart popolati con dati coerenti anno su anno
- Note sui limiti del dataset documentate

## Stato

- intake
- **2026-07-21**: esteso da 1 a 31 sedi (PR #700)
- **2026-10-28**: **corretti gli importi** (`importo_complessivo_gara`, `importo_lotto`). Il clean usava `normalize_italian_number` su valori in **formato standard** (`84976869.76`): la macro rimuove i punti e moltiplicava il valore per 10ⁿ (×10..×10^10 — es. `84.976.869,76` pubblicato come `8.497.686.976`). Ora usa `cast_double`. Verificato cella per cella contro la fonte: 40.631 valori, 0 differenze.
