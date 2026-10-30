"""Tests de routes Flask pour CDC Health Profile Explorer.
À lancer avec les dépendances installées : python test_web_app.py
"""
from app import app, FEATURES

EXAMPLE = {
    "HighBP": 0, "HighChol": 0, "CholCheck": 1, "BMI": 27,
    "Smoker": 0, "Stroke": 0, "HeartDiseaseorAttack": 0,
    "PhysActivity": 1, "Fruits": 1, "Veggies": 1,
    "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0,
    "GenHlth": 2, "MentHlth": 0, "PhysHlth": 0, "DiffWalk": 0,
    "Sex": 1, "Age": 9, "Education": 5, "Income": 6,
}

client = app.test_client()

for path in ("/", "/groupes", "/methodologie"):
    response = client.get(path)
    assert response.status_code == 200, f"{path}: HTTP {response.status_code}"

health = client.get("/health")
assert health.status_code == 200
assert health.get_json().get("ready") is True, health.get_json()

# Une observation complète doit donner une seule affectation.
result = client.post("/", data=EXAMPLE)
assert result.status_code == 200
assert "RÉSULTAT DE L’AFFECTATION".encode("utf-8") in result.data

# Les champs non renseignés sont imputés avec les valeurs du train.
incomplete = {key: value for key, value in EXAMPLE.items() if key != "BMI"}
result_missing = client.post("/", data=incomplete)
assert result_missing.status_code == 200
assert b"variable(s) imput\xc3\xa9e(s)" in result_missing.data

# Un formulaire trop incomplet affiche une erreur lisible.
result_short = client.post("/", data={"BMI": 27, "Age": 9})
assert result_short.status_code == 200
assert b"au moins cinq variables" in result_short.data

# L'API accepte les champs absents (imputation) et rejette les clés inconnues.
api_ok = client.post("/api/predict", json=incomplete)
assert api_ok.status_code == 200, api_ok.get_json()
api_bad = client.post("/api/predict", json={**EXAMPLE, "UnknownFeature": 1})
assert api_bad.status_code == 400, api_bad.get_json()

print("TESTS WEB RÉUSSIS")
print("Routes : /, /groupes, /methodologie, /health")
print("Formulaire complet, imputation, validation et API : OK")
print(f"Variables du modèle : {len(FEATURES)}")
