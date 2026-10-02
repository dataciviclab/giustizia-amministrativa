"""Contract: codelist sedi + nome_sede canonico nei clean GA.

Source of truth: datasets/ga-ricorsi-pervenuti-class/data/sedi_canonici.csv

1. Il CSV copre i codice_sede attesi (1..33)
2. Ogni clean con out/ presente espone solo nomi con " - "
3. Su ga_ricorsi_pervenuti_class il nome per codice coincide col codelist

Se i parquet clean non esistono (PR solo config), i test sui dati skippano.
Il test sul CSV gira sempre.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "out" / "data" / "clean"
CODELIST = (
    ROOT
    / "datasets"
    / "ga-ricorsi-pervenuti-class"
    / "data"
    / "sedi_canonici.csv"
)

DATASETS = [
    "ga_ricorsi_pervenuti_class",
    "ga_ricorsi_definiti",
    "ga_sentenze",
    "ga_pareri",
    "ga_sentenze_brevi",
    "ga_ricorsi_tipo_decisione",
    "ga_cross",
]

# Codici storici OpenGA GA (31 sedi + consultive CdS/CGA)
EXPECTED_CODES = set(range(1, 34))


def _load_codelist() -> dict[int, str]:
    import csv

    assert CODELIST.exists(), f"codelist mancante: {CODELIST}"
    mapping: dict[int, str] = {}
    with CODELIST.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[int(row["codice_sede"])] = row["nome_sede_canonico"].strip()
    return mapping


def _clean_parquet(slug: str) -> Path | None:
    base = CLEAN / slug
    if not base.exists():
        return None
    files = sorted(base.rglob("*_clean.parquet"))
    return files[-1] if files else None


@pytest.mark.contract
def test_codelist_sedi_covers_expected_codes() -> None:
    mapping = _load_codelist()
    codes = set(mapping)
    missing = EXPECTED_CODES - codes
    extra = codes - EXPECTED_CODES
    assert not missing, f"codelist mancante codici: {sorted(missing)}"
    assert not extra, f"codelist codici inattesi: {sorted(extra)}"
    for code, name in mapping.items():
        assert " - " in name, f"codelist codice {code}: nome senza ' - ': {name!r}"


@pytest.mark.contract
@pytest.mark.parametrize("slug", DATASETS)
def test_nome_sede_has_canonical_separator(slug: str) -> None:
    path = _clean_parquet(slug)
    if path is None:
        pytest.skip(f"clean non presente per {slug}")

    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL parquet; LOAD parquet;")
    rows = con.execute(
        f"""
        SELECT DISTINCT nome_sede
        FROM read_parquet('{path}')
        WHERE nome_sede IS NOT NULL
        """
    ).fetchall()
    assert rows, f"{slug}: nessun nome_sede"
    broken = [name for (name,) in rows if " - " not in str(name)]
    assert not broken, (
        f"{slug}: nome_sede senza separatore canonico ' - ': {broken[:5]}"
    )


@pytest.mark.contract
def test_pervenuti_nome_sede_matches_codelist() -> None:
    path = _clean_parquet("ga_ricorsi_pervenuti_class")
    if path is None:
        pytest.skip("clean pervenuti non presente")

    import duckdb

    mapping = _load_codelist()
    con = duckdb.connect()
    con.execute("INSTALL parquet; LOAD parquet;")
    rows = con.execute(
        f"""
        SELECT DISTINCT codice_sede, nome_sede
        FROM read_parquet('{path}')
        WHERE nome_sede IS NOT NULL
        """
    ).fetchall()

    unmatched = []
    wrong = []
    for code, name in rows:
        code_i = int(code)
        if code_i not in mapping:
            unmatched.append((code_i, name))
            continue
        if name != mapping[code_i]:
            wrong.append((code_i, name, mapping[code_i]))

    assert not unmatched, f"codici senza codelist (aggiornare CSV): {unmatched[:5]}"
    assert not wrong, f"nome_sede non allineato al codelist: {wrong[:5]}"
