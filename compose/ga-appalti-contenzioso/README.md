# ga-appalti-contenzioso — Compose: ricorsi appalti ↔ atti che li decidono

## Grano

`codice_sede × numero_ricorso` (un ricorso in materia di appalti).

Unisce:

| Ruolo | Fonte | Contenuto |
|---|---|---|
| ricorsi (raw) | `openga_ricorsi_appalto` | CIG, importo gara/lotti, settore, provincia, stazione appaltante |
| decisioni (support) | `ga_sentenze`, `ga_decreti`, `ga_ordinanze` | atti pubblicati sul ricorso |

## Perché esiste

`openga_ricorsi_appalto` porta il contesto di gara ma non l'esito;
`sentenze`/`decreti`/`ordinanze` portano la decisione ma non sanno nulla della
gara. Il ponte è `(codice_sede, numero_ricorso)` — il numero ricorso **non** è
unico tra sedi (38% di duplicati usato da solo).

Copertura verificata: **26.344 ricorsi su 29.029 (90,8%)** hanno almeno un atto
a valle; 2.685 sono senza decisione pubblicata alla data del run.

## Collegamenti

| Join | Chiave | Nota |
|---|---|---|
| ricorsi ↔ atti | `codice_sede, numero_ricorso` | 90,8% coperto |
| ricorsi ↔ ANAC | `codice_cig` / `cf_amministrazione_appaltante` | 21.560 CIG, 2.955 SA (cross-repo, non in questo compose) |

## Aggregazioni

Lo stesso ricorso può comparire su più righe in `openga_ricorsi_appalto`
(più gare/CIG impugnati: fino a 127 righe). Il clean aggrega al ricorso:

- `n_cig` / `n_gare` — quante gare distinte impugna il ricorso
- `importo_gara` = **MAX** di `importo_complessivo_gara` (non somma: il valore è
  ripetuto su ogni lotto)
- `n_lotti` / `importo_lotti` — dettaglio lotti
- `esito_decisione`: `ACCOGLIE` se almeno un atto accoglie, poi `RESPINGE`,
  altrimenti `ALTRO`; `SENZA DECISIONE` senza atti
- `durata_giorni`: prima decisione che definisce − deposito del ricorso
  (NULL se negativa: poche date incoerenti di fonte)

## Mart

| Tabella | Grano | Contenuto |
|---|---|---|
| `mart_esiti_settore` | anno × settore | ricorsi, copertura decisioni, tassi, durata mediana, importo mediano |
| `mart_esiti_provincia` | provincia | stessa lettura territoriale |

## Segnale (serie 2017-2026)

- durata mediana dei ricorsi appalti: **144 giorni** (contro 234-381 delle
  sentenze GA in generale): il rito appalti è molto più rapido
- tasso di accoglimento sui decisi: ~30% (2025: 31,3% settori ordinari,
  26,1% settori speciali)
- copertura decisioni ~92% negli anni pieni, più bassa sugli anni recenti
  (atti non ancora pubblicati)

Limite di fonte: `provincia` e `settore` mancano per molti ricorsi
(18.364 su 29.029 senza provincia) → riga `NON DISPONIBILE` nei mart.

## Esecuzione

```bash
toolkit run --config datasets/openga-ricorsi-appalto/dataset.yml
toolkit run --config datasets/ga-sentenze/dataset.yml
toolkit run --config datasets/ga-decreti/dataset.yml
toolkit run --config datasets/ga-ordinanze/dataset.yml

toolkit run --config compose/ga-appalti-contenzioso/dataset.yml
```
