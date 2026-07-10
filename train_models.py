# Backend/train_models.py
# Lancez avec : python train_models.py

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report,
)
import joblib, json, os

# ── Dataset ────────────────────────────────────────────────────────────────────
df = pd.read_excel('dataset_final.xlsx')
y  = df['Disease']

FEATURES_ALL = [
    'AGE', 'Gender', 'smoke', 'FVC', 'FEC1', 'FEV1_FVC_Ratio',
    'PEFR', 'O2', 'ABG-P-O2', 'ABG-P-CO2', 'ABG-pH Level',
    'Scan', 'Asthama', 'Other diseaes', 'Peak_Flow'
]

# Standard : spirometrie de base disponible (FVC, FEV1, ratio, Peak Flow)
# Remplace l'ancien modele base qui avait F1=52% car sans spirometrie
# les 14 maladies pulmonaires sont quasi indistinguables
FEATURES_BASE = [
    'AGE', 'Gender', 'smoke',
    'FVC', 'FEC1', 'FEV1_FVC_Ratio', 'Peak_Flow',
    'PEFR', 'O2', 'Scan', 'Asthama', 'Other diseaes'
]

os.makedirs('app/ml_models', exist_ok=True)

print(f"\nDataset : {len(df)} lignes | {y.nunique()} classes : {sorted(y.unique().tolist())}")
print(f"Distribution :\n{y.value_counts().to_string()}\n")


# ── Évaluation complète ────────────────────────────────────────────────────────
def evaluate_model(name, pipe, X_train, X_test, y_train, y_test, X_full, y_full):
    """
    Calcule accuracy / F1 / précision / rappel sur train ET test,
    effectue une validation croisée 5-fold, et diagnostique le surapprentissage.
    """
    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # ── Métriques train (pour mesurer l'écart)
    y_pred_train = pipe.predict(X_train)
    train_acc  = accuracy_score(y_train, y_pred_train)
    train_f1   = f1_score(y_train, y_pred_train, average='weighted', zero_division=0)
    train_prec = precision_score(y_train, y_pred_train, average='weighted', zero_division=0)
    train_rec  = recall_score(y_train, y_pred_train, average='weighted', zero_division=0)

    # ── Métriques test (vraie généralisation)
    y_pred = pipe.predict(X_test)
    test_acc  = accuracy_score(y_test, y_pred)
    test_f1   = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    test_prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    test_rec  = recall_score(y_test, y_pred, average='weighted', zero_division=0)

    # ── Validation croisée 5-fold sur le dataset complet
    cv_scores = cross_validate(
        pipe, X_full, y_full, cv=kfold, n_jobs=-1,
        scoring={
            'accuracy':  'accuracy',
            'f1':        'f1_weighted',
            'precision': 'precision_weighted',
            'recall':    'recall_weighted',
        },
    )
    cv_f1_mean  = cv_scores['test_f1'].mean()
    cv_f1_std   = cv_scores['test_f1'].std()
    cv_acc_mean = cv_scores['test_accuracy'].mean()

    # ── Diagnostic surapprentissage (gap F1 train - test)
    gap = train_f1 - test_f1
    if gap > 0.10:
        overfit_status = f"SURAPPRENTISSAGE  ecart F1 = {gap:.1%}  (> 10 %)"
        overfit_risk   = "high"
    elif gap > 0.05:
        overfit_status = f"Legere tendance   ecart F1 = {gap:.1%}  (5-10 %)"
        overfit_risk   = "medium"
    else:
        overfit_status = f"Bonne generalisation  ecart F1 = {gap:.1%}  (< 5 %)"
        overfit_risk   = "low"

    if cv_f1_std > 0.05:
        overfit_status += f"  | CV instable (sigma = {cv_f1_std:.1%})"

    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")
    print(f"  TRAIN  | Accuracy {train_acc:.1%}  F1 {train_f1:.1%}  "
          f"Precision {train_prec:.1%}  Rappel {train_rec:.1%}")
    print(f"  TEST   | Accuracy {test_acc:.1%}  F1 {test_f1:.1%}  "
          f"Precision {test_prec:.1%}  Rappel {test_rec:.1%}")
    print(f"  CV 5x  | Accuracy {cv_acc_mean:.1%}  F1 {cv_f1_mean:.1%} +/- {cv_f1_std:.1%}")
    print(f"\n  Surapprentissage : {overfit_status}")
    print(f"\n  Rapport de classification (test) :")
    print(classification_report(y_test, y_pred, zero_division=0))

    return {
        "train_accuracy":  round(train_acc  * 100, 1),
        "train_f1":        round(train_f1   * 100, 1),
        "train_precision": round(train_prec * 100, 1),
        "train_recall":    round(train_rec  * 100, 1),
        "test_accuracy":   round(test_acc   * 100, 1),
        "test_f1":         round(test_f1    * 100, 1),
        "test_precision":  round(test_prec  * 100, 1),
        "test_recall":     round(test_rec   * 100, 1),
        "cv_f1_mean":      round(cv_f1_mean * 100, 1),
        "cv_f1_std":       round(cv_f1_std  * 100, 1),
        "cv_accuracy":     round(cv_acc_mean* 100, 1),
        "overfit_gap":     round(gap        * 100, 1),
        "overfit_risk":    overfit_risk,
    }


# ── Test compatibilité dataset externe ────────────────────────────────────────
def test_dataset_compatibility(pipe, features, model_name):
    """
    Verifie que le pipeline fonctionne avec des donnees de morphologie differente :
    - distributions uniformes avec 20 % de NaN
    - distribution gaussienne (echelle differente)
    - valeurs extremes hors plage d'entrainement
    """
    print(f"\n  Test compatibilite dataset externe ({model_name})")
    rng    = np.random.default_rng(2026)
    passed = 0
    total  = 3

    # Test 1 : donnees uniformes + 20 % NaN
    try:
        n      = 80
        df_ext = pd.DataFrame({f: rng.uniform(0, 100, n) for f in features})
        mask   = rng.random((n, len(features))) < 0.20
        df_ext[mask] = np.nan
        preds  = pipe.predict(df_ext)
        assert len(preds) == n
        print(f"     OK  Donnees uniformes + 20% NaN     -> {n} predictions")
        passed += 1
    except Exception as e:
        print(f"     KO  Donnees uniformes + NaN          -> {e}")

    # Test 2 : distribution gaussienne (echelle differente du dataset original)
    try:
        n        = 50
        df_gauss = pd.DataFrame({f: rng.normal(50, 25, n) for f in features})
        preds    = pipe.predict(df_gauss)
        assert len(preds) == n
        print(f"     OK  Distribution gaussienne          -> {n} predictions")
        passed += 1
    except Exception as e:
        print(f"     KO  Distribution gaussienne          -> {e}")

    # Test 3 : valeurs extremes (x10 du max habituel)
    try:
        n       = 30
        df_ext2 = pd.DataFrame({f: rng.uniform(0, 1000, n) for f in features})
        preds   = pipe.predict(df_ext2)
        assert len(preds) == n
        print(f"     OK  Valeurs extremes (x10)           -> {n} predictions")
        passed += 1
    except Exception as e:
        print(f"     KO  Valeurs extremes                 -> {e}")

    status = "COMPATIBLE" if passed == total else f"PARTIEL ({passed}/{total} tests)"
    print(f"     {status} avec datasets externes")
    return passed == total


# ── MODELE EQUIPE (15 features) ───────────────────────────────────────────────
print("=" * 60)
print("Entrainement MODELE EQUIPE (15 features)...")
X_B = df[FEATURES_ALL]
X_train_B, X_test_B, y_train_B, y_test_B = train_test_split(
    X_B, y, test_size=0.2, random_state=42, stratify=y
)
pipe_B = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler',  StandardScaler()),
    ('model',   RandomForestClassifier(
        n_estimators=300,
        max_depth=20,           # limite la profondeur -> reduit surapprentissage
        min_samples_leaf=2,     # evite feuilles sur 1 seul exemple
        min_samples_split=5,    # evite splits sur tres peu d'exemples
        max_features='sqrt',    # RF standard : racine(nb_features) features par split
        class_weight='balanced',# compense les classes desequilibrees
        random_state=42,
        n_jobs=-1,
    ))
])
pipe_B.fit(X_train_B, y_train_B)
metrics_B = evaluate_model(
    "MODELE EQUIPE", pipe_B,
    X_train_B, X_test_B, y_train_B, y_test_B,
    X_B, y,
)
test_dataset_compatibility(pipe_B, FEATURES_ALL, "modele equipe")
joblib.dump(pipe_B, 'app/ml_models/model_equipe.pkl')


# ── MODELE BASE (8 features) ──────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Entrainement MODELE BASE (8 features)...")
X_A = df[FEATURES_BASE]
X_train_A, X_test_A, y_train_A, y_test_A = train_test_split(
    X_A, y, test_size=0.2, random_state=42, stratify=y
)
pipe_A = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler',  StandardScaler()),
    ('model',   RandomForestClassifier(
        n_estimators=500,
        max_depth=15,
        min_samples_leaf=2,
        min_samples_split=5,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
    ))
])
pipe_A.fit(X_train_A, y_train_A)
metrics_A = evaluate_model(
    "MODELE BASE", pipe_A,
    X_train_A, X_test_A, y_train_A, y_test_A,
    X_A, y,
)
test_dataset_compatibility(pipe_A, FEATURES_BASE, "modele base")
joblib.dump(pipe_A, 'app/ml_models/model_base.pkl')


# ── Metadata ───────────────────────────────────────────────────────────────────
classes = sorted(y.unique().tolist())
meta = {
    "classes":          classes,
    "features_base":    FEATURES_BASE,
    "features_equipe":  FEATURES_ALL,
    # Modele base
    "precision_base":          metrics_A["test_accuracy"],   # compat API existante
    "f1_base":                 metrics_A["test_f1"],
    "recall_base":             metrics_A["test_recall"],
    "precision_score_base":    metrics_A["test_precision"],
    "cv_f1_base":              metrics_A["cv_f1_mean"],
    "overfit_risk_base":       metrics_A["overfit_risk"],
    "overfit_gap_base":        metrics_A["overfit_gap"],
    # Modele equipe
    "precision_equipe":        metrics_B["test_accuracy"],   # compat API existante
    "f1_equipe":               metrics_B["test_f1"],
    "recall_equipe":           metrics_B["test_recall"],
    "precision_score_equipe":  metrics_B["test_precision"],
    "cv_f1_equipe":            metrics_B["cv_f1_mean"],
    "overfit_risk_equipe":     metrics_B["overfit_risk"],
    "overfit_gap_equipe":      metrics_B["overfit_gap"],
}
with open('app/ml_models/metadata.json', 'w') as f:
    json.dump(meta, f, indent=2)


# ── Resume final ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  RESUME FINAL")
print("=" * 60)
for label, m in [("Modele base   ", metrics_A), ("Modele equipe ", metrics_B)]:
    print(
        f"  {label} | "
        f"Accuracy {m['test_accuracy']}%  "
        f"F1 {m['test_f1']}%  "
        f"Precision {m['test_precision']}%  "
        f"Rappel {m['test_recall']}%  "
        f"CV-F1 {m['cv_f1_mean']}%+/-{m['cv_f1_std']}%  "
        f"Surrapprentissage : {m['overfit_risk']} ({m['overfit_gap']}%)"
    )
print(f"\n  Fichiers sauvegardes dans app/ml_models/")
print(f"  -> model_base.pkl  | model_equipe.pkl  | metadata.json")
