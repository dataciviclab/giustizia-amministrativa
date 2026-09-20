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
3. **Quali materie hanno più contenzioso?** → classificazioni per volume e tasso di accoglimento
4. **Quanto è produttiva ogni sede?** → provvedimenti che definiscono vs non definiscono
5. **Qual è il backlog di ricorsi pendenti?** → stock mensile per sede
6. **Com'è composto il contenzioso sugli appalti?** → ricorsi appalto con CIG (joinabile con ANAC)

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
| `compose/ga-cross` | Compose: flusso pervenuti → definiti → esito | 2017-2026 | 3 |

### Mart analitici (17 totali)

**Per dataset** (14): 2 mart cadauno (per sede + per tipo/classificazione)

**Compose** (3): panoramica, flusso per sede, esiti per materia

## Dashboard

Dashboard Streamlit con 3 livelli (da costruire):

| Livello | Pagina | Contenuto |
|---|---|---|
| **Monitoraggio** | Panoramica | Trend nazionale, volumi per anno, tasso definizione |
| **Intelligence** | Esiti | Tasso accoglimento per materia e sede, trend |
| | Appalti | Contenzioso sugli appalti, join con ANAC |
| **Esplorazione** | Scheda Sede | Profilo completo di ogni sede |
| | Query SQL | Query libera su tutti i dataset |

## Come si usa

```bash
# Setup
pip install -r requirements.txt

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

# Test
python -m pytest tests/
```

## Struttura

```
giustizia-amministrativa/
├── datasets/                   # 7 dataset (toolkit pipeline)
│   ├── ga-sentenze/
│   ├── ga-decreti/
│   ├── ga-ordinanze/
│   ├── ga-ricorsi-definiti/
│   ├── ga-ricorsi-pervenuti-class/
│   ├── ga-provvedimenti/
│   └── ga-ricorsi-appalto/
├── compose/
│   └── ga-cross/              # cross-dataset (flusso pervenuti→definiti)
├── dashboard/                  # Streamlit (da costruire)
├── out/                        # output pipeline (raw/clean/mart)
├── registry/                   # artifact catalog
├── tests/                      # contract test
├── prefetch.py                 # script download CKAN
├── Makefile
└── requirements.txt
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
