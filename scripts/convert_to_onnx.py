"""
convert_to_onnx.py
------------------
À lancer depuis Backend/ :
    python -m scripts.convert_to_onnx

Convertit model_base.pkl et model_equipe.pkl en ONNX
pour pouvoir les utiliser dans le navigateur (offline PWA).
"""
import json
import logging
from pathlib import Path

import joblib
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

logger = logging.getLogger(__name__)

MODEL_DIR = Path("app") / "ml_models"
OUTPUT_DIR = MODEL_DIR / "onnx"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def convertir(nom_pkl: str, nom_onnx: str, nb_features: int):
    """Convert a single model to ONNX format."""
    pkl_path = MODEL_DIR / nom_pkl
    if not pkl_path.exists():
        logger.error(f"❌ Fichier introuvable : {pkl_path}")
        return False

    logger.info(f"Chargement {nom_pkl}...")
    model = joblib.load(pkl_path)

    nb_classes = len(model.classes_)
    logger.info(f"   Classes ({nb_classes}) : {list(model.classes_)}")
    logger.info(f"   Features  : {nb_features}")

    # Conversion ONNX
    initial_type = [("float_input", FloatTensorType([None, nb_features]))]
    logger.info("Conversion en cours...")
    onnx_model = convert_sklearn(
        model,
        initial_types=initial_type,
        options={type(model): {"zipmap": False}},
    )

    out_path = OUTPUT_DIR / nom_onnx
    with open(out_path, "wb") as f:
        f.write(onnx_model.SerializeToString())

    size_mb = out_path.stat().st_size / (1024 * 1024)
    logger.info(f"✅ {nom_onnx} — {size_mb:.1f} Mo")
    return True


def main():
    """Main conversion routine."""
    meta_path = MODEL_DIR / "metadata.json"
    if not meta_path.exists():
        logger.error(f"❌ metadata.json introuvable dans {MODEL_DIR}")
        return

    with open(meta_path) as f:
        meta = json.load(f)

    features_base = meta.get("features_base", [])
    features_equipe = meta.get("features_equipe", [])

    logger.info("=" * 50)
    logger.info("CONVERSION PKL → ONNX")
    logger.info("=" * 50)

    ok_base = convertir("model_base.pkl", "model_base.onnx", len(features_base))
    ok_equipe = convertir(
        "model_equipe.pkl", "model_equipe.onnx", len(features_equipe)
    )

    if ok_base and ok_equipe:
        frontend_meta = {
            "classes": list(meta.get("classes", [])),
            "features_base": features_base,
            "features_equipe": features_equipe,
            "precision_base": meta.get("precision_base", 53.2),
            "precision_equipe": meta.get("precision_equipe", 96.8),
        }
        meta_out = OUTPUT_DIR / "metadata.json"
        with open(meta_out, "w", encoding="utf-8") as f:
            json.dump(frontend_meta, f, indent=2, ensure_ascii=False)

        logger.info("")
        logger.info("✅ Conversion terminée !")
        logger.info(f"   Fichiers générés dans : {OUTPUT_DIR}")
        logger.info("")
        logger.info("Prochaine étape :")
        logger.info("   Copiez le dossier app/ml_models/onnx/ dans Frontend/public/models/")
    else:
        logger.error("❌ Conversion échouée — vérifiez les chemins des modèles")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    main()
