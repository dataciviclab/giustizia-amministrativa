# ga-definizioni — Compose: come si definiscono i ricorsi

Compose complementare a `ga_cross`.

| Compose | Grano | Domanda |
|---|---|---|
| `ga_cross` | sede × **classificazione** × anno | Flusso pervenuti→definiti→esito + mix brevi per materia |
| **`ga_definizioni`** | sede × anno | **Come** si chiude: sentenza vs decreto decisori vs altri, con contesto esiti e mix brevi |

## Fonti

| Ruolo | Dataset |
|---|---|
| raw (primary) | `ga_ricorsi_tipo_decisione` |
| support | `ga_ricorsi_definiti` (esiti) |
| support | `ga_sentenze_brevi` (mix breve/pieno per sede) |

## Mart

| Tabella | Contenuto |
|---|---|
| `mart_mezzi_anno` | Trend nazionale: % sentenza / decreto / altri + quota brevi |
| `mart_sintesi_sede` | Una riga per sede×anno con mix e contesto |
| `mart_outlier_sedi` | Sedi con mix anomalo vs media nazionale (delta%) |

## `rd_definiti` — solo esiti definitori

Il contesto esiti arriva da `ga_ricorsi_definiti`, la cui fonte conta i ricorsi
**per esito registrato**: `rd_definiti` somma solo gli esiti definitori della
codelist `datasets/ga-ricorsi-definiti/data/esiti_codelist.csv` (stessa regola
di `ga_cross`). Il volume escluso resta in `rd_esiti_interlocutori`.

Prima di questo filtro `rd_definiti` stava ~+15% (2017) → +32% (2026) sopra
`totale_definiti` dello stesso compose, pubblicando due misure incompatibili
dello stesso concetto.

## Perché non sta in ga_cross

`ga_ricorsi_tipo_decisione` non ha `classificazione_ricorso`. Forzarlo nel cross significherebbe broadcast per materia — lo stesso errore che correggeva `ga_cross` sulle sentenze.

## Esecuzione

```bash
# Prima i dataset singoli (tipo-decisione, definiti, sentenze-brevi)
toolkit run --config datasets/ga-ricorsi-tipo-decisione/dataset.yml
toolkit run --config datasets/ga-ricorsi-definiti/dataset.yml
toolkit run --config datasets/ga-sentenze-brevi/dataset.yml

# Poi il compose
toolkit run --config compose/ga-definizioni/dataset.yml
# oppure
make compose
```
