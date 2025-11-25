# Atelier 02 : Pipeline Machine Learning complet

## Objectifs pédagogiques

1. Construire un pipeline ML de bout en bout (de la donnée au déploiement).
2. Préparer les données pour le machine learning (feature engineering).
3. Entraîner, évaluer et comparer plusieurs modèles.
4. Déployer un modèle en production via une API REST.
5. Documenter la méthodologie et les performances dans `resultats.md`.

## Contexte

Vous êtes Data Scientist pour une entreprise e-commerce. Vous devez créer un système de prédiction pour un problème métier concret parmi :

- Prédiction de churn client.
- Prévision de ventes.
- Classification de produits (catégorisation automatique).
- Détection de fraude.
- Recommandation de produits.

Livrable attendu : un pipeline ML complet avec API de prédiction déployée.

## Prérequis

- Python 3.8+
- Bibliothèques : pandas, scikit-learn, xgboost, matplotlib, joblib, flask/fastapi
- Connaissances en machine learning (supervisé)
- Compréhension des métriques d'évaluation

## Installation

```bash
pip install pandas scikit-learn xgboost matplotlib seaborn joblib flask fastapi uvicorn
```

## Étapes guidées

### Phase 1 : Définition du problème

#### Étape 1.1 : Choix du problème métier
Sélectionnez un problème concret et documentez :
- Variable cible (target) : qu'est-ce qu'on prédit ?
- Métriques de succès : accuracy, precision, recall, F1, ROC-AUC, RMSE, MAE ?
- Impact métier : pourquoi ce problème est important ?

#### Étape 1.2 : Collecte de données
```bash
# Option 1 : Utiliser un dataset public
# Kaggle : https://www.kaggle.com/datasets
# UCI ML Repository : https://archive.ics.uci.edu/

# Option 2 : Créer un dataset synthétique réaliste
cd atelier-02
python generer_donnees_ml.py
```

Documentez la source des données dans `donnees/README.md`.

### Phase 2 : Exploration et préparation

#### Étape 2.1 : EDA approfondie
Créez `notebooks/01_exploration.ipynb` :
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("donnees/raw/dataset.csv")

# Analyse univariée
print(df.describe())
df.hist(figsize=(15, 10))
plt.show()

# Analyse multivariée
sns.pairplot(df, hue='target')
plt.show()

# Détection des outliers
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1
outliers = df[((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
print(f"Nombre d'outliers : {len(outliers)}")

# Analyse des corrélations
corr_matrix = df.corr()
sns.heatmap(corr_matrix, annot=True)
plt.show()
```

#### Étape 2.2 : Feature Engineering
Créez `src/feature_engineering.py` :
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

def creer_features(df):
    """Crée de nouvelles features"""
    # Features temporelles
    if 'date' in df.columns:
        df['annee'] = pd.to_datetime(df['date']).dt.year
        df['mois'] = pd.to_datetime(df['date']).dt.month
        df['jour_semaine'] = pd.to_datetime(df['date']).dt.dayofweek
    
    # Features d'interaction
    if 'montant' in df.columns and 'quantite' in df.columns:
        df['montant_par_unite'] = df['montant'] / df['quantite']
    
    # Features agrégées
    if 'client_id' in df.columns:
        df['nb_commandes_client'] = df.groupby('client_id')['commande_id'].transform('count')
        df['ca_total_client'] = df.groupby('client_id')['montant'].transform('sum')
    
    return df

def encoder_variables(df, colonnes_categorielles):
    """Encode les variables catégorielles"""
    le = LabelEncoder()
    for col in colonnes_categorielles:
        if col in df.columns:
            df[f'{col}_encoded'] = le.fit_transform(df[col])
    return df

def normaliser_variables(df, colonnes_numeriques):
    """Normalise les variables numériques"""
    scaler = StandardScaler()
    df[colonnes_numeriques] = scaler.fit_transform(df[colonnes_numeriques])
    return df, scaler
```

#### Étape 2.3 : Gestion des valeurs manquantes
```python
# Stratégies selon le type de variable
df['col_num'].fillna(df['col_num'].median(), inplace=True)
df['col_cat'].fillna(df['col_cat'].mode()[0], inplace=True)
```

#### Étape 2.4 : Sélection de features
```python
from sklearn.feature_selection import SelectKBest, f_classif

selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X, y)
selected_features = X.columns[selector.get_support()]
```

### Phase 3 : Modélisation

#### Étape 3.1 : Baseline
Créez `src/models/baseline.py` :
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Modèle baseline simple
baseline = LogisticRegression()
baseline.fit(X_train, y_train)
y_pred = baseline.predict(X_test)

print(f"Accuracy baseline : {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))
```

#### Étape 3.2 : Modèles multiples
Créez `src/models/train.py` :
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import xgboost as xgb
from sklearn.model_selection import cross_val_score

models = {
    'Logistic Regression': LogisticRegression(),
    'Random Forest': RandomForestClassifier(n_estimators=100),
    'XGBoost': xgb.XGBClassifier(),
    'SVM': SVC(probability=True)
}

results = {}
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    results[name] = {
        'mean': scores.mean(),
        'std': scores.std()
    }
    print(f"{name}: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

#### Étape 3.3 : Optimisation des hyperparamètres
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2]
}

grid_search = GridSearchCV(
    xgb.XGBClassifier(),
    param_grid,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)
print(f"Meilleurs paramètres : {grid_search.best_params_}")
print(f"Meilleur score : {grid_search.best_score_:.4f}")
```

### Phase 4 : Évaluation et sélection

#### Étape 4.1 : Évaluation rigoureuse
Créez `src/models/evaluate.py` :
```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)

def evaluer_modele(model, X_test, y_test):
    """Évalue un modèle avec plusieurs métriques"""
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }
    
    print("Métriques d'évaluation :")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    print("\nMatrice de confusion :")
    print(confusion_matrix(y_test, y_pred))
    
    return metrics
```

#### Étape 4.2 : Interprétabilité
```python
import shap

# Feature importance
feature_importance = model.feature_importances_
feature_names = X.columns
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

# SHAP values (si XGBoost)
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

### Phase 5 : Pipeline de production

#### Étape 5.1 : Créer le pipeline
Créez `src/pipeline.py` :
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=100))
])

pipeline.fit(X_train, y_train)
```

#### Étape 5.2 : Sauvegarder le modèle
```python
import joblib

joblib.dump(pipeline, 'models/pipeline_v1.pkl')
joblib.dump(scaler, 'models/scaler_v1.pkl')
```

#### Étape 5.3 : API de prédiction
Créez `src/api/app.py` (Flask) :
```python
from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load('models/pipeline_v1.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    df = pd.DataFrame([data])
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0]
    
    return jsonify({
        'prediction': int(prediction),
        'probability': float(max(probability))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Ou avec FastAPI :
```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()
model = joblib.load('models/pipeline_v1.pkl')

class PredictionRequest(BaseModel):
    feature1: float
    feature2: float
    # ... autres features

@app.post('/predict')
def predict(request: PredictionRequest):
    df = pd.DataFrame([request.dict()])
    prediction = model.predict(df)[0]
    return {'prediction': int(prediction)}
```

#### Étape 5.4 : Tests
Créez `tests/test_pipeline.py` :
```python
import unittest
from src.pipeline import pipeline
from src.api.app import app

class TestPipeline(unittest.TestCase):
    def test_prediction(self):
        # Test de prédiction
        result = pipeline.predict(X_test[:1])
        self.assertIsNotNone(result)
    
    def test_api(self):
        # Test de l'API
        with app.test_client() as client:
            response = client.post('/predict', json={'feature1': 1.0, 'feature2': 2.0})
            self.assertEqual(response.status_code, 200)
```

### Phase 6 : Documentation et déploiement

#### Étape 6.1 : Documentation
Créez `documentation/README.md` avec :
- Méthodologie détaillée.
- Performances du modèle (métriques).
- Guide d'utilisation de l'API.
- Limitations et améliorations futures.

#### Étape 6.2 : Déploiement (optionnel)
```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/api/app.py"]
```

## Structure attendue
```
atelier-02/
├── README.md
├── donnees/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_modeling.ipynb
├── src/
│   ├── feature_engineering.py
│   ├── pipeline.py
│   ├── models/
│   │   ├── train.py
│   │   └── evaluate.py
│   └── api/
│       └── app.py
├── models/
│   └── (modèles sauvegardés)
├── tests/
│   └── test_pipeline.py
└── solutions/
    └── votre-nom/
        └── (votre solution complète)
```

## Critères d'évaluation
- Pipeline ML complet et fonctionnel de bout en bout
- Feature engineering pertinent et documenté
- Modèles bien entraînés, évalués et comparés
- Code propre, modulaire et testé
- API fonctionnelle avec validation des inputs
- Documentation complète (méthodologie + performances)
- Performance du modèle justifiée avec métriques appropriées

## Conseils
- Commencez simple, complexifiez progressivement
- Documentez chaque étape (choix, résultats)
- Visualisez vos résultats (métriques, features importance)
- Testez sur différents datasets (train/validation/test)
- Pensez à la production dès le début (pipeline, API)
- Validez avec des métriques métier (pas seulement techniques)

## Fonctionnalités avancées (Bonus)
- AutoML (Auto-sklearn, TPOT)
- Deep Learning (TensorFlow/PyTorch)
- A/B testing du modèle
- Monitoring en production (MLflow, Weights & Biases)
- Retraining automatique
- Explicabilité avancée (LIME, SHAP)

## Soumission
```bash
mkdir -p solutions/votre-nom
# Placez tous vos fichiers dans ce dossier
git add solutions/votre-nom/
git commit -m "Atelier 02 - Votre Nom"
git push origin main
```
Remplacez `votre-nom` par vos nom/prénom.
