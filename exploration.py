import pandas as pd

# 1. Chargement des fichiers
sorties = pd.read_csv("data/sorties_peche_exercice.csv")
navires = pd.read_csv("data/navires_referentiel.csv")
armements = pd.read_csv("data/armements.csv")
quotas = pd.read_csv("data/quotas.csv")

# 2. Normalisation des données

# Noms des bateaux
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

# Campagnes des quotas
quotas["campagne_normalisee"] = (
    quotas["campagne"]
    .str.strip()
    .str.replace("/", "-")
)
quotas["campagne_sortie"] = quotas["campagne_normalisee"]

# Dates des sorties
sorties["date_normalisee"] = pd.to_datetime(
    sorties["date_sortie"],
    format="mixed",
    dayfirst=True
)

# Zones
sorties["zone_normalisee"] = (
    sorties["zone"]
    .str.strip()
    .str.lower()
    .str.replace("-", " ")
    .str.replace("crozzet", "crozet")
)

# 3. Contrôles de qualité

bateaux_sorties = sorties["bateau_normalise"].unique()
bateaux_navires = navires["bateau_normalise"].unique()

print("Bateaux sans correspondance dans le référentiel :")
for bateau in bateaux_sorties:
    if bateau not in bateaux_navires:
        print(bateau)

print()
print("Espèces présentes dans les sorties mais absentes des quotas :")
especes_sorties = sorties["espece"].unique()
especes_quotas = quotas["espece"].unique()
for espece in especes_sorties:
    if espece not in especes_quotas:
        print(espece)

print()
print("Nombre de sorties avec une quantité négative :")
print(sorties[sorties["quantite_kg"] < 0].shape[0])

print("Nombre d'identifiants de sortie en double :")
print(sorties["id_sortie"].duplicated().sum())

# 4. Jointures pour associer chaque sortie à son armement

sorties_avec_armement = sorties.merge(
    navires[["bateau_normalise", "armement_id"]],
    on="bateau_normalise",
    how="left"
)

sorties_completes = sorties_avec_armement.merge(
    armements,
    on="armement_id",
    how="left"
)

print()
print("Bateaux sans nom d'armement :")
print(
    sorties_completes[
        sorties_completes["nom_armement"].isna()
    ]["bateau"].unique()
)

# 5. Attribution d'une campagne à chaque sortie

sorties_completes["annee"] = sorties_completes["date_normalisee"].dt.year
sorties_completes["campagne_sortie"] = (
    sorties_completes["annee"].astype(str)
    + "-"
    + (sorties_completes["annee"] + 1).astype(str)
)

# 6. Sélection des sorties utilisables pour les calculs

sorties_calcul = sorties_completes[
    (sorties_completes["armement_id"].notna())
    & (sorties_completes["quantite_kg"].notna())
    & (sorties_completes["quantite_kg"] >= 0)
]

print()
print("Nombre total de sorties :")
print(sorties_completes.shape[0])
print("Nombre de sorties utilisables pour le calcul :")
print(sorties_calcul.shape[0])

# 7. Somme des quantités pêchées

consommation = (
    sorties_calcul
    .groupby(
        ["armement_id", "nom_armement", "espece", "campagne_sortie"]
    )
    ["quantite_kg"]
    .sum()
    .reset_index()
)

# 8. Jointure entre les quantités pêchées et les quotas

suivi_quotas = consommation.merge(
    quotas,
    on=["armement_id", "espece", "campagne_sortie"],
    how="left"
)

# Noms plus clairs pour les prochains calculs
suivi_quotas = suivi_quotas.rename(
    columns={
        "quantite_kg": "quantite_pechee_kg",
        "quota_kg_alloue": "quota_alloue_kg",
    }
)

print()
print("Suivi des quotas :")
print(
    suivi_quotas[
        [
            "armement_id",
            "nom_armement",
            "espece",
            "campagne_sortie",
            "quantite_pechee_kg",
            "quota_alloue_kg",
        ]
    ].head(20)
)

suivi_quotas["quota_restant_kg"] = (
    suivi_quotas["quota_alloue_kg"]
    - suivi_quotas["quantite_pechee_kg"]
)

print(
    suivi_quotas[
        [
            "quota_alloue_kg",
            "quantite_pechee_kg",
            "quota_restant_kg",
        ]
    ].head(10)
)

suivi_quotas["taux_consommation_pct"] = suivi_quotas["quantite_pechee_kg"] / suivi_quotas["quota_alloue_kg"] * 100

print(
    suivi_quotas[
        [
            "quantite_pechee_kg",
            "quota_alloue_kg",
            "quota_restant_kg",
            "taux_consommation_pct",
        ]
    ].head(10)
)

suivi_quotas["taux_consommation_pct"] = (
    suivi_quotas["taux_consommation_pct"].round(1)
)

statuts = []

for taux in suivi_quotas["taux_consommation_pct"]:
    if pd.isna(taux):
        statuts.append("Quota non renseigné")
    elif taux > 100:
        statuts.append("Quota dépassé")
    else:
        statuts.append("Quota respecté")

suivi_quotas["statut_quota"] = statuts

print("Nombre de situations par statut :")
print(suivi_quotas["statut_quota"].value_counts())