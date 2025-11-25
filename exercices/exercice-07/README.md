# Exercice 07 : dbt (data build tool) – Transformation SQL moderne

## Objectifs pédagogiques

1. Installer dbt et configurer un projet.
2. Créer des modèles de transformation SQL modulaires.
3. Implémenter des tests de qualité des données.
4. Générer de la documentation automatique.
5. Documenter votre approche de transformation dans `resultats.md`.

## Contexte

Vous êtes Data Engineer pour une entreprise e-commerce. Vous devez transformer les données brutes de votre data warehouse en modèles analytiques exploitables pour :

- Créer une table de faits `fct_ventes` consolidée.
- Construire des dimensions (`dim_clients`, `dim_produits`, `dim_temps`).
- Calculer des métriques business (CA, panier moyen, taux de conversion).
- Assurer la qualité des données avec des tests automatisés.

Livrable attendu : un projet dbt complet avec modèles, tests et documentation.

## Préparation

Utilisez la base de données de l'exercice 02 ou créez-en une nouvelle avec des tables sources.

## Installation

```bash
# Pour PostgreSQL
pip install dbt-postgres

# Pour SQLite
pip install dbt-sqlite

# Vérifier l'installation
dbt --version
```

## Étapes guidées

### 1. Initialiser un projet dbt
```bash
dbt init m2_di_project
cd m2_di_project
```

### 2. Configurer la connexion
Éditez `~/.dbt/profiles.yml` (ou `profiles.yml` dans le projet) :
```yaml
m2_di_project:
  outputs:
    dev:
      type: postgres  # ou sqlite
      host: localhost
      port: 5432
      user: votre_user
      password: votre_password
      dbname: boutique
      schema: public
    prod:
      type: postgres
      # ... configuration production
  target: dev
```

### 3. Tester la connexion
```bash
dbt debug
```

### 4. Créer les sources (sources.yml)
Créez `models/sources.yml` :
```yaml
version: 2

sources:
  - name: raw_data
    description: "Données brutes de la boutique"
    database: boutique
    schema: public
    tables:
      - name: clients
        description: "Table des clients"
      - name: produits
        description: "Table des produits"
      - name: commandes
        description: "Table des commandes"
      - name: details_commandes
        description: "Détails des commandes"
```

### 5. Créer les modèles de transformation

#### Modèle 1 : stg_clients.sql (staging)
Créez `models/staging/stg_clients.sql` :
```sql
{{ config(materialized='view') }}

select
    client_id,
    nom,
    prenom,
    email,
    ville,
    pays,
    date_inscription
from {{ source('raw_data', 'clients') }}
```

#### Modèle 2 : stg_produits.sql
Créez `models/staging/stg_produits.sql` :
```sql
{{ config(materialized='view') }}

select
    produit_id,
    nom_produit,
    categorie,
    prix,
    stock
from {{ source('raw_data', 'produits') }}
where prix > 0  -- Exclure les produits invalides
```

#### Modèle 3 : stg_commandes.sql
Créez `models/staging/stg_commandes.sql` :
```sql
{{ config(materialized='view') }}

select
    commande_id,
    client_id,
    date_commande,
    montant_total,
    statut
from {{ source('raw_data', 'commandes') }}
```

#### Modèle 4 : fct_ventes.sql (fait)
Créez `models/marts/fct_ventes.sql` :
```sql
{{ config(materialized='table') }}

with commandes as (
    select * from {{ ref('stg_commandes') }}
),
details as (
    select
        dc.commande_id,
        dc.produit_id,
        dc.quantite,
        dc.prix_unitaire,
        dc.quantite * dc.prix_unitaire as montant_ligne
    from {{ source('raw_data', 'details_commandes') }} dc
)
select
    c.commande_id,
    c.client_id,
    c.date_commande,
    d.produit_id,
    d.quantite,
    d.montant_ligne,
    c.montant_total as montant_commande_total
from commandes c
inner join details d on c.commande_id = d.commande_id
```

#### Modèle 5 : dim_clients.sql (dimension)
Créez `models/marts/dim_clients.sql` :
```sql
{{ config(materialized='table') }}

select
    client_id,
    nom,
    prenom,
    email,
    ville,
    pays,
    date_inscription,
    current_date - date_inscription as anciennete_jours
from {{ ref('stg_clients') }}
```

#### Modèle 6 : dim_produits.sql
Créez `models/marts/dim_produits.sql` :
```sql
{{ config(materialized='table') }}

select
    produit_id,
    nom_produit,
    categorie,
    prix,
    stock,
    case
        when prix < 50 then 'Economique'
        when prix < 150 then 'Standard'
        else 'Premium'
    end as segment_prix
from {{ ref('stg_produits') }}
```

#### Modèle 7 : métriques business (marts/business_metrics.sql)
Créez `models/marts/business_metrics.sql` :
```sql
{{ config(materialized='table') }}

select
    date_trunc('month', date_commande) as mois,
    count(distinct client_id) as nb_clients_uniques,
    count(distinct commande_id) as nb_commandes,
    sum(montant_ligne) as ca_total,
    avg(montant_commande_total) as panier_moyen,
    sum(quantite) as quantite_totale_vendue
from {{ ref('fct_ventes') }}
group by 1
order by 1 desc
```

### 6. Ajouter des tests de qualité

Créez `models/schema.yml` :
```yaml
version: 2

models:
  - name: stg_clients
    description: "Table staging des clients"
    columns:
      - name: client_id
        description: "Identifiant unique du client"
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
          - not_null

  - name: fct_ventes
    description: "Table de faits des ventes"
    columns:
      - name: montant_ligne
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 10000
      - name: quantite
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 1
              max_value: 100

sources:
  - name: raw_data
    tables:
      - name: commandes
        columns:
          - name: montant_total
            tests:
              - not_null
              - dbt_utils.accepted_range:
                  min_value: 0
```

### 7. Exécuter les transformations
```bash
# Compiler les modèles (vérifier la syntaxe)
dbt compile

# Exécuter tous les modèles
dbt run

# Exécuter un modèle spécifique
dbt run --select fct_ventes

# Exécuter les tests
dbt test

# Exécuter un test spécifique
dbt test --select stg_clients
```

### 8. Générer la documentation
```bash
# Générer la documentation
dbt docs generate

# Servir la documentation
dbt docs serve
```

Accédez à http://localhost:8080 pour voir la documentation interactive.

### 9. Utiliser des macros (optionnel)
Créez `macros/calculer_taux_croissance.sql` :
```sql
{% macro calculer_taux_croissance(ca_actuel, ca_precedent) %}
    case
        when {{ ca_precedent }} = 0 then null
        else (({{ ca_actuel }} - {{ ca_precedent }}) / {{ ca_precedent }}) * 100
    end
{% endmacro %}
```

Utilisez-la dans un modèle :
```sql
select
    mois,
    ca_total,
    lag(ca_total) over (order by mois) as ca_mois_precedent,
    {{ calculer_taux_croissance('ca_total', 'lag(ca_total) over (order by mois)') }} as taux_croissance
from {{ ref('business_metrics') }}
```

### 10. Créer des seeds (données de référence)
Créez `seeds/categories_prioritaires.csv` :
```csv
categorie,priorite
Electronique,1
Vetements,2
Alimentaire,3
```

Chargez les seeds :
```bash
dbt seed
```

## Structure attendue
```
exercice-07/
├── README.md
├── m2_di_project/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_clients.sql
│   │   │   ├── stg_produits.sql
│   │   │   └── stg_commandes.sql
│   │   ├── marts/
│   │   │   ├── fct_ventes.sql
│   │   │   ├── dim_clients.sql
│   │   │   ├── dim_produits.sql
│   │   │   └── business_metrics.sql
│   │   ├── sources.yml
│   │   └── schema.yml
│   ├── dbt_project.yml
│   └── profiles.yml
└── solutions/
    └── votre-nom/
        ├── m2_di_project/
        ├── screenshots/
        ├── resultats.md
        └── documentation.md
```

## Critères d'évaluation
- dbt installé et configuré
- Projet dbt complet avec modèles staging et marts
- Tests de qualité implémentés et passants
- Documentation générée et accessible
- Structure modulaire et réutilisable
- Respect de la structure de soumission

## Conseils
- Suivez la convention staging → marts pour organiser vos modèles
- Utilisez les tests dbt pour garantir la qualité des données
- Documentez vos modèles avec des descriptions claires
- Utilisez les macros pour éviter la duplication de code
- Organisez vos modèles par domaine métier

## Ressources
- Documentation dbt : https://docs.getdbt.com/
- Guide de démarrage : https://docs.getdbt.com/docs/get-started
- Best practices : https://docs.getdbt.com/guides/best-practices

## Soumission
```bash
mkdir -p solutions/votre-nom
# Copiez votre projet dbt complet
git add solutions/votre-nom/
git commit -m "Solution exercice 07 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
