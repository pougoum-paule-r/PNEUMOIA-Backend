# Backend/train_models.py
# Lancez avec : python train_models.py

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import joblib, json, os

# ── Chargez votre dataset ─────────────────────────
df = pd.read_excel('dataset_final.xlsx')
y  = df['Disease']

FEATURES_ALL = [
    'AGE', 'Gender', 'smoke', 'FVC', 'FEC1', 'FEV1_FVC_Ratio',
    'PEFR', 'O2', 'ABG-P-O2', 'ABG-P-CO2', 'ABG-pH Level',
    'Scan', 'Asthama', 'Other diseaes', 'Peak_Flow'
]

FEATURES_BASE = [
    'AGE', 'Gender', 'smoke',
    'PEFR', 'O2', 'Scan', 'Asthama', 'Other diseaes'
]

os.makedirs('app/ml_models', exist_ok=True)

# ── MODÈLE ÉQUIPÉ ─────────────────────────────────
print("Entraînement modèle équipé...")
X_B = df[FEATURES_ALL]
X_train_B, X_test_B, y_train_B, y_test_B = train_test_split(
    X_B, y, test_size=0.2, random_state=42, stratify=y
)
pipe_B = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler',  StandardScaler()),
    ('model',   RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1))
])
pipe_B.fit(X_train_B, y_train_B)
acc_B = accuracy_score(y_test_B, pipe_B.predict(X_test_B))
print(f" Modèle équipé : {acc_B*100:.1f}%")
joblib.dump(pipe_B, 'app/ml_models/model_equipe.pkl')

# ── MODÈLE BASE ───────────────────────────────────
print("Entraînement modèle base...")
X_A = df[FEATURES_BASE]
X_train_A, X_test_A, y_train_A, y_test_A = train_test_split(
    X_A, y, test_size=0.2, random_state=42, stratify=y
)
pipe_A = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler',  StandardScaler()),
    ('model',   RandomForestClassifier(n_estimators=500, random_state=42, n_jobs=-1))
])
pipe_A.fit(X_train_A, y_train_A)
acc_A = accuracy_score(y_test_A, pipe_A.predict(X_test_A))
print(f" Modèle base : {acc_A*100:.1f}%")
joblib.dump(pipe_A, 'app/ml_models/model_base.pkl')

# ── METADATA ──────────────────────────────────────
classes = sorted(y.unique().tolist())
meta = {
    "classes":          classes,
    "features_base":    FEATURES_BASE,
    "features_equipe":  FEATURES_ALL,
    "precision_base":   round(acc_A*100, 1),
    "precision_equipe": round(acc_B*100, 1),
}
with open('app/ml_models/metadata.json', 'w') as f:
    json.dump(meta, f, indent=2)

print("\n Terminé !")
print(f"   app/ml_models/model_base.pkl   → {acc_A*100:.1f}%")
print(f"   app/ml_models/model_equipe.pkl → {acc_B*100:.1f}%")
print(f"   app/ml_models/metadata.json")