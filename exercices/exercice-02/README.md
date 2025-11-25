# Exercice 02 : Metabase – Self-Service BI pour équipes métier

## Objectifs pédagogiques

1. Installer Metabase et connecter une base SQLite locale.
2. Créer des questions (queries) interactives sans code SQL.
3. Construire un dashboard self-service pour les équipes commerciales.
4. Documenter les insights métier dans `resultats.md`.

## Contexte

Vous êtes analyste BI pour une boutique e-commerce. Les équipes commerciales ont besoin d’accéder rapidement à :

- La liste des clients actifs par région.
- Le chiffre d’affaires par catégorie de produit.
- Les commandes en attente de traitement.
- Le panier moyen par client.

Livrable attendu : un dashboard « Analyse Boutique » accessible aux non-techniques.

## Préparation des données

```bash
cd exercice-02
python creer_base_donnees.py       # crée donnees/boutique.db
```

## Installation rapide de Metabase

### Via Docker (recommandé)
```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```
Connexion : http://localhost:3000 (configuration initiale au premier accès).

### Installation native
Téléchargez le JAR depuis https://www.metabase.com/start/oss/ puis :
```bash
java -jar metabase.jar
```

## Étapes guidées

### 1. Configuration initiale
- Accédez à http://localhost:3000
- Créez un compte administrateur
- Choisissez votre langue et préférences

### 2. Ajouter la base de données
- Settings > Admin > Databases > Add database
- Sélectionnez SQLite
- Nom : "Boutique E-commerce"
- Fichier : chemin vers `donnees/boutique.db`
- Testez la connexion puis sauvegardez

### 3. Explorer les données
- Browse Data > explorez les tables : `clients`, `produits`, `commandes`, `details_commandes`
- Visualisez quelques enregistrements pour comprendre la structure

### 4. Créer des questions (au moins 6)

#### Question 1 : Liste des clients
- Simple question > Table `clients`
- Affichez : nom, prénom, email, ville
- Sauvegardez comme "Liste des clients"

#### Question 2 : Produits premium (> 100€)
- Simple question > Table `produits`
- Filtre : `prix > 100`
- Trier par prix décroissant
- Sauvegardez comme "Produits premium"

#### Question 3 : Chiffre d'affaires total
- Simple question > Table `commandes`
- Métrique : SUM de `montant_total`
- Visualisation : Number
- Sauvegardez comme "CA Total"

#### Question 4 : Commandes avec noms clients
- Custom question > SQL Editor
```sql
SELECT 
  co.commande_id,
  co.date_commande,
  co.montant_total,
  c.nom || ' ' || c.prenom as client_nom
FROM commandes co
JOIN clients c ON co.client_id = c.client_id
ORDER BY co.date_commande DESC
```
- Sauvegardez comme "Commandes détaillées"

#### Question 5 : Top 5 clients par CA
- Custom question > SQL Editor
```sql
SELECT 
  c.nom,
  c.prenom,
  SUM(co.montant_total) as ca_total
FROM clients c
JOIN commandes co ON c.client_id = co.client_id
GROUP BY c.client_id, c.nom, c.prenom
ORDER BY ca_total DESC
LIMIT 5
```
- Visualisation : Bar Chart
- Sauvegardez comme "Top 5 clients"

#### Question 6 : Panier moyen par catégorie
- Custom question > SQL Editor
```sql
SELECT 
  p.categorie,
  AVG(dc.quantite * dc.prix_unitaire) as panier_moyen
FROM details_commandes dc
JOIN produits p ON dc.produit_id = p.produit_id
GROUP BY p.categorie
ORDER BY panier_moyen DESC
```
- Visualisation : Bar Chart
- Sauvegardez comme "Panier moyen par catégorie"

### 5. Créer des visualisations
Pour chaque question, choisissez la visualisation appropriée :
- Table : pour les listes détaillées
- Bar Chart : pour les comparaisons
- Line Chart : pour les tendances temporelles
- Pie Chart : pour les répartitions
- Number : pour les métriques uniques

### 6. Créer le dashboard "Analyse Boutique"
- Dashboards > New dashboard
- Ajoutez toutes vos questions
- Organisez par thème : Vue d'ensemble / Clients / Produits / Commandes
- Ajustez les tailles des panneaux

### 7. Ajouter des filtres
- Ajoutez un filtre par date (sur les commandes)
- Ajoutez un filtre par catégorie de produit
- Testez les filtres en temps réel

### 8. Fonctionnalités avancées (optionnel)
- Créer des modèles de données (Data Model) pour définir les relations
- Configurer des alertes (ex: CA < seuil)
- Partager le dashboard (lien public ou utilisateurs spécifiques)

## Structure attendue
```
exercice-02/
├── README.md
├── donnees/
│   └── boutique.db
└── solutions/
    └── votre-nom/
        ├── screenshots/
        ├── resultats.md
        └── requetes_sql.md
```

## Critères d'évaluation
- Metabase installé et accessible
- Base de données connectée
- Au moins 6 questions créées avec visualisations appropriées
- Dashboard fonctionnel avec filtres
- Documentation complète (captures + rapport d'analyse)
- Respect de la structure de soumission

## Conseils
- Commencez par l'éditeur visuel (Simple question) pour les requêtes simples
- Passez à SQL Editor pour les requêtes complexes avec jointures
- Testez chaque question avant de l'ajouter au dashboard
- Organisez vos dashboards par thème métier
- Utilisez les modèles de données pour simplifier les requêtes futures

## Ressources
- Documentation Metabase : https://www.metabase.com/docs/
- Guide de démarrage : https://www.metabase.com/learn/getting-started
- Exemples de questions : https://www.metabase.com/learn

## Soumission
```bash
mkdir -p solutions/votre-nom
# Déposer vos fichiers (screenshots, resultats.md, requetes_sql.md)
git add solutions/votre-nom/
git commit -m "Solution exercice 02 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
