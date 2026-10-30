"""Tests fonctionnels de service pour CDC Health Profile Explorer.
À lancer depuis le dossier deploy : python test_deployment.py
"""
import json
from pathlib import Path

from cluster_service import load_artifact, predict_cluster

BASE = Path(__file__).resolve().parent
artifact = load_artifact(BASE / "model_cdc_diabetes.joblib")
dashboard = json.loads((BASE / "cluster_dashboard_data.json").read_text(encoding="utf-8"))
assert dashboard["selected_model"] == artifact["best_model_name"]
assert len(artifact["selected_features"]) == 21

example = {
    "HighBP": 0, "HighChol": 0, "CholCheck": 1, "BMI": 27,
    "Smoker": 0, "Stroke": 0, "HeartDiseaseorAttack": 0,
    "PhysActivity": 1, "Fruits": 1, "Veggies": 1,
    "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0,
    "GenHlth": 2, "MentHlth": 0, "PhysHlth": 0, "DiffWalk": 0,
    "Sex": 1, "Age": 9, "Education": 5, "Income": 6,
}
label, info = predict_cluster(example, artifact)
known_labels = {int(item["cluster_id"]) for item in dashboard["cluster_sizes"]}
assert label in known_labels, f"Label inconnu : {label}"
assert info["distance"] is not None

# Une clé absente est imputée à partir des valeurs conservées de l'entraînement.
incomplete = dict(example)
incomplete.pop("BMI")
label_missing, _ = predict_cluster(incomplete, artifact)
assert label_missing in known_labels

# Un champ inconnu doit être signalé explicitement.
try:
    predict_cluster({**example, "UnknownFeature": 1}, artifact)
except ValueError as exc:
    assert "Variables inconnues" in str(exc)
else:
    raise AssertionError("Une variable inconnue n'a pas été rejetée.")

# Les valeurs hors domaine doivent être rejetées.
try:
    predict_cluster({**example, "HighBP": 4}, artifact)
except ValueError as exc:
    assert "HighBP" in str(exc)
else:
    raise AssertionError("Une valeur binaire invalide n'a pas été rejetée.")

print("TESTS DU SERVICE RÉUSSIS")
print(f"Modèle chargé : {artifact['best_model_name']}")
print(f"Variables : {len(artifact['selected_features'])}")
print(f"Affectation d'exemple : cluster {label}")
print("Clé absente : imputation stockée appliquée")
print("Variable inconnue et valeur hors domaine : erreurs attendues")
