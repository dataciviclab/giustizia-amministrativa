"""Contract dei compose GA: schema atti, grano appalti, split giurisdizionale.

1. i quattro dataset atti hanno schema identico (l'union di `ga_atti` e' per
   posizione: una colonna aggiunta solo a uno dei quattro romperebbe il compose)
2. `ga_atti` espone 4 tipo_atto e durate non negative
3. `ga_appalti_contenzioso` ha grano ricorso unico e copertura decisioni ~90%
4. `ga_cross` ha tipo_sede completo e `mart_panoramica_tipo_sede` somma ai
   totali di `mart_panoramica`

I test sui parquet si skippano se out/ non esiste (PR solo config).
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "out" / "data" / "clean"
MART = ROOT / "out" / "data" / "mart"

ATTI = ("ga_sentenze", "ga_ordinanze", "ga_decreti", "ga_pareri")


def _parquet(directory: Path, slug: str) -> Path | None:
    base = directory / slug
    if not base.exists():
        return None
    files = sorted(base.rglob("*.parquet"))
    return files[-1] if files else None


def _read(path: Path):
    import pandas as pd

    return pd.read_parquet(path)


@pytest.mark.contract
def test_atti_datasets_share_schema() -> None:
    frames = {}
    for slug in ATTI:
        path = _parquet(CLEAN, slug)
        if path is None:
            pytest.skip(f"clean {slug} non presente")
        frames[slug] = _read(path)
    reference = list(frames[ATTI[0]].columns)
    for slug, frame in frames.items():
        assert list(frame.columns) == reference, f"{slug}: schema diverso da {ATTI[0]}"


@pytest.mark.contract
def test_ga_atti_tipo_atto_e_durate() -> None:
    path = _parquet(CLEAN, "ga_atti")
    if path is None:
        pytest.skip("clean ga_atti non presente")
    frame = _read(path)
    assert set(frame["tipo_atto"].unique()) == {"sentenza", "ordinanza", "decreto", "parere"}
    durate = frame["durata_giorni"].dropna()
    assert len(durate) > 0, "nessuna durata calcolata"
    assert (durate >= 0).all(), "durata negativa: il filtro sulle date non regge"
    # la durata esiste solo per gli atti che definiscono
    assert frame.loc[frame["flg_definisce"] != "D", "durata_giorni"].isna().all()


@pytest.mark.contract
def test_appalti_grano_ricorso_unico() -> None:
    path = _parquet(CLEAN, "ga_appalti_contenzioso")
    if path is None:
        pytest.skip("clean ga_appalti_contenzioso non presente")
    frame = _read(path)
    duplicated = frame.duplicated(subset=["codice_sede", "numero_ricorso"]).sum()
    assert duplicated == 0, f"{duplicated} ricorsi duplicati: il grano non e' unico"


@pytest.mark.regression
def test_appalti_copertura_decisioni() -> None:
    path = _parquet(CLEAN, "ga_appalti_contenzioso")
    if path is None:
        pytest.skip("clean ga_appalti_contenzioso non presente")
    frame = _read(path)
    assert frame["ha_decisione"].isna().sum() == 0, "ha_decisione con NULL"
    share = frame["ha_decisione"].mean()
    # copertura "ha un atto che definisce" (non "ha un atto"): ~82%
    assert 0.75 <= share <= 0.90, f"copertura decisioni fuori range: {share:.1%}"
    # la decisione e' un atto definitorio, non un provvedimento qualsiasi
    assert (frame["ha_decisione"] == (frame["n_atti_definitori"] > 0)).all(), (
        "ha_decisione non coincide con n_atti_definitori > 0"
    )
    assert (frame["esito_decisione"] == "SENZA DECISIONE").equals(~frame["ha_decisione"]), (
        "esito_decisione incoerente con ha_decisione"
    )
    # la durata esiste dove c'e' una decisione, salvo poche date invertite
    mismatch = int((frame["ha_decisione"] != frame["durata_giorni"].notna()).sum())
    assert mismatch <= 5, f"{mismatch} ricorsi con decisione senza durata calcolabile"


@pytest.mark.contract
def test_ga_cross_tipo_sede() -> None:
    path = _parquet(CLEAN, "ga_cross")
    if path is None:
        pytest.skip("clean ga_cross non presente")
    frame = _read(path)
    assert frame["tipo_sede"].isna().sum() == 0, "tipo_sede con NULL"
    assert set(frame["tipo_sede"].unique()) == {"giurisdizionale", "consultivo"}
    consultive = frame.loc[frame["tipo_sede"] == "consultivo", "codice_sede"].unique()
    assert sorted(consultive) == [31, 33], f"sedi consultive inattese: {sorted(consultive)}"


@pytest.mark.contract
def test_panoramica_tipo_sede_somma_ai_totali() -> None:
    panorama = _parquet(MART, "ga_cross")
    if panorama is None:
        pytest.skip("mart ga_cross non presente")
    base_files = sorted((MART / "ga_cross").rglob("mart_panoramica.parquet"))
    tipo_files = sorted((MART / "ga_cross").rglob("mart_panoramica_tipo_sede.parquet"))
    if not base_files or not tipo_files:
        pytest.skip("mart_panoramica_tipo_sede non presente")
    base = _read(base_files[-1])[["anno", "totale_pervenuti", "totale_definiti"]]
    tipo = _read(tipo_files[-1])
    aggregated = tipo.groupby("anno", as_index=False)[["totale_pervenuti", "totale_definiti"]].sum()
    merged = base.merge(aggregated, on="anno", suffixes=("_base", "_tipo"))
    assert len(merged) > 0
    for column in ("totale_pervenuti", "totale_definiti"):
        delta = (merged[f"{column}_base"] - merged[f"{column}_tipo"]).abs().max()
        assert delta < 1, f"{column}: split tipo_sede non somma ai totali (delta {delta})"
