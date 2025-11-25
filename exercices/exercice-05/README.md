# Exercice 05 : Grafana + Prometheus - Monitoring complet

## Objectifs pédagogiques

1. Concevoir un stack de supervision open source prêt pour la production.
2. Collecter et explorer des métriques système (CPU, mémoire, réseau, RPS).
3. Créer un dashboard Grafana opérationnel avec filtres, variables et panels variés.
4. Configurer des alertes fiables pour prévenir les incidents.
5. Documenter vos choix (PromQL, structure du dashboard, plan d’alerte).

## Contexte métier

Vous gérez la plateforme d’une API critique. Les incidents des dernières semaines demandent un monitoring fiable pour :

- Identifier rapidement les pics de charge.
- Isoler les serveurs défaillants.
- Surveiller les latences et les erreurs applicatives.
- Prévenir les équipes (Slack/mail) lorsque les seuils sont dépassés.

## Prérequis techniques

- Docker + Docker Compose installés.
- Port 3000 (Grafana) et 9090 (Prometheus) libres.
- 2 Go de RAM disponibles.
- Connaissances de base en PromQL recommandées.

## Installation

Créez un fichier `docker-compose.yml` :

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

## Données et exporter custom

1. **Générez des métriques synthétiques** :
   ```bash
   cd exercice-05
   python generer_metriques.py
   ```
   Ce script crée `donnees/metriques.csv` (base historique).

2. **Lancez l’exporter HTTP** (faux service exposant les métriques en temps réel) :
   ```bash
   python exporter_metriques.py
   ```
   L’exporter écoute sur `http://localhost:8000/metrics` et expose les séries `app_cpu_usage`, `app_memory_usage`, etc.

3. **Ajoutez ce target dans `prometheus.yml`** (déjà prévu dans la configuration ci-dessus).

## Plan de travail

### Étape 1 : Configuration Prometheus

Créez `prometheus.yml` :

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'metriques'
    static_configs:
      - targets: ['host.docker.internal:8000']
```

### Étape 2 : Démarrer les services

```bash
docker-compose up -d
```

### Étape 3 : Vérifier Prometheus

1. **Accédez à Prometheus** : http://localhost:9090
2. **Testez une requête** : `up`
3. **Explorez les métriques disponibles**

### Étape 4 : Configuration Grafana

1. **Accédez à Grafana** : http://localhost:3000
2. **Identifiants** : admin/admin
3. **Ajoutez Prometheus comme source** :
   - Configuration > Data Sources
   - Add data source > Prometheus
   - URL : http://prometheus:9090
   - Save & Test

### Étape 5 : Créer des dashboards

Créez au moins 6 panneaux :

1. **Time Series** : Utilisation CPU par serveur (moyenne sur 5 min).
2. **Gauge** : Mémoire disponible avec seuils visuels.
3. **Bar Chart** : Top serveurs par charge moyenne sur 1h.
4. **Stat** : Nombre total de requêtes par minute.
5. **Heatmap** : Distribution des latences (p95, p99).
6. **Table** : Synthèse par serveur (CPU, mémoire, réseau, état).

Ajoutez également :
7. **Panel “Erreurs”** : courbe du taux de requêtes 5xx.
8. **Panel “Alert status”** : affichage des alertes actives.
9. **Panel “Annotations”** : événements clés (deploy, incidents).

### Étape 6 : Alertes

1. **Créez des règles d'alerte** :
   - CPU > 80%
   - Mémoire < 10%
   - Disque > 90%

2. **Configurez les notifications** (Alertmanager ou intégration Slack/email).

### Étape 7 : Documentation

Dans `resultats.md`, décrivez :
- Votre architecture (schéma rapide).
- Le détail des panels clés (PromQL, interprétation).
- Les alertes mises en place et leur logique.
- Les risques détectés dans les données simulées.

## Structure attendue

```
exercice-05/
├── README.md (ce fichier)
├── docker-compose.yml
├── prometheus.yml
├── exporter_metriques.py
├── generer_metriques.py
└── solutions/
    └── votre-nom/
        ├── dashboard.json
        ├── screenshots/
        └── resultats.md
```

## Critères d'évaluation

- [ ] Prometheus et Grafana installés
- [ ] Métriques collectées
- [ ] Au moins 6 panneaux créés
- [ ] Alertes configurées
- [ ] Dashboard exporté
- [ ] Documentation complète

## Conseils

- Utilisez les variables de dashboard
- Organisez les panneaux par catégorie
- Testez les alertes
- Documentez vos requêtes PromQL

## Ressources

- Documentation Grafana : https://grafana.com/docs/
- Documentation Prometheus : https://prometheus.io/docs/
- PromQL : https://prometheus.io/docs/prometheus/latest/querying/basics/

## Aide

Si vous êtes bloqué :
1. Vérifiez les logs Docker
2. Consultez la documentation
3. Ouvrez une issue sur le dépôt GitHub

## Comment soumettre votre solution

### Étapes pour pousser votre exercice sur GitHub

1. **Générez les métriques** :
   ```bash
   cd exercice-05
   python generer_metriques.py
   ```

2. **Créez votre dossier de solution** :
   ```bash
   mkdir -p solutions/votre-nom
   cd solutions/votre-nom
   ```

3. **Exportez votre dashboard** depuis Grafana
4. **Prenez des captures d'écran**
5. **Créez un fichier `resultats.md`**

6. **Ajoutez et commitez** :
   ```bash
   git add solutions/votre-nom/
   git commit -m "Solution exercice 05 - Votre Nom"
   git push origin main
   ```

**Important** : N'oubliez pas de remplacer "votre-nom" par votre vrai nom !
