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

I test sui parquet si skippano se out/ non esiste (PR solo config).
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


def _read(path: Path):
    import pandas as pd

    return pd.read_parquet(path)


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
    frame = _read(path)
    mapping = _load_codelist()
    observed = {_canonical(esito) for esito in frame["esito_provvedimento"].dropna().unique()}
    unmapped = sorted(observed - set(mapping))
    assert not unmapped, f"esiti non mappati in codelist: {unmapped}"
    assert frame["esito_definitorio"].isna().sum() == 0, "esito_definitorio con NULL"
    # il flag pubblicato deve essere coerente con la codelist
    for esito, flag in mapping.items():
        rows = frame[frame["esito_provvedimento"].map(_canonical) == esito]
        if not len(rows):
            continue
        assert set(rows["esito_definitorio"].unique()) == {bool(flag)}, (
            f"flag incoerente per {esito!r}"
        )


@pytest.mark.contract
@pytest.mark.regression
def test_definiti_aligned_between_composes() -> None:
    panorama_path = _mart("ga_cross", "mart_panoramica")
    mezzi_path = _mart("ga_definizioni", "mart_mezzi_anno")
    if panorama_path is None or mezzi_path is None:
        pytest.skip("mart compose non presenti")
    panorama = _read(panorama_path)
    mezzi = _read(mezzi_path)
    joined = panorama[["anno", "totale_definiti"]].merge(mezzi[["anno", "rd_definiti"]], on="anno")
    assert len(joined) > 0
    for row in joined.itertuples():
        assert abs(row.totale_definiti - row.rd_definiti) <= 1, (
            f"{row.anno}: ga_cross.definiti={row.totale_definiti} "
            f"!= ga_definizioni.rd_definiti={row.rd_definiti}"
        )


@pytest.mark.contract
@pytest.mark.regression
def test_definiti_within_tolerance_of_official_theme() -> None:
    panorama_path = _mart("ga_cross", "mart_panoramica")
    official = _parquet(CLEAN, "ga_ricorsi_tipo_decisione")
    if panorama_path is None or official is None:
        pytest.skip("mart ga_cross o clean tipo-decisione non presenti")
    panorama = _read(panorama_path)
    frame = _read(official)
    totals = frame.groupby("anno")["totale_definiti"].sum()
    for row in panorama.itertuples():
        expected = totals.get(row.anno)
        if expected is None or not expected:
            continue
        delta = (row.totale_definiti / expected - 1) * 100
        assert abs(delta) <= RESIDUAL_TOLERANCE_PCT, (
            f"{row.anno}: definiti {row.totale_definiti} vs ufficiale {expected:.0f} "
            f"({delta:+.1f}%, tolleranza {RESIDUAL_TOLERANCE_PCT}%)"
        )
