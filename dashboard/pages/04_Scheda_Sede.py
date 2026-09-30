"""Scheda Sede — Profilo completo di ogni sede della giustizia amministrativa."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lab_connectors.formatters import fmt_num, fmt_pct
from sources import YEAR_DEFAULT, YEARS, load_mart, query_cross

st.title("🏛️ Scheda Sede")

# ── Carica lista sedi dal compose ───────────────────────────────────
df_sedi_all = load_mart("ga_cross", "mart_sede_flusso", YEAR_DEFAULT)

if df_sedi_all.empty:
    st.warning("Nessuna sede disponibile.")
    st.stop()

sedi = sorted(df_sedi_all["nome_sede"].unique())
sede = st.selectbox("Seleziona sede", sedi)

year = st.selectbox("Anno", YEARS, index=YEARS.index(YEAR_DEFAULT))

# ── Trend pervenuti/definiti per la sede ───────────────────────────
st.subheader(f"Trend — {sede}")

df_sede_all = df_sedi_all[df_sedi_all["nome_sede"] == sede].sort_values("anno")

if not df_sede_all.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sede_all["anno"],
        y=df_sede_all["pervenuti"],
        mode="lines+markers",
        name="Pervenuti",
        line=dict(color="#6366f1", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df_sede_all["anno"],
        y=df_sede_all["definiti"],
        mode="lines+markers",
        name="Definiti",
        line=dict(color="#059669", width=2),
    ))
    fig.update_layout(
        height=350,
        margin={"t": 20, "b": 40},
        xaxis_title="Anno",
        yaxis_title="N. ricorsi",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, width="stretch")

    # KPI for selected year
    df_yr = df_sede_all[df_sede_all["anno"] == year]
    if not df_yr.empty:
        row = df_yr.iloc[0]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Pervenuti", fmt_num(row["pervenuti"]))
        k2.metric("Definiti", fmt_num(row["definiti"]))
        tasso_def = row["tasso_definizione"]
        k3.metric("Tasso definizione", fmt_pct(tasso_def, signed=False))
        tasso_acc = row["tasso_accoglimento"]
        k4.metric("Tasso accoglimento", fmt_pct(tasso_acc, signed=False))

# ── Tasso accoglimento per materia (sede specifica) ────────────────
st.markdown("---")
st.subheader("Tasso accoglimento per materia")

df_materie_sede = query_cross(f"""
    SELECT
        classificazione_ricorso,
        SUM(accoglimenti) AS accoglimenti,
        SUM(rigetti) AS rigetti,
        SUM(pervenuti) AS pervenuti
    FROM clean_input
    WHERE nome_sede = '{sede}' AND classificazione_ricorso IS NOT NULL
    GROUP BY classificazione_ricorso
    HAVING SUM(pervenuti) >= 10
    ORDER BY pervenuti DESC
""", years=(year,))

if not df_materie_sede.empty:
    df_materie_sede["tasso_accoglimento"] = (
        df_materie_sede["accoglimenti"] * 100 /
        (df_materie_sede["accoglimenti"] + df_materie_sede["rigetti"]).replace(0, 1)
    ).round(1)

    top_n = st.slider("Top materie", 5, 30, 15, key="top_materie_sede")
    df_plot = df_materie_sede.head(top_n)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_plot["pervenuti"],
        y=df_plot["classificazione_ricorso"],
        orientation="h",
        marker_color="#6366f1",
        name="Pervenuti",
    ))
    fig2.update_layout(
        height=max(300, top_n * 22),
        margin={"t": 20, "b": 40, "l": 350},
        yaxis=dict(categoryorder="total ascending"),
        xaxis_title="N. ricorsi pervenuti",
    )
    st.plotly_chart(fig2, width="stretch")

    with st.expander("Tabella completa"):
        st.dataframe(
            df_materie_sede[["classificazione_ricorso", "pervenuti", "accoglimenti", "rigetti", "tasso_accoglimento"]]
            .rename(columns={
                "classificazione_ricorso": "Materia",
                "pervenuti": "Pervenuti",
                "accoglimenti": "Accolti",
                "rigetti": "Rigetti",
                "tasso_accoglimento": "Tasso %",
            }),
            width="stretch",
            hide_index=True,
        )

# ── Confronto con altre sedi ───────────────────────────────────────
st.markdown("---")
st.subheader("Confronto con altre sedi")

if not df_sedi_all.empty:
    df_confronto = df_sedi_all[df_sedi_all["anno"] == year].copy()
    df_confronto["tasso_accoglimento"] = df_confronto["tasso_accoglimento"].fillna(0)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_confronto["pervenuti"],
        y=df_confronto["tasso_accoglimento"],
        mode="markers+text",
        text=df_confronto["nome_sede"].str[:25],
        textposition="top center",
        textfont=dict(size=9),
        marker=dict(
            size=15,
            color=["#6366f1" if s == sede else "#d1d5db" for s in df_confronto["nome_sede"]],
        ),
    ))
    fig3.update_layout(
        height=450,
        margin={"t": 20, "b": 40},
        xaxis_title="N. ricorsi pervenuti",
        yaxis_title="Tasso accoglimento %",
    )
    st.plotly_chart(fig3, width="stretch")

st.caption("Dati: OpenGA (openga.giustizia-amministrativa.it) · CC BY 4.0")
