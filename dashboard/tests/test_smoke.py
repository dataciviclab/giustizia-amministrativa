"""Smoke test — pagine, helper e contratto registry della dashboard."""

from __future__ import annotations

import ast
import json
import py_compile
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke

DASH = Path(__file__).resolve().parent.parent
ROOT = DASH.parent
PAGES_DIR = DASH / "pages"
REGISTRY = ROOT / "registry" / "registry.json"

MODULES = [
    DASH / "app.py",
    DASH / "sources.py",
]

# Helper che le pagine devono poter usare (contract wiring PR #8)
REQUIRED_HELPERS = {
    "query_pareri",
    "query_sentenze_brevi",
    "query_tipo_decisione",
    "load_definizioni_mezzi_anno",
    "load_definizioni_sintesi_sede",
    "load_definizioni_outlier",
}

# Slug/mart che la dashboard assume pubblicati (GCS + registry)
REQUIRED_REGISTRY = {
    "ga_cross": {"mart_panoramica", "mart_sede_flusso", "mart_esiti"},
    "ga_definizioni": {"mart_mezzi_anno", "mart_sintesi_sede", "mart_outlier_sedi"},
}


@pytest.mark.parametrize("module", MODULES, ids=lambda p: p.stem)
def test_module_compiles(module: Path) -> None:
    py_compile.compile(str(module), doraise=True)


@pytest.mark.parametrize(
    "page",
    sorted(PAGES_DIR.glob("*.py")),
    ids=lambda p: p.stem,
)
def test_page_compiles(page: Path) -> None:
    """Ogni pagina deve compilarsi senza errori di sintassi."""
    py_compile.compile(str(page), doraise=True)


def test_sources_exposes_ga_helpers() -> None:
    tree = ast.parse((DASH / "sources.py").read_text(encoding="utf-8"))
    names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    missing = REQUIRED_HELPERS - names
    assert not missing, f"sources.py manca helper: {sorted(missing)}"


def test_navigation_includes_mezzi_page() -> None:
    text = (DASH / "app.py").read_text(encoding="utf-8")
    assert "06_Mezzi_Definizione.py" in text
    assert "Mezzi di Definizione" in text


def test_mezzi_page_uses_grezzo_helpers() -> None:
    """Gli helper grezzi non devono restare codice morto: la pagina li chiama."""
    text = (PAGES_DIR / "06_Mezzi_Definizione.py").read_text(encoding="utf-8")
    for helper in ("query_pareri", "query_sentenze_brevi", "query_tipo_decisione"):
        assert helper in text, f"06_Mezzi_Definizione non usa {helper}"


@pytest.mark.contract
def test_registry_exposes_dashboard_marts() -> None:
    """Slug e mart assunti dalla dashboard devono esistere nel registry."""
    assert REGISTRY.exists(), f"registry mancante: {REGISTRY}"
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    datasets = {d.get("slug") for d in reg.get("datasets", [])}
    marts_by_ds: dict[str, set[str]] = {}
    for m in reg.get("marts", []):
        marts_by_ds.setdefault(m.get("dataset"), set()).add(m.get("table"))

    for slug, tables in REQUIRED_REGISTRY.items():
        assert slug in datasets, f"registry manca dataset {slug}"
        have = marts_by_ds.get(slug, set())
        missing = tables - have
        assert not missing, f"registry manca mart per {slug}: {sorted(missing)}"
