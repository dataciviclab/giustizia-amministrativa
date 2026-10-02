#!/usr/bin/env python3
"""Giustizia Amministrativa · Dashboard Streamlit"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="Giustizia Amministrativa · Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(
    repo_name="giustizia-amministrativa",
    repo_url="https://github.com/dataciviclab/giustizia-amministrativa",
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Esiti.py", title="Esiti Ricorsi", icon="⚖️"),
        st.Page("pages/06_Mezzi_Definizione.py", title="Mezzi di Definizione", icon="⚙️"),
        st.Page("pages/03_Appalti.py", title="Appalti Pubblici", icon="🏗️"),
        st.Page("pages/04_Scheda_Sede.py", title="Scheda Sede", icon="🏛️"),
    ],
    "Strumenti": [
        st.Page("pages/05_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

pg.run()
