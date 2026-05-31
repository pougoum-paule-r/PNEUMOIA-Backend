@"
# PNEUMOIA - Backend

API REST développée avec **FastAPI** pour la plateforme de diagnostic médical PNEUMOIA.

## Stack technique
- Python / FastAPI
- PostgreSQL + Alembic (migrations)
- JWT Authentication
- IA / ML models (diagnostic pneumonie)

## Branches
- ``main`` : branche stable de référence
- ``BackendMedecin`` : fonctionnalités dashboard médecin
- ``dev-Back`` : développement en cours
- ``prod-back`` : version de production

## Lancer le projet
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
"@ | Out-File -FilePath "README.md" -Encoding utf8