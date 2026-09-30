"""Panoramica — Visione d'insieme della giustizia amministrativa italiana."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lab_connectors.formatters import fmt_num, fmt_pct
from sources import YEAR_DEFAULT, YEARS, load_mart

st.title("⚖️ Giustizia Amministrativa")
st.markdown("31 sedi, 2017–2026 — contenzioso, sentenze e provvedimenti da OpenGA.")

year = st.selectbox("Anno", YEARS, index=YEARS.index(YEAR_DEFAULT))

# ── KPI nazionali ──────────────────────────────────────────────────
df = load_mart("ga_cross", "mart_panoramica", year)

if df.empty:
    st.warning("Nessun dato disponibile per quest'anno.")
    st.stop()

# ga_cross mart_panoramica contains ALL years in one file
# Filter to selected year for KPI
df_year = df[df["anno"] == year]
if df_year.empty:
    st.warning(f"Nessun dato per l'anno {year}.")
    st.stop()

row = df_year.iloc[0]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Ricorsi pervenuti", fmt_num(row["totale_pervenuti"]))
k2.metric("Ricorsi definiti", fmt_num(row["totale_definiti"]))
k3.metric("Tasso definizione", fmt_pct(row["tasso_definizione"], signed=False))
k4.metric("Tasso accoglimento", fmt_pct(row["tasso_accoglimento"], signed=False))
k5.metric("Sedi attive", fmt_num(row["n_sedi"]))

st.markdown("---")

# ── Trend nazionale 2017–2026 ──────────────────────────────────────
st.subheader("Trend nazionale")

# ga_cross mart_panoramica has all years
df_trend = df.copy()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df_trend["anno"],
    y=df_trend["totale_pervenuti"],
    name="Pervenuti",
    marker_color="#6366f1",
))
fig.add_trace(go.Bar(
    x=df_trend["anno"],
    y=df_trend["totale_definiti"],
    name="Definiti",
    marker_color="#059669",
))
fig.update_layout(
    barmode="group",
    height=350,
    margin={"t": 20, "b": 40},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, width="stretch")

# ── Tassi nel tempo ────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Tasso di definizione")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_trend["anno"],
        y=df_trend["tasso_definizione"],
        mode="lines+markers",
        line=dict(color="#6366f1", width=3),
        name="Tasso definizione",
    ))
    fig2.add_hline(y=100, line_dash="dash", line_color="gray",
                   annotation_text="100% = bilanciato")
    fig2.update_layout(
        height=300,
        margin={"t": 20, "b": 40},
        yaxis_title="%",
        yaxis=dict(range=[0, max(df_trend["tasso_definizione"].max() * 1.1, 150)]),
    )
    st.plotly_chart(fig2, width="stretch")

with col_right:
    st.subheader("Tasso di accoglimento")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_trend["anno"],
        y=df_trend["tasso_accoglimento"],
        mode="lines+markers",
        line=dict(color="#059669", width=3),
        name="Tasso accoglimento",
    ))
    fig3.update_layout(
        height=300,
        margin={"t": 20, "b": 40},
        yaxis_title="%",
        yaxis=dict(range=[0, 80]),
    )
    st.plotly_chart(fig3, width="stretch")

# ── Top 10 sedi per volume ────────────────────────────────────────
st.markdown("---")
st.subheader(f"Top sedi per volume — {year}")

df_sedi = load_mart("ga_cross", "mart_sede_flusso", year)
if not df_sedi.empty:
    # Filter to selected year
    df_sedi_yr = df_sedi[df_sedi["anno"] == year] if "anno" in df_sedi.columns else df_sedi
    df_top = (
        df_sedi_yr.groupby("nome_sede", as_index=False)
        .agg({"pervenuti": "sum", "definiti": "sum", "accoglimenti": "sum", "rigetti": "sum"})
        .nlargest(10, "pervenuti")
    )
    df_top["tasso_accoglimento"] = (
        df_top["accoglimenti"] * 100 / (df_top["accoglimenti"] + df_top["rigetti"]).replace(0, 1)
    ).round(1)

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_top["pervenuti"],
        y=df_top["nome_sede"],
        orientation="h",
        marker_color="#6366f1",
        name="Pervenuti",
    ))
    fig4.add_trace(go.Bar(
        x=df_top["definiti"],
        y=df_top["nome_sede"],
        orientation="h",
        marker_color="#059669",
        name="Definiti",
    ))
    fig4.update_layout(
        barmode="group",
        height=400,
        margin={"t": 20, "b": 40, "l": 200},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(categoryorder="total ascending"),
    )
    st.plotly_chart(fig4, width="stretch")

    with st.expander("Dettaglio tassi per sede"):
        st.dataframe(
            df_top[["nome_sede", "pervenuti", "definiti", "tasso_accoglimento"]]
            .rename(columns={
                "nome_sede": "Sede",
                "pervenuti": "Pervenuti",
                "definiti": "Definiti",
                "tasso_accoglimento": "Tasso accoglimento %",
            }),
            use_container_width=True,
            hide_index=True,
        )

st.caption("Dati: OpenGA (openga.giustizia-amministrativa.it) · CC BY 4.0")
