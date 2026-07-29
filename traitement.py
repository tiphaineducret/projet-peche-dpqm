import pandas as pd


# Chargement des fichiers
sorties = pd.read_csv("data/sorties_peche_exercice.csv")
navires = pd.read_csv("data/navires_referentiel.csv")
armements = pd.read_csv("data/armements.csv")
quotas = pd.read_csv("data/quotas.csv")


# Normalisation des noms de bateaux
sorties["bateau_normalise"] = (
    sorties["bateau"]
    .str.strip()
    .str.lower()
    .str.replace("-", " ")
)

navires["bateau_normalise"] = (
    navires["nom_bateau"]
    .str.strip()
    .str.lower()
    .str.replace("-", " ")
)


# Normalisation des campagnes
quotas["campagne_normalisee"] = (
    quotas["campagne"]
    .str.strip()
    .str.replace("/", "-")
)


# Conversion des dates
sorties["date_normalisee"] = pd.to_datetime(
    sorties["date_sortie"],
    format="mixed",
    dayfirst=True
)


# Normalisation des zones
sorties["zone_normalisee"] = (
    sorties["zone"]
    .str.strip()
    .str.lower()
    .str.replace("-", " ")
    .str.replace("crozzet", "crozet")
)


# Ajout de l'armement correspondant à chaque bateau
sorties_avec_armement = sorties.merge(
    navires[["bateau_normalise", "armement_id"]],
    on="bateau_normalise",
    how="left"
)


# Ajout du nom de l'armement
sorties_completes = sorties_avec_armement.merge(
    armements,
    on="armement_id",
    how="left"
)


# Attribution d'une campagne à chaque sortie
sorties_completes["annee"] = sorties_completes["date_normalisee"].dt.year

sorties_completes["campagne_sortie"] = (
    sorties_completes["annee"].astype(str)
    + "-"
    + (sorties_completes["annee"] + 1).astype(str)
)


# Conservation des sorties utilisables pour les calculs
sorties_calcul = sorties_completes[
    (sorties_completes["armement_id"].notna())
    & (sorties_completes["quantite_kg"].notna())
    & (sorties_completes["quantite_kg"] >= 0)
]


# Calcul des quantités pêchées
consommation = (
    sorties_calcul
    .groupby(
        ["armement_id", "nom_armement", "espece", "campagne_sortie"]
    )["quantite_kg"]
    .sum()
    .reset_index()
)

consommation = consommation.rename(
    columns={"quantite_kg": "quantite_pechee_kg"}
)


# Rapprochement entre les quantités pêchées et les quotas
quotas["campagne_sortie"] = quotas["campagne_normalisee"]

suivi_quotas = consommation.merge(
    quotas,
    on=["armement_id", "espece", "campagne_sortie"],
    how="left"
)

suivi_quotas = suivi_quotas.rename(
    columns={"quota_kg_alloue": "quota_alloue_kg"}
)


# Calcul du quota restant et du taux de consommation
suivi_quotas["quota_restant_kg"] = (
    suivi_quotas["quota_alloue_kg"]
    - suivi_quotas["quantite_pechee_kg"]
)

suivi_quotas["taux_consommation_pct"] = (
    suivi_quotas["quantite_pechee_kg"]
    / suivi_quotas["quota_alloue_kg"]
    * 100
).round(2)


# Attribution d'un statut à chaque quota
statuts = []

for taux in suivi_quotas["taux_consommation_pct"]:
    if pd.isna(taux):
        statuts.append("Quota non renseigné")
    elif taux > 100:
        statuts.append("Quota dépassé")
    else:
        statuts.append("Quota respecté")

suivi_quotas["statut_quota"] = statuts
