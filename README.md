# Giustizia Amministrativa — OpenGA

**Contenzioso, sentenze e provvedimenti della Giustizia Amministrativa italiana — 31 sedi, 2017-2026.**

Sistema di intelligence sulla giustizia amministrativa: raccoglie i dati ufficiali dal portale [OpenGA](https://openga.giustizia-amministrativa.it), li trasforma in mart analitici e li rende interrogabili via dashboard Streamlit.

- **Fonte**: [OpenGA - Giustizia Amministrativa](https://openga.giustizia-amministrativa.it)
- **Copertura**: 2017-2026, Italia (31 sedi: CdS, CGA Sicilia, 27 TAR, 2 TRGA)
- **Unità di analisi**: Ricorso, Sentenza, Decreto, Ordinanza
- **Licenza**: CC BY 4.0
- **Output pubblico**: Dashboard Streamlit + Discussion

## Cosa risponde

1. **Quanti ricorsi arrivano e come variano nel tempo?** → trend pervenuti per sede/materia 2017-2026
2. **Come si chiudono i ricorsi?** → esiti (accoglimento/rigetto) per sede/materia
3. **Con quale meccanismo si definiscono?** → sentenza vs decreto decisori vs altri (`ga-ricorsi-tipo-decisione`, compose `ga-definizioni`)
4. **Quante sentenze brevi vs piene?** → mix per materia e sede (`ga-sentenze-brevi`)
5. **Quali materie hanno più contenzioso?** → classificazioni per volume e tasso di accoglimento
6. **Quanto è produttiva ogni sede?** → provvedimenti che definiscono vs non definiscono
7. **Qual è il backlog di ricorsi pendenti?** → stock mensile per tutte le sedi (`ga-ricorsi-pendenti`; legacy CdS-only: `openga-ricorsi-cds`)
8. **Com'è composto il contenzioso sugli appalti?** → ricorsi appalto con CIG (joinabile con ANAC)
9. **Quanto tempo impiegano le sezioni consultive?** → pareri CdS/CGA con lag deposito→pubblicazione (`ga-pareri`)

## Dataset

| Dataset | Cosa contiene | Anni | Mart |
|---|---|---|---|
| `ga-sentenze` | Sentenze di tutti i giudici amministrativi | 2017-2026 | 2 |
| `ga-decreti` | Decreti di tutti i giudici amministrativi | 2017-2026 | 2 |
| `ga-ordinanze` | Ordinanze di tutti i giudici amministrativi | 2017-2026 | 2 |
| `ga-ricorsi-definiti` | Ricorsi chiusi con esito per materia | 2017-2026 | 2 |
| `ga-ricorsi-pervenuti-class` | Ricorsi in ingresso per materia | 2017-2026 | 2 |
| `ga-provvedimenti` | Provvedimenti pubblicati per sede | 2017-2026 | 2 |
| `ga-ricorsi-appalto` | Ricorsi in materia d'appalto (con CIG) | 2017-2026 | 2 |
| `ga-pareri` | Pareri sezioni consultive (CdS + CGA) | 2017-2026 | 2 |
| `ga-sentenze-brevi` | Sentenze brevi vs piene per materia | 2017-2026 | 2 |
| `ga-ricorsi-tipo-decisione` | Definizioni per meccanismo (sentenza/decreto/altro) | 2017-2026 | 2 |
| `openga-ricorsi-cds` | Ricorsi pendenti CdS (stock mensile, slug `openga_ricorsi_cds`) — legacy, superseded da `ga-ricorsi-pendenti` | 2023-2026 | 1 |
| `ga-ricorsi-pendenti` | Stock mensile pendenti per tutte le 33 sedi | 2020-2026* | 2 |
| `compose/ga-cross` | Compose: flusso pervenuti → definiti → esito + mix brevi + stock pendenti (grano materia/flusso) | 2017-2026 | 4 |
| `compose/ga-definizioni` | Compose: mezzi di definizione per sede×anno | 2017-2026 | 3 |

\* Copertura reale della fonte OpenGA: 2020-2023 + 2025-2026 (2024 assente, gap di pubblicazione).

### Mart analitici

**Per dataset**: 2 mart cadauno (per sede + per tipo/classificazione)

**Compose**: `ga_cross` (panoramica, flusso sede, esiti+materia, **stock pendente per sede**) · `ga_definizioni` (mezzi anno, sintesi sede, outlier)

## Dashboard

Dashboard Streamlit multi-pagina (`dashboard/`), pronta a leggere i clean/mart del repo:

| Livello | Pagina | Contenuto |
|---|---|---|
| **Monitoraggio** | Panoramica | Trend nazionale, volumi, tasso definizione, quota brevi |
| **Intelligence** | Esiti | Tasso accoglimento per materia e sede, quota sentenze brevi |
| | Mezzi di Definizione | Sentenza vs decreto decisori vs altri (compose `ga_definizioni`) |
| | Appalti | Contenzioso sugli appalti (CIG) |
| **Esplorazione** | Scheda Sede | Profilo completo di ogni sede |
| | Query SQL | Query libera sui dataset del registry |

> Dataset `ga_pareri` e `ga_sentenze_brevi` sono interrogabili via Query SQL; le pagine analitiche usano i compose (`ga_cross`, `ga_definizioni`) che li aggregano.

## Come si usa

```bash
# Setup (pyproject — vedi ADR-001 §8)
pip install -e ".[dev]"

# Validare config
make check

# Eseguire tutti i pipeline (include script download)
make run

# Eseguire compose (dopo i singoli)
make compose

# Eseguire tutto
make run-all

# Dashboard
cd dashboard && streamlit run app.py

# Contract test (richiede out/ già runnato)
python -m pytest tests/ -q
```

## Struttura

```
giustizia-amministrativa/
├── datasets/                   # toolkit pipeline
│   ├── ga-sentenze/
│   ├── ga-decreti/
│   ├── ga-ordinanze/
│   ├── ga-ricorsi-definiti/
│   ├── ga-ricorsi-pervenuti-class/
│   ├── ga-provvedimenti/
│   ├── ga-ricorsi-appalto/     # slug: openga_ricorsi_appalto
│   ├── ga-pareri/
│   ├── ga-sentenze-brevi/
│   ├── ga-ricorsi-tipo-decisione/
│   ├── ga-ricorsi-pendenti/
│   └── openga-ricorsi-cds/     # pendenti CdS (stock mensile)
├── compose/
│   ├── ga-cross/              # flusso pervenuti→definiti + mix brevi (materia)
│   └── ga-definizioni/        # mezzi di definizione per sede×anno
├── dashboard/                  # Streamlit multi-pagina
├── out/                        # output pipeline (raw/clean/mart)
├── registry/                   # artifact catalog
├── tests/                      # contract test
├── prefetch.py                 # script download CKAN
└── Makefile
```

## CI/CD

- **check.yml**: Valida i config YAML su ogni PR/push
- **pipeline.yml**: Esegue le pipeline, sync GCS, aggiorna registry

## Perché fidarsi

- Fonti ufficiali OpenGA (openga.giustizia-amministrativa.it)
- Trasformazioni documentate in SQL
- Controlli automatici prima della pubblicazione (CI + contract test)
- Standard condivisi del DataCivicLab (`.github`)

## Partecipa

- **Discussions** → domande civiche, interpretazioni, proposte di metriche
- **Issues** → bug, problemi tecnici, miglioramenti della pipeline

## Confine con il toolkit

Il motore della pipeline vive nel repository `toolkit`. Questa repo non replica
la logica di esecuzione: definisce input, regole e output attesi per ogni dataset.

- bug o feature di CLI, runner, validazioni runtime → repo `toolkit`
- bug o modifiche a fonti, mapping, SQL, mart, docs → questa repo

## Licenza

- **Dati OpenGA**: CC BY 4.0
- **Codice**: MIT
