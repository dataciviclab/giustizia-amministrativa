"""Smoke test — verifica che pagine e moduli dashboard si compilano."""

from __future__ import annotations

import py_compile
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke

DASH = Path(__file__).resolve().parent.parent
PAGES_DIR = DASH / "pages"

MODULES = [
    DASH / "app.py",
    DASH / "sources.py",
]


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


def test_sources_exposes_new_ga_helpers() -> None:
    """I nuovi dataset GA devono essere raggiungibili da sources."""
    import ast

    tree = ast.parse((DASH / "sources.py").read_text(encoding="utf-8"))
    names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required = {
        "query_pareri",
        "query_sentenze_brevi",
        "query_tipo_decisione",
        "load_definizioni_mezzi_anno",
        "load_definizioni_sintesi_sede",
        "load_definizioni_outlier",
    }
    missing = required - names
    assert not missing, f"sources.py manca helper: {sorted(missing)}"


def test_navigation_includes_mezzi_page() -> None:
    text = (DASH / "app.py").read_text(encoding="utf-8")
    assert "06_Mezzi_Definizione.py" in text
    assert "Mezzi di Definizione" in text
