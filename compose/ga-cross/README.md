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

Il clean preferisce il nome da `pervenuti` (e in fallback `definiti`/`sentenze_brevi`, contratto con ` - `). Il raw OpenGA dei pervenuti omette i separatori; il fix a monte è in `datasets/ga-ricorsi-pervenuti-class/sql/clean.sql`.

## mart_sede_stock — flusso × stock

Affianca ai flussi per sede/anno il **pendente medio dichiarato**
(`ga-ricorsi-pendenti`, support). Colonne chiave:

- `pendenti_media` / `pendenti_min` / `pendenti_max` — stock mensile
  aggregato a livello annuo (NULL dove la fonte non copre l'anno)
- `pendenti_n_mesi` — mesi disponibili: 2020 e 2026 parziali; **2017-2019
  e 2024 assenti** (gap di pubblicazione OpenGA)
- `definisci_su_pendente` — `definiti / pendenti_media`: ~1 significa che
  gli anni di definizione assorbono l'arretrato alla velocita' con cui si
  forma; > 1 = burn-down attivo

## FULL JOIN: righe non appaiate preservate

Definiti e sentenze sono joinati a FULL (non LEFT): le righe la cui combinazione
(anno × sede × classificazione) non trova match nei pervenuti **restano nel
clean** con `pervenuti = 0` e `tasso_definizione = NULL`. Senza questa scelta,
lo scarto di appaiamento (tassonomia OpenGA divergente tra file — da ~900 a
~1200 classificazioni dal 2022) sottostimava i totali nazionali fino al −33%
sui definiti nel 2022. Le somme per sede/materia nei mart sono quindi su
tutte le righe; `tasso_definizione` va letto con prudenza sulle righe a
`pervenuti = 0` (definizioni di ricorsi depositati in anni/classificazioni
precedenti).
