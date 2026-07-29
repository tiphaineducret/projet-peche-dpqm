import streamlit as st
import plotly.express as px

from traitement import sorties_completes, suivi_quotas


st.set_page_config(
    page_title="Suivi des quotas de pêche",
    layout="wide"
)

st.title("Tableau de bord du suivi des quotas de pêche")

st.write(
    "Cette application permet de suivre les quantités pêchées, "
    "les quotas alloués et l'historique des sorties de pêche."
)

tab1, tab2 = st.tabs(["Suivi des quotas", "Historique des sorties"])

with tab1:
    st.subheader("Suivi de la consommation des quotas")

    filtre1, filtre2, filtre3 = st.columns(3)

    with filtre1:
        campagne = st.selectbox(
            "Choisir une campagne",
            ["Toutes"] + suivi_quotas["campagne_sortie"].unique().tolist()
        )

    with filtre2:
        armement = st.selectbox(
            "Choisir un armement",
            ["Tous"] + suivi_quotas["nom_armement"].unique().tolist()
        )

    with filtre3:
        espece = st.selectbox(
            "Choisir une espèce",
            ["Toutes"] + suivi_quotas["espece"].unique().tolist()
        )

    suivi_filtre = suivi_quotas.copy()

    if campagne != "Toutes":
        suivi_filtre = suivi_filtre[
            suivi_filtre["campagne_sortie"] == campagne
        ]

    if armement != "Tous":
        suivi_filtre = suivi_filtre[
            suivi_filtre["nom_armement"] == armement
        ]

    if espece != "Toutes":
        suivi_filtre = suivi_filtre[
            suivi_filtre["espece"] == espece
        ]

    suivi_avec_quota = suivi_filtre[
        suivi_filtre["quota_alloue_kg"].notna()
    ]

    quantite_comparee = suivi_avec_quota["quantite_pechee_kg"].sum()
    quota_total = suivi_avec_quota["quota_alloue_kg"].sum()
    quota_restant = suivi_avec_quota["quota_restant_kg"].sum()

    if suivi_avec_quota.shape[0] == 0:
        quantite_comparee_affichee = "Non calculable"
        quota_total_affiche = "Non renseigné"
        quota_restant_affiche = "Non calculable"
    else:
        quantite_comparee_affichee = round(quantite_comparee, 1)
        quota_total_affiche = round(quota_total, 1)
        quota_restant_affiche = round(quota_restant, 1)

    quotas_depasses = suivi_filtre[
        suivi_filtre["statut_quota"] == "Quota dépassé"
    ]

    nombre_depassements = quotas_depasses.shape[0]

    nombre_quotas_absents = suivi_filtre[
        suivi_filtre["statut_quota"] == "Quota non renseigné"
    ].shape[0]

    quantite_sans_quota = suivi_filtre[
        suivi_filtre["statut_quota"] == "Quota non renseigné"
    ]["quantite_pechee_kg"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Quantité comparée aux quotas (kg)",
            quantite_comparee_affichee
        )

    with col2:
        st.metric("Quota alloué (kg)", quota_total_affiche)

    with col3:
        st.metric("Quota restant (kg)", quota_restant_affiche)

    with col4:
        st.metric("Quotas dépassés", nombre_depassements)

    colonnes_suivi = [
        "campagne_sortie",
        "nom_armement",
        "espece",
        "quantite_pechee_kg",
        "quota_alloue_kg",
        "quota_restant_kg",
        "taux_consommation_pct",
        "statut_quota"
    ]

    if nombre_depassements == 0:
        st.markdown(
            ":green[Aucun quota dépassé pour cette sélection.]"
        )
    else:
        st.markdown(
            ":red["
            + str(nombre_depassements)
            + " quota(s) dépassé(s) pour cette sélection.]"
        )

        st.write("Liste des quotas dépassés :")
        st.dataframe(
            quotas_depasses[colonnes_suivi],
            width="stretch"
        )

    if nombre_quotas_absents > 0:
        st.warning(
            str(nombre_quotas_absents)
            + " quota(s) non renseigné(s), correspondant à "
            + str(round(quantite_sans_quota, 1))
            + " kg pêchés non inclus dans les indicateurs de quota."
        )

    nombre_par_statut = (
        suivi_filtre
        .groupby("statut_quota")
        .size()
        .reset_index(name="Nombre")
    )

    st.subheader("Répartition des statuts des quotas")

    fig = px.bar(
        nombre_par_statut,
        x="statut_quota",
        y="Nombre",
        color="statut_quota",
        color_discrete_map={
            "Quota respecté": "#2E8B57",
            "Quota dépassé": "#D64545",
            "Quota non renseigné": "#808080"
        },
        labels={
            "statut_quota": "Statut",
            "Nombre": "Nombre de situations"
        }
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Détail du suivi")

    st.dataframe(
        suivi_filtre[colonnes_suivi],
        width="stretch"
    )

with tab2:
    st.subheader("Historique des sorties de pêche")

    filtre4, filtre5, filtre6, filtre7 = st.columns(4)

    with filtre4:
        campagne_historique = st.selectbox(
            "Choisir une campagne pour l'historique",
            ["Toutes"]
            + sorties_completes["campagne_sortie"].unique().tolist()
        )

    with filtre5:
        bateau_historique = st.selectbox(
            "Choisir un bateau",
            ["Tous"] + sorties_completes["bateau"].unique().tolist()
        )

    with filtre6:
        espece_historique = st.selectbox(
            "Choisir une espèce pour l'historique",
            ["Toutes"] + sorties_completes["espece"].unique().tolist()
        )

    with filtre7:
        zone_historique = st.selectbox(
            "Choisir une zone",
            ["Toutes"]
            + sorties_completes["zone_normalisee"].dropna().unique().tolist()
        )

    sorties_filtrees = sorties_completes.copy()

    if campagne_historique != "Toutes":
        sorties_filtrees = sorties_filtrees[
            sorties_filtrees["campagne_sortie"] == campagne_historique
        ]

    if bateau_historique != "Tous":
        sorties_filtrees = sorties_filtrees[
            sorties_filtrees["bateau"] == bateau_historique
        ]

    if espece_historique != "Toutes":
        sorties_filtrees = sorties_filtrees[
            sorties_filtrees["espece"] == espece_historique
        ]

    if zone_historique != "Toutes":
        sorties_filtrees = sorties_filtrees[
            sorties_filtrees["zone_normalisee"] == zone_historique
        ]
        
    nombre_sorties = sorties_filtrees.shape[0]

    sorties_valides = sorties_filtrees[
        sorties_filtrees["quantite_kg"] >= 0
    ]

    quantite_totale_sorties = sorties_valides["quantite_kg"].sum()

    nombre_anomalies = sorties_filtrees["quantite_kg"].isna().sum()
    nombre_anomalies = nombre_anomalies + (
        sorties_filtrees["quantite_kg"] < 0
    ).sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Nombre de sorties", nombre_sorties)

    with col2:
        st.metric(
            "Quantité totale pêchée (kg)",
            round(quantite_totale_sorties, 1)
        )

    with col3:
        st.metric("Quantités écartées du calcul", nombre_anomalies)

    if nombre_sorties == 0:
        st.warning("Aucune sortie ne correspond aux filtres sélectionnés.")

    quantites_par_date = (
        sorties_valides
        .groupby("date_normalisee")["quantite_kg"]
        .sum()
        .reset_index()
    )

    st.subheader("Évolution des quantités pêchées")

    if quantites_par_date.shape[0] > 0:
        fig_historique = px.line(
            quantites_par_date,
            x="date_normalisee",
            y="quantite_kg",
            markers=True,
            labels={
                "date_normalisee": "Date",
                "quantite_kg": "Quantité pêchée (kg)"
            }
        )

        st.plotly_chart(fig_historique, use_container_width=True)
    else:
        st.info("Aucune quantité valide à représenter sur le graphique.")

    colonnes_historique = [
        "id_sortie",
        "date_normalisee",
        "bateau",
        "nom_armement",
        "zone_normalisee",
        "espece",
        "quantite_kg"
    ]

    st.subheader("Détail des sorties")

    st.dataframe(
        sorties_filtrees[colonnes_historique],
        width="stretch"
    )

with st.expander("Voir la qualité des données"):
    quantites_manquantes = sorties_completes["quantite_kg"].isna().sum()

    quantites_negatives = (
        sorties_completes["quantite_kg"] < 0
    ).sum()

    zones_manquantes = sorties_completes["zone"].isna().sum()

    armements_manquants = (
        sorties_completes["armement_id"].isna().sum()
    )

    st.write("Quantités manquantes :", quantites_manquantes)
    st.write("Quantités négatives :", quantites_negatives)
    st.write("Zones manquantes :", zones_manquantes)
    st.write("Sorties sans armement :", armements_manquants)
