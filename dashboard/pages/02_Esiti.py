"""Esiti Ricorsi — Tasso accoglimento per materia e sede."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lab_connectors.formatters import fmt_num, fmt_pct
from sources import YEAR_DEFAULT, YEARS, query_definiti, query_cross, load_mart

st.title("⚖️ Esiti dei Ricorsi")

year = st.selectbox("Anno", YEARS, index=YEARS.index(YEAR_DEFAULT))

# ── KPI esiti ──────────────────────────────────────────────────────
df_esiti = query_definiti(f"""
    SELECT
        esito_provvedimento,
        SUM(numero_ricorsi_definiti) AS totale
    FROM clean_input
    WHERE anno = {year}
    GROUP BY esito_provvedimento
    ORDER BY totale DESC
""", year)

if df_esiti.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

totale = int(df_esiti["totale"].sum())
accoglimenti = int(df_esiti.loc[df_esiti["esito_provvedimento"] == "ACCOGLIE", "totale"].sum())
rigetti = int(df_esiti.loc[df_esiti["esito_provvedimento"] == "RESPINGE", "totale"].sum())
inammissibili = int(df_esiti.loc[
    df_esiti["esito_provvedimento"].str.contains("INAMMISSIBILE", na=False), "totale"
].sum())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Totale definiti", fmt_num(totale))
k2.metric("Accolti", fmt_num(accoglimenti))
k3.metric("Rigetti", fmt_num(rigetti))
k4.metric("Inammissibili", fmt_num(inammissibili))

st.markdown("---")

# ── Distribuzione esiti ────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Distribuzione esiti")
    top_n = st.slider("Top esiti", 5, 20, 10, key="top_esiti")
    df_top_esiti = df_esiti.head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_top_esiti["totale"],
        y=df_top_esiti["esito_provvedimento"],
        orientation="h",
        marker_color="#6366f1",
    ))
    fig.update_layout(
        height=max(250, top_n * 25),
        margin={"t": 20, "b": 40, "l": 250},
        yaxis=dict(categoryorder="total ascending"),
        xaxis_title="N. ricorsi",
    )
    st.plotly_chart(fig, width="stretch")

with col_right:
    st.subheader("Dettaglio")
    st.dataframe(
        df_esiti.rename(columns={
            "esito_provvedimento": "Esito",
            "totale": "N. ricorsi",
        }),
        width="stretch",
        hide_index=True,
    )

# ── Tasso accoglimento per materia ────────────────────────────────
st.markdown("---")
st.subheader("Tasso accoglimento per materia")

# Use ga_cross compose (has all years in one mart file)
df_materie_all = load_mart("ga_cross", "mart_esiti", year)
if not df_materie_all.empty:
    df_materie = (
        df_materie_all[df_materie_all["anno"] == year]
        .groupby("classificazione_ricorso", as_index=False)
        .agg({
            "accoglimenti": "sum",
            "rigetti": "sum",
            "pervenuti": "sum",
        })
        .query("pervenuti >= 50")
        .sort_values("pervenuti", ascending=False)
    )

    if not df_materie.empty:
        df_materie["tasso_accoglimento"] = (
            df_materie["accoglimenti"] * 100 /
            (df_materie["accoglimenti"] + df_materie["rigetti"]).replace(0, 1)
        ).round(1)

        top_materie = st.slider("Top materie", 5, 30, 15, key="top_materie")
        df_plot = df_materie.head(top_materie)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_plot["pervenuti"],
            y=df_plot["classificazione_ricorso"],
            orientation="h",
            marker_color="#6366f1",
            name="Pervenuti",
        ))
        fig2.update_layout(
            height=max(300, top_materie * 22),
            margin={"t": 20, "b": 40, "l": 350},
            yaxis=dict(categoryorder="total ascending"),
            xaxis_title="N. ricorsi pervenuti",
        )
        st.plotly_chart(fig2, width="stretch")

        # Scatter: volume vs tasso accoglimento
        st.subheader("Volume vs tasso accoglimento")
        # Label only top 10 by volume to avoid overlap
        top_labels = df_materie.nlargest(10, "pervenuti")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_materie["pervenuti"],
            y=df_materie["tasso_accoglimento"],
            mode="markers",
            marker=dict(
                size=df_materie["pervenuti"] / df_materie["pervenuti"].max() * 40 + 5,
                color=df_materie["tasso_accoglimento"],
                colorscale="RdYlGn",
                colorbar=dict(title="Tasso %"),
            ),
            text=df_materie["classificazione_ricorso"],
            hovertemplate="%{text}<br>Pervenuti: %{x:,}<br>Tasso: %{y:.1f}%<extra></extra>",
        ))
        # Add labels only for top 10
        for _, row in top_labels.iterrows():
            fig3.add_annotation(
                x=row["pervenuti"],
                y=row["tasso_accoglimento"],
                text=row["classificazione_ricorso"][:35],
                showarrow=True,
                arrowhead=0,
                ax=0,
                ay=-25,
                font=dict(size=9),
            )
        fig3.update_layout(
            height=500,
            margin={"t": 20, "b": 40},
            xaxis_title="N. ricorsi pervenuti",
            yaxis_title="Tasso accoglimento %",
            yaxis=dict(range=[0, 105]),
        )
        st.plotly_chart(fig3, width="stretch")

        with st.expander("Tabella completa materie"):
            st.dataframe(
                df_materie[["classificazione_ricorso", "pervenuti", "accoglimenti", "rigetti", "tasso_accoglimento"]]
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

st.caption("Dati: OpenGA (openga.giustizia-amministrativa.it) · CC BY 4.0")
