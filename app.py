import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

FICHIER = "arrivees.csv"

# ======================
# Charger données
# ======================
def charger_donnees():
    if os.path.exists(FICHIER):
        df = pd.read_csv(FICHIER)
        df['date_heure_arrivee'] = pd.to_datetime(df['date_heure_arrivee'])
        return df
    return pd.DataFrame(columns=["nom_patient", "date_heure_arrivee", "latitude", "longitude"])

# ======================
# Sauvegarder
# ======================
def sauvegarder(df):
    df.to_csv(FICHIER, index=False)

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Hospital Tracker", layout="wide")
st.title("🏥 Dashboard des arrivées des patients")

df = charger_donnees()

menu = st.sidebar.radio("Menu", ["➕ Ajouter", "📊 Dashboard", "📋 Données"])

# ======================
# AJOUT
# ======================
if menu == "➕ Ajouter":
    st.header("Ajouter une arrivée")

    nom = st.text_input("Nom du patient")

    col1, col2 = st.columns(2)
    lat = col1.number_input("Latitude", value=0.0)
    lon = col2.number_input("Longitude", value=0.0)

    if st.button("Enregistrer"):
        if nom:
            nouvelle_ligne = {
                "nom_patient": nom,
                "date_heure_arrivee": datetime.now(),
                "latitude": lat,
                "longitude": lon
            }

            df = pd.concat([df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
            sauvegarder(df)

            st.success("✅ Arrivée enregistrée")
        else:
            st.error("⚠️ Nom requis")

# ======================
# DASHBOARD
# ======================
elif menu == "📊 Dashboard":
    st.header("📊 Analyse des données")

    if df.empty:
        st.warning("Aucune donnée disponible")
    else:
        # Filtres
        st.subheader("📅 Filtrer par date")
        date_min = df['date_heure_arrivee'].min().date()
        date_max = df['date_heure_arrivee'].max().date()

        date_selection = st.date_input("Choisir période", [date_min, date_max])

        df_filtre = df[
            (df['date_heure_arrivee'].dt.date >= date_selection[0]) &
            (df['date_heure_arrivee'].dt.date <= date_selection[1])
        ]

        # KPI
        st.markdown("## 📊 Indicateurs clés")
        col1, col2 = st.columns(2)
        col1.metric("Total patients", len(df_filtre))
        col2.metric("Heure de pointe", df_filtre['date_heure_arrivee'].dt.hour.mode()[0] if not df_filtre.empty else "-")

        st.markdown("---")

        # ======================
        # Graphique 1 : Histogramme
        # ======================
        st.subheader("📈 Arrivées par heure")

        df_filtre['heure'] = df_filtre['date_heure_arrivee'].dt.hour

        fig1 = px.histogram(
            df_filtre,
            x="heure",
            nbins=24,
            title="Distribution des arrivées par heure",
            color_discrete_sequence=["#1f77b4"]
        )

        st.plotly_chart(fig1, use_container_width=True)

        # ======================
        # Graphique 2 : Courbe
        # ======================
        st.subheader("📈 Évolution des arrivées")

        par_jour = df_filtre.groupby(df_filtre['date_heure_arrivee'].dt.date).size().reset_index(name="patients")

        fig2 = px.line(
            par_jour,
            x="date_heure_arrivee",
            y="patients",
            markers=True
        )

        st.plotly_chart(fig2, use_container_width=True)

        # ======================
        # Graphique 3 : Heatmap
        # ======================
        st.subheader("🔥 Heatmap (jour vs heure)")

        df_filtre['jour'] = df_filtre['date_heure_arrivee'].dt.day_name()

        heatmap_data = df_filtre.pivot_table(
            index='jour',
            columns='heure',
            aggfunc='size',
            fill_value=0
        )

        fig3 = px.imshow(
            heatmap_data,
            aspect="auto",
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig3, use_container_width=True)

        # ======================
        # Carte
        # ======================
        st.subheader("📍 Localisation des patients")

        fig_map = px.scatter_mapbox(
            df_filtre,
            lat="latitude",
            lon="longitude",
            hover_name="nom_patient",
            zoom=10,
            height=400
        )

        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)

# ======================
# DONNÉES
# ======================
elif menu == "📋 Données":
    st.header("📋 Données enregistrées")

    if df.empty:
        st.warning("Aucune donnée")
    else:
        st.dataframe(df)

        # Export CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📤 Télécharger CSV", csv, "arrivees.csv", "text/csv")
