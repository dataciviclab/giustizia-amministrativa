"""Contract: nome_sede canonico nei clean GA.

Protegge il fix del bug OpenGA sui pervenuti (NOME_SEDE senza " - ").
Se i parquet clean non esistono (PR solo config), il test viene skippato.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "out" / "data" / "clean"

# Dataset che devono esporre nomi sede con separatori canonici
DATASETS = [
    "ga_ricorsi_pervenuti_class",
    "ga_ricorsi_definiti",
    "ga_sentenze",
    "ga_sentenze_brevi",
    "ga_cross",
    "ga_ricorsi_tipo_decisione",
]


def _clean_parquet(slug: str) -> Path | None:
    base = CLEAN / slug
    if not base.exists():
        return None
    files = sorted(base.rglob("*_clean.parquet"))
    return files[-1] if files else None


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

    # Contratto Lab: i nomi sede canonici contengono sempre " - "
    # (es. "TAR LAZIO - ROMA", "CdS CONSULTIVE - ROMA")
    broken = [name for (name,) in rows if " - " not in str(name)]
    assert not broken, (
        f"{slug}: nome_sede senza separatore canonico ' - ': {broken[:5]}"
    )
