# ga-cross — Compose flusso GA (materia)

## Grano

`anno × codice_sede × classificazione_ricorso`

## Colonne clean

| Colonna | Note |
|---|---|
| `pervenuti` | flusso ingresso per materia/anno (da `ga_ricorsi_pervenuti_class`) |
| `definiti` | chiusure per materia/anno (da `ga_ricorsi_definiti`) |
| `sentenze` / `sentenze_brevi` / `sentenze_piene` | da `ga_sentenze_brevi` — **al grano materia** |
| `accoglimenti` / `rigetti` | esiti su definiti |
| `tasso_definizione` | `definiti / pervenuti` — vedi nota sotto |
| `tasso_accoglimento` | `accoglimenti / (accoglimenti + rigetti)` |
| `quota_sentenze_brevi` | % brevi sulle sentenze della stessa materia |

## Nota: `tasso_definizione` può superare il 100%

Non è un bug di calcolo:

- `pervenuti` è un **flusso** per anno di **deposito**
- `definiti` è un flusso per anno di **sentenza/chiusura**
- I definiti di un anno possono includere ricorsi depositati in anni precedenti (arretrato che si scioglie)

Quindi `definiti > pervenuti` su una materia/anno è lecito (circa il 20-38% delle righe nella serie 2017-2026). Per un tasso "di carico" usare sempre pervenuti e definiti dello stesso anno **con questa avvertenza**, oppure leggere il mix da `ga_definizioni`.

## nome_sede

Il clean preferisce il nome da `definiti`/`sentenze_brevi` (contratto con ` - `). Il raw OpenGA dei pervenuti omette i separatori; il fix a monte è in `datasets/ga-ricorsi-pervenuti-class/sql/clean.sql`.
