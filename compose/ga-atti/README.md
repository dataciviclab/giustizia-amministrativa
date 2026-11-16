# ga-atti — Compose: un provvedimento per riga, con durata

## Grano

`anno × codice_sede × numero_provvedimento` (atto pubblicato).

Unisce i quattro dataset atti, che hanno schema identico:

| `tipo_atto` | Dataset | Righe 2017-2026 |
|---|---|---|
| `sentenza` | `ga_sentenze` | 501.531 |
| `ordinanza` | `ga_ordinanze` | 301.580 |
| `decreto` | `ga_decreti` | 273.418 |
| `parere` | `ga_pareri` (solo CdS + CGA consultive) | 22.993 |

## Perché esiste

Prima ogni dataset atto aveva gli stessi due mart (`mart_esiti_per_sede`,
`mart_esiti_per_tipo`): 8 tabelle con lo stesso SQL copiato, e nessun posto
dove confrontare le famiglie di provvedimento o misurare la durata. Questo
compose sostituisce quella duplicazione e aggiunge la durata, che nel repo
del civile esisteva (`durata_civile`) e qui mancava.

## `durata_giorni`

`data_pubblicazione − data_deposito_ricorso`, calcolata **solo** per gli atti
che definiscono il ricorso (`flg_definisce = 'D'`) e solo con date coerenti.
Le poche righe con date invertite restano NULL (144 ordinanze e 2.410 decreti
sul totale 2017-2026) invece di produrre durate negative.

Attenzione: non è la durata "netta" (non sconta sospensioni, rinvii, mutamenti
di rito). È il tempo trascorso dal deposito alla pubblicazione dell'atto che
chiude il ricorso — la stessa logica dei cruscotti di settore.

## Mart

| Tabella | Grano | Contenuto |
|---|---|---|
| `mart_durata_sede` | anno × sede × tipo_atto | ricorsi definiti, durata mediana / p90 / media |
| `mart_durata_anno` | anno × tipo_atto | trend nazionale, p75 e p90 |
| `mart_esiti_per_tipo_atto` | anno × tipo_atto × esito | volumi per esito e quanti definiscono |

Un ricorso definito da più atti conta una volta (MIN della durata per ricorso).

## Qualità del dato (verificata sul run 2026)

| Controllo | Esito |
|---|---|
| righe per `tipo_atto` vs dataset sorgente | identiche, nessun doppio conteggio |
| coerenza `tipo_atto` × `tipo_provvedimento` | pulita (sentenza↔SENTENZA/BREVE, decreto↔DECRETO *, ordinanza↔ORDINANZA *) |
| copertura `durata_giorni` | sentenze 99,0%, pareri 80,4%, decreti 62,7%, ordinanze 6,0% (solo gli atti che definiscono) |
| date di deposito placeholder (01-01) | 135 righe su 704.663 con durata (0,02%) — non spostano le mediane |
| durate estreme | legittime: ricorsi depositati 1979-1999 ancora definiti (`numero_ricorso` codifica l'anno di deposito). 42.119 atti oltre 10 anni, 2.802 oltre 20 |
| durata 0 giorni | 131 atti con pubblicazione = deposito |

**2026 è parziale**: contiene solo gli atti pubblicati fino al run, quindi
favorisce i ricorsi decisi in fretta e la mediana dell'anno è sottostimata.
Non usarlo per confronti di serie.

## Segnale che abilita (2017 → 2025, sentenze)

| anno | ricorsi definiti | durata mediana | p90 |
|---|---|---|---|
| 2017 | 42.978 | 381 gg | 2.541 gg |
| 2021 | 49.913 | 362 gg | 2.379 gg |
| 2025 | 59.552 | **243 gg** | **1.196 gg** |

I decreti restano su orizzonti molto più lunghi (2.918 gg di mediana nel 2017,
882 nel 2025): sono in larga parte definizioni di ricorsi depositati anni prima.

## Esecuzione

```bash
# prima i dataset atti
toolkit run --config datasets/ga-sentenze/dataset.yml
toolkit run --config datasets/ga-ordinanze/dataset.yml
toolkit run --config datasets/ga-decreti/dataset.yml
toolkit run --config datasets/ga-pareri/dataset.yml

toolkit run --config compose/ga-atti/dataset.yml
```
