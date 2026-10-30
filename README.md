# CDC Health Profile Explorer — déploiement

Application Flask en français fondée sur le notebook CDC Diabetes Health Indicators (UCI ID 891). Elle déploie **un seul modèle : K-Means**, retenu lors de l'exécution de la règle multicritère du notebook. Elle ne réentraîne rien à l'ouverture ou à la prédiction.

## Contenu de ce dossier

- `model_cdc_diabetes.joblib` : artefact créé à partir du CSV complet fourni, avec le K-Means ajusté, le `StandardScaler`, les 21 variables ordonnées et les valeurs d'imputation.
- `cluster_dashboard_data.json` : métriques et profils calculés par le notebook exécuté, y compris les effectifs, la part de chaque cluster et la distribution descriptive de `Diabetes_012` après le clustering.
- `cluster_service.py` : `load_artifact()` et `predict_cluster(patient_dict)`.
- `app.py`, `templates/index.html`, `static/style.css` : interface web et API JSON.
- `requirements-model.txt` : versions Python packages alignées sur l'artefact exécuté.
- `render.yaml` et `Procfile` : configuration pour un hébergement compatible avec Gunicorn.

Les artefacts inclus ont été générés depuis le fichier de données complet fourni dans l'environnement. Le notebook source original charge les données UCI. Les métriques affichées proviennent de l'exécution du notebook sur les 253 680 lignes et son échantillon aléatoire de 3 000 individus (`RANDOM_STATE = 42`). Modèle retenu par le classement multicritère : K-Means.

## 1. Lancer localement (Windows)

Installe Python 3.13.5, ouvre PowerShell dans ce dossier, puis :

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Ouvre `http://127.0.0.1:5000`. La navigation propose trois pages : `/` pour le formulaire d’affectation (page principale), `/groupes` pour le tableau de bord analytique et `/methodologie` pour les informations et limites. Vérifie `http://127.0.0.1:5000/health` ; la réponse attendue contient `"ready": true`. Lance `python test_deployment.py` pour tester le service de prédiction et `python test_web_app.py` pour tester les routes et le formulaire. Les champs laissés vides dans le formulaire sont imputés avec les valeurs mémorisées à l’entraînement ; au moins cinq variables doivent être renseignées. Les variables inconnues transmises à l’API sont refusées.

Le modèle a été sérialisé avec Python 3.13.5, scikit-learn 1.8.0, NumPy 2.3.5, pandas 2.2.3 et joblib 1.5.3. Garder ces versions identiques réduit les risques de problème de compatibilité.

## 2. Tester l'API

`POST /api/predict` avec un objet JSON contenant les 21 champs ou un sous-ensemble. Le service vérifie aussi les valeurs binaires et les plages attendues des variables ordinales et numériques. Les champs absents sont imputés avec les valeurs mémorisées par le notebook ; les noms de champs inconnus renvoient une erreur 400.

Exemple (valeurs illustratives, pas une personne réelle) :

```json
{
  "HighBP": 0, "HighChol": 0, "CholCheck": 1, "BMI": 27,
  "Smoker": 0, "Stroke": 0, "HeartDiseaseorAttack": 0,
  "PhysActivity": 1, "Fruits": 1, "Veggies": 1,
  "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0,
  "GenHlth": 2, "MentHlth": 0, "PhysHlth": 0, "DiffWalk": 0,
  "Sex": 1, "Age": 9, "Education": 5, "Income": 6
}
```

Dans le formulaire HTML, les champs sont facultatifs, mais au moins cinq variables doivent être renseignées. Les champs vides sont imputés avec les valeurs mémorisées à l'entraînement et le résultat indique le nombre de variables imputées. Dans l'API, un champ omis est également considéré manquant et imputé comme au prétraitement ; un champ inconnu est refusé.

## 3. Déployer sur Render

1. Décompresse le dossier et crée un dépôt GitHub contenant **le contenu de ce dossier à sa racine**.
2. Dans Render, choisis **New → Web Service** et connecte le dépôt.
3. Runtime : Python. Build command : `pip install -r requirements-model.txt`. Start command : `gunicorn app:app --workers 1 --threads 4 --timeout 120`.
4. Le fichier `render.yaml` contient déjà la configuration de démarrage et le contrôle de santé. Conserve Python 3.13.5 et les dépendances épinglées pour correspondre à l'artefact joblib.
5. Après déploiement, consulte `/health`. L'application doit retourner `ready: true` avant d'utiliser le formulaire.

La création effective d'un service public nécessite ton compte GitHub/Render ; elle n'est pas effectuée depuis cet environnement.

## Limites

Les clusters sont des profils statistiques descriptifs, pas des diagnostics ni des probabilités de diabète. La prévalence du statut `Diabetes_012` est calculée après le clustering et ne participe pas à l'affectation. L'apprentissage utilise 21 variables standardisées sur 3 000 individus ; la figure IMC/âge n'en montre que deux. La distance euclidienne sur variables binaires/ordinales présente des limites. Les valeurs saisies ne sont pas enregistrées dans une base de données par l'application.
