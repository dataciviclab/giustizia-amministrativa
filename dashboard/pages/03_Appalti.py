"""Appalti Pubblici — Contenzioso sugli appalti con CIG."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lab_connectors.formatters import fmt_num, fmt_pct
from sources import YEAR_DEFAULT, YEARS, query_appalti

st.title("🏗️ Appalti Pubblici")
st.markdown("Ricorsi in materia d'appalto con codice CIG — joinabile con ANAC.")

year = st.selectbox("Anno", YEARS, index=YEARS.index(YEAR_DEFAULT))

# ── KPI ────────────────────────────────────────────────────────────
df_kpi = query_appalti(f"""
    SELECT
        COUNT(*) AS n_ricorsi,
        COUNT(DISTINCT codice_cig) AS n_gare,
        SUM(CASE WHEN importo_complessivo_gara > 0 AND importo_complessivo_gara < 1000000000 THEN importo_complessivo_gara ELSE NULL END) AS importo_totale
    FROM clean_input
    WHERE anno = {year}
""", year)

if df_kpi.empty or df_kpi.iloc[0]["n_ricorsi"] == 0:
    st.warning("Nessun dato appalti disponibile per quest'anno.")
    st.stop()

row = df_kpi.iloc[0]
k1, k2, k3 = st.columns(3)
k1.metric("Ricorsi appalto", fmt_num(int(row["n_ricorsi"])))
k2.metric("Gare distinte", fmt_num(int(row["n_gare"])))
importo = row["importo_totale"]
if importo and importo > 0:
    k3.metric("Importo totale gare", f"€ {importo/1e9:,.1f} mld")
else:
    k3.metric("Importo totale gare", "N/A")

st.markdown("---")

# ── Per sede e classificazione ─────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Ricorsi per sede")
    df_sede = query_appalti(f"""
        SELECT nome_sede, COUNT(*) AS n_ricorsi
        FROM clean_input
        WHERE anno = {year}
        GROUP BY nome_sede
        ORDER BY n_ricorsi DESC
        LIMIT 15
    """, year)

    if not df_sede.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_sede["n_ricorsi"],
            y=df_sede["nome_sede"],
            orientation="h",
            marker_color="#6366f1",
        ))
        fig.update_layout(
            height=max(250, len(df_sede) * 25),
            margin={"t": 20, "b": 40, "l": 200},
            yaxis=dict(categoryorder="total ascending"),
            xaxis_title="N. ricorsi",
        )
        st.plotly_chart(fig, width="stretch")

with col_right:
    st.subheader("Per classificazione")
    df_class = query_appalti(f"""
        SELECT classificazione_ricorso, COUNT(*) AS n_ricorsi
        FROM clean_input
        WHERE anno = {year}
        GROUP BY classificazione_ricorso
        ORDER BY n_ricorsi DESC
        LIMIT 15
    """, year)

    if not df_class.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_class["n_ricorsi"],
            y=df_class["classificazione_ricorso"],
            orientation="h",
            marker_color="#059669",
        ))
        fig2.update_layout(
            height=max(250, len(df_class) * 25),
            margin={"t": 20, "b": 40, "l": 300},
            yaxis=dict(categoryorder="total ascending"),
            xaxis_title="N. ricorsi",
        )
        st.plotly_chart(fig2, width="stretch")

# ── Top gare per importo ───────────────────────────────────────────
st.markdown("---")
st.subheader("Top gare per importo")

df_gare = query_appalti(f"""
    SELECT
        codice_cig,
        oggetto_gara,
        importo_complessivo_gara,
        nome_sede,
        denominazione_amministrazione_appaltante,
        provincia,
        settore
    FROM clean_input
    WHERE anno = {year} AND codice_cig IS NOT NULL
        AND importo_complessivo_gara > 0
        AND importo_complessivo_gara < 1000000000
    ORDER BY importo_complessivo_gara DESC
    LIMIT 20
""", year)

if not df_gare.empty:
    df_gare["importo_fmt"] = df_gare["importo_complessivo_gara"].apply(
        lambda x: f"€ {x/1e6:,.0f} M" if x and x >= 1e6 else (f"€ {x:,.0f}" if x else "N/A")
    )
    st.dataframe(
        df_gare[["codice_cig", "oggetto_gara", "importo_fmt", "nome_sede",
                  "denominazione_amministrazione_appaltante", "provincia"]]
        .rename(columns={
            "codice_cig": "CIG",
            "oggetto_gara": "Oggetto gara",
            "importo_fmt": "Importo",
            "nome_sede": "Sede",
            "denominazione_amministrazione_appaltante": "Appaltante",
            "provincia": "Prov.",
        }),
        width="stretch",
        hide_index=True,
    )

# ── Per settore ────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Per settore")

df_settore = query_appalti(f"""
    SELECT settore, COUNT(*) AS n_ricorsi
    FROM clean_input
    WHERE anno = {year} AND settore IS NOT NULL
    GROUP BY settore
    ORDER BY n_ricorsi DESC
""", year)

if not df_settore.empty:
    fig3 = go.Figure()
    fig3.add_trace(go.Pie(
        labels=df_settore["settore"],
        values=df_settore["n_ricorsi"],
        hole=0.4,
    ))
    fig3.update_layout(
        height=350,
        margin={"t": 20, "b": 20},
    )
    st.plotly_chart(fig3, width="stretch")

st.caption("Dati: OpenGA (openga.giustizia-amministrativa.it) · CC BY 4.0")
