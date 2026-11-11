## Tecnico

- 31 source `ckan` (`download_all: true`), una per sede
- Ogni source scarica i CSV diretti (`prefer_datastore: false`), schema identico per tutte le 31 sedi
- Clean.sql: `clean.read.mode: all` + `union_by_name=true`, macro standard (`cast_bigint`, `normalize_string`, `cast_double`)
- TAR Valle d'Aosta: solo 2024-2026 (9 risorse vs 12 delle altre sedi)
- Frequenza mensile: i dati vengono aggiornati ogni mese dalla fonte
- Granularità: singolo ricorso (record-level)

## Analitico

- Colonna `ANNO_DEPOSITO_RICORSO`: anno effettivo di deposito (non coincide necessariamente con l'anno file)
- `IMPORTO_COMPLESSIVO_GARA` e `IMPORTO_LOTTO`: formato italiano (punto migliaia, virgola decimale) — gestito da `normalize_italian_number`
- `CLASSIFICAZIONE_RICORSO`: tassonomia che include "APPALTI SANITÀ", "PIANO NAZIONALE DI RIPRESA E RESILIENZA (PNRR)", "APPALTI PUBBLICI DI SERVIZI/LAVORI", ecc.
- `CODICE_CIG`: presente per tutti i record (100% copertura), permette join con dataset ANAC
- **Dettagli ANAC quasi sempre null**: `CF_AMMINISTRAZIONE_APPALTANTE`, `DENOMINAZIONE_AMMINISTRAZIONE_APPALTANTE`, `IMPORTO_COMPLESSIVO_GARA`, `PROVINCIA`, `LUOGO_ISTAT` sono popolati solo per una frazione trascurabile dei record. OpenGA pubblica il ricorso e il CIG ma non ha ancora integrato i dettagli ANAC completi.
- **Importi**: quando presenti, `IMPORTO_COMPLESSIVO_GARA` è l'importo totale della gara, non del singolo lotto. Per somme aggregate va deduplicato per `numero_gara`.
- **2023**: solo 182 ricorsi (dato parziale, back-fill al momento del lancio del portale a dicembre 2024)

## Cautele

- I dettagli economici/geografici sono quasi sempre null — il dataset dà il CIG e la classificazione, ma per importi/enti/territorio serve join con ANAC
- La serie storica 2023 è parziale (182 ricorsi), non confrontabile con gli anni successivi
- `DATA_SCADENZA_OFFERTA` e `DATA_PUBBLICAZIONE` talvolta vuote
- L'`ANNO_DEPOSITO_RICORSO` nei file recenti può includere ricorsi depositati in anni precedenti
- PK non dichiarabile: stessi `(sede, numero_ricorso)` possono avere CIG diversi (un ricorso può riguardare più gare/lotti)
