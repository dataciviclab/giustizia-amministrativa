"""Query SQL — Interroga direttamente i dati della giustizia amministrativa."""

from pathlib import Path

from lab_connectors.duckdb.sql_page import render_sql_query
from lab_connectors.registry import load_registry

registry = load_registry(Path(__file__).parent.parent.parent / "registry" / "registry.json")

render_sql_query(
    registry=registry,
    prefix="giustizia-amministrativa/",
    default_slug="ga_cross",
    title="🧪 Query SQL",
    description=(
        "Interroga direttamente i dati della giustizia amministrativa. "
        "Usa ``clean_input`` come nome della tabella virtuale. "
    ),
)
