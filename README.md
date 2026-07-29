# Suivi des sorties de pêche et des quotas

Ce projet a été réalisé dans le cadre d'un exercice technique pour un stage à la DPQM des TAAF.

Il s'agit d'une application Streamlit permettant :

- de consulter l'historique des sorties de pêche ;
- de filtrer les sorties par campagne, bateau, espèce et zone ;
- de suivre les quantités pêchées par armement, espèce et campagne ;
- de comparer les quantités pêchées aux quotas alloués ;
- de repérer les quotas dépassés et les quotas non renseignés ;
- de consulter quelques indicateurs sur la qualité des données.

Les données utilisées dans ce projet sont fictives.

## Fichiers utilisés

Le dossier `data` contient quatre fichiers CSV :

- `sorties_peche_exercice.csv` : historique des sorties de pêche ;
- `navires_referentiel.csv` : correspondance entre les bateaux et les armements ;
- `armements.csv` : identifiants et noms des armements ;
- `quotas.csv` : quotas attribués par armement, espèce et campagne.

Le fichier `traitement.py` charge, nettoie et relie ces données.

Le fichier `app.py` contient l'application Streamlit.

## Ma démarche et mon raisonnement

J'ai commencé par chercher à comprendre le besoin métier avant de construire l'application. Le suivi des quotas repose sur plusieurs informations qui se trouvent dans des fichiers différents : une sortie est associée à un bateau, le bateau dépend d'un armement et cet armement dispose de quotas définis par espèce et par campagne.

J'ai donc représenté le cheminement des données de la manière suivante :

`Sortie de pêche → Bateau → Armement → Quota`

Cette compréhension m'a permis d'identifier les informations nécessaires aux jointures et de définir les indicateurs utiles. L'objectif principal n'était pas seulement d'afficher les sorties, mais de permettre au service de répondre rapidement à plusieurs questions :

- quelle quantité un armement a-t-il pêchée ?
- quel quota lui a été attribué ?
- combien lui reste-t-il ?
- le quota est-il respecté, dépassé ou non renseigné ?
- quelles sorties expliquent les résultats affichés ?

J'ai ensuite avancé progressivement.

1. J'ai exploré séparément les quatre fichiers : premières lignes, dimensions, colonnes, types, valeurs manquantes, doublons et valeurs uniques importantes.
2. J'ai comparé les valeurs utilisées pour relier les fichiers, notamment les noms de bateaux, les armements, les espèces et les campagnes.
3. J'ai repéré plusieurs incohérences : différences de casse, espaces, tirets, faute dans une zone, formats de dates différents, quantités négatives ou manquantes et références absentes.
4. J'ai créé des colonnes normalisées afin de conserver les valeurs originales tout en disposant de valeurs propres pour les comparaisons et les jointures.
5. J'ai relié les sorties aux navires puis aux armements, avant de regrouper les quantités par armement, espèce et campagne.
6. J'ai rapproché ces résultats des quotas pour calculer le quota restant, le taux de consommation et un statut compréhensible.
7. J'ai enfin construit l'application autour de deux usages : le suivi synthétique des quotas et la consultation détaillée de l'historique.

Lorsque le sujet ne précisait pas une règle métier, j'ai préféré formuler une hypothèse explicite plutôt que de choisir une règle sans la documenter. C'est notamment le cas pour l'attribution d'une sortie à une campagne. J'ai également choisi de conserver les anomalies dans l'historique pour qu'elles restent visibles, tout en les excluant des calculs lorsqu'elles pouvaient fausser les résultats.

J'ai testé les filtres, les indicateurs et les graphiques avec différents cas : quota respecté, quota dépassé, quota non renseigné, sélection avec une seule sortie et sélection sans résultat.

## Prise en main de Streamlit

Je n'avais jamais développé d'application avec Streamlit avant cet exercice. Cette technologie est prévue dans le programme de troisième année de mon BUT Science des données, mais je ne l'avais pas encore étudiée en cours (Je vais rentrer en deuxième année).

Je me suis donc documentée et j'ai appris son fonctionnement progressivement : création de l'application, organisation en onglets, ajout de filtres, affichage d'indicateurs, de tableaux et de graphiques interactifs. J'ai essayé de rester sur une structure simple, lisible et que je suis capable d'expliquer.

J'ai consacré un peu plus de temps que la durée indicative de l'exercice, principalement pour me documenter sur Streamlit, comprendre les éléments que j'utilisais et vérifier le fonctionnement de l'application. Ce temps supplémentaire m'a permis de ne pas seulement reproduire du code, mais de mieux comprendre la démarche et les choix réalisés.

Cette découverte a été un plaisir, car elle m'a permis de mettre en pratique le traitement de données dans une application concrète et de suivre un projet depuis l'exploration des fichiers jusqu'à la création d'une interface utilisable.

## Utilisation de l'intelligence artificielle

J'ai utilisé l'intelligence artificielle Claude pour relire mon code et m'aider à résoudre certains blocages rencontrés pendant ma découverte de Streamlit.

## Installation

Dans un Terminal, se placer dans le dossier du projet :

```bash
cd projet_peche_dpqm
```

Créer un environnement virtuel :

```bash
python3 -m venv .venv
```

Activer l'environnement :

```bash
source .venv/bin/activate
```

Installer les bibliothèques nécessaires :

```bash
python -m pip install -r requirements.txt
```

## Lancement de l'application

Lorsque l'environnement virtuel est activé, lancer :

```bash
python -m streamlit run app.py
```

L'application s'ouvre ensuite dans le navigateur.

## Traitements réalisés

Plusieurs problèmes de qualité ont été repérés dans les fichiers.

Les traitements suivants ont été appliqués :

- suppression des espaces inutiles et passage en minuscules pour comparer les noms de bateaux ;
- remplacement des tirets par des espaces dans les noms de bateaux et les zones ;
- correction de la faute `crozzet` en `crozet` ;
- conversion des différents formats de dates en dates utilisables par Pandas ;
- harmonisation du séparateur des campagnes (`2024/2025` devient `2024-2025`) ;
- jointure entre les sorties, les navires et les armements ;
- regroupement des quantités par armement, espèce et campagne ;
- comparaison des quantités pêchées avec les quotas alloués.

Les quantités négatives et les quantités manquantes sont conservées dans l'historique, mais elles sont exclues du calcul de la consommation des quotas.

## Hypothèses et limites

Une sortie réalisée pendant l'année 2024 est rattachée à la campagne `2024-2025`. Cette règle a été choisie car les dates exactes de début et de fin des campagnes ne sont pas précisées dans le sujet.

Deux bateaux présents dans les sorties, `Amsterdam I` et `Curieuse`, n'ont pas de correspondance dans le référentiel des navires. Leurs sorties restent visibles dans l'historique, mais elles ne peuvent pas être attribuées à un armement et sont donc exclues du calcul des quotas.

L'espèce `Raie` est présente dans les sorties mais absente du fichier des quotas. Les quantités correspondantes sont indiquées comme ayant un quota non renseigné.

Certaines autres combinaisons entre une campagne, un armement et une espèce ne possèdent pas non plus de quota. Elles ne sont pas incluses dans les indicateurs comparant la pêche aux quotas.

Les données contiennent également :

- 42 quantités manquantes ;
- 12 quantités négatives ;
- 51 zones manquantes ;
- 91 sorties sans armement associé.

Ces informations sont affichées dans la partie « Qualité des données » de l'application.

## Fonctionnalités de l'application

L'onglet « Suivi des quotas » contient :

- des filtres par campagne, armement et espèce ;
- des indicateurs sur les quantités, les quotas et les dépassements ;
- une alerte lorsqu'un quota est dépassé ;
- un graphique présentant la répartition des statuts ;
- un tableau détaillé des résultats.

L'onglet « Historique des sorties » contient :

- des filtres par campagne, bateau, espèce et zone ;
- le nombre de sorties et la quantité totale valide ;
- le nombre de quantités écartées du calcul ;
- un graphique présentant l'évolution des quantités ;
- le détail des sorties filtrées.

## Améliorations possibles

Avec davantage de temps, il serait possible :

- de confirmer les dates exactes des campagnes avec le service métier ;
- de compléter le référentiel des navires et les quotas manquants ;
- d'ajouter des tests automatiques ;
- de permettre le téléchargement des résultats filtrés ;
- d'améliorer encore la présentation des tableaux et des graphiques.
