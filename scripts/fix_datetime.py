"""
fix_datetime.py
---------------
À placer dans Backend/ (même niveau que app/)
Puis lancer : python -m scripts.fix_datetime

Corrige le bug : default=lambda: datetime.utcnow  ← manque ()
dans tous les modèles SQLAlchemy.
"""
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

MODELS_DIR = Path("app") / "models"

if not MODELS_DIR.is_dir():
    logger.error(f"ERREUR : dossier '{MODELS_DIR}' introuvable.")
    logger.error("Lancez ce script depuis le dossier Backend/ (là où se trouve app/)")
    exit(1)

fixes = [
    # lambda: datetime.utcnow  →  datetime.utcnow
    (r"default=lambda:\s*datetime\.utcnow(?!\(\))", "default=datetime.utcnow"),
    (
        r"onupdate=lambda:\s*datetime\.utcnow(?!\(\))",
        "onupdate=datetime.utcnow",
    ),
]

total = 0
for filename in sorted(MODELS_DIR.glob("*.py")):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    new = content
    for pattern, replacement in fixes:
        new = re.sub(pattern, replacement, new)

    if new != content:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new)
        logger.info(f"✅ Corrigé : {filename.name}")
        total += 1

if total:
    logger.info(f"\n{total} fichier(s) corrigé(s).")
    logger.info("\nÉtape suivante :")
    logger.info("  alembic revision --autogenerate -m 'add_patient_fields'")
    logger.info("  alembic upgrade head")
else:
    logger.info("Aucun fichier à corriger.")
