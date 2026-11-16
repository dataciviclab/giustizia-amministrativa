"""Contract dei compose GA: schema atti, grano appalti, split giurisdizionale.

1. i quattro dataset atti hanno schema identico (l'union di `ga_atti` e' per
   posizione: una colonna aggiunta solo a uno dei quattro romperebbe il compose)
2. `ga_atti` espone 4 tipo_atto e durate non negative
3. `ga_appalti_contenzioso` ha grano ricorso unico e le decisioni sono atti
   definitori (non "esiste un provvedimento")
4. `ga_cross` ha tipo_sede completo e `mart_panoramica_tipo_sede` somma ai
   totali di `mart_panoramica`

I parquet si leggono con duckdb: e' l'unica dipendenza dichiarata del repo
(pandas/pyarrow non sono installati nel job Pipeline e i test non devono
dipenderne). I test si skippano se out/ non esiste (PR solo config).
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


@pytest.mark.contract
def test_atti_datasets_share_schema() -> None:
    schemas: dict[str, list[str]] = {}
    for slug in ATTI:
        path = _parquet(CLEAN, slug)
        if path is None:
            pytest.skip(f"clean {slug} non presente")
        rows = _rows("DESCRIBE SELECT * FROM read_parquet(?)", (path,))
        schemas[slug] = [row[0] for row in rows]
    reference = schemas[ATTI[0]]
    for slug, columns in schemas.items():
        assert columns == reference, f"{slug}: schema diverso da {ATTI[0]}"


@pytest.mark.contract
def test_ga_atti_tipo_atto_e_durate() -> None:
    path = _parquet(CLEAN, "ga_atti")
    if path is None:
        pytest.skip("clean ga_atti non presente")
    tipi = {row[0] for row in _rows("SELECT DISTINCT tipo_atto FROM read_parquet(?)", (path,))}
    assert tipi == {"sentenza", "ordinanza", "decreto", "parere"}
    negative, = _rows(
        "SELECT count(*) FROM read_parquet(?) WHERE durata_giorni < 0", (path,)
    )[0]
    assert negative == 0, f"{negative} durate negative: il filtro sulle date non regge"
    computed, total = _rows(
        """
        SELECT count(*) FILTER (WHERE flg_definisce = 'D' AND durata_giorni IS NOT NULL),
               count(*) FILTER (WHERE flg_definisce = 'D')
        FROM read_parquet(?)
        """,
        (path,),
    )[0]
    assert computed / total > 0.95, "durata mancante su troppi atti che definiscono"
    spurious, = _rows(
        """
        SELECT count(*) FROM read_parquet(?)
        WHERE flg_definisce <> 'D' AND durata_giorni IS NOT NULL
        """,
        (path,),
    )[0]
    assert spurious == 0, f"{spurious} righe senza flg D con durata calcolata"


@pytest.mark.contract
def test_appalti_grano_ricorso_unico() -> None:
    path = _parquet(CLEAN, "ga_appalti_contenzioso")
    if path is None:
        pytest.skip("clean ga_appalti_contenzioso non presente")
    duplicated, = _rows(
        """
        SELECT count(*) FROM (
            SELECT codice_sede, numero_ricorso
            FROM read_parquet(?)
            GROUP BY 1, 2
            HAVING count(*) > 1
        )
        """,
        (path,),
    )[0]
    assert duplicated == 0, f"{duplicated} ricorsi duplicati: il grano non e' unico"


@pytest.mark.regression
def test_appalti_copertura_decisioni() -> None:
    path = _parquet(CLEAN, "ga_appalti_contenzioso")
    if path is None:
        pytest.skip("clean ga_appalti_contenzioso non presente")
    nulli, con_decisione, totale, incoerenti, senza, mismatch = _rows(
        """
        SELECT
            count(*) FILTER (WHERE ha_decisione IS NULL),
            count(*) FILTER (WHERE ha_decisione),
            count(*),
            count(*) FILTER (WHERE ha_decisione <> (n_atti_definitori > 0)),
            count(*) FILTER (WHERE (esito_decisione = 'SENZA DECISIONE') <> (NOT ha_decisione)),
            count(*) FILTER (WHERE ha_decisione <> (durata_giorni IS NOT NULL))
        FROM read_parquet(?)
        """,
        (path,),
    )[0]
    assert nulli == 0, "ha_decisione con NULL"
    share = con_decisione / totale
    # copertura "ha un atto che definisce" (non "ha un atto"): ~82%
    assert 0.75 <= share <= 0.90, f"copertura decisioni fuori range: {share:.1%}"
    assert incoerenti == 0, "ha_decisione non coincide con n_atti_definitori > 0"
    assert senza == 0, "esito_decisione incoerente con ha_decisione"
    # la durata esiste dove c'e' una decisione, salvo poche date invertite
    assert mismatch <= 5, f"{mismatch} ricorsi con decisione senza durata calcolabile"


@pytest.mark.contract
def test_ga_cross_tipo_sede() -> None:
    path = _parquet(CLEAN, "ga_cross")
    if path is None:
        pytest.skip("clean ga_cross non presente")
    nulli, tipi = _rows(
        """
        SELECT count(*) FILTER (WHERE tipo_sede IS NULL),
               list(DISTINCT tipo_sede ORDER BY tipo_sede)
        FROM read_parquet(?)
        """,
        (path,),
    )[0]
    assert nulli == 0, "tipo_sede con NULL"
    assert tipi == ["consultivo", "giurisdizionale"]
    consultive = [
        row[0]
        for row in _rows(
            """
            SELECT DISTINCT codice_sede FROM read_parquet(?)
            WHERE tipo_sede = 'consultivo' ORDER BY 1
            """,
            (path,),
        )
    ]
    assert consultive == [31, 33], f"sedi consultive inattese: {consultive}"


@pytest.mark.contract
def test_panoramica_tipo_sede_somma_ai_totali() -> None:
    panorama = _mart("ga_cross", "mart_panoramica")
    tipo = _mart("ga_cross", "mart_panoramica_tipo_sede")
    if panorama is None or tipo is None:
        pytest.skip("mart_panoramica_tipo_sede non presente")
    anni, delta_pervenuti, delta_definiti = _rows(
        """
        WITH split AS (
            SELECT anno, sum(totale_pervenuti) AS pervenuti, sum(totale_definiti) AS definiti
            FROM read_parquet(?)
            GROUP BY anno
        )
        SELECT count(*),
               max(abs(split.pervenuti - base.totale_pervenuti)),
               max(abs(split.definiti - base.totale_definiti))
        FROM split
        JOIN read_parquet(?) AS base USING (anno)
        """,
        (tipo, panorama),
    )[0]
    assert anni > 0
    assert delta_pervenuti < 1, f"split tipo_sede non somma ai pervenuti (delta {delta_pervenuti})"
    assert delta_definiti < 1, f"split tipo_sede non somma ai definiti (delta {delta_definiti})"
