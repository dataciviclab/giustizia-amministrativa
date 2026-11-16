# ga-cross — Compose flusso GA (materia)

## Grano

`anno × codice_sede × classificazione_ricorso`

## Colonne clean

| Colonna | Note |
|---|---|
| `pervenuti` | flusso ingresso per materia/anno (da `ga_ricorsi_pervenuti_class`) |
| `tipo_sede` | `giurisdizionale` / `consultivo` (sedi 31 e 33 = CdS/CGA CONSULTIVE: pareri, non ricorsi) |
| `definiti` | chiusure per materia/anno, **solo esiti definitori** (da `ga_ricorsi_definiti`) |
| `esiti_interlocutori` | volume di provvedimenti interlocutori escluso da `definiti` (non sono ricorsi distinti) |
| `sentenze` / `sentenze_brevi` / `sentenze_piene` | da `ga_sentenze_brevi` — **al grano materia** |
| `accoglimenti` / `rigetti` | esiti su definiti |
| `tasso_definizione` | `definiti / pervenuti` — vedi nota sotto |
| `tasso_accoglimento` | `accoglimenti / (accoglimenti + rigetti)` |
| `quota_sentenze_brevi` | % brevi sulle sentenze della stessa materia |

## Nota: `definiti` conta solo esiti definitori

La fonte OpenGA (`ricorsi-definiti-per-classificazione-ed-esito`) ha grano
`anno × mese × sede × classificazione × esito`: lo stesso ricorso compare una
volta per ogni esito ricevuto. Gli esiti interlocutori (riunione, rinvio,
nomina commissario ad acta, misura cautelare, compenso difensore, …) vanno
esclusi, altrimenti il totale cresce a ogni passaggio procedurale.

La classificazione vive in `datasets/ga-ricorsi-definiti/data/esiti_codelist.csv`
(colonna `esito_definitorio`) ed è la stessa usata da `ga_definizioni`.

Effetto sui totali nazionali (`mart_panoramica.totale_definiti`), prima → dopo:

| anno | somma grezza | definitori | tema ufficiale | scarto prima | scarto dopo |
|---|---|---|---|---|---|
| 2017 | 98.858 | 89.314 | 85.979 | +15,0% | +3,9% |
| 2022 | 92.590 | 81.818 | 76.943 | +20,3% | +6,3% |
| 2025 | 96.300 | 76.947 | 73.064 | +31,8% | +5,3% |

Resta uno scarto positivo del 4-8% rispetto al tema ufficiale
`ricorsi-definiti-per-tipo-di-decisione`: la fonte conta comunque per
(classificazione × esito), quindi un ricorso riclassificato su piu' materie
resta contato piu' volte. Per il **livello** nazionale usare
`ga_definizioni.totale_definiti`; `ga_cross.definiti` serve per la
**distribuzione** per materia.

## Nota: `tasso_definizione` può superare il 100%

Non è un bug di calcolo:

- `pervenuti` è un **flusso** per anno di **deposito**
- `definiti` è un flusso per anno di **sentenza/chiusura**
- I definiti di un anno possono includere ricorsi depositati in anni precedenti (arretrato che si scioglie)

Quindi `definiti > pervenuti` su una materia/anno è lecito (circa il 20-38% delle righe nella serie 2017-2026). Per un tasso "di carico" usare sempre pervenuti e definiti dello stesso anno **con questa avvertenza**, oppure leggere il mix da `ga_definizioni`.

Dopo il fix sugli esiti interlocutori il tasso nazionale annuo scende in
98-145% (era 122-160% col numeratore gonfiato): il residuo sopra il 100% è
solo l'effetto coorte descritto qui — nel 2025 è 98%.

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

## mart_panoramica_tipo_sede — giurisdizionale vs consultivo

Le sedi 31 (CdS CONSULTIVE) e 33 (CGA CONSULTIVE) esprimono **pareri**, non
ricorsi: valgono il 2-4% dei pervenuti annui e nei totali nazionali di
`mart_panoramica` sono indistinguibili. Il mart per `tipo_sede` li separa
(spacca: stesso anno, tassi molto diversi — nel 2025 accoglimento 60,0%
giurisdizionale contro 23,6% consultivo).

Il flag arriva dalla codelist sedi
(`datasets/ga-ricorsi-pervenuti-class/data/sedi_canonici.csv`, colonna
`tipo_sede`), esposta in questo compose come support `file` e non come path
hardcoded nel SQL.

## Deriva tassonomia materia (2022)

`classificazione_ricorso` non è stabile: ~1.000 valori fino al 2021, 1.329 nel
2022. Il FULL JOIN tiene i totali, ma il match ponderato dei definiti scende
al **66,5%** nel 2022 (90-95% negli altri anni) e le materie cambiano nome.
Esempio: le classificazioni `APPALTI PUBBLICI ...` si azzerano dal 2022 mentre
i ricorsi appalti restano ~3.000/anno — per quel dominio usare
`compose/ga-appalti-contenzioso`. Dettaglio e numeri in
`datasets/ga-ricorsi-pervenuti-class/notes.md`.

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
