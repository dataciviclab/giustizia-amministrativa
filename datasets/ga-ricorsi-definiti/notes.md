# ga-ricorsi-definiti — Note tecniche

## `esito_definitorio`: la fonte conta per esito, non per ricorso

OpenGA pubblica `{sede}-ricorsi-definiti-per-classificazione-ed-esito` con grano

```
ANNO_SENTENZA × MESE_SENTENZA × CODICE_SEDE × CLASSIFICAZIONE_RICORSO × ESITO_PROVVEDIMENTO
```

Un ricorso che riceve un esito interlocutorio (riunione, rinvio, nomina
commissario ad acta, misura cautelare, compenso difensore, …) e poi una
sentenza compare in **piu' righe**. Sommare `numero_ricorsi_definiti` senza
filtro non da' i ricorsi distinti definiti: il totale eccede il tema ufficiale
`ricorsi-definiti-per-tipo-di-decisione` di +15% nel 2017 e +32% nel 2026,
con bias crescente perché gli interlocutori crescono (8.570 → 19.353 tra 2017
e 2025).

## Codelist

- File: `data/esiti_codelist.csv` — `esito_provvedimento, definitorio, motivo`
- 130 esiti osservati sul portale (2017-2026, 33 sedi), 42 interlocutori
- Il clean espone `esito_definitorio` (BOOLEAN) via `LEFT JOIN` sulla codelist
- Join canonicalizzato: le doppie virgolette dei refusi di fonte
  (`DICHIARA L''INCOMPETENZA …`) sono collassate solo per il match; il valore
  pubblicato in `esito_provvedimento` resta quello di fonte
- Esito non mappato ⇒ `esito_definitorio = FALSE` (fail-closed). Il test
  `tests/test_esiti_codelist_contract.py` fallisce finche' non entra in codelist

## Regola di lettura

| Domanda | Colonna |
|---|---|
| Quanti ricorsi si sono definiti? | `totale_definiti` di `ga_ricorsi_tipo_decisione` / `ga_definizioni` |
| Come si distribuiscono per materia? | `definiti` di `ga_cross` (solo definitori) |
| Quanto volume procedurale c'e' attorno? | `esiti_interlocutori` |

Residuo noto: `ga_cross.definiti` resta +4-8% sopra il tema ufficiale, perché
la fonte conta comunque per (classificazione × esito) e un ricorso
riclassificato su piu' materie viene contato piu' volte.

## Run

```bash
toolkit run clean --config datasets/ga-ricorsi-definiti/dataset.yml
toolkit run mart  --config datasets/ga-ricorsi-definiti/dataset.yml
# poi i compose che lo usano come support
make compose
```
