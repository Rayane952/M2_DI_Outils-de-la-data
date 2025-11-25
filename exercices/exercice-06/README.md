# Exercice 06 : Apache Airflow – Orchestration de pipelines de données

## Objectifs pédagogiques

1. Installer Airflow et comprendre l'architecture des DAGs.
2. Créer des workflows automatisés pour l'ETL.
3. Configurer des dépendances entre tâches et gérer les erreurs.
4. Monitorer l'exécution et documenter les pipelines.
5. Documenter vos choix d'orchestration dans `resultats.md`.

## Contexte

Vous êtes Data Engineer pour une entreprise e-commerce. Vous devez orchestrer un pipeline quotidien qui :

- Extrait les données de ventes depuis une API ou un fichier.
- Transforme et nettoie les données.
- Charge les données dans un data warehouse.
- Envoie un rapport par email en cas de succès.
- Gère les erreurs et les retries automatiques.

Livrable attendu : un DAG Airflow fonctionnel avec monitoring.

## Installation

### Option 1 : Docker Compose (recommandé)
```bash
# Télécharger le fichier docker-compose.yml officiel
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.7.0/docker-compose.yaml'

# Initialiser la base de données
docker-compose up airflow-init

# Démarrer Airflow
docker-compose up -d

# Accéder à l'interface : http://localhost:8080
# Identifiants : airflow / airflow
```

### Option 2 : Installation native
```bash
# Créer un environnement virtuel
python -m venv airflow-env
source airflow-env/bin/activate  # Linux/Mac
# ou airflow-env\Scripts\activate  # Windows

# Installer Airflow
pip install apache-airflow

# Initialiser la base de données
airflow db init

# Créer un utilisateur admin
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --password admin \
    --role Admin

# Démarrer le scheduler
airflow scheduler

# Dans un autre terminal, démarrer le webserver
airflow webserver --port 8080
```

## Structure du projet

Créez la structure suivante :
```
exercice-06/
├── README.md
├── dags/
│   └── pipeline_ventes.py
├── data/
│   ├── raw/
│   └── processed/
└── logs/
```

## Étapes guidées

### 1. Préparer les données de test
Créez un script `generer_donnees.py` qui génère des fichiers de ventes quotidiens :
```python
import pandas as pd
from datetime import datetime, timedelta
import os

os.makedirs("data/raw", exist_ok=True)

# Générer des données pour les 7 derniers jours
for i in range(7):
    date = datetime.now() - timedelta(days=i)
    df = pd.DataFrame({
        'date': [date.strftime('%Y-%m-%d')] * 100,
        'produit_id': range(1, 101),
        'quantite': [1] * 100,
        'montant': [10.0 + i * 0.5 for i in range(100)]
    })
    filename = f"data/raw/ventes_{date.strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False)
    print(f"Généré : {filename}")
```

### 2. Créer votre premier DAG
Créez `dags/pipeline_ventes.py` :
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import os

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'pipeline_ventes_quotidien',
    default_args=default_args,
    description='Pipeline ETL pour les ventes quotidiennes',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'ventes'],
)

def extraire_donnees(**context):
    """Extrait les données du jour"""
    execution_date = context['ds']
    print(f"Extraction des données pour le {execution_date}")
    # Ici, vous pourriez appeler une API ou lire depuis une base
    return f"data/raw/ventes_{execution_date.replace('-', '')}.csv"

def transformer_donnees(**context):
    """Transforme et nettoie les données"""
    ti = context['ti']
    fichier_source = ti.xcom_pull(task_ids='extraire')
    
    if not os.path.exists(fichier_source):
        raise FileNotFoundError(f"Fichier non trouvé : {fichier_source}")
    
    df = pd.read_csv(fichier_source)
    
    # Transformations
    df['montant_total'] = df['quantite'] * df['montant']
    df['date'] = pd.to_datetime(df['date'])
    
    # Sauvegarder
    os.makedirs("data/processed", exist_ok=True)
    fichier_dest = fichier_source.replace('raw', 'processed')
    df.to_csv(fichier_dest, index=False)
    
    print(f"Données transformées sauvegardées dans {fichier_dest}")
    return fichier_dest

def charger_donnees(**context):
    """Charge les données dans le data warehouse"""
    ti = context['ti']
    fichier = ti.xcom_pull(task_ids='transformer')
    
    df = pd.read_csv(fichier)
    
    # Ici, vous chargeriez dans PostgreSQL, BigQuery, etc.
    # Pour l'exercice, on simule juste
    print(f"Chargement de {len(df)} lignes dans le data warehouse")
    print(f"CA total : {df['montant_total'].sum():.2f}€")
    
    return len(df)

# Définir les tâches
tache_extraire = PythonOperator(
    task_id='extraire',
    python_callable=extraire_donnees,
    dag=dag,
)

tache_transformer = PythonOperator(
    task_id='transformer',
    python_callable=transformer_donnees,
    dag=dag,
)

tache_charger = PythonOperator(
    task_id='charger',
    python_callable=charger_donnees,
    dag=dag,
)

tache_notifier = BashOperator(
    task_id='notifier',
    bash_command='echo "Pipeline terminé avec succès le {{ ds }}"',
    dag=dag,
)

# Définir les dépendances
tache_extraire >> tache_transformer >> tache_charger >> tache_notifier
```

### 3. Tester le DAG
```bash
# Vérifier la syntaxe
python dags/pipeline_ventes.py

# Lister les DAGs
airflow dags list

# Tester une tâche
airflow tasks test pipeline_ventes_quotidien extraire 2024-01-01
```

### 4. Améliorer le DAG avec fonctionnalités avancées

#### Ajouter des capteurs
```python
from airflow.sensors.filesystem import FileSensor

attendre_fichier = FileSensor(
    task_id='attendre_fichier',
    filepath='data/raw/',
    fs_conn_id='fs_default',
    poke_interval=30,
    timeout=3600,
    dag=dag,
)
```

#### Ajouter des branches conditionnelles
```python
from airflow.operators.python import BranchPythonOperator

def verifier_qualite(**context):
    ti = context['ti']
    fichier = ti.xcom_pull(task_ids='transformer')
    df = pd.read_csv(fichier)
    
    if len(df) < 10:
        return 'alerte_qualite'
    return 'charger'

branche_qualite = BranchPythonOperator(
    task_id='verifier_qualite',
    python_callable=verifier_qualite,
    dag=dag,
)
```

#### Ajouter des pools et priorités
```python
tache_extraire = PythonOperator(
    task_id='extraire',
    python_callable=extraire_donnees,
    pool='etl_pool',
    priority_weight=10,
    dag=dag,
)
```

### 5. Monitorer dans l'interface Airflow
- Accédez à http://localhost:8080
- Visualisez le graphe du DAG
- Suivez l'exécution des tâches en temps réel
- Consultez les logs de chaque tâche
- Analysez les métriques et les durées d'exécution

### 6. Gérer les variables et connexions
```python
from airflow.models import Variable

api_key = Variable.get("api_key_ventes")
```

Dans l'interface Airflow : Admin > Variables > Add

## Structure attendue
```
exercice-06/
├── README.md
├── dags/
│   └── pipeline_ventes.py
├── data/
│   ├── raw/
│   └── processed/
└── solutions/
    └── votre-nom/
        ├── pipeline_ventes.py
        ├── screenshots/
        ├── resultats.md
        └── architecture.md
```

## Critères d'évaluation
- Airflow installé et accessible
- DAG fonctionnel avec au moins 4 tâches
- Gestion des dépendances et des erreurs
- Documentation complète (screenshots + explications)
- Respect de la structure de soumission

## Conseils
- Testez chaque tâche individuellement avant de les chaîner
- Utilisez XCom pour passer des données entre tâches
- Configurez des retries et des timeouts appropriés
- Documentez vos DAGs avec des descriptions claires
- Utilisez les tags pour organiser vos DAGs

## Ressources
- Documentation Airflow : https://airflow.apache.org/docs/
- Tutoriels : https://airflow.apache.org/docs/apache-airflow/stable/tutorial/
- Exemples de DAGs : https://github.com/apache/airflow/tree/main/airflow/example_dags

## Soumission
```bash
mkdir -p solutions/votre-nom
# Copiez votre DAG et les fichiers de documentation
git add solutions/votre-nom/
git commit -m "Solution exercice 06 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
