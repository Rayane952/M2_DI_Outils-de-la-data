# Atelier 01 : Dashboard analytique complet avec outils open source

## Objectifs pédagogiques

1. Intégrer plusieurs outils BI open source (Superset, Metabase, ou solution custom).
2. Créer un pipeline de préparation de données reproductible.
3. Développer un dashboard interactif et professionnel.
4. Présenter et documenter un projet data complet.

## Contexte

Vous êtes data analyst pour une entreprise e-commerce. La direction vous demande de créer un dashboard analytique complet permettant de :

- Suivre les KPIs métier en temps réel.
- Analyser les tendances de ventes, clients et produits.
- Identifier les opportunités et problèmes.
- Prendre des décisions stratégiques basées sur les données.

Livrable attendu : un dashboard interactif déployé et documenté.

## Prérequis

- Tous les exercices précédents complétés (01-07).
- Outils BI : Superset, Metabase, ou framework web (Streamlit/Dash).
- Bibliothèques Python : pandas, matplotlib, seaborn, plotly.
- Connaissances en visualisation de données et storytelling.

## Installation

```bash
# Pour solution custom avec Streamlit
pip install pandas matplotlib seaborn plotly streamlit

# Ou pour Dash
pip install pandas matplotlib seaborn plotly dash
```

## Étapes guidées

### Phase 1 : Préparation des données

#### Étape 1.1 : Collecte et consolidation
```bash
# Utilisez les données des exercices précédents ou créez un dataset réaliste
cd atelier-01
python generer_donnees_completes.py  # si vous créez un générateur
```

#### Étape 1.2 : Nettoyage et préparation
Créez `src/data_preparation.py` :
```python
import pandas as pd
import numpy as np

def nettoyer_donnees(df):
    """Nettoie et prépare les données"""
    # Supprimer les doublons
    df = df.drop_duplicates()
    
    # Gérer les valeurs manquantes
    df['montant'] = df['montant'].fillna(0)
    
    # Convertir les dates
    df['date'] = pd.to_datetime(df['date'])
    
    # Créer des colonnes dérivées
    df['annee'] = df['date'].dt.year
    df['mois'] = df['date'].dt.month
    df['jour_semaine'] = df['date'].dt.day_name()
    
    return df

def enrichir_donnees(df):
    """Enrichit les données avec des métriques calculées"""
    # Segment de client
    df['segment_client'] = pd.cut(
        df['montant_total'],
        bins=[0, 50, 150, float('inf')],
        labels=['Economique', 'Standard', 'Premium']
    )
    
    # Panier moyen
    df['panier_moyen'] = df.groupby('client_id')['montant'].transform('mean')
    
    return df

if __name__ == "__main__":
    # Charger les données brutes
    df_raw = pd.read_csv("donnees/raw/ventes.csv")
    
    # Nettoyer
    df_clean = nettoyer_donnees(df_raw)
    
    # Enrichir
    df_final = enrichir_donnees(df_clean)
    
    # Sauvegarder
    os.makedirs("donnees/processed", exist_ok=True)
    df_final.to_csv("donnees/processed/ventes_final.csv", index=False)
```

#### Étape 1.3 : Créer un pipeline reproductible
Assurez-vous que votre pipeline peut être exécuté plusieurs fois avec les mêmes résultats.

### Phase 2 : Analyses exploratoires

#### Étape 2.1 : Analyses descriptives
Créez `notebooks/01_exploration.ipynb` :
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("donnees/processed/ventes_final.csv")

# Statistiques générales
print(df.describe())
print(df.info())

# Distributions
df['montant'].hist(bins=50)
plt.title("Distribution des montants")
plt.show()

# Corrélations
corr_matrix = df.select_dtypes(include=[np.number]).corr()
sns.heatmap(corr_matrix, annot=True)
plt.show()
```

#### Étape 2.2 : Analyses métier
- Analyse des ventes : évolution temporelle, saisonnalité, tendances.
- Analyse des clients : segmentation, comportement d'achat, valeur vie client.
- Analyse des produits : performance par catégorie, top produits, rotation.
- Analyse de rentabilité : marge par produit, ROI par campagne.

#### Étape 2.3 : Identifier les insights
Documentez dans `notebooks/insights.md` :
- Opportunités détectées.
- Problèmes identifiés.
- Recommandations actionnables.

### Phase 3 : Visualisations interactives

#### Étape 3.1 : Créer au moins 10 visualisations

1. **KPIs principaux** (Number cards) :
   - CA total
   - Nombre de transactions
   - Panier moyen
   - Nombre de clients uniques

2. **Évolution temporelle** (Line Chart) :
   - CA par jour/mois
   - Nombre de commandes par jour

3. **Comparaisons** (Bar Chart) :
   - CA par catégorie
   - Top 10 produits
   - CA par région

4. **Répartitions** (Pie Chart / Treemap) :
   - Répartition CA par catégorie
   - Répartition clients par segment

5. **Corrélations** (Heatmap / Scatter) :
   - Matrice de corrélation
   - Relation prix/quantité

6. **Distributions** (Histogram / Boxplot) :
   - Distribution des montants
   - Distribution par segment client

#### Étape 3.2 : Ajouter de l'interactivité
- Filtres par période, catégorie, région.
- Drill-down (navigation hiérarchique).
- Tooltips informatifs.
- Mise à jour dynamique des graphiques.

### Phase 4 : Dashboard interactif

#### Option A : Streamlit (recommandé)
Créez `dashboard/app.py` :
```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard E-commerce", layout="wide")

# Charger les données
@st.cache_data
def load_data():
    return pd.read_csv("donnees/processed/ventes_final.csv")

df = load_data()

# Sidebar avec filtres
st.sidebar.header("Filtres")
categorie = st.sidebar.multiselect("Catégorie", df['categorie'].unique())
date_range = st.sidebar.date_input("Période", value=[df['date'].min(), df['date'].max()])

# Filtrer les données
df_filtered = df[df['categorie'].isin(categorie) if categorie else df.index]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("CA Total", f"{df_filtered['montant'].sum():,.0f}€")
with col2:
    st.metric("Transactions", f"{len(df_filtered):,}")
with col3:
    st.metric("Panier Moyen", f"{df_filtered['montant'].mean():.2f}€")
with col4:
    st.metric("Clients Uniques", f"{df_filtered['client_id'].nunique():,}")

# Graphiques
st.header("Évolution des ventes")
fig = px.line(df_filtered.groupby('date')['montant'].sum().reset_index(), 
              x='date', y='montant', title="CA par jour")
st.plotly_chart(fig, use_container_width=True)

st.header("CA par catégorie")
fig = px.bar(df_filtered.groupby('categorie')['montant'].sum().reset_index(),
             x='categorie', y='montant')
st.plotly_chart(fig, use_container_width=True)
```

Lancez avec :
```bash
streamlit run dashboard/app.py
```

#### Option B : Dash
Créez `dashboard/app_dash.py` avec une structure similaire mais utilisant Dash.

#### Option C : Intégration avec Superset/Metabase
- Créez vos visualisations dans Superset ou Metabase.
- Organisez-les dans un dashboard cohérent.
- Configurez les filtres et interactions.

### Phase 5 : Documentation et présentation

#### Étape 5.1 : Documentation technique
Créez un README complet avec :
- Guide d'installation.
- Structure du projet.
- Instructions d'utilisation.
- Documentation du code.

#### Étape 5.2 : Présentation métier
Créez `presentation/slides.md` ou un PDF avec :
- Contexte et objectifs.
- Méthodologie.
- Résultats clés (5-10 slides).
- Storytelling des données.
- Recommandations actionnables.

#### Étape 5.3 : Rapport d'analyse
Créez `presentation/rapport_analyse.md` :
- Méthodologie détaillée.
- Résultats et visualisations.
- Insights et recommandations.
- Limitations et améliorations futures.

## Structure attendue
```
atelier-01/
├── README.md
├── donnees/
│   ├── raw/
│   ├── processed/
│   └── final/
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── insights.md
├── src/
│   ├── data_preparation.py
│   ├── analysis.py
│   └── visualizations.py
├── dashboard/
│   ├── app.py (ou app_dash.py)
│   └── components/
├── presentation/
│   ├── slides.pdf
│   └── rapport_analyse.md
└── solutions/
    └── votre-nom/
        └── (votre solution complète)
```

## Critères d'évaluation
- Projet complet et fonctionnel de bout en bout
- Code propre, modulaire et bien organisé
- Dashboard interactif, esthétique et utilisable
- Analyses pertinentes et approfondies
- Visualisations claires et informatives
- Documentation complète (technique + métier)
- Présentation professionnelle avec storytelling

## Conseils
- Commencez simple, itérez ensuite pour améliorer
- Testez votre dashboard avec des utilisateurs réels
- Pensez à l'expérience utilisateur (UX)
- Utilisez des couleurs cohérentes et accessibles
- Ajoutez des annotations aux graphiques pour guider la lecture
- Racontez une histoire avec vos données (storytelling)

## Fonctionnalités avancées (Bonus)
- Prédictions avec machine learning intégrées
- Alertes automatiques sur anomalies détectées
- Export PDF automatique des rapports
- Authentification utilisateur
- Connexion à une base de données en temps réel
- Déploiement en production (Heroku, AWS, etc.)

## Soumission
```bash
mkdir -p solutions/votre-nom
# Placez tous vos fichiers dans ce dossier
git add solutions/votre-nom/
git commit -m "Atelier 01 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
