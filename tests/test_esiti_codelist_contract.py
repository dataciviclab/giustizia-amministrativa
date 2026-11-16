"""Contract: codelist esiti OpenGA + coerenza dei "definiti" tra i compose.

Source of truth: datasets/ga-ricorsi-definiti/data/esiti_codelist.csv

OpenGA pubblica "ricorsi definiti per classificazione ed esito" con grano
`anno × mese × sede × classificazione × esito`: un ricorso che riceve un esito
interlocutorio (riunione, rinvio, nomina commissario ad acta, misura cautelare)
e poi una sentenza compare in piu' righe. Sommare senza filtro gonfia il totale
(+15% nel 2017, +32% nel 2026 contro il tema ufficiale "per tipo di decisione")
con un bias crescente nel tempo.

1. La codelist e' ben formata (definitorio 0/1, motivo non vuoto, nessun dup)
2. Ogni esito del clean ga_ricorsi_definiti e' in codelist (fail-closed sul resto)
3. ga_cross.definiti == ga_definizioni.rd_definiti (stessa regola sui due compose)
4. Il totale definiti resta entro il 12% dal tema ufficiale tipo-decisione

I parquet si leggono con duckdb: e' l'unica dipendenza dichiarata del repo
(pandas/pyarrow non sono installati nel job Pipeline). I test sui dati si
skippano se out/ non esiste (PR solo config).
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CODELIST = ROOT / "datasets" / "ga-ricorsi-definiti" / "data" / "esiti_codelist.csv"
CLEAN = ROOT / "out" / "data" / "clean"
MART = ROOT / "out" / "data" / "mart"

# Tolleranza residua documentata: la fonte resta un conteggio per
# (classificazione × esito), quindi il netto puo' superare i ricorsi distinti
# del tema ufficiale per ricorsi riclassificati su piu' materie.
RESIDUAL_TOLERANCE_PCT = 12.0


def _load_codelist() -> dict[str, int]:
    assert CODELIST.exists(), f"codelist mancante: {CODELIST}"
    mapping: dict[str, int] = {}
    with CODELIST.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            esito = (row["esito_provvedimento"] or "").strip()
            assert esito, "codelist: esito_provvedimento vuoto"
            assert esito not in mapping, f"codelist: esito duplicato {esito!r}"
            definitorio = int(row["definitorio"])
            assert definitorio in (0, 1), f"codelist: definitorio non binario per {esito!r}"
            assert (row["motivo"] or "").strip(), f"codelist: motivo vuoto per {esito!r}"
            mapping[esito] = definitorio
    return mapping


def _parquet(directory: Path, slug: str) -> Path | None:
    base = directory / slug
    if not base.exists():
        return None
    files = sorted(base.rglob("*.parquet"))
    return files[-1] if files else None


def _mart(slug: str, name: str) -> Path | None:
    base = MART / slug
    if not base.exists():
        return None
    files = sorted(base.rglob(f"{name}.parquet"))
    return files[-1] if files else None


def _rows(sql: str, params: tuple[Path, ...] = ()) -> list[tuple]:
    import duckdb

    con = duckdb.connect()
    try:
        return con.execute(sql, [str(p) for p in params]).fetchall()
    finally:
        con.close()


def _canonical(esito: str) -> str:
    """Collassa le doppie virgolette dei refusi di fonte."""
    return (esito or "").strip().replace("''", "'")


@pytest.mark.contract
def test_codelist_is_complete_and_binary() -> None:
    mapping = _load_codelist()
    assert len(mapping) >= 120, f"codelist troppo corta: {len(mapping)} esiti"
    definitori = [esito for esito, flag in mapping.items() if flag == 1]
    interlocutori = [esito for esito, flag in mapping.items() if flag == 0]
    assert definitori, "codelist senza esiti definitori"
    assert interlocutori, "codelist senza esiti interlocutori"
    assert "NOMINA COMMISSARIO AD ACTA" in interlocutori
    assert "ACCOGLIE" in definitori
    assert "RESPINGE" in definitori


@pytest.mark.contract
def test_clean_esiti_are_all_codelisted() -> None:
    path = _parquet(CLEAN, "ga_ricorsi_definiti")
    if path is None:
        pytest.skip("clean ga_ricorsi_definiti non presente")
    mapping = _load_codelist()

    observed = {
        _canonical(row[0])
        for row in _rows(
            "SELECT DISTINCT esito_provvedimento FROM read_parquet(?)", (path,)
        )
        if row[0] is not None
    }
    unmapped = sorted(observed - set(mapping))
    assert not unmapped, f"esiti non mappati in codelist: {unmapped}"

    nulli, = _rows(
        "SELECT count(*) FILTER (WHERE esito_definitorio IS NULL) FROM read_parquet(?)",
        (path,),
    )[0]
    assert nulli == 0, "esito_definitorio con NULL"

    # un esito (canonicalizzato) deve avere un solo flag pubblicato
    by_esito: dict[str, set[bool]] = {}
    for esito, flag in _rows(
        """
        SELECT esito_provvedimento, bool_or(esito_definitorio)
        FROM read_parquet(?)
        GROUP BY esito_provvedimento
        """,
        (path,),
    ):
        by_esito.setdefault(_canonical(esito), set()).add(bool(flag))
    for esito, flags in by_esito.items():
        assert len(flags) == 1, f"flag incoerente per {esito!r}: {flags}"
        assert flags == {bool(mapping[esito])}, (
            f"esito {esito!r}: clean dice {flags}, codelist dice {mapping[esito]}"
        )


@pytest.mark.regression
def test_definiti_aligned_between_composes() -> None:
    panorama = _mart("ga_cross", "mart_panoramica")
    mezzi = _mart("ga_definizioni", "mart_mezzi_anno")
    if panorama is None or mezzi is None:
        pytest.skip("mart compose non presenti")
    anni, delta = _rows(
        """
        SELECT count(*), max(abs(p.totale_definiti - m.rd_definiti))
        FROM read_parquet(?) AS p
        JOIN read_parquet(?) AS m USING (anno)
        """,
        (panorama, mezzi),
    )[0]
    assert anni > 0
    assert delta <= 1, f"ga_cross.definiti e ga_definizioni.rd_definiti divergono di {delta}"


@pytest.mark.regression
def test_definiti_within_tolerance_of_official_theme() -> None:
    panorama = _mart("ga_cross", "mart_panoramica")
    official = _parquet(CLEAN, "ga_ricorsi_tipo_decisione")
    if panorama is None or official is None:
        pytest.skip("mart ga_cross o clean tipo-decisione non presenti")
    peggiore, anno_peggiore = _rows(
        """
        WITH official AS (
            SELECT anno, sum(totale_definiti) AS ufficiale
            FROM read_parquet(?)
            GROUP BY anno
        )
        SELECT max(abs(p.totale_definiti / official.ufficiale - 1) * 100) AS delta,
               arg_max(p.anno, abs(p.totale_definiti / official.ufficiale - 1)) AS anno
        FROM read_parquet(?) AS p
        JOIN official USING (anno)
        """,
        (official, panorama),
    )[0]
    assert peggiore is not None
    assert peggiore <= RESIDUAL_TOLERANCE_PCT, (
        f"{anno_peggiore}: definiti fuori tolleranza ({peggiore:.1f}% "
        f"vs {RESIDUAL_TOLERANCE_PCT}%)"
    )
