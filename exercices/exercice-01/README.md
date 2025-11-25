# Exercice 01 : Apache Superset – Tableau de bord ventes

## Objectifs pédagogiques

1. Installer Superset et connecter une base SQLite locale.
2. Construire un dataset propre à partir des ventes e-commerce 2024.
3. Concevoir un dashboard lisible et filtrable pour les équipes métier.
4. Documenter les enseignements clés dans `resultats.md`.

## Contexte

Vous êtes analyste BI pour une boutique en ligne. Le marketing veut suivre :

- Le chiffre d’affaires mensuel.
- Les meilleures catégories/produits.
- Les clients les plus actifs.

Livrable attendu : un dashboard « Analyse des ventes » autonome.

## Préparation des données

```bash
cd exercice-01
python generer_donnees.py          # génère donnees/ventes.csv
python creer_base_donnees.py       # crée donnees/ventes.db
```

## Installation rapide de Superset

### Via Docker (recommandé)
```bash
docker run -d -p 8088:8088 --name superset apache/superset
docker exec -it superset superset db upgrade
docker exec -it superset superset fab create-admin   --username admin --firstname Admin --lastname User   --email admin@example.com --password admin
docker exec -it superset superset init
```
Connexion : http://localhost:8088 (admin/admin).

### Installation native
Voir https://superset.apache.org/docs/installation si vous préférez éviter Docker.

## Étapes guidées

### 1. Connexion à la base
- Data > Databases > +Database
- SQLAlchemy URI : `sqlite:///donnees/ventes.db`
- Test Connection → Save

### 2. Création du dataset
- Data > Datasets > +Dataset → table `ventes`
- Vérifier les types (date, montants, quantités)
- Ajouter si besoin une colonne calculée (`quantite * prix_unitaire`)

### 3. Charts requis
1. CA par mois (bar chart)
2. Évolution des ventes (line chart)
3. Répartition CA par catégorie (pie ou sunburst)
4. Top 10 produits (table triée)
5. Activité par client (bar horizontale)
6. Cartouche d’indicateurs (CA total, panier moyen, nombre de transactions)

### 4. Dashboard « Analyse des ventes »
- Créer un dashboard, ajouter tous les charts
- Organiser en colonnes : Vue d’ensemble / Produits / Clients
- Ajouter deux filtres liés : période + catégorie
- Tester un scénario (ex : mois d’avril, catégorie Electronique)

### 5. Livrables
Dans `solutions/votre-nom/` :
- `dashboard_export.json`
- `screenshots/` (captures annotées)
- `resultats.md` : insights, anomalies, recommandations
- `requetes_sql.md` si SQL Lab est utilisé

## Structure attendue
```
exercice-01/
├── README.md
├── donnees/
│   ├── ventes.csv
│   └── ventes.db
└── solutions/
    └── votre-nom/
        ├── dashboard_export.json
        ├── screenshots/
        ├── resultats.md
        └── requetes_sql.md
```

## Critères d’évaluation
- Superset installé et accessible
- Dataset opérationnel
- Dashboard complet et filtrable
- Documentation livrée (export + captures + rapport)
- Respect de la structure de soumission

## Conseils
- Sauvegardez chaque chart avant de quitter Explore.
- Utilisez le Time range pour grouper par mois.
- Donnez des titres explicites aux panels.
- Mentionnez vos métriques dans `resultats.md`.

## Soumission
```bash
mkdir -p solutions/votre-nom
# Déposer vos fichiers
git add solutions/votre-nom/
git commit -m "Solution exercice 01 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
