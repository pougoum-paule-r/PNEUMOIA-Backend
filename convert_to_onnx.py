"""
convert_to_onnx.py
------------------
À lancer depuis Backend/ :
    python convert_to_onnx.py

Convertit model_base.pkl et model_equipe.pkl en ONNX
pour pouvoir les utiliser dans le navigateur (offline PWA).
"""
import joblib
import json
import numpy as np
from pathlib import Path
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

MODEL_DIR  = Path("app/ml_models")
OUTPUT_DIR = Path("app/ml_models/onnx")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def convertir(nom_pkl: str, nom_onnx: str, nb_features: int):
    pkl_path = MODEL_DIR / nom_pkl
    if not pkl_path.exists():
        print(f"❌ Fichier introuvable : {pkl_path}")
        return False

    print(f"Chargement {nom_pkl}...")
    model = joblib.load(pkl_path)

    nb_classes = len(model.classes_)
    print(f"   Classes ({nb_classes}) : {list(model.classes_)}")
    print(f"   Features  : {nb_features}")

    # Conversion ONNX
    initial_type = [('float_input', FloatTensorType([None, nb_features]))]
    print(f"Conversion en cours...")
    onnx_model = convert_sklearn(
        model,
        initial_types=initial_type,
        options={type(model): {'zipmap': False}},  # retourne des probabilités en array, pas dict
    )

    out_path = OUTPUT_DIR / nom_onnx
    with open(out_path, 'wb') as f:
        f.write(onnx_model.SerializeToString())

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"✅ {nom_onnx} — {size_mb:.1f} Mo")
    return True

def main():
    # Charger metadata pour connaître les features
    meta_path = MODEL_DIR / "metadata.json"
    if not meta_path.exists():
        print(f"❌ metadata.json introuvable dans {MODEL_DIR}")
        return

    with open(meta_path) as f:
        meta = json.load(f)

    features_base   = meta.get("features_base",   [])
    features_equipe = meta.get("features_equipe",  [])

    print("=" * 50)
    print("CONVERSION PKL → ONNX")
    print("=" * 50)

    ok_base   = convertir("model_base.pkl",   "model_base.onnx",   len(features_base))
    ok_equipe = convertir("model_equipe.pkl", "model_equipe.onnx", len(features_equipe))

    if ok_base and ok_equipe:
        # Sauvegarder les metadata pour le frontend
        frontend_meta = {
            "classes":         list(meta.get("classes", [])),
            "features_base":   features_base,
            "features_equipe": features_equipe,
            "precision_base":  meta.get("precision_base",  53.2),
            "precision_equipe": meta.get("precision_equipe", 96.8),
        }
        meta_out = OUTPUT_DIR / "metadata.json"
        with open(meta_out, "w", encoding="utf-8") as f:
            json.dump(frontend_meta, f, indent=2, ensure_ascii=False)

        print()
        print("✅ Conversion terminée !")
        print(f"   Fichiers générés dans : {OUTPUT_DIR}")
        print()
        print("Prochaine étape :")
        print("   Copiez le dossier app/ml_models/onnx/ dans Frontend/public/models/")
    else:
        print("❌ Conversion échouée — vérifiez les chemins des modèles")

if __name__ == "__main__":
    main()