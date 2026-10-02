"""Fonti dati per la dashboard Giustizia Amministrativa.

Multi-dataset: registry del repo + compose ga_cross e ga_definizioni.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from lab_connectors.duckdb.queries import (
    load_mart_table as _load_mart_table,
)
from lab_connectors.duckdb.queries import (
    query_clean as _query_clean,
)
from lab_connectors.formatters import fmt_num, fmt_pct

ROOT = Path(__file__).parent.parent
PREFIX = "giustizia-amministrativa/"
YEARS = list(range(2017, 2027))
YEAR_DEFAULT = 2026


def _q(slug: str, sql: str, year: int = YEAR_DEFAULT):
    return _query_clean(slug, sql, [year], prefix=PREFIX, local_root=None)


def _q_multi(slug: str, sql: str, years: list[int]):
    return _query_clean(slug, sql, years, prefix=PREFIX, local_root=None)


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(slug: str, table: str, year: int = YEAR_DEFAULT):
    return _load_mart_table(slug, table, year, prefix=PREFIX, local_root=None)


@st.cache_data(ttl=3600, show_spinner=False)
def query_pervenuti(sql: str, year: int = YEAR_DEFAULT):
    return _q("ga_ricorsi_pervenuti_class", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_definiti(sql: str, year: int = YEAR_DEFAULT):
    return _q("ga_ricorsi_definiti", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_provvedimenti(sql: str, year: int = YEAR_DEFAULT):
    return _q("ga_provvedimenti", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_appalti(sql: str, year: int = YEAR_DEFAULT):
    return _q("openga_ricorsi_appalto", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_cds(sql: str, year: int = YEAR_DEFAULT):
    return _q("openga_ricorsi_cds", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_sentenze(sql: str, year: int = YEAR_DEFAULT):
    return _q("ga_sentenze", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_cross(sql: str, years: tuple[int, ...] = tuple(YEARS)):
    return _q_multi("ga_cross", sql, list(years))


@st.cache_data(ttl=3600, show_spinner=False)
def query_pareri(sql: str, year: int = YEAR_DEFAULT):
    return _q("ga_pareri", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_sentenze_brevi(sql: str, year: int = YEAR_DEFAULT):
    return _q("ga_sentenze_brevi", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_tipo_decisione(sql: str, year: int = YEAR_DEFAULT):
    return _q("ga_ricorsi_tipo_decisione", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_definizioni_mezzi_anno(year: int = YEAR_DEFAULT):
    return load_mart("ga_definizioni", "mart_mezzi_anno", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_definizioni_sintesi_sede(year: int = YEAR_DEFAULT):
    return load_mart("ga_definizioni", "mart_sintesi_sede", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_definizioni_outlier(year: int = YEAR_DEFAULT):
    return load_mart("ga_definizioni", "mart_outlier_sedi", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_sentenze_esiti(year: int = YEAR_DEFAULT):
    sql = """
    SELECT esito_provvedimento, COUNT(*) AS n
    FROM clean_input
    GROUP BY esito_provvedimento
    ORDER BY n DESC
    """
    return _q("ga_sentenze", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_ordinanze_esiti(year: int = YEAR_DEFAULT):
    sql = """
    SELECT esito_provvedimento, COUNT(*) AS n
    FROM clean_input
    GROUP BY esito_provvedimento
    ORDER BY n DESC
    """
    return _q("ga_ordinanze", sql, year)
