-- ============================================================
--  PneumoIA — Schéma PostgreSQL complet
--  IDs : PNEU-XXXXXXX pour médecins, VARCHAR(15) pour tous
-- ============================================================

-- ============================================================
--  1. TYPES ENUM
-- ============================================================

CREATE TYPE statut_medecin      AS ENUM ('en_attente','valide','rejete','suspendu');
CREATE TYPE type_document       AS ENUM (
    'diplome_specialisation',
    'diplome_medecine',
    'inscription_ordre',
    'autorisation_exercice',
    'carte_professionnelle',
    'cni'
);
CREATE TYPE sexe_patient        AS ENUM ('M','F','autre');
CREATE TYPE statut_acces        AS ENUM ('en_attente','accorde','refuse');
CREATE TYPE statut_consultation AS ENUM ('en_attente','terminee');
CREATE TYPE etat_patient        AS ENUM ('stable','surveille','urgent','critique');
CREATE TYPE type_communaute     AS ENUM ('publique','privee');
CREATE TYPE role_membre         AS ENUM ('createur','admin','membre');
CREATE TYPE statut_membre       AS ENUM ('en_attente','accepte','refuse');
CREATE TYPE type_publication    AS ENUM ('cas_clinique','question','article','discussion');
CREATE TYPE type_reaction       AS ENUM ('utile','insightful','accord','desaccord');
CREATE TYPE type_destinataire   AS ENUM ('medecin','admin');

-- ============================================================
--  2. TABLE : admins
--  ID format : ADM-XXXXXXX (généré côté Python)
-- ============================================================

CREATE TABLE admins (
    id            VARCHAR(15)  PRIMARY KEY,
    nom           VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone         VARCHAR(20),
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP
);

-- ============================================================
--  3. TABLE : medecins
--  ID format : PNEU-XXXXXXX (généré côté Python)
-- ============================================================

CREATE TABLE medecins (
    id               VARCHAR(15)     PRIMARY KEY,
    civilite         VARCHAR(10),
    nom              VARCHAR(100)    NOT NULL,
    prenom           VARCHAR(100)    NOT NULL,
    email            VARCHAR(150)    UNIQUE NOT NULL,
    password_hash    VARCHAR(255)    NOT NULL,
    specialite       VARCHAR(100),
    numero_rpps      VARCHAR(20)     UNIQUE,
    etablissement    VARCHAR(200),
    photo_url        VARCHAR(500),
    statut           statut_medecin  NOT NULL DEFAULT 'en_attente',
    motif_rejet      TEXT,
    valide_par       VARCHAR(15)     REFERENCES admins(id) ON DELETE SET NULL,
    valide_le        TIMESTAMP,
    activation_token    VARCHAR(255),
    activation_expires  TIMESTAMP,
    created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
--  4. TABLE : documents_medecin
-- ============================================================

CREATE TABLE documents_medecin (
    id            VARCHAR(15)    PRIMARY KEY,
    medecin_id    VARCHAR(15)    NOT NULL REFERENCES medecins(id) ON DELETE CASCADE,
    type_document type_document  NOT NULL,
    url_fichier   VARCHAR(500)   NOT NULL,
    nom_fichier   VARCHAR(255),
    taille_octets INTEGER,
    mime_type     VARCHAR(100),
    created_at    TIMESTAMP      NOT NULL DEFAULT NOW()
);

-- ============================================================
--  5. TABLE : patients
-- ============================================================

CREATE TABLE patients (
    id               VARCHAR(15)   PRIMARY KEY,
    nom              VARCHAR(100)  NOT NULL,
    prenom           VARCHAR(100)  NOT NULL,
    date_naissance   DATE,
    sexe             sexe_patient,
    groupe_sanguin   VARCHAR(5),
    allergies        JSONB         NOT NULL DEFAULT '[]',
    antecedents      JSONB         NOT NULL DEFAULT '[]',
    religion         VARCHAR(100),
    telephone        VARCHAR(20),
    email            VARCHAR(150),
    created_by       VARCHAR(15)   REFERENCES medecins(id) ON DELETE SET NULL,
    created_at       TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ============================================================
--  6. TABLE : acces_patient
-- ============================================================

CREATE TABLE acces_patient (
    id                        VARCHAR(15)   PRIMARY KEY,
    patient_id                VARCHAR(15)   NOT NULL REFERENCES patients(id)  ON DELETE CASCADE,
    medecin_demandeur_id      VARCHAR(15)   NOT NULL REFERENCES medecins(id)  ON DELETE CASCADE,
    medecin_proprietaire_id   VARCHAR(15)   NOT NULL REFERENCES medecins(id)  ON DELETE CASCADE,
    statut                    statut_acces  NOT NULL DEFAULT 'en_attente',
    justificatif_demande      TEXT,
    motif_refus               TEXT,
    created_at                TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMP,
    CONSTRAINT uq_acces_medecin_patient UNIQUE (patient_id, medecin_demandeur_id)
);

-- ============================================================
--  7. TABLE : consultations
-- ============================================================

CREATE TABLE consultations (
    id               VARCHAR(15)          PRIMARY KEY,
    patient_id       VARCHAR(15)          NOT NULL REFERENCES patients(id)  ON DELETE RESTRICT,
    medecin_id       VARCHAR(15)          NOT NULL REFERENCES medecins(id)  ON DELETE RESTRICT,
    symptomes        JSONB                NOT NULL,
    statut           statut_consultation  NOT NULL DEFAULT 'en_attente',
    avis_medecin     TEXT,
    prescriptions    JSONB                NOT NULL DEFAULT '[]',
    recommandations  TEXT,
    prochain_rdv     TIMESTAMP,
    partage          JSONB                NOT NULL DEFAULT '{}',
    created_at       TIMESTAMP            NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP
);

-- ============================================================
--  8. TABLE : diagnostics_ia
-- ============================================================

CREATE TABLE diagnostics_ia (
    id                  VARCHAR(15)   PRIMARY KEY,
    consultation_id     VARCHAR(15)   NOT NULL UNIQUE REFERENCES consultations(id) ON DELETE CASCADE,
    maladies            JSONB         NOT NULL,
    recommandations     JSONB,
    etat_patient        etat_patient,
    version_modele      VARCHAR(20),
    duree_inference_ms  INTEGER,
    created_at          TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ============================================================
--  9. TABLE : feedbacks_ia
-- ============================================================

CREATE TABLE feedbacks_ia (
    id               VARCHAR(15)  PRIMARY KEY,
    diagnostic_id    VARCHAR(15)  NOT NULL REFERENCES diagnostics_ia(id) ON DELETE CASCADE,
    medecin_id       VARCHAR(15)  NOT NULL REFERENCES medecins(id)       ON DELETE CASCADE,
    concordance      BOOLEAN,
    diagnostic_final VARCHAR(200),
    commentaire      TEXT,
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 10. TABLE : communautes
-- ============================================================

CREATE TABLE communautes (
    id           VARCHAR(15)      PRIMARY KEY,
    nom          VARCHAR(200)     NOT NULL,
    description  TEXT,
    type         type_communaute  NOT NULL DEFAULT 'publique',
    specialite   VARCHAR(100),
    avatar_url   VARCHAR(500),
    createur_id  VARCHAR(15)      NOT NULL REFERENCES medecins(id) ON DELETE RESTRICT,
    nb_membres   INTEGER          NOT NULL DEFAULT 1,
    nb_cas       INTEGER          NOT NULL DEFAULT 0,
    created_at   TIMESTAMP        NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 11. TABLE : membres_communaute
-- ============================================================

CREATE TABLE membres_communaute (
    id             VARCHAR(15)    PRIMARY KEY,
    communaute_id  VARCHAR(15)    NOT NULL REFERENCES communautes(id) ON DELETE CASCADE,
    medecin_id     VARCHAR(15)    NOT NULL REFERENCES medecins(id)    ON DELETE CASCADE,
    role           role_membre    NOT NULL DEFAULT 'membre',
    statut         statut_membre  NOT NULL DEFAULT 'accepte',
    joined_at      TIMESTAMP      NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_membre_communaute UNIQUE (communaute_id, medecin_id)
);

-- ============================================================
-- 12. TABLE : publications
-- ============================================================

CREATE TABLE publications (
    id               VARCHAR(15)       PRIMARY KEY,
    communaute_id    VARCHAR(15)       NOT NULL REFERENCES communautes(id)   ON DELETE CASCADE,
    auteur_id        VARCHAR(15)       NOT NULL REFERENCES medecins(id)       ON DELETE RESTRICT,
    consultation_id  VARCHAR(15)       REFERENCES consultations(id)           ON DELETE SET NULL,
    titre            VARCHAR(300)      NOT NULL,
    contenu          TEXT,
    type             type_publication  NOT NULL,
    tags             JSONB             NOT NULL DEFAULT '[]',
    nb_commentaires  INTEGER           NOT NULL DEFAULT 0,
    nb_reactions     INTEGER           NOT NULL DEFAULT 0,
    created_at       TIMESTAMP         NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 13. TABLE : commentaires
-- ============================================================

CREATE TABLE commentaires (
    id              VARCHAR(15)  PRIMARY KEY,
    publication_id  VARCHAR(15)  NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    auteur_id       VARCHAR(15)  NOT NULL REFERENCES medecins(id)     ON DELETE RESTRICT,
    contenu         TEXT         NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 14. TABLE : reactions
-- ============================================================

CREATE TABLE reactions (
    id              VARCHAR(15)    PRIMARY KEY,
    publication_id  VARCHAR(15)    NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    medecin_id      VARCHAR(15)    NOT NULL REFERENCES medecins(id)     ON DELETE CASCADE,
    type            type_reaction  NOT NULL,
    CONSTRAINT uq_reaction_medecin_publication UNIQUE (publication_id, medecin_id)
);

-- ============================================================
-- 15. TABLE : otp_codes
-- ============================================================

CREATE TABLE otp_codes (
    id          VARCHAR(15)  PRIMARY KEY,
    medecin_id  VARCHAR(15)  NOT NULL REFERENCES medecins(id) ON DELETE CASCADE,
    code        VARCHAR(6)   NOT NULL,
    expires_at  TIMESTAMP    NOT NULL,
    used        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 16. TABLE : notifications
-- ============================================================

CREATE TABLE notifications (
    id               VARCHAR(15)         PRIMARY KEY,
    destinataire_id  VARCHAR(15)         NOT NULL,
    type_dest        type_destinataire   NOT NULL,
    type_notif       VARCHAR(100)        NOT NULL,
    titre            VARCHAR(300)        NOT NULL,
    message          TEXT,
    meta             JSONB               NOT NULL DEFAULT '{}',
    lu               BOOLEAN             NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMP           NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 17. TABLE : audit_logs
-- ============================================================

CREATE TABLE audit_logs (
    id          VARCHAR(15)  PRIMARY KEY,
    medecin_id  VARCHAR(15)  REFERENCES medecins(id) ON DELETE SET NULL,
    action      VARCHAR(200) NOT NULL,
    details     JSONB        NOT NULL DEFAULT '{}',
    ip_address  INET,
    user_agent  VARCHAR(500),
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 18. TABLE : cas_cliniques_publics
-- ============================================================

CREATE TABLE cas_cliniques_publics (
    id                   VARCHAR(15)  PRIMARY KEY,
    titre                VARCHAR(300) NOT NULL,
    pathologie           VARCHAR(200),
    description          TEXT,
    tags                 JSONB        NOT NULL DEFAULT '[]',
    pdf_url              VARCHAR(500),
    auteur_id            VARCHAR(15)  REFERENCES medecins(id) ON DELETE SET NULL,
    anonymise            BOOLEAN      NOT NULL DEFAULT TRUE,
    nb_vues              INTEGER      NOT NULL DEFAULT 0,
    nb_telechargements   INTEGER      NOT NULL DEFAULT 0,
    created_at           TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE ressources_medicales (
    id                VARCHAR(15)  PRIMARY KEY,
    medecin_id        VARCHAR(15)  NOT NULL REFERENCES medecins(id) ON DELETE CASCADE,
    titre             VARCHAR(300) NOT NULL,
    resume            TEXT         NOT NULL,
    contenu           TEXT,
    pdf_url           VARCHAR(500),
    pathologie        VARCHAR(100),
    tags              JSONB        NOT NULL DEFAULT '[]',
    niveau            VARCHAR(50)  DEFAULT '3ème année',
    nb_telechargements INTEGER     NOT NULL DEFAULT 0,
    nb_vues           INTEGER      NOT NULL DEFAULT 0,
    publie            BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP
);

CREATE INDEX idx_ressources_medecin    ON ressources_medicales(medecin_id);
CREATE INDEX idx_ressources_pathologie ON ressources_medicales(pathologie);
CREATE INDEX idx_ressources_publie     ON ressources_medicales(publie);

-- ============================================================
--  INDEXES
-- ============================================================

CREATE INDEX idx_medecins_statut        ON medecins(statut);
CREATE INDEX idx_medecins_email         ON medecins(email);
CREATE INDEX idx_docs_medecin           ON documents_medecin(medecin_id);
CREATE INDEX idx_patients_created_by    ON patients(created_by);
CREATE INDEX idx_patients_nom_prenom    ON patients(nom, prenom);
CREATE INDEX idx_acces_proprietaire     ON acces_patient(medecin_proprietaire_id);
CREATE INDEX idx_acces_demandeur        ON acces_patient(medecin_demandeur_id);
CREATE INDEX idx_acces_statut           ON acces_patient(statut);
CREATE INDEX idx_consult_medecin        ON consultations(medecin_id);
CREATE INDEX idx_consult_patient        ON consultations(patient_id);
CREATE INDEX idx_consult_statut         ON consultations(statut);
CREATE INDEX idx_consult_created        ON consultations(created_at DESC);
CREATE INDEX idx_diag_consultation      ON diagnostics_ia(consultation_id);
CREATE INDEX idx_feedback_medecin       ON feedbacks_ia(medecin_id);
CREATE INDEX idx_feedback_diagnostic    ON feedbacks_ia(diagnostic_id);
CREATE INDEX idx_communautes_type       ON communautes(type);
CREATE INDEX idx_communautes_createur   ON communautes(createur_id);
CREATE INDEX idx_membres_medecin        ON membres_communaute(medecin_id);
CREATE INDEX idx_pub_communaute         ON publications(communaute_id);
CREATE INDEX idx_pub_auteur             ON publications(auteur_id);
CREATE INDEX idx_pub_type               ON publications(type);
CREATE INDEX idx_pub_created            ON publications(created_at DESC);
CREATE INDEX idx_comment_publication    ON commentaires(publication_id);
CREATE INDEX idx_otp_medecin            ON otp_codes(medecin_id);
CREATE INDEX idx_otp_expires            ON otp_codes(expires_at);
CREATE INDEX idx_notif_destinataire     ON notifications(destinataire_id, lu);
CREATE INDEX idx_notif_created          ON notifications(created_at DESC);
CREATE INDEX idx_audit_medecin          ON audit_logs(medecin_id);
CREATE INDEX idx_audit_action           ON audit_logs(action);
CREATE INDEX idx_audit_created          ON audit_logs(created_at DESC);
CREATE INDEX idx_cas_pathologie         ON cas_cliniques_publics(pathologie);
CREATE INDEX idx_cas_created            ON cas_cliniques_publics(created_at DESC);

-- ============================================================
--  COMMENTAIRES
-- ============================================================

COMMENT ON TABLE admins                IS 'Administrateurs de la plateforme PneumoIA';
COMMENT ON TABLE medecins              IS 'Médecins inscrits — ID format PNEU-XXXXXXX';
COMMENT ON TABLE documents_medecin     IS 'Documents justificatifs uploadés lors de l''inscription';
COMMENT ON TABLE patients              IS 'Dossiers patients créés par les médecins';
COMMENT ON TABLE acces_patient         IS 'Demandes d''accès inter-médecins aux dossiers patients';
COMMENT ON TABLE consultations         IS 'Consultations médicales avec symptômes et avis';
COMMENT ON TABLE diagnostics_ia        IS 'Résultats de l''analyse IA pour chaque consultation';
COMMENT ON TABLE feedbacks_ia          IS 'Retour du médecin sur la pertinence du diagnostic IA';
COMMENT ON TABLE communautes           IS 'Communautés médicales de partage de cas cliniques';
COMMENT ON TABLE membres_communaute    IS 'Appartenance des médecins aux communautés';
COMMENT ON TABLE publications          IS 'Publications dans les communautés';
COMMENT ON TABLE commentaires          IS 'Commentaires sur les publications';
COMMENT ON TABLE reactions             IS 'Réactions aux publications';
COMMENT ON TABLE otp_codes             IS 'Codes OTP 6 chiffres pour la double authentification';
COMMENT ON TABLE notifications         IS 'Notifications in-app pour médecins et admins';
COMMENT ON TABLE audit_logs            IS 'Journal d''audit des actions utilisateur';
COMMENT ON TABLE cas_cliniques_publics IS 'Cas cliniques publics affichés sur la landing page';