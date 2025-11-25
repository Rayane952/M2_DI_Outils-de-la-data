# Atelier 03 : Stack moderne de données complète

## Objectifs pédagogiques

1. Intégrer plusieurs outils de la stack moderne (ELK, Airflow, dbt, Grafana, Superset).
2. Créer un pipeline de données complet de bout en bout.
3. Mettre en place le monitoring et l'observabilité.
4. Déployer une solution production-ready avec Docker.
5. Documenter l'architecture et les choix techniques dans `resultats.md`.

## Contexte

Vous êtes Data Engineer pour une application e-commerce. Vous devez créer une stack complète de données qui inclut :

- Collecte de données en temps réel (logs, métriques, transactions).
- Stockage dans un data warehouse (PostgreSQL).
- Transformation avec dbt (modèles staging → marts).
- Orchestration avec Airflow (DAGs automatisés).
- Monitoring avec Grafana (dashboards opérationnels).
- Dashboard analytique avec Superset (BI pour les équipes métier).

Livrable attendu : une stack complète déployée avec Docker Compose, documentée et fonctionnelle.

## Prérequis

- Tous les exercices précédents complétés (01-07).
- Docker et Docker Compose installés.
- Connaissances en architecture de données et microservices.
- Familiarité avec les outils : ELK, Airflow, dbt, Grafana, Superset.

## Installation

```bash
# Vérifier Docker
docker --version
docker-compose --version
```

## Étapes guidées

### Phase 1 : Architecture

#### Étape 1.1 : Dessiner l'architecture
Créez `architecture/diagramme.md` avec :
- Schéma complet du système (composants et flux).
- Flux de données (de la source au dashboard).
- Technologies choisies et justifications.
- Points d'intégration entre les composants.

Exemple d'architecture :
```
[Générateur de données] 
    ↓
[PostgreSQL] ← [dbt] ← [Airflow]
    ↓
[Elasticsearch] ← [Logstash]
    ↓
[Kibana] + [Grafana] + [Superset]
```

#### Étape 1.2 : Planifier l'implémentation
Documentez dans `architecture/plan.md` :
- Liste des composants à déployer.
- Dépendances entre composants.
- Ordre d'implémentation recommandé.
- Configuration requise pour chaque service.

### Phase 2 : Infrastructure Docker

#### Étape 2.1 : Créer docker-compose.yml
Créez `docker-compose.yml` à la racine :
```yaml
version: '3.8'

services:
  # Data Warehouse
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: data_engineer
      POSTGRES_PASSWORD: password
      POSTGRES_DB: data_warehouse
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - data_network

  # Airflow
  airflow-webserver:
    image: apache/airflow:2.7.0
    command: webserver
    ports:
      - "8080:8080"
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
    depends_on:
      - postgres
    networks:
      - data_network

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - data_network

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/config:/usr/share/logstash/config
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch
    networks:
      - data_network

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - data_network

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - data_network

  # Prometheus (pour Grafana)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - data_network

  # Superset
  superset:
    image: apache/superset:latest
    ports:
      - "8088:8088"
    environment:
      - SUPERSET_SECRET_KEY=your-secret-key
    volumes:
      - superset_data:/app/superset
    depends_on:
      - postgres
    networks:
      - data_network

volumes:
  postgres_data:
  es_data:
  prometheus_data:
  grafana_data:
  superset_data:

networks:
  data_network:
    driver: bridge
```

#### Étape 2.2 : Configurer les services
Créez les dossiers de configuration :
```bash
mkdir -p logstash/config logstash/pipeline
mkdir -p prometheus
mkdir -p grafana/dashboards
mkdir -p airflow/dags
```

### Phase 3 : Collecte de données

#### Étape 3.1 : Générateur de données
Créez `data_generator/generator.py` :
```python
import time
import json
import random
from datetime import datetime
import psycopg2

def generer_transaction():
    """Génère une transaction e-commerce"""
    return {
        'transaction_id': f"TXN{int(time.time())}{random.randint(1000, 9999)}",
        'client_id': random.randint(1, 1000),
        'produit_id': random.randint(1, 100),
        'montant': round(random.uniform(10, 500), 2),
        'date': datetime.now().isoformat(),
        'statut': random.choice(['success', 'failed', 'pending'])
    }

def inserer_postgres(transaction):
    """Insère dans PostgreSQL"""
    conn = psycopg2.connect(
        host='localhost',
        database='data_warehouse',
        user='data_engineer',
        password='password'
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions_raw (transaction_id, client_id, produit_id, montant, date, statut)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (transaction['transaction_id'], transaction['client_id'], 
          transaction['produit_id'], transaction['montant'], 
          transaction['date'], transaction['statut']))
    conn.commit()
    cur.close()
    conn.close()

def generer_log():
    """Génère un log applicatif"""
    return {
        'timestamp': datetime.now().isoformat(),
        'level': random.choice(['INFO', 'WARNING', 'ERROR']),
        'message': f"API request {random.choice(['/api/products', '/api/orders', '/api/users'])}",
        'response_time': random.randint(10, 500),
        'status_code': random.choice([200, 200, 200, 404, 500])
    }

if __name__ == "__main__":
    # Générer des données en continu
    while True:
        transaction = generer_transaction()
        inserer_postgres(transaction)
        
        log = generer_log()
        # Écrire dans un fichier pour Logstash
        with open('logs/app.log', 'a') as f:
            f.write(json.dumps(log) + '\n')
        
        time.sleep(1)
```

#### Étape 3.2 : Configuration Logstash
Créez `logstash/pipeline/logstash.conf` :
```ruby
input {
  file {
    path => "/usr/share/logstash/logs/app.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

### Phase 4 : Transformation avec dbt

#### Étape 4.1 : Projet dbt
Créez `dbt_project/` avec la structure standard dbt :
```bash
dbt init dbt_project
cd dbt_project
```

#### Étape 4.2 : Modèles de transformation
Créez les modèles staging et marts comme dans l'exercice 07, mais connectés à PostgreSQL.

#### Étape 4.3 : Intégration Airflow
Créez `airflow/dags/dbt_dag.py` :
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    'dbt_transform',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily'
)

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/airflow/dbt_project && dbt run',
    dag=dag
)

dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /opt/airflow/dbt_project && dbt test',
    dag=dag
)

dbt_run >> dbt_test
```

### Phase 5 : Monitoring

#### Étape 5.1 : Dashboard Grafana
- Connectez Grafana à PostgreSQL et Prometheus.
- Créez des dashboards pour :
  - Métriques de pipeline (succès/échec des DAGs).
  - Métriques de données (volume, qualité).
  - Métriques business (ventes, clients).

#### Étape 5.2 : Dashboard Kibana
- Créez des visualisations pour les logs applicatifs.
- Analysez les erreurs et les temps de réponse.
- Configurez des alertes.

### Phase 6 : Dashboard analytique

#### Étape 6.1 : Superset
- Connectez Superset à PostgreSQL.
- Créez des visualisations basées sur les modèles dbt.
- Organisez-les dans un dashboard métier.

### Phase 7 : Documentation et déploiement

#### Étape 7.1 : Documentation complète
Créez `documentation/README.md` avec :
- Architecture détaillée.
- Guide d'installation et de démarrage.
- Guide d'utilisation de chaque composant.
- Troubleshooting commun.

#### Étape 7.2 : Instructions de déploiement
```bash
# Démarrer toute la stack
docker-compose up -d

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f [service_name]

# Arrêter
docker-compose down
```

## Structure attendue
```
atelier-03/
├── README.md
├── docker-compose.yml
├── architecture/
│   ├── diagramme.md
│   └── plan.md
├── data_generator/
│   └── generator.py
├── dbt_project/
│   └── (projet dbt complet)
├── airflow/
│   └── dags/
├── logstash/
│   ├── config/
│   └── pipeline/
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   └── dashboards/
└── solutions/
    └── votre-nom/
        └── (votre solution complète)
```

## Critères d'évaluation
- Architecture complète, justifiée et documentée
- Infrastructure Docker fonctionnelle (tous les services démarrés)
- Pipeline de données complet (collecte → transformation → visualisation)
- Monitoring opérationnel (Grafana + Kibana avec dashboards)
- Dashboard analytique fonctionnel (Superset connecté)
- Documentation complète (installation, utilisation, troubleshooting)
- Solution production-ready (gestion d'erreurs, logs, volumes persistants)

## Conseils
- Commencez simple : déployez un service à la fois
- Testez chaque composant individuellement avant d'intégrer
- Utilisez Docker pour l'isolation et la reproductibilité
- Documentez au fur et à mesure (ne pas attendre la fin)
- Pensez à la scalabilité (volumes, réseaux, ressources)
- Configurez les healthchecks pour chaque service

## Fonctionnalités avancées (Bonus)
- Streaming en temps réel avec Kafka
- Machine Learning intégré (modèles prédictifs)
- CI/CD pour le déploiement automatique
- Multi-environnements (dev, staging, prod)
- Backup et recovery automatisés
- Monitoring avancé avec alertes (PagerDuty, Slack)

## Soumission
```bash
mkdir -p solutions/votre-nom
# Placez tous vos fichiers dans ce dossier
git add solutions/votre-nom/
git commit -m "Atelier 03 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
