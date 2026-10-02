"""Mezzi di definizione — come si chiudono i ricorsi (sentenza vs decreto)."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from lab_connectors.formatters import fmt_num, fmt_pct
from sources import (
    YEAR_DEFAULT,
    YEARS,
    load_definizioni_mezzi_anno,
    load_definizioni_outlier,
    load_definizioni_sintesi_sede,
)

st.title("⚙️ Mezzi di definizione")
st.markdown(
    "Come si chiudono i ricorsi: **sentenza** vs **decreto decisori** vs altri provvedimenti. "
    "Complementare a *Esiti* (accoglimento/rigetto). "
    "Fonte: compose `ga_definizioni` (grano sede×anno)."
)

year = st.selectbox("Anno", YEARS, index=YEARS.index(YEAR_DEFAULT))

df_all = load_definizioni_mezzi_anno(year)
if df_all.empty:
    st.warning("Nessun dato disponibile per compose ga_definizioni.")
    st.stop()

df_year = df_all[df_all["anno"] == year]
if df_year.empty:
    st.warning(f"Nessun dato per l'anno {year}.")
    st.stop()

row = df_year.iloc[0]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Definiti (meccanismo)", fmt_num(row["totale_definiti"]))
k2.metric("% con sentenza", fmt_pct(row["sentenza_pct"], signed=False))
k3.metric("% con decreto", fmt_pct(row["decreto_pct"], signed=False))
k4.metric("% sentenze brevi", fmt_pct(row["quota_brevi_pct"], signed=False))
k5.metric("Tasso accoglimento", fmt_pct(row["tasso_accoglimento"], signed=False))

st.caption(
    "Nota: `tasso_accoglimento` qui è calcolato su `ga_ricorsi_definiti` "
    "(support del compose), non su `tipo_decisione`."
)

st.markdown("---")

# ── Trend mix nazionale ────────────────────────────────────────────
st.subheader("Trend nazionale — mix di definizione")

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df_all["anno"],
    y=df_all["sentenza_pct"],
    name="% sentenza",
    marker_color="#059669",
))
fig.add_trace(go.Bar(
    x=df_all["anno"],
    y=df_all["decreto_pct"],
    name="% decreto decisori",
    marker_color="#f59e0b",
))
fig.add_trace(go.Bar(
    x=df_all["anno"],
    y=df_all["altri_pct"],
    name="% altri provvedimenti",
    marker_color="#94a3b8",
))
fig.add_trace(go.Scatter(
    x=df_all["anno"],
    y=df_all["quota_brevi_pct"],
    name="% sentenze brevi",
    mode="lines+markers",
    line=dict(color="#6366f1", width=2, dash="dot"),
    yaxis="y2",
))
fig.update_layout(
    barmode="stack",
    height=380,
    margin={"t": 20, "b": 40},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis=dict(title="% definizioni", range=[0, 100]),
    yaxis2=dict(title="% brevi", overlaying="y", side="right", range=[0, 40]),
)
st.plotly_chart(fig, width="stretch")

# ── Sintesi per sede ───────────────────────────────────────────────
st.markdown("---")
st.subheader(f"Mezzi per sede — {year}")

df_sedi = load_definizioni_sintesi_sede(year)
if not df_sedi.empty:
    df_y = df_sedi[df_sedi["anno"] == year].copy()
    if not df_y.empty:
        df_y = df_y.sort_values("totale_definiti", ascending=False)
        top_n = st.slider("Top sedi", 5, 20, 10, key="top_mezzi_sedi")
        df_plot = df_y.head(top_n)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_plot["sentenza_pct"],
            y=df_plot["nome_sede"],
            orientation="h",
            name="% sentenza",
            marker_color="#059669",
        ))
        fig2.add_trace(go.Bar(
            x=df_plot["decreto_pct"],
            y=df_plot["nome_sede"],
            orientation="h",
            name="% decreto",
            marker_color="#f59e0b",
        ))
        fig2.add_trace(go.Bar(
            x=df_plot["altri_pct"],
            y=df_plot["nome_sede"],
            orientation="h",
            name="% altri",
            marker_color="#94a3b8",
        ))
        fig2.update_layout(
            barmode="stack",
            height=max(320, top_n * 28),
            margin={"t": 20, "b": 40, "l": 200},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(title="% definizioni", range=[0, 100]),
            yaxis=dict(categoryorder="total ascending"),
        )
        st.plotly_chart(fig2, width="stretch")

        # Scatter: volume vs quota sentenza / quota brevi
        st.subheader("Volume vs mix")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_y["totale_definiti"],
            y=df_y["sentenza_pct"],
            mode="markers+text",
            text=df_y["nome_sede"].str[:22],
            textposition="top center",
            textfont=dict(size=9),
            marker=dict(size=12, color="#059669"),
            name="Sedi",
            hovertemplate="%{text}<br>Definiti: %{x:,}<br>Sentenza: %{y:.1f}%<extra></extra>",
        ))
        fig3.update_layout(
            height=420,
            margin={"t": 20, "b": 40},
            xaxis_title="N. definiti (meccanismo)",
            yaxis_title="% con sentenza",
            yaxis=dict(range=[0, 100]),
        )
        st.plotly_chart(fig3, width="stretch")

        with st.expander("Tabella completa sedi"):
            cols = [
                "nome_sede",
                "totale_definiti",
                "sentenza_pct",
                "decreto_pct",
                "altri_pct",
                "quota_brevi_pct",
                "tasso_accoglimento",
            ]
            st.dataframe(
                df_y[cols].rename(columns={
                    "nome_sede": "Sede",
                    "totale_definiti": "Definiti",
                    "sentenza_pct": "% sentenza",
                    "decreto_pct": "% decreto",
                    "altri_pct": "% altri",
                    "quota_brevi_pct": "% brevi",
                    "tasso_accoglimento": "Tasso accogl. %",
                }),
                width="stretch",
                hide_index=True,
            )

# ── Outlier ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader(f"Sedi con mix anomalo vs media nazionale — {year}")

df_out = load_definizioni_outlier(year)
if not df_out.empty:
    df_oy = df_out[df_out["anno"] == year].copy()
    if not df_oy.empty:
        df_oy = df_oy.sort_values("delta_decreto_pct", ascending=False)
        top_out = st.slider("Top outlier", 3, 15, 8, key="top_outlier")
        df_plot_o = df_oy.head(top_out)

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=df_plot_o["delta_decreto_pct"],
            y=df_plot_o["nome_sede"],
            orientation="h",
            marker_color=[
                "#dc2626" if v > 0 else "#059669" for v in df_plot_o["delta_decreto_pct"]
            ],
            name="Δ %decreto vs nazionale",
        ))
        fig4.update_layout(
            height=max(240, top_out * 28),
            margin={"t": 20, "b": 40, "l": 200},
            xaxis_title="Δ punti % sul mix decreti (sede − nazionale)",
            yaxis=dict(categoryorder="total ascending"),
        )
        st.plotly_chart(fig4, width="stretch")

        st.dataframe(
            df_plot_o[[
                "nome_sede",
                "totale_definiti",
                "sentenza_pct",
                "decreto_pct",
                "delta_decreto_pct",
                "quota_brevi_pct",
            ]].rename(columns={
                "nome_sede": "Sede",
                "totale_definiti": "Definiti",
                "sentenza_pct": "% sentenza",
                "decreto_pct": "% decreto",
                "delta_decreto_pct": "Δ decreto pp",
                "quota_brevi_pct": "% brevi",
            }),
            width="stretch",
            hide_index=True,
        )

st.caption(
    "Dati: OpenGA via compose ga_definizioni · CC BY 4.0 · "
    "Complementare a ga_cross (grano materia)."
)
