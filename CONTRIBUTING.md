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
pip install -r requirements.txt
make check
```

## Workflow

1. Crea un branch da `main`: `git checkout -b feat/nome-feature`
2. Fai le tue modifiche
3. Verifica: `make check`
4. Apri una PR seguendo il template

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
