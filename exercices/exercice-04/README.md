# Exercice 04 : Apache Spark + Jupyter – Analyse Big Data

## Objectifs pédagogiques

1. Installer PySpark et configurer un environnement Jupyter.
2. Traiter des volumes de données importants avec Spark DataFrames.
3. Effectuer des agrégations et jointures distribuées.
4. Créer des visualisations à partir de résultats Spark.
5. Documenter les performances et les insights dans `resultats.md`.

## Contexte

Vous êtes Data Engineer pour une plateforme e-commerce. Vous devez analyser un historique de transactions volumineux (plusieurs millions de lignes) pour :

- Calculer le chiffre d'affaires par région et par mois.
- Identifier les produits les plus vendus.
- Analyser les tendances d'achat par segment de client.
- Détecter des anomalies dans les transactions.

Livrable attendu : un notebook Jupyter avec analyses Spark et visualisations.

## Préparation des données

```bash
cd exercice-04
python generer_donnees.py          # génère donnees/transactions.csv (plusieurs millions de lignes)
```

## Installation

### Option 1 : PySpark (recommandé)
```bash
pip install pyspark jupyter pandas matplotlib seaborn
```

### Option 2 : Spark standalone
Téléchargez Spark depuis https://spark.apache.org/downloads.html et configurez :
```bash
export SPARK_HOME=/chemin/vers/spark
export PATH=$PATH:$SPARK_HOME/bin
```

## Étapes guidées

### 1. Démarrer Jupyter avec Spark
```bash
cd exercice-04
jupyter notebook
```
Créez un nouveau notebook Python.

### 2. Initialiser Spark Session
Dans la première cellule du notebook :
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("AnalyseTransactions") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
```

### 3. Charger les données
```python
# Lire le fichier CSV
df = spark.read.csv(
    "donnees/transactions.csv",
    header=True,
    inferSchema=True
)

# Afficher le schéma
df.printSchema()

# Compter le nombre total de lignes
print(f"Nombre total de transactions : {df.count():,}")
```

### 4. Explorations de base
```python
# Aperçu des données
df.show(10)

# Statistiques descriptives
df.describe().show()

# Vérifier les valeurs nulles
from pyspark.sql.functions import col, when, count
df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).show()
```

### 5. Analyses requises

#### Analyse 1 : CA par région et par mois
```python
ca_par_region_mois = df.groupBy("region", "mois") \
    .agg(sum("montant").alias("ca_total")) \
    .orderBy("region", "mois")

ca_par_region_mois.show(50)
```

#### Analyse 2 : Top 10 produits les plus vendus
```python
top_produits = df.groupBy("produit_id", "nom_produit") \
    .agg(
        sum("quantite").alias("quantite_totale"),
        sum("montant").alias("ca_total")
    ) \
    .orderBy(desc("quantite_totale")) \
    .limit(10)

top_produits.show()
```

#### Analyse 3 : Tendances d'achat par segment client
```python
tendances_segment = df.groupBy("segment_client", "mois") \
    .agg(
        count("*").alias("nb_transactions"),
        avg("montant").alias("panier_moyen"),
        sum("montant").alias("ca_total")
    ) \
    .orderBy("segment_client", "mois")

tendances_segment.show(50)
```

#### Analyse 4 : Détection d'anomalies (transactions > 3 écarts-types)
```python
from pyspark.sql.functions import stddev, mean

stats = df.select(
    mean("montant").alias("moyenne"),
    stddev("montant").alias("ecart_type")
).collect()[0]

seuil = stats.moyenne + 3 * stats.ecart_type

anomalies = df.filter(col("montant") > seuil) \
    .orderBy(desc("montant"))

print(f"Seuil d'anomalie : {seuil:.2f}€")
anomalies.show(20)
```

### 6. Jointures complexes
```python
# Si vous avez une table produits séparée
# produits_df = spark.read.csv("donnees/produits.csv", header=True, inferSchema=True)

# Jointure et analyse
# df_enrichi = df.join(produits_df, "produit_id", "left")
# df_enrichi.groupBy("categorie").agg(sum("montant").alias("ca")).show()
```

### 7. Optimisations Spark
```python
# Cachez les DataFrames fréquemment utilisés
df.cache()

# Utilisez des partitions appropriées
df_repartitioned = df.repartition(4, "region")

# Vérifiez le plan d'exécution
df.groupBy("region").agg(sum("montant")).explain(True)
```

### 8. Visualisations
```python
# Convertir en Pandas pour visualisation (sur échantillon)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Échantillonner pour la visualisation (si trop volumineux)
df_sample = df.sample(fraction=0.01).toPandas()

# Graphique CA par région
ca_region = df.groupBy("region").agg(sum("montant").alias("ca")).toPandas()
plt.figure(figsize=(10, 6))
sns.barplot(data=ca_region, x="region", y="ca")
plt.title("Chiffre d'affaires par région")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### 9. Sauvegarder les résultats
```python
# Sauvegarder en CSV
ca_par_region_mois.coalesce(1).write.mode("overwrite").csv("resultats/ca_region_mois", header=True)

# Ou en Parquet (format optimisé Spark)
df.write.mode("overwrite").parquet("donnees/transactions_parquet")
```

## Structure attendue
```
exercice-04/
├── README.md
├── donnees/
│   ├── transactions.csv
│   └── transactions_parquet/ (optionnel)
├── notebooks/
│   └── analyse_transactions.ipynb
├── resultats/
│   └── (fichiers générés)
└── solutions/
    └── votre-nom/
        ├── analyse_transactions.ipynb
        ├── screenshots/
        ├── resultats.md
        └── performances.md
```

## Critères d'évaluation
- Spark installé et fonctionnel
- Notebook Jupyter complet avec toutes les analyses
- Utilisation appropriée des opérations Spark (groupBy, join, agg)
- Visualisations claires et pertinentes
- Documentation des performances et optimisations
- Respect de la structure de soumission

## Conseils
- Utilisez `.cache()` pour les DataFrames réutilisés plusieurs fois
- Évitez les collect() sur de gros volumes (utilisez toPandas() avec échantillonnage)
- Vérifiez le plan d'exécution avec `.explain()` pour optimiser
- Utilisez le format Parquet pour de meilleures performances
- Documentez les temps d'exécution dans `performances.md`

## Ressources
- Documentation PySpark : https://spark.apache.org/docs/latest/api/python/
- Guide Spark SQL : https://spark.apache.org/docs/latest/sql-programming-guide.html
- Tutoriels Jupyter : https://jupyter.org/documentation

## Soumission
```bash
mkdir -p solutions/votre-nom
# Copiez votre notebook et les fichiers de résultats
git add solutions/votre-nom/
git commit -m "Solution exercice 04 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
