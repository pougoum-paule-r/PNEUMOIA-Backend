"""
fix_datetime.py
---------------
À placer dans Backend/ (même niveau que app/)
Puis lancer : python fix_datetime.py

Corrige le bug : default=lambda: datetime.utcnow  ← manque ()
dans tous les modèles SQLAlchemy.
"""
import os, re

MODELS_DIR = os.path.join("app", "models")

if not os.path.isdir(MODELS_DIR):
    print(f"ERREUR : dossier '{MODELS_DIR}' introuvable.")
    print("Lancez ce script depuis le dossier Backend/ (là où se trouve app/)")
    exit(1)

fixes = [
    # lambda: datetime.utcnow  →  datetime.utcnow
    (r"default=lambda:\s*datetime\.utcnow(?!\(\))",  "default=datetime.utcnow"),
    (r"onupdate=lambda:\s*datetime\.utcnow(?!\(\))", "onupdate=datetime.utcnow"),
]

total = 0
for filename in sorted(os.listdir(MODELS_DIR)):
    if not filename.endswith(".py"):
        continue
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    new = content
    for pattern, replacement in fixes:
        new = re.sub(pattern, replacement, new)

    if new != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"  ✅ Corrigé : {filename}")
        total += 1

print(f"\n{total} fichier(s) corrigé(s)." if total else "\nAucun fichier à corriger.")
print("\nÉtape suivante :")
print("  alembic revision --autogenerate -m 'add_patient_fields'")
print("  alembic upgrade head")