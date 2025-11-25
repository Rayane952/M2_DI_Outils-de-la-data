import yaml
import json

# Lire YAML
with open("create_Dashboard_Exercice-1_1.yaml", "r", encoding="utf-8") as f:
    yaml_data = yaml.safe_load(f)

# Convertir en JSON
with open("dashboard_export.json", "w", encoding="utf-8") as f:
    json.dump(yaml_data, f, indent=4, ensure_ascii=False)

print("Conversion terminée !")