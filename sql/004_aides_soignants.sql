-- ============================================================
-- Migration 004 — Aides Soignants
-- ============================================================

-- 1. Ajouter colonnes code référent au médecin
ALTER TABLE medecins
    ADD COLUMN IF NOT EXISTS code_referent       VARCHAR(10) UNIQUE,
    ADD COLUMN IF NOT EXISTS code_referent_actif BOOLEAN NOT NULL DEFAULT TRUE;

-- 2. Table aides soignants
CREATE TABLE IF NOT EXISTS aides_soignants (
    id            VARCHAR(15)  PRIMARY KEY,
    medecin_id    VARCHAR(15)  NOT NULL REFERENCES medecins(id) ON DELETE CASCADE,
    nom           VARCHAR(100) NOT NULL,
    prenom        VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    telephone     VARCHAR(20),
    statut        VARCHAR(20)  NOT NULL DEFAULT 'en_attente',

    -- Permissions
    peut_creer_patient    BOOLEAN NOT NULL DEFAULT TRUE,
    peut_lire_dossier     BOOLEAN NOT NULL DEFAULT TRUE,
    peut_modifier_patient BOOLEAN NOT NULL DEFAULT TRUE,
    peut_saisir_symptomes BOOLEAN NOT NULL DEFAULT TRUE,
    peut_supprimer        BOOLEAN NOT NULL DEFAULT FALSE,
    peut_voir_diagnostic  BOOLEAN NOT NULL DEFAULT FALSE,
    peut_prescrire        BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 3. Colonne de traçabilité dans patients
ALTER TABLE patients
    ADD COLUMN IF NOT EXISTS created_by_aide VARCHAR(15)
        REFERENCES aides_soignants(id) ON DELETE SET NULL;

-- 4. Index
CREATE INDEX IF NOT EXISTS idx_aides_medecin  ON aides_soignants(medecin_id);
CREATE INDEX IF NOT EXISTS idx_aides_statut   ON aides_soignants(statut);
CREATE INDEX IF NOT EXISTS idx_patients_aide  ON patients(created_by_aide);

-- 5. Générer les codes référents pour les médecins existants
UPDATE medecins
SET code_referent = CONCAT('AS-', UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 5)))
WHERE code_referent IS NULL;
