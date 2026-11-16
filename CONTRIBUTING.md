# Contribuire a Giustizia Amministrativa

Grazie per il tuo interesse! Ecco come contribuire.

## Tipi di contribuzione

- **Bug report** → apri un Issue
- **Feature request** → apri un Issue con label `enhancement`
- **Fix** → apri una PR seguendo il template
- **Dati** → segnala fonti mancanti o errori nei dataset

## Setup locale

```bash
git clone https://github.com/dataciviclab/giustizia-amministrativa.git
cd giustizia-amministrativa
pip install -e ".[dev,pipeline]"
make check
```

## Workflow

1. Crea un branch da `main`: `git checkout -b feat/nome-feature`
2. Fai le tue modifiche
3. Verifica: `make check`
4. Apri una PR seguendo il template
5. **Prima del merge**, se hai toccato `datasets/`, `compose/` o `tests/`,
   lancia la pipeline sul branch (vedi sotto)

### Pipeline pre-merge

Il workflow `Pipeline` **non gira sulle PR**: parte su `pull_request: closed`
(post-merge), sullo schedule mensile o su `workflow_dispatch`. Per non
scoprire i rossi dopo il merge, va lanciato a mano sul branch:

```bash
gh workflow run pipeline.yml --ref <branch>
gh run list --workflow=pipeline.yml --branch <branch> --limit 1
```

Il job esegue `make run-all && python -m pytest tests/ dashboard/tests -q`.
Richiede i secret GCP (presenti per i branch del repo).

Nota per i test: il job Pipeline installa `.[dev,pipeline]` e **non** ha
pandas/pyarrow. I test che leggono parquet devono usare `duckdb`
(vedi `tests/test_sede_names_contract.py` come riferimento), non
`pandas.read_parquet`.

## Standard

- Segui gli standard del DataCivicLab (vedi [lab-ops/standards](https://github.com/dataciviclab/.github/tree/main/docs/standards))
- I dataset usano `toolkit` per la pipeline (raw → clean → mart)
- Ogni dataset ha un `dataset.yml` come contratto
- Non committare output pipeline (`out/`, `*.parquet`, `*.csv` generati)

## Test

```bash
python -m pytest tests/
```

I test devono avere marcatori: `contract`, `policy`, `regression`, `adapter`, `pure_unit`, `smoke`.

## Domande?

Apri una Discussion o scrivi a maintainers@dataciviclab.org.
