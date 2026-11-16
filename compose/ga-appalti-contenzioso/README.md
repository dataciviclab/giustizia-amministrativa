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

Copertura verificata: **26.344 ricorsi su 29.029 (90,8%)** hanno almeno un
provvedimento pubblicato, ma solo **23.706 (81,7%) hanno un atto che definisce
il ricorso** (`flg_definisce = 'D'`). I 2.638 con sole ordinanze interlocutorie
non sono decisi: `ha_decisione`, `esito_decisione` e `durata_giorni` usano solo
i definitori.

## Collegamenti

| Join | Chiave | Nota |
|---|---|---|
| ricorsi ↔ atti | `codice_sede, numero_ricorso` | 90,8% con un atto, 81,7% con una decisione |
| ricorsi ↔ ANAC | `codice_cig` / `cf_amministrazione_appaltante` | 21.560 CIG, 2.955 SA (cross-repo, non in questo compose) |

## Aggregazioni

Lo stesso ricorso può comparire su più righe in `openga_ricorsi_appalto`
(più gare/CIG impugnati: fino a 127 righe). Il clean aggrega al ricorso:

- `n_cig` / `n_gare` — quante gare distinte impugna il ricorso
- `importo_gara` = **MAX** di `importo_complessivo_gara` (non somma: il valore è
  ripetuto su ogni lotto)
- `n_lotti` / `importo_lotti` — dettaglio lotti
- `n_atti` / `n_atti_definitori` — provvedimenti pubblicati vs atti che chiudono
- `ha_decisione` — vero solo se esiste almeno un atto definitorio
- `esito_decisione` — calcolato **sui soli definitori**: `ACCOGLIE` se almeno
  uno accoglie, poi `RESPINGE`, altrimenti `ALTRO` (esiti non di merito);
  `SENZA DECISIONE` senza atti definitori
- `durata_giorni`: prima decisione che definisce − deposito del ricorso
  (NULL se negativa: poche date incoerenti di fonte)
- `settore` / `provincia` / stazione appaltante: valore di fonte, `MULTIPLO` se
  il ricorso impugna gare con attributi diversi (75 ricorsi), `NON DISPONIBILE`
  se assenti — niente `any_value`, che non è riproducibile

## Mart

| Tabella | Grano | Contenuto |
|---|---|---|
| `mart_esiti_settore` | anno × settore | ricorsi, copertura decisioni, tassi, durata mediana, importo mediano |
| `mart_esiti_provincia` | provincia | stessa lettura territoriale |

## Segnale (serie 2017-2026)

- durata mediana dei ricorsi appalti: **144 giorni** (contro 234-381 delle
  sentenze GA in generale): il rito appalti è molto più rapido
- tasso di accoglimento sui decisi di merito: **~31%** (2025: 30,7% settori
  ordinari, 23,0% settori speciali)
- copertura decisioni (atti definitori): 82-91% negli anni pieni, **35,8% nel 2026**

Limite di fonte: `provincia` e `settore` mancano per molti ricorsi e la
copertura **cresce nel tempo**: settore 21,8% (2018) → 93,9% (2025), provincia
10,1% → 81,1%. I `tasso_*` per settore dei primi anni sono calcolati su un
quinto dei ricorsi: non sono una serie comparabile, servono come ordine di
grandezza. Riempimenti: riga `NON DISPONIBILE`, `MULTIPLO` quando il ricorso
impugna gare con attributi diversi.

## Qualità del dato (verificata sul run 2026)

| Controllo | Esito |
|---|---|
| copertura decisioni per anno (atti definitori) | 84,4% (2018) → 82,6% (2025); **35,8% sul 2026** (atti non ancora pubblicati); 2017 praticamente vuoto (1 ricorso) |
| ricorsi con soli atti interlocutori | 2.638: restano `SENZA DECISIONE`, prima contavano come decisi |
| composizione esiti (2025) | ACCOGLIE 12,9%, RESPINGE 30,5%, ALTRO 39,2% (inammissibile, improcedibile, perenzione), SENZA DECISIONE 17,4% |
| tasso di accoglimento | calcolato su accoglie/(accoglie+respinge), non sul totale |
| settore disponibile | 57% dei ricorsi sull'intera serie (SETTORI ORDINARI 15.236, SPECIALI 1.522) |
| importo gara | p50 6,0 mln, p99 1,6 mld, max 14,7 mld: **non validati**, ci sono outlier di fonte. Usare mediane, non medie |
| ricorsi multi-gara | 27.283 con 1 CIG, 1.744 con più CIG (max 127 righe per un ricorso), 75 con provincia multipla |
| coerenza `ha_decisione` ↔ `durata_giorni` | 1 solo caso discordante (data di fonte invertita) |

Le due nozioni di "definitorio" (atto `flg_definisce='D'` vs codelist esiti del
dataset `ga-ricorsi-definiti`) sono spiegate in `compose/ga-atti/README.md`:
qui si usa il flag di atto.

**2017 e 2026 non sono anni pieni**: il primo è il primo anno della fonte, il
secondo è in corso. Per i trend usare 2018-2025.

## Esecuzione

```bash
toolkit run --config datasets/openga-ricorsi-appalto/dataset.yml
toolkit run --config datasets/ga-sentenze/dataset.yml
toolkit run --config datasets/ga-decreti/dataset.yml
toolkit run --config datasets/ga-ordinanze/dataset.yml

toolkit run --config compose/ga-appalti-contenzioso/dataset.yml
```
