-- ============================================================
--  Migration : ajout des colonnes de profil étendu
--  À exécuter dans pgAdmin → Query Tool sur la base pneumoia
-- ============================================================

ALTER TABLE medecins ADD COLUMN IF NOT EXISTS telephone VARCHAR(30);
ALTER TABLE medecins ADD COLUMN IF NOT EXISTS adresse   VARCHAR(300);
ALTER TABLE medecins ADD COLUMN IF NOT EXISTS bio       TEXT;
ALTER TABLE medecins ADD COLUMN IF NOT EXISTS linkedin  VARCHAR(300);
ALTER TABLE medecins ADD COLUMN IF NOT EXISTS website   VARCHAR(300);

-- Vérification : affiche les colonnes de la table medecins
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'medecins'
ORDER BY ordinal_position;
