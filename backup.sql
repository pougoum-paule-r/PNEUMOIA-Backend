--
-- PostgreSQL database dump
--

\restrict 8R3ilzTlhSaSzsdSC8ablWktObZLD3Fdy2Xaw1xyEhReuXlHCGX1g33fIru9ih5

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: auteur_type_commentaire; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.auteur_type_commentaire AS ENUM (
    'medecin',
    'aide_soignant'
);


ALTER TYPE public.auteur_type_commentaire OWNER TO pneumo_user;

--
-- Name: auteur_type_like_com; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.auteur_type_like_com AS ENUM (
    'medecin',
    'aide_soignant'
);


ALTER TYPE public.auteur_type_like_com OWNER TO pneumo_user;

--
-- Name: auteur_type_like_msg; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.auteur_type_like_msg AS ENUM (
    'medecin',
    'aide_soignant'
);


ALTER TYPE public.auteur_type_like_msg OWNER TO pneumo_user;

--
-- Name: auteur_type_msg; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.auteur_type_msg AS ENUM (
    'medecin',
    'aide_soignant'
);


ALTER TYPE public.auteur_type_msg OWNER TO pneumo_user;

--
-- Name: categorie_requete; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.categorie_requete AS ENUM (
    'bug_technique',
    'probleme_acces',
    'erreur_ia',
    'lenteur',
    'interface',
    'autre'
);


ALTER TYPE public.categorie_requete OWNER TO pneumo_user;

--
-- Name: etat_patient; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.etat_patient AS ENUM (
    'stable',
    'surveille',
    'urgent',
    'critique'
);


ALTER TYPE public.etat_patient OWNER TO pneumo_user;

--
-- Name: role_membre; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.role_membre AS ENUM (
    'createur',
    'admin',
    'membre'
);


ALTER TYPE public.role_membre OWNER TO pneumo_user;

--
-- Name: sexe_patient; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.sexe_patient AS ENUM (
    'M',
    'F',
    'autre'
);


ALTER TYPE public.sexe_patient OWNER TO pneumo_user;

--
-- Name: statut_acces; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_acces AS ENUM (
    'en_attente',
    'accorde',
    'refuse'
);


ALTER TYPE public.statut_acces OWNER TO pneumo_user;

--
-- Name: statut_clinique_enum; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_clinique_enum AS ENUM (
    'stable',
    'surveille',
    'urgent',
    'critique'
);


ALTER TYPE public.statut_clinique_enum OWNER TO pneumo_user;

--
-- Name: statut_consultation; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_consultation AS ENUM (
    'en_attente',
    'terminee'
);


ALTER TYPE public.statut_consultation OWNER TO pneumo_user;

--
-- Name: statut_medecin; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_medecin AS ENUM (
    'en_attente',
    'valide',
    'rejete',
    'suspendu',
    'corbeille'
);


ALTER TYPE public.statut_medecin OWNER TO pneumo_user;

--
-- Name: statut_membre; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_membre AS ENUM (
    'en_attente',
    'accepte',
    'refuse'
);


ALTER TYPE public.statut_membre OWNER TO pneumo_user;

--
-- Name: statut_question; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_question AS ENUM (
    'en_attente',
    'repondu'
);


ALTER TYPE public.statut_question OWNER TO pneumo_user;

--
-- Name: statut_question_admin; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_question_admin AS ENUM (
    'en_attente',
    'repondu',
    'publiee_faq'
);


ALTER TYPE public.statut_question_admin OWNER TO pneumo_user;

--
-- Name: statut_requete; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.statut_requete AS ENUM (
    'en_attente',
    'en_cours',
    'resolu',
    'ferme'
);


ALTER TYPE public.statut_requete OWNER TO pneumo_user;

--
-- Name: type_communaute; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.type_communaute AS ENUM (
    'publique',
    'privee'
);


ALTER TYPE public.type_communaute OWNER TO pneumo_user;

--
-- Name: type_destinataire; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.type_destinataire AS ENUM (
    'medecin',
    'admin',
    'aide_soignant'
);


ALTER TYPE public.type_destinataire OWNER TO pneumo_user;

--
-- Name: type_document; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.type_document AS ENUM (
    'diplome_specialisation',
    'diplome_medecine',
    'inscription_ordre',
    'autorisation_exercice',
    'carte_professionnelle',
    'cni'
);


ALTER TYPE public.type_document OWNER TO pneumo_user;

--
-- Name: type_message_equipe; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.type_message_equipe AS ENUM (
    'rapport',
    'alerte',
    'info'
);


ALTER TYPE public.type_message_equipe OWNER TO pneumo_user;

--
-- Name: type_publication; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.type_publication AS ENUM (
    'cas_clinique',
    'question',
    'article',
    'discussion'
);


ALTER TYPE public.type_publication OWNER TO pneumo_user;

--
-- Name: type_reaction; Type: TYPE; Schema: public; Owner: pneumo_user
--

CREATE TYPE public.type_reaction AS ENUM (
    'utile',
    'insightful',
    'accord',
    'desaccord'
);


ALTER TYPE public.type_reaction OWNER TO pneumo_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: acces_patient; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.acces_patient (
    id character varying(15) NOT NULL,
    patient_id character varying(15) NOT NULL,
    medecin_demandeur_id character varying(15) NOT NULL,
    medecin_proprietaire_id character varying(15) NOT NULL,
    statut public.statut_acces NOT NULL,
    justificatif_demande text,
    motif_refus text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.acces_patient OWNER TO pneumo_user;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.admins (
    id character varying(15) NOT NULL,
    nom character varying(100),
    email character varying(150) NOT NULL,
    password_hash character varying(255) NOT NULL,
    phone character varying(20),
    reset_otp character varying(6),
    otp_expiry timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.admins OWNER TO pneumo_user;

--
-- Name: aides_soignants; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.aides_soignants (
    id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password_hash character varying(255) NOT NULL,
    telephone character varying(20),
    statut character varying(20) NOT NULL,
    peut_creer_patient boolean NOT NULL,
    peut_lire_dossier boolean NOT NULL,
    peut_modifier_patient boolean NOT NULL,
    peut_saisir_symptomes boolean NOT NULL,
    peut_supprimer boolean NOT NULL,
    peut_voir_diagnostic boolean NOT NULL,
    peut_prescrire boolean NOT NULL,
    preferences jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.aides_soignants OWNER TO pneumo_user;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO pneumo_user;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.audit_logs (
    id character varying(15) NOT NULL,
    medecin_id character varying(15),
    action character varying(200) NOT NULL,
    details jsonb NOT NULL,
    ip_address inet,
    user_agent character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO pneumo_user;

--
-- Name: avis; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.avis (
    id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    prenom character varying(100) NOT NULL,
    nom character varying(100) NOT NULL,
    civilite character varying(20),
    specialite character varying(150),
    etablissement character varying(200),
    ville character varying(100),
    photo_url character varying(500),
    note integer NOT NULL,
    commentaire text NOT NULL,
    vu boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    statut character varying(20) DEFAULT 'publie'::character varying NOT NULL,
    archived_at timestamp without time zone
);


ALTER TABLE public.avis OWNER TO pneumo_user;

--
-- Name: avis_medecins; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.avis_medecins (
    id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    note integer NOT NULL,
    contenu text NOT NULL,
    vu boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.avis_medecins OWNER TO pneumo_user;

--
-- Name: avis_patient; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.avis_patient (
    id character varying(15) NOT NULL,
    patient_id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    contenu text NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.avis_patient OWNER TO pneumo_user;

--
-- Name: cas_cliniques_publics; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.cas_cliniques_publics (
    id character varying(15) NOT NULL,
    titre character varying(300) NOT NULL,
    pathologie character varying(200),
    description text,
    tags jsonb NOT NULL,
    pdf_url character varying(500),
    auteur_id character varying(15),
    anonymise boolean NOT NULL,
    nb_vues integer NOT NULL,
    nb_telechargements integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.cas_cliniques_publics OWNER TO pneumo_user;

--
-- Name: commentaires; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.commentaires (
    id character varying(15) NOT NULL,
    publication_id character varying(15) NOT NULL,
    auteur_id character varying(15) NOT NULL,
    contenu text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    parent_id character varying(15),
    auteur_aide_id character varying(15),
    auteur_type public.auteur_type_commentaire DEFAULT 'medecin'::public.auteur_type_commentaire NOT NULL,
    likes_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.commentaires OWNER TO pneumo_user;

--
-- Name: communautes; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.communautes (
    id character varying(15) NOT NULL,
    nom character varying(200) NOT NULL,
    description text,
    type public.type_communaute NOT NULL,
    specialite character varying(100),
    avatar_url character varying(500),
    createur_id character varying(15) NOT NULL,
    nb_membres integer NOT NULL,
    nb_cas integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.communautes OWNER TO pneumo_user;

--
-- Name: consultations; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.consultations (
    id character varying(15) NOT NULL,
    patient_id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    antecedents_consultation jsonb,
    symptomes jsonb NOT NULL,
    statut public.statut_consultation NOT NULL,
    avis_medecin text,
    observations text,
    prescriptions jsonb NOT NULL,
    recommandations text,
    prochain_rdv timestamp without time zone,
    partage jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    statut_clinique public.statut_clinique_enum
);


ALTER TABLE public.consultations OWNER TO pneumo_user;

--
-- Name: diagnostics_ia; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.diagnostics_ia (
    id character varying(15) NOT NULL,
    consultation_id character varying(15) NOT NULL,
    maladies jsonb NOT NULL,
    recommandations jsonb,
    etat_patient public.etat_patient,
    version_modele character varying(20),
    duree_inference_ms integer,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.diagnostics_ia OWNER TO pneumo_user;

--
-- Name: documents_medecin; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.documents_medecin (
    id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    type_document public.type_document NOT NULL,
    url_fichier character varying(500) NOT NULL,
    nom_fichier character varying(255),
    taille_octets integer,
    mime_type character varying(100),
    created_at timestamp without time zone NOT NULL,
    statut character varying(20) DEFAULT 'en_attente'::character varying NOT NULL,
    motif_rejet character varying(500)
);


ALTER TABLE public.documents_medecin OWNER TO pneumo_user;

--
-- Name: faq_publiees; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.faq_publiees (
    id character varying(15) NOT NULL,
    admin_id character varying(15),
    question text NOT NULL,
    reponse text NOT NULL,
    categorie character varying(50) NOT NULL,
    publie boolean NOT NULL,
    nb_vues integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.faq_publiees OWNER TO pneumo_user;

--
-- Name: feedbacks_ia; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.feedbacks_ia (
    id character varying(15) NOT NULL,
    diagnostic_id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    concordance boolean,
    diagnostic_final character varying(200),
    commentaire text,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.feedbacks_ia OWNER TO pneumo_user;

--
-- Name: likes_commentaires; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.likes_commentaires (
    id character varying(20) NOT NULL,
    commentaire_id character varying(15) NOT NULL,
    auteur_type public.auteur_type_like_com NOT NULL,
    auteur_id character varying(20) NOT NULL
);


ALTER TABLE public.likes_commentaires OWNER TO pneumo_user;

--
-- Name: likes_messages_equipe; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.likes_messages_equipe (
    id character varying(20) NOT NULL,
    message_id character varying(20) NOT NULL,
    auteur_type public.auteur_type_like_msg NOT NULL,
    auteur_id character varying(20) NOT NULL
);


ALTER TABLE public.likes_messages_equipe OWNER TO pneumo_user;

--
-- Name: medecins; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.medecins (
    id character varying(15) NOT NULL,
    civilite character varying(10),
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password_hash character varying(255) NOT NULL,
    specialite character varying(100),
    numero_rpps character varying(20),
    etablissement character varying(200),
    photo_url character varying(500),
    telephone character varying(30),
    adresse character varying(300),
    bio text,
    linkedin character varying(300),
    website character varying(300),
    statut public.statut_medecin NOT NULL,
    motif_rejet text,
    valide_par character varying(15),
    valide_le timestamp without time zone,
    activation_token character varying(255),
    activation_expires timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    preferences jsonb DEFAULT '{}'::jsonb,
    code_referent character varying(10),
    code_referent_actif boolean DEFAULT true NOT NULL,
    ville character varying(100),
    suspension_raison text,
    suspension_duree character varying(50),
    suspension_par character varying(15),
    suspension_le timestamp without time zone,
    statut_precedent character varying(20),
    supprime_le timestamp without time zone,
    supprime_par character varying(15),
    relance_sent boolean DEFAULT false NOT NULL,
    relance_at timestamp without time zone,
    updated_at timestamp without time zone,
    rejete_par character varying(15),
    derniere_connexion timestamp without time zone
);


ALTER TABLE public.medecins OWNER TO pneumo_user;

--
-- Name: membres_communaute; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.membres_communaute (
    id character varying(15) NOT NULL,
    communaute_id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    role public.role_membre NOT NULL,
    statut public.statut_membre NOT NULL,
    joined_at timestamp without time zone NOT NULL
);


ALTER TABLE public.membres_communaute OWNER TO pneumo_user;

--
-- Name: messages_equipe; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.messages_equipe (
    id character varying(20) NOT NULL,
    medecin_referent_id character varying(15) NOT NULL,
    auteur_type public.auteur_type_msg NOT NULL,
    auteur_medecin_id character varying(15),
    auteur_aide_id character varying(15),
    parent_id character varying(20),
    contenu text NOT NULL,
    type_msg public.type_message_equipe NOT NULL,
    pinned boolean NOT NULL,
    likes_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.messages_equipe OWNER TO pneumo_user;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.notifications (
    id character varying(15) NOT NULL,
    destinataire_id character varying(15) NOT NULL,
    type_dest public.type_destinataire NOT NULL,
    type_notif character varying(100) NOT NULL,
    titre character varying(300) NOT NULL,
    message text,
    meta jsonb NOT NULL,
    lu boolean NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.notifications OWNER TO pneumo_user;

--
-- Name: otp_codes; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.otp_codes (
    id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    code character varying(6) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    used boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    purpose character varying(20) DEFAULT 'login'::character varying NOT NULL,
    fail_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.otp_codes OWNER TO pneumo_user;

--
-- Name: parametres; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.parametres (
    id character varying(36) NOT NULL,
    cle character varying(100) NOT NULL,
    valeur jsonb NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.parametres OWNER TO pneumo_user;

--
-- Name: patients; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.patients (
    id character varying(15) NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    civilite character varying(10),
    date_naissance date,
    sexe public.sexe_patient,
    groupe_sanguin character varying(5),
    religion character varying(100),
    telephone character varying(20),
    email character varying(150),
    adresse character varying(300),
    profession character varying(150),
    personne_a_contacter character varying(150),
    telephone_urgence character varying(20),
    allergies jsonb NOT NULL,
    antecedents jsonb NOT NULL,
    created_by character varying(15),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    deleted_by character varying(15),
    aide_id character varying(15),
    created_by_aide character varying(15)
);


ALTER TABLE public.patients OWNER TO pneumo_user;

--
-- Name: publications; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.publications (
    id character varying(15) NOT NULL,
    communaute_id character varying(15),
    auteur_id character varying(15) NOT NULL,
    consultation_id character varying(15),
    titre character varying(300) NOT NULL,
    contenu text,
    type public.type_publication NOT NULL,
    tags jsonb NOT NULL,
    nb_commentaires integer NOT NULL,
    nb_reactions integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    ressource_id character varying(30)
);


ALTER TABLE public.publications OWNER TO pneumo_user;

--
-- Name: questions_admin; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.questions_admin (
    id character varying(20) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    titre character varying(200) NOT NULL,
    message text NOT NULL,
    statut public.statut_question_admin NOT NULL,
    reponse text,
    created_at timestamp without time zone NOT NULL,
    repondu_at timestamp without time zone
);


ALTER TABLE public.questions_admin OWNER TO pneumo_user;

--
-- Name: questions_medecins; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.questions_medecins (
    id character varying(15) NOT NULL,
    medecin_id character varying(15),
    question text NOT NULL,
    categorie character varying(50) NOT NULL,
    statut public.statut_question NOT NULL,
    reponse text,
    repondu_par character varying(15),
    repondu_le timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.questions_medecins OWNER TO pneumo_user;

--
-- Name: reactions; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.reactions (
    id character varying(15) NOT NULL,
    publication_id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    type public.type_reaction NOT NULL
);


ALTER TABLE public.reactions OWNER TO pneumo_user;

--
-- Name: requetes_medecins; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.requetes_medecins (
    id character varying(20) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    nom_medecin character varying(300),
    email_medecin character varying(300),
    titre character varying(300) NOT NULL,
    categorie public.categorie_requete NOT NULL,
    description text NOT NULL,
    statut public.statut_requete NOT NULL,
    action_admin character varying(300),
    reponse_admin text,
    repondu_par character varying(15),
    repondu_le timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    traite_le timestamp without time zone
);


ALTER TABLE public.requetes_medecins OWNER TO pneumo_user;

--
-- Name: ressources_medicales; Type: TABLE; Schema: public; Owner: pneumo_user
--

CREATE TABLE public.ressources_medicales (
    id character varying(15) NOT NULL,
    medecin_id character varying(15) NOT NULL,
    titre character varying(300) NOT NULL,
    resume text NOT NULL,
    contenu text,
    pdf_url character varying(500),
    pathologie character varying(100),
    tags json NOT NULL,
    niveau character varying(50),
    nb_telechargements integer NOT NULL,
    nb_vues integer NOT NULL,
    publie boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.ressources_medicales OWNER TO pneumo_user;

--
-- Data for Name: acces_patient; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.acces_patient (id, patient_id, medecin_demandeur_id, medecin_proprietaire_id, statut, justificatif_demande, motif_refus, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.admins (id, nom, email, password_hash, phone, reset_otp, otp_expiry, created_at, updated_at) FROM stdin;
OBG8EN6SN1OY	\N	adminpneumoia@gmail.com	$2b$12$HHxQOYiu5huRe8j/7prQ.Onm0w8Tqhn2R9kjjmQr9rTHhJ1NEWojq	+237656616801	\N	\N	2026-06-03 03:50:17.626079	2026-07-07 11:31:16.961306
\.


--
-- Data for Name: aides_soignants; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.aides_soignants (id, medecin_id, nom, prenom, email, password_hash, telephone, statut, peut_creer_patient, peut_lire_dossier, peut_modifier_patient, peut_saisir_symptomes, peut_supprimer, peut_voir_diagnostic, peut_prescrire, preferences, created_at) FROM stdin;
AIDE-7829840	PNEU-6888059	lili	yu	pougoumpaule@gmail.com	$2b$12$AeOPaGI966DFoQo6D.aEie.gfJ1qPPG4jO704oCCpTIkrAFOaB2WW	5670989877	actif	t	t	t	t	f	f	f	{}	2026-06-17 14:22:02.269171
AIDE-9233662	PNEU-6888059	olive	maya	mayadisney76@gmail.com	$2b$12$pVz1ScyV0hKVAInru67fDO8BFW7amiaL9dfDpMU.Mf/H4uMu0osze	656678984	actif	t	t	t	t	f	f	f	{}	2026-06-19 17:57:30.681046
AIDE-5375941	PNEU-6888059	RAFF	RAFF	mayadisney76+2@gmail.com	$2b$12$T7Xk23bnNAR6jKPwymju4O8PuqxbSSH862Q7m1xeZbgMcE4XXjPum	676234567	actif	t	t	t	t	f	f	f	{}	2026-06-25 18:01:19.096594
AIDE-5828352	PNEU-1772790	Soignante	Maya	mayadisneyolive21+@gmail.com	$2b$12$G/8gEVkR.5gJUdV2RAq.w.6qYSH0dNMYRtSYSWF0.KSBwj9DTUW.e	6 76 45 56 43	actif	t	t	t	t	f	f	f	{}	2026-07-02 08:25:36.277445
AIDE-2609616	PNEU-8414821	AIDE	TestModifié	aide.test@pneumoia.com	$2b$12$4eyYtcNCjiUVz2pN1rUxMugN2vUOg4t8t1ZKSCAu.dgsCmgpsUVdm	\N	actif	t	t	t	t	f	f	f	{"theme": "dark"}	2026-07-09 10:33:23.029699
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.alembic_version (version_num) FROM stdin;
8f7bfb7b3e5c
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.audit_logs (id, medecin_id, action, details, ip_address, user_agent, created_at) FROM stdin;
3XY8QC2MI6A3	PNEU-3918267	demande_validee	{"email": "mayadisneyolive21@gmail.com", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Disney Olive Maya"}	\N	\N	2026-06-15 20:25:31.510139
63IP0FNN4EE5	PNEU-3918267	medecin_suspendu	{"duree": "30 jours", "raison": "Autre", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Disney Olive Maya"}	\N	\N	2026-06-16 13:19:36.460524
J3099ZTXBN3F	PNEU-3918267	medecin_reactive	{"email": "mayadisneyolive21@gmail.com", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Disney Olive Maya"}	\N	\N	2026-06-16 17:38:08.968687
1NYFZL33Z64A	PNEU-3918267	demande_rejetee	{"motif": "N° CNOM invalide ou introuvable : Votre CNI arrive bientot a inspiration veillez , fournis un plus valide.", "admin_id": "system", "medecin_nom": "Disney Olive Maya"}	\N	\N	2026-06-16 18:17:50.343711
RHK6FEE387YN	PNEU-3918267	relance_envoyee	{"email": "mayadisneyolive21@gmail.com", "admin_id": "OBG8EN6SN1OY"}	\N	\N	2026-06-16 18:44:08.262609
TKEBS2QFA8CY	PNEU-3918267	relance_envoyee	{"email": "mayadisneyolive21@gmail.com", "admin_id": "OBG8EN6SN1OY"}	\N	\N	2026-06-16 18:44:08.41952
O849SBXBAHG0	PNEU-6888059	demande_validee	{"email": "mayadisney76@gmail.com", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "GRILL Sydney Maya"}	\N	\N	2026-06-16 20:37:48.114449
NY3IWEN4JOO2	\N	avis_supprime	{"avis_id": "EFUYUI80455B", "admin_id": "OBG8EN6SN1OY"}	\N	\N	2026-06-17 14:13:01.729854
KIPJNWA8HO32	\N	faq_repondu	{"admin_id": "OBG8EN6SN1OY", "question_id": "QST-1ZVQ6BVV0K"}	\N	\N	2026-06-17 16:20:17.81952
1D99LW3DKPJH	\N	faq_repondu	{"admin_id": "OBG8EN6SN1OY", "question_id": "QST-50AWM4WKNI"}	\N	\N	2026-06-18 17:05:30.643461
UXDPHQ8V1M4T	\N	avis_supprime	{"avis_id": "HUPLSJQF0RJD", "admin_id": "OBG8EN6SN1OY", "medecin_email": "mayadisney76@gmail.com"}	\N	\N	2026-06-18 17:50:06.216029
AGMMQXAEAWMS	\N	avis_supprime	{"avis_id": "ROJ02FPGG3RJ", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-18 18:01:48.472959
8ERBQCXWZQ73	\N	avis_supprime	{"avis_id": "QXU4CNVT6T0C", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-18 18:05:09.860347
3B5R9Q4AWYYC	PNEU-3318326	demande_validee	{"email": "pougoumpaule@gmail.com", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Paule Paule"}	\N	\N	2026-06-18 19:45:24.674981
UP5BS608OGT4	\N	faq_repondu	{"admin_id": "OBG8EN6SN1OY", "question_id": "QST-JWDUVWEIR2"}	\N	\N	2026-06-19 16:10:48.50288
DJVAO4SIP4AZ	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-19 16:43:15.107557
QZDAQ0I71RKU	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-19 16:43:15.296834
6MXGQQA54TBG	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-19 16:43:17.659877
ZZE1BBTZ70XW	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-19 16:43:17.750192
TGF9GBHQCN5B	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-19 17:23:49.791842
9D8J18E6EAKA	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-19 17:23:49.874908
DDOJ6JRX6QUN	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-06-19 17:47:16.220396
JTF4TUV804PJ	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-06-19 17:47:23.319963
1H7NJZ1LM53X	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:31:34.620538
SLM90E27VLM9	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:31:34.760964
NTUEU1XXCQC1	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:34:51.061345
KB2G21W0RU72	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:34:51.116717
OF0W1PSQRRAE	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "PUT", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:44:21.825642
LOG6P2XZMGBN	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "PUT", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:44:42.061747
PPTS131QH56K	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:45:16.038883
STQON4BT1EXY	\N	erreur_systeme	{"url": "/api/admin/parametres", "type": "ModuleNotFoundError", "method": "GET", "message": "No module named 'app.models.parametre'"}	\N	\N	2026-06-22 08:45:16.368197
FFEP5SPTDHIS	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 10:45:07.77098
3JGTN0EE00XN	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 10:45:08.852999
G517XVK5RXL5	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 10:46:19.817705
4S7W2R9NIUP3	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 10:46:20.28359
KE373EWPIVMY	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 16:15:32.236002
NCQ3AML4GNA9	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 16:15:32.419483
Y1TII5SUYJHJ	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 16:22:35.20845
DXLG5O0YFCEX	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 16:22:35.365974
GQFM4YVMJW4S	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:46:42.7522
W2NBSU9MZSUV	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:46:42.876504
9R6FXATKNZT4	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:12.352829
9P44Q5D50Q39	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:12.743408
TMOVA2Z0TARW	\N	demande_rejetee	{"motif": "Document expiré : kkkkkkk", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Pougoum Paule"}	\N	\N	2026-06-23 17:50:09.051574
XW6VIGIIMAY7	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:19.541636
WMZEBLRDWH1M	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:20.188021
DZIWMZGZY7OL	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:30.822717
4Z1BYL5GACUG	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:30.922427
4JVUA4T17HBT	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:40.390571
XC1G0AQNHGHS	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:40.476663
ZLEBJG5P4LRW	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:58.836685
0WVC15RLDO4X	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:50:59.497817
M54AV3XTCP75	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:52:11.842942
WC4DWA3HOB7D	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:52:12.293992
4VOO3QWQDFSL	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:52:38.334028
18QKP15MK3VI	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:52:38.538502
A16HNXMOWAX5	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:52:41.507912
GJ17GB1H8PGK	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:00:05.537991
ZB45LVAPTKLJ	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 17:52:41.620516
KTMYKUJXXBUJ	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:04:44.28472
WB26INMBN9I6	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:10:17.363149
S4W1Y0SN10I4	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:10:17.597537
MVVES909ODAG	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:00:05.236359
KNN426FD7A7E	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:04:43.985974
LYB1K3YWMMFC	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:13:26.678301
7TJ5V6P8O70V	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:13:26.688132
FA93P07GB7PR	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:16:24.298278
GTAEN6OJ7TJV	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column commentaires.parent_id does not exist\\n[SQL: SELECT commentaires.id AS commentaires_id, commentaires.publication_id AS commentaires_publication_id, commentaires.parent_id AS commentaires_parent_id, commentaires.auteur_type AS commentaires_auteur_type, commentaires.auteur_id AS commentaires_auteur_id, commentaires.auteur_aide_id AS commentaires_auteur_aide_id, commentaires.contenu AS"}	\N	\N	2026-06-23 18:16:24.542747
7C09MJ4M64KD	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:10:16.100244
RBBOADZH3VZW	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:10:16.36844
COL8YCLBEASI	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:11:59.20479
X4DHAJFQ5JCU	\N	demande_rejetee	{"motif": "Document expiré : jj", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Disneyolive  Maya"}	\N	\N	2026-06-23 18:13:23.003497
TWTH3SZSBI3B	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:11:59.312125
DOF1UNBCHUIC	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:18:24.441685
ZMQQELCQZPJV	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:18:24.792772
5RFRW6OZ6HZT	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:19:38.815332
X0T22KSYES1Q	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:19:39.540782
G10TS5NHURTY	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:22:37.422809
Q376G9RC2QRP	\N	erreur_systeme	{"url": "/api/admin/demandes/refusees", "type": "IntegrityError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: null value in column \\"medecin_id\\" of relation \\"consultations\\" violates not-null constraint\\nDETAIL:  Failing row contains (3LASDGV8CQZY, LYJES29AB9IF, null, {\\"vih\\": false, \\"bpco\\": false, \\"alcool\\": false, \\"asthme\\": false, ..., {\\"efr\\": false, \\"fvc\\": null, \\"fec1\\": null, \\"toux\\": true, \\"motif\\":..., terminee, Yeux pale , et peau de chvre , Yeux pale , et peau de chvre , {\\"suivi\\": \\"15 jours\\", \\"dur"}	\N	\N	2026-06-23 22:22:37.627989
TK20C5AVF4HD	\N	faq_repondu	{"admin_id": "OBG8EN6SN1OY", "question_id": "QST-O27JWEKI3I"}	\N	\N	2026-06-25 18:37:27.925531
Y1B7NMRCZOUP	\N	avis_supprime	{"avis_id": "F0L16N8TUJA9", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-25 18:53:19.451344
4HB559HG4JZS	\N	avis_supprime	{"avis_id": "QKW0D88K56EJ", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-25 18:55:37.781417
XPD594DL74D9	\N	avis_supprime	{"avis_id": "IG3GA7NO1PGK", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-25 18:55:37.781848
6DZSK1RWMT3Q	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e/20/f405)"}	\N	\N	2026-06-26 19:25:34.367609
AY5WUOAIZ4QR	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:26:34.267338
E0JKVRGOJJJX	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:27:35.765059
1AKGRI8OVYEG	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:28:36.147628
FL5ETZJ1GKLH	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:29:37.579313
GREL7KM73172	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:30:38.090815
FX67NKH7GXG8	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:31:39.378102
O0T3HYWYF93C	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:34:45.710531
KMH5PG3EA3HE	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:35:43.951057
OEPOVUWEAORG	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:36:45.098838
B7XJF7UQ3IJZ	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:37:46.400959
VQDE0L9A7PWT	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:38:47.00162
TZOIHKN32YK3	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:39:47.945072
X6UZ9YK8MAQ5	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:45:54.284142
MVBE6RT1QIZX	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:40:49.342324
CG24IJLZOMDW	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:41:50.105026
S3WDTBJ8XJM6	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:43:52.284157
5TQO7PSXB235	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:44:53.309967
19AP8YXVDPT5	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:46:55.278914
SDDY5V9CIRNX	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:42:51.030403
MNZTEM7KTET2	\N	erreur_systeme	{"url": "/api/admin/avis", "type": "ProgrammingError", "method": "GET", "message": "(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column avis.archived_at does not exist\\n[SQL: SELECT avis.id, avis.medecin_id, avis.prenom, avis.nom, avis.civilite, avis.specialite, avis.etablissement, avis.ville, avis.photo_url, avis.note, avis.commentaire, avis.statut, avis.vu, avis.created_at, avis.archived_at \\nFROM avis \\nWHERE avis.archived_at IS NULL ORDER BY avis.created_at DESC]\\n(Background on this error at: https://sqlalche.me/e"}	\N	\N	2026-06-26 19:47:56.334204
4TJ0WLBHUBRC	\N	avis_archive	{"avis_id": "7KU1V2XQDBHY", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-26 20:22:38.407451
R6TC3EM9CSTW	\N	avis_archive	{"avis_id": "CTXIFKOSXVX6", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-26 20:23:00.779777
AWSR028D6SYN	\N	avis_archive	{"avis_id": "PBY19A1WMVXN", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-06-26 20:23:03.948345
4DWAN9KHYQ9Q	\N	demande_rejetee	{"motif": "Document bientôt périmé : mll", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "TOmys Meli "}	\N	\N	2026-06-23 22:11:54.194276
AE6800RNLKAL	PNEU-3318326	medecin_corbeille	{"admin_id": "OBG8EN6SN1OY", "medecin_nom": "Paule Paule", "statut_precedent": "valide"}	\N	\N	2026-06-27 14:50:06.200646
ITG4YJYGBZ9M	PNEU-2997228	demande_rejetee	{"motif": "Documents flous / illisibles : k neden ;klllllllllllllllllllllllllllnndwnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnc", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Pirout DALRILL"}	\N	\N	2026-06-28 19:53:54.183005
WNWDEZFULIFC	PNEU-2997228	medecin_corbeille	{"admin_id": "OBG8EN6SN1OY", "medecin_nom": "Pirout DALRILL", "statut_precedent": "rejete"}	\N	\N	2026-06-28 20:10:14.1254
GYYPZWH2E2J3	\N	faq_repondu	{"admin_id": "OBG8EN6SN1OY", "question_id": "QST-VUNYQFZ1AO"}	\N	\N	2026-06-28 20:35:40.143909
T61OQIT1OFDX	\N	faq_repondu	{"admin_id": "OBG8EN6SN1OY", "question_id": "QST-1ZVMSLNR3F"}	\N	\N	2026-06-28 21:19:44.896339
EBAUJ7XQRUMX	PNEU-1772790	demande_validee	{"email": "mayadisney76+5@gmail.com", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "Brithnette DeLamoir"}	\N	\N	2026-07-01 22:39:51.266197
MFI663X3S55B	\N	faq_repondu	{"admin_id": "OBG8EN6SN1OY", "question_id": "QST-NYZOVCHNDY"}	\N	\N	2026-07-01 23:07:25.463607
G2JMH6ZWGVEH	\N	avis_archive	{"avis_id": "FA7L3XEZ01U0", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-1772790"}	\N	\N	2026-07-01 23:10:23.203865
G60TV6WXJG9W	\N	avis_archive	{"avis_id": "SD0Z02IGUN8A", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-1772790"}	\N	\N	2026-07-01 23:10:31.115801
R10ELEJMR7Z8	\N	avis_supprime	{"avis_id": "MDIOP8QKDEA7", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-1772790"}	\N	\N	2026-07-01 23:10:39.740529
VVKN3GS7ULCB	\N	avis_supprime	{"avis_id": "6BAHF7DIFMZX", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-07-01 23:10:45.517077
YJH61RRMOESK	\N	avis_supprime	{"avis_id": "T8278TM6Z5F2", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-6888059"}	\N	\N	2026-07-01 23:10:51.25336
O1HWOU787Z35	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-07-02 08:12:56.199331
HN3LX8DCHTQS	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-07-02 08:13:02.196536
X61FQ2YYVQ2A	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-07-02 08:13:08.99318
LNTTY9TJ3LSK	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-07-02 08:13:13.99858
GPHXXB6O6VTM	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-07-02 08:14:06.939617
Z22AWT9SGXA7	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_supprime_par_fkey\\"\\nDETAIL:  Key (supprime_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TI"}	\N	\N	2026-07-02 08:14:10.317757
VWRVU3X3KJBD	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-2605484) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:10:08.885104
VRV3KA8KRHWV	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-8415027) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:11:16.465279
2NC5YZQ4TI92	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-2553710) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:11:18.439657
VYYPHDAGQRVG	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-4225664) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:11:19.51343
5ZRPTRFA5OJZ	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-6198462) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:11:20.464574
7CD4WMH44SAJ	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-0223939) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:11:25.503858
RBBCUCI1KCPS	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-4311999) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:23:02.507226
VEGIH0RCLFDS	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-5282348) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:30:44.493184
H83MJMIMQF0T	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-4536385) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:37:35.212621
X5HO39GYJJJ8	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-8892535) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:38:14.419843
O1ZMN4MWP2F3	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-9399683) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:38:15.478336
20URH1CXLGDT	\N	erreur_systeme	{"url": "/api/v1/ressources/medecin/creer", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"publications\\" violates foreign key constraint \\"publications_ressource_id_fkey\\"\\nDETAIL:  Key (ressource_id)=(RES-5849183) is not present in table \\"ressources_medicales\\".\\n[SQL: INSERT INTO publications (id, communaute_id, auteur_id, consultation_id, ressource_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at) VALUES ($1::VARCHAR, $2::VARC"}	\N	\N	2026-07-02 11:38:15.827461
H5B04V47Y0KQ	\N	avis_archive	{"avis_id": "WDXA5UKRZYQI", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-1772790"}	\N	\N	2026-07-02 11:59:38.756739
UPYK1EV6DLC9	\N	avis_archive	{"avis_id": "XVRFOPL74IU0", "admin_id": "OBG8EN6SN1OY", "medecin_id": "PNEU-1772790"}	\N	\N	2026-07-02 11:59:47.868104
6YZWOKOXWISL	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOU"}	\N	\N	2026-07-02 13:03:33.944736
G077F4J7OKUX	\N	erreur_systeme	{"url": "/api/v1/auth/verify-otp", "type": "IntegrityError", "method": "POST", "message": "(raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)\\n(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOU"}	\N	\N	2026-07-02 13:04:50.665606
G9HPCX4CSTXT	\N	erreur_systeme	{"url": "/api/admin/medecins/PNEU-6888059/reactiver", "type": "NameError", "method": "POST", "message": "name 'Notification' is not defined"}	\N	\N	2026-07-03 06:41:53.80356
D4OS2EIH5K4E	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_par=$4::VARCHAR, suspension_le=$5::TIMESTAMP WITHOUT TIME ZONE WHERE medecins"}	\N	\N	2026-07-03 06:52:34.392111
6ETFFIQK6XFH	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_par=$4::VARCHAR, suspension_le=$5::TIMESTAMP WITHOUT TIME ZONE WHERE medecins"}	\N	\N	2026-07-03 06:52:41.634673
KWAEY1EHUQQY	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_par=$4::VARCHAR, suspension_le=$5::TIMESTAMP WITHOUT TIME ZONE WHERE medecins"}	\N	\N	2026-07-03 06:52:46.368029
AWWLQTSSUUK0	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_par=$4::VARCHAR, suspension_le=$5::TIMESTAMP WITHOUT TIME ZONE WHERE medecins"}	\N	\N	2026-07-03 06:53:57.640987
H6MPXYIXY2MC	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_par=$4::VARCHAR, suspension_le=$5::TIMESTAMP WITHOUT TIME ZONE WHERE medecins"}	\N	\N	2026-07-03 06:54:02.292442
WX3BL4DLT3O4	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_par=$4::VARCHAR, suspension_le=$5::TIMESTAMP WITHOUT TIME ZONE WHERE medecins"}	\N	\N	2026-07-03 06:54:28.737243
HLP2WKY5DLT9	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_duree=$4::VARCHAR, suspension_par=$5::VARCHAR, suspension_le=$6::TIMESTAMP WI"}	\N	\N	2026-07-03 07:03:11.054007
QR81C37BNQB0	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_duree=$4::VARCHAR, suspension_par=$5::VARCHAR, suspension_le=$6::TIMESTAMP WI"}	\N	\N	2026-07-03 07:10:26.485116
2IV2SWRLQ88C	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_duree=$4::VARCHAR, suspension_par=$5::VARCHAR, suspension_le=$6::TIMESTAMP WI"}	\N	\N	2026-07-03 07:17:37.755759
WQN9IEJO0EMC	\N	erreur_systeme	{"url": "/api/v1/auth/reset-verify-otp", "type": "IntegrityError", "method": "POST", "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: insert or update on table \\"medecins\\" violates foreign key constraint \\"medecins_suspension_par_fkey\\"\\nDETAIL:  Key (suspension_par)=(system) is not present in table \\"admins\\".\\n[SQL: UPDATE medecins SET statut=$1::statut_medecin, updated_at=$2::TIMESTAMP WITHOUT TIME ZONE, suspension_raison=$3::VARCHAR, suspension_duree=$4::VARCHAR, suspension_par=$5::VARCHAR, suspension_le=$6::TIMESTAMP WI"}	\N	\N	2026-07-03 07:23:23.949517
GB2NP08ILDG9	PNEU-6888059	compte_bloque_tentatives	{"type": "reset_password", "email": "mayadisney76@gmail.com", "raison": "3 tentatives OTP incorrectes lors de la réinitialisation", "tentatives": 3}	\N	\N	2026-07-03 07:34:00.816509
P4JDF4V3NOWZ	\N	erreur_systeme	{"url": "/api/admin/medecins/PNEU-6888059/reactiver", "type": "NameError", "method": "POST", "message": "name 'Notification' is not defined"}	\N	\N	2026-07-03 07:36:07.820771
WYAZC909NK2N	PNEU-6888059	compte_bloque_tentatives	{"type": "reset_password", "email": "mayadisney76@gmail.com", "raison": "3 tentatives OTP incorrectes lors de la réinitialisation", "tentatives": 3}	\N	\N	2026-07-04 12:59:56.798861
XI3PSUD8OG5G	PNEU-6888059	medecin_reactive	{"email": "mayadisney76@gmail.com", "admin_id": "OBG8EN6SN1OY", "medecin_nom": "GRILL Sydney Maya"}	\N	\N	2026-07-04 13:07:38.228086
\.


--
-- Data for Name: avis; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.avis (id, medecin_id, prenom, nom, civilite, specialite, etablissement, ville, photo_url, note, commentaire, vu, created_at, statut, archived_at) FROM stdin;
7KU1V2XQDBHY	PNEU-6888059	GRILL	Sydney Maya	Mme	Pneumologie	Hopital de reference 		\N	2	vkhxsvdjwvxj d	t	2026-06-26 19:19:15.212687	publie	2026-06-26 20:22:38.354711
CTXIFKOSXVX6	PNEU-6888059	GRILL	Sydney Maya	Mme	Pneumologie	Hopital de reference 		\N	2	vojcwknnd	t	2026-06-26 19:18:59.006058	publie	2026-06-26 20:23:00.770716
PBY19A1WMVXN	PNEU-6888059	GRILL	Sydney Maya	Mme	Pneumologie	Hopital de reference 		\N	1	nul nul	t	2026-06-26 19:18:38.772925	publie	2026-06-26 20:23:03.94388
FA7L3XEZ01U0	PNEU-1772790	Brithnette	DeLamoir	Dr	Pneumologie	Chu de Douala		http://localhost:8000/uploads/PNEU-1772790/photo_profil.jpg	4	i encoutered some bugs but everything is ok	t	2026-07-01 23:09:48.673397	publie	2026-07-01 23:10:23.197868
SD0Z02IGUN8A	PNEU-1772790	Brithnette	DeLamoir	Dr	Pneumologie	Chu de Douala		http://localhost:8000/uploads/PNEU-1772790/photo_profil.jpg	5	outstandings	t	2026-07-01 23:09:07.819284	publie	2026-07-01 23:10:31.110337
WDXA5UKRZYQI	PNEU-1772790	Brithnette	DeLamoir	Dr	Pneumologie	Chu de Douala		http://localhost:8000/uploads/PNEU-1772790/photo_profil.jpg	5	kkk	t	2026-07-02 11:39:32.575223	publie	2026-07-02 11:59:38.743479
XVRFOPL74IU0	PNEU-1772790	Brithnette	DeLamoir	Dr	Pneumologie	Chu de Douala		http://localhost:8000/uploads/PNEU-1772790/photo_profil.jpg	1	jjj	t	2026-07-02 11:39:07.040842	publie	2026-07-02 11:59:47.852496
\.


--
-- Data for Name: avis_medecins; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.avis_medecins (id, medecin_id, note, contenu, vu, created_at) FROM stdin;
\.


--
-- Data for Name: avis_patient; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.avis_patient (id, patient_id, medecin_id, contenu, created_at) FROM stdin;
\.


--
-- Data for Name: cas_cliniques_publics; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.cas_cliniques_publics (id, titre, pathologie, description, tags, pdf_url, auteur_id, anonymise, nb_vues, nb_telechargements, created_at) FROM stdin;
\.


--
-- Data for Name: commentaires; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.commentaires (id, publication_id, auteur_id, contenu, created_at, parent_id, auteur_aide_id, auteur_type, likes_count) FROM stdin;
QI4DTL1ITAUS	LE3ISCR74GNE	PNEU-1772790	kkk	2026-07-02 11:26:43.67409	\N	\N	medecin	0
9QPM8EDL0BSX	8C1409U6CU0L	PNEU-8414821	Très intéressant, merci !	2026-07-08 21:37:25.031402	\N	\N	medecin	0
7GP0BPOAYE74	JG62NWAVCFTU	PNEU-8414821	Très intéressant, merci !	2026-07-08 21:38:08.15585	\N	\N	medecin	0
00LMOYLXQ1AV	P724CQJ3YYX6	PNEU-8414821	Très intéressant, merci !	2026-07-08 21:43:55.375692	\N	\N	medecin	0
HYQ7BBZOLN06	UR9TQU74SFCA	PNEU-8414821	Très intéressant, merci !	2026-07-08 22:15:15.45901	\N	\N	medecin	0
B2AL37515BEN	KO28C36UAMJ7	PNEU-8414821	Très intéressant, merci !	2026-07-08 22:21:55.744674	\N	\N	medecin	0
1V5UW972GIQQ	5CMZY4HG8SHH	PNEU-8414821	Très intéressant, merci !	2026-07-08 22:23:30.719911	\N	\N	medecin	0
3DEAPFNW30U5	17RXW3HTO1O3	PNEU-8414821	Très intéressant, merci !	2026-07-09 10:33:26.247126	\N	\N	medecin	0
EMAJ4NAPHQOS	S05MT84X2SXV	PNEU-8414821	Très intéressant, merci !	2026-07-09 11:15:26.999231	\N	\N	medecin	0
VPM4X8SC2KYB	GQTA5SS55RJZ	PNEU-8414821	Très intéressant, merci !	2026-07-09 11:17:31.830666	\N	\N	medecin	0
\.


--
-- Data for Name: communautes; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.communautes (id, nom, description, type, specialite, avatar_url, createur_id, nb_membres, nb_cas, created_at) FROM stdin;
\.


--
-- Data for Name: consultations; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.consultations (id, patient_id, medecin_id, antecedents_consultation, symptomes, statut, avis_medecin, observations, prescriptions, recommandations, prochain_rdv, partage, created_at, updated_at, statut_clinique) FROM stdin;
9LB5G1S9VTW0	SORB1HEPGCNB	PNEU-6888059	{"vih": false, "bpco": true, "alcool": false, "asthme": true, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": true, "hypertension": true, "cancer_poumon": true, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun", "allergie_medicaments": "Aspirine , anti-douleur", "exposition_professionnelle": ""}	{"efr": false, "fvc": 1.3, "fec1": 1.2, "toux": false, "motif": "Fatigue generale , vomissement de sang , vertige , soif intense , polyphagie , nausee , douleur thoracique ", "fievre": false, "dyspnee": true, "fatigue": false, "scanner": false, "wheezing": false, "evolution": "aggravation", "peak_flow": 1.6, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": true, "perte_poids": true, "temperature": null, "douleur_type": "angineux", "fievre_duree": "", "maux_de_tete": true, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": 23.5, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": "2026-03-04", "sueurs_nocturnes": true, "douleur_thoracique": true, "fievre_temperature": null, "tension_systolique": 90.0, "frequence_cardiaque": 40.0, "tension_diastolique": 60.0, "traitement_deja_pris": "aucun", "frequence_respiratoire": null}	terminee	Couleur de yeux jaune moutarde , chaleur et douleur au touche du thorax 	Couleur de yeux jaune moutarde , chaleur et douleur au touche du thorax 	{"suivi": "7 jours", "duree_arret": 7, "medicaments": "aucun", "arret_travail": true, "conseils_maison": "repos , hydratation", "hospitalisation": false, "recommandations": "Vérifier la composition des médicaments (certificat halal si disponible)\\nAdapter les horaires de prise médicamenteuse pendant le Ramadan\\nConsulter un imam si nécessaire pour les cas d'urgence médicale\\nBronchodilatateurs courte durée (Salbutamol)\\nCorticostéroïdes inhalés\\nPlan d'action écrit\\nÉviction des allergènes\\nContrôle du débit de pointe", "motif_hospitalisation": null}	Vérifier la composition des médicaments (certificat halal si disponible)\nAdapter les horaires de prise médicamenteuse pendant le Ramadan\nConsulter un imam si nécessaire pour les cas d'urgence médicale\nBronchodilatateurs courte durée (Salbutamol)\nCorticostéroïdes inhalés\nPlan d'action écrit\nÉviction des allergènes\nContrôle du débit de pointe	\N	{"type": null, "actif": false, "anonymiser": true, "destinataire_id": null, "envoyer_mail_patient": false}	2026-06-16 20:47:37.146385	2026-06-16 21:02:47.996277	stable
3LASDGV8CQZY	LYJES29AB9IF	PNEU-3918267	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": true, "hepatite_c": true, "tuberculose": false, "hypertension": true, "cancer_poumon": true, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "", "allergie_medicaments": "", "exposition_professionnelle": ""}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": "Diarhee , insomnie, cephalee , douleur toracique , douleur articulaire douleur lombaire , vomissement de sang , hypertension", "fievre": false, "dyspnee": false, "fatigue": true, "scanner": false, "wheezing": false, "evolution": "aggravation", "peak_flow": null, "sibilants": true, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": true, "perte_poids": true, "temperature": 8.0, "douleur_type": "angineux", "fievre_duree": "", "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": -2.0, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": "2026-04-04", "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": 15.0, "frequence_cardiaque": 4.0, "tension_diastolique": 6.0, "traitement_deja_pris": "aucun ", "frequence_respiratoire": 30.0}	terminee	Yeux pale , et peau de chvre 	Yeux pale , et peau de chvre 	{"suivi": "15 jours", "duree_arret": 28, "medicaments": "Aucun pour l'instant", "arret_travail": true, "conseils_maison": "Repos , hydratation", "hospitalisation": false, "recommandations": "radio\\n", "motif_hospitalisation": null}	radio\n	\N	{"type": null, "actif": false, "anonymiser": true, "destinataire_id": null, "envoyer_mail_patient": false}	2026-06-16 05:05:10.662544	2026-06-16 10:45:34.319249	\N
0U3FLCO4QI11	97Z8C325B8LH	PNEU-6888059	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": true, "hypertension": true, "cancer_poumon": false, "duree_tabagisme": 7, "profession_risque": false, "cigarettes_par_jour": 7, "traitement_en_cours": "aucun ", "allergie_medicaments": "Aucun", "exposition_professionnelle": ""}	{"efr": false, "fvc": 17.0, "fec1": 34.6, "toux": false, "motif": "Douleurs thoracique , douleurs a la miction , toux chronique , demangeaison cutanee, Cephalee violent , perte de connaissance ,", "fievre": false, "dyspnee": true, "fatigue": true, "scanner": false, "wheezing": false, "evolution": "aggravation", "peak_flow": 345.0, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 45.0, "douleur_type": "angineux", "fievre_duree": "", "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": true, "dyspnee_stade": 1, "saturation_o2": 21.0, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": true, "debut_symptomes": "2026-02-16", "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": 28.0, "frequence_cardiaque": 12.0, "tension_diastolique": 20.0, "traitement_deja_pris": "aucun", "frequence_respiratoire": 22.0}	en_attente			{"suivi": "7 jours", "duree_arret": null, "medicaments": "", "arret_travail": false, "conseils_maison": "", "hospitalisation": false, "recommandations": "", "motif_hospitalisation": null}		\N	{"type": null, "actif": false, "anonymiser": true, "destinataire_id": null, "envoyer_mail_patient": false}	2026-06-17 14:32:53.477157	2026-06-17 14:42:51.806902	stable
8FMABMRKN6NS	CT7V6LZQO2SV	PNEU-6888059	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun", "allergie_medicaments": "", "exposition_professionnelle": ""}	{"efr": false, "fvc": 97.0, "fec1": 75.0, "toux": false, "motif": "Douleurs osseuses profondes , perte de taille , deformation du squelle ,  infection osseuses, ", "fievre": false, "dyspnee": true, "fatigue": false, "scanner": false, "wheezing": false, "evolution": "", "peak_flow": 350.0, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": true, "perte_poids": true, "temperature": 28.0, "douleur_type": "angineux", "fievre_duree": "", "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": true, "dyspnee_stade": 1, "saturation_o2": 20.0, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": "", "sueurs_nocturnes": true, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": 96.0, "frequence_cardiaque": 100.0, "tension_diastolique": 45.0, "traitement_deja_pris": "", "frequence_respiratoire": 43.0}	en_attente	\N	\N	{}	\N	\N	{}	2026-06-18 16:41:03.885714	2026-06-18 16:41:03.997597	\N
ECZND2MCHYW0	MQO58PFGVZLC	PNEU-6888059	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun", "allergie_medicaments": "", "exposition_professionnelle": ""}	{"efr": false, "fvc": 97.0, "fec1": 75.0, "toux": false, "motif": "Douleurs osseuses profondes , perte de taille , deformation du squelle ,  infection osseuses, ", "fievre": false, "dyspnee": true, "fatigue": false, "scanner": false, "wheezing": false, "evolution": "", "peak_flow": 350.0, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": true, "perte_poids": true, "temperature": 28.0, "douleur_type": "angineux", "fievre_duree": "", "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": true, "dyspnee_stade": 1, "saturation_o2": 20.0, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": "", "sueurs_nocturnes": true, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": 96.0, "frequence_cardiaque": 100.0, "tension_diastolique": 45.0, "traitement_deja_pris": "", "frequence_respiratoire": 43.0}	en_attente	\N	\N	{}	\N	\N	{}	2026-06-18 16:41:03.882389	2026-06-18 16:41:04.012883	\N
85IKTY7A8E5Q	CDM985JJ78RJ	PNEU-6888059	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": true, "diabete": false, "typhoide": true, "paludisme": true, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "", "allergie_medicaments": "", "exposition_professionnelle": ""}	{"efr": false, "fvc": 5.0, "fec1": 4.0, "toux": true, "motif": "retuo oouuyutnklklli", "fievre": true, "dyspnee": false, "fatigue": true, "scanner": false, "wheezing": false, "evolution": "aggravation", "peak_flow": 650.0, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": true, "temperature": 42.0, "douleur_type": "angineux", "fievre_duree": "3", "maux_de_tete": true, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": 95.0, "abg_ph_anormal": true, "dyspnee_effort": false, "abg_co2_anormal": true, "debut_symptomes": "2026-06-16", "sueurs_nocturnes": true, "douleur_thoracique": false, "fievre_temperature": 42.0, "tension_systolique": 7.35, "frequence_cardiaque": 5.0, "tension_diastolique": 7.35, "traitement_deja_pris": "", "frequence_respiratoire": 650.0}	terminee	yeux jonatre 	yeux jonatre 	{"suivi": "7 jours", "duree_arret": 7, "medicaments": "", "arret_travail": true, "conseils_maison": "repos", "hospitalisation": true, "recommandations": "Traitement symptomatique\\nMucolytiques et fluidifiants\\nAntibiothérapie si purulent > 7 jours\\nHydratation\\nArrêt du tabac", "motif_hospitalisation": null}	Traitement symptomatique\nMucolytiques et fluidifiants\nAntibiothérapie si purulent > 7 jours\nHydratation\nArrêt du tabac	\N	{"type": null, "actif": false, "anonymiser": true, "destinataire_id": null, "envoyer_mail_patient": false}	2026-06-18 16:44:51.769349	2026-06-18 16:51:15.151374	surveille
MFFAIT4M5NG0	VUDFTD98XREM	PNEU-6888059	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun ", "allergie_medicaments": "aucun ", "exposition_professionnelle": ""}	{"efr": false, "fvc": 3.34, "fec1": 2.5, "toux": false, "motif": "ouiytt", "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": "aggravation", "peak_flow": 650.0, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 40.0, "douleur_type": "angineux", "fievre_duree": "4", "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": 56.0, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": true, "debut_symptomes": "2026-06-16", "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": 40.0, "tension_systolique": 46.0, "frequence_cardiaque": 765.0, "tension_diastolique": 65.0, "traitement_deja_pris": "", "frequence_respiratoire": 456.0}	en_attente	\N	\N	{"suivi": "7 jours", "duree_arret": null, "medicaments": null, "arret_travail": false, "conseils_maison": null, "hospitalisation": false, "recommandations": null, "motif_hospitalisation": null}	\N	\N	{"type": null, "actif": false, "anonymiser": true, "destinataire_id": null, "envoyer_mail_patient": false}	2026-06-18 18:12:39.312401	2026-06-18 18:28:44.692322	stable
V14MF8MZ4ORN	Q7D9ARPMBNWG	PNEU-6888059	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": true, "cigarettes_par_jour": 0, "traitement_en_cours": "Aucun", "allergie_medicaments": "arachide , peniceline", "exposition_professionnelle": ""}	{"efr": false, "fvc": 35.0, "fec1": 100.0, "toux": true, "motif": "Maux de tete , toux accrue , douleur thoracique", "fievre": true, "dyspnee": true, "fatigue": true, "scanner": false, "wheezing": true, "evolution": "aggravation", "peak_flow": 600.0, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": true, "temperature": 45.0, "douleur_type": "angineux", "fievre_duree": "6", "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": true, "dyspnee_stade": 1, "saturation_o2": 78.0, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": true, "debut_symptomes": "2026-03-12", "sueurs_nocturnes": true, "douleur_thoracique": true, "fievre_temperature": 45.0, "tension_systolique": 9000.0, "frequence_cardiaque": 190.0, "tension_diastolique": 29.0, "traitement_deja_pris": "Aucun", "frequence_respiratoire": 400.0}	en_attente	\N	\N	{"suivi": "7 jours", "duree_arret": null, "medicaments": null, "arret_travail": false, "conseils_maison": null, "hospitalisation": false, "recommandations": null, "motif_hospitalisation": null}	\N	\N	{"type": null, "actif": false, "anonymiser": true, "destinataire_id": null, "envoyer_mail_patient": false}	2026-06-25 18:13:21.140598	2026-06-25 18:29:45.268423	critique
TRHIB029EFD2	DGCOG3YQNGWM	PNEU-1772790	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": true, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "Aucun", "allergie_medicaments": "Aucun", "exposition_professionnelle": ""}	{"efr": false, "fvc": 4.0, "fec1": 3.2, "toux": false, "motif": "douleur thoracique , toux grasse avec sang ", "fievre": false, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": "aggravation", "peak_flow": 450.0, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 37.0, "douleur_type": "angineux", "fievre_duree": "", "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": "", "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": 98.0, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": "2026-06-17", "sueurs_nocturnes": false, "douleur_thoracique": true, "fievre_temperature": null, "tension_systolique": 120.0, "frequence_cardiaque": 72.0, "tension_diastolique": 80.0, "traitement_deja_pris": "", "frequence_respiratoire": 16.0}	terminee	Yeux jonatre , peau matte	Yeux jonatre , peau matte	{"suivi": "7 jours", "duree_arret": 7, "medicaments": "Aucun pour l'instant", "arret_travail": true, "conseils_maison": "Hydratation", "hospitalisation": false, "recommandations": "Examen de radio thoracique", "motif_hospitalisation": null}	Examen de radio thoracique	\N	{"type": null, "actif": false, "anonymiser": true, "destinataire_id": null, "envoyer_mail_patient": false}	2026-07-02 08:36:21.843592	2026-07-02 09:32:42.032188	surveille
BTZXO5S3XTG1	3WDN51B9ID8L	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 21:31:23.310222	2026-07-08 21:31:23.545761	surveille
OMKBRXULQ6C4	H2XSG6PROW2B	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 14:19:44.356229	2026-07-08 14:19:44.584912	surveille
1AQT1UNKEZT4	6SG43ENX8UFN	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 21:37:23.588109	2026-07-08 21:37:23.861519	surveille
KH3DOGRMCKTH	DJ29ZR3V6O0Y	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 21:38:06.598771	2026-07-08 21:38:06.985209	surveille
SSF61DW01X6Q	7CEO9TIE3HWK	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 21:43:53.596511	2026-07-08 21:43:53.932028	surveille
QYZ9VSSQTRTZ	489MI5ZW3VIW	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 22:15:13.811731	2026-07-08 22:15:14.207767	surveille
QW1O0I8X9Y8H	6NR18SGF5RDV	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 22:21:53.974539	2026-07-08 22:21:54.200866	surveille
DUKSRAS4OV0D	AI15S1DRRWDF	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-09 10:33:24.883081	2026-07-09 10:33:25.064448	surveille
G8Q8PCEXRLR3	5MAKB9OPJ5B3	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-08 22:23:28.707596	2026-07-08 22:23:28.941798	surveille
DEOZORJFCYUQ	2OKLME8F1Z2T	PNEU-8414821	{"diabete": false, "hypertension": true}	{"toux": true, "temperature": 37.5}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-09 10:33:23.311443	2026-07-09 10:33:23.402998	\N
F5K4D9JO43WL	HKXMFGMWS2AK	PNEU-8414821	{"diabete": false, "hypertension": true}	{"toux": true, "temperature": 37.5}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-09 11:14:59.34896	2026-07-09 11:14:59.403975	\N
3O3R3DFNU54H	BCT82NL034GE	PNEU-8414821	{"diabete": false, "hypertension": true}	{"toux": true, "temperature": 37.5}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-09 11:15:25.080826	2026-07-09 11:15:25.124181	\N
HAVVPJ8CZ7J7	BD4PYCC2705B	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-09 11:15:25.934912	2026-07-09 11:15:26.066041	surveille
QPFB1B8V8D6R	F7D66KKRU26D	PNEU-8414821	{"diabete": false, "hypertension": true}	{"toux": true, "temperature": 37.5}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-09 11:17:29.245464	2026-07-09 11:17:29.311828	\N
2XZ3QMHAYFAS	OH83J7BC5FNG	PNEU-8414821	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	{"efr": false, "fvc": null, "fec1": null, "toux": true, "motif": null, "fievre": true, "dyspnee": false, "fatigue": false, "scanner": false, "wheezing": false, "evolution": null, "peak_flow": null, "sibilants": false, "toux_sang": false, "toux_type": "seche", "crepitants": false, "hemoptysie": false, "rhinorrhee": false, "courbatures": false, "perte_poids": false, "temperature": 38.5, "douleur_type": null, "fievre_duree": null, "maux_de_tete": false, "pefr_anormal": false, "recherche_bk": false, "toux_couleur": null, "dyspnee_repos": false, "dyspnee_stade": 1, "saturation_o2": null, "abg_ph_anormal": false, "dyspnee_effort": false, "abg_co2_anormal": false, "debut_symptomes": null, "sueurs_nocturnes": false, "douleur_thoracique": false, "fievre_temperature": null, "tension_systolique": null, "frequence_cardiaque": null, "tension_diastolique": null, "traitement_deja_pris": null, "frequence_respiratoire": null}	en_attente	\N	\N	{}	\N	\N	{}	2026-07-09 11:17:30.273837	2026-07-09 11:17:30.487594	surveille
\.


--
-- Data for Name: diagnostics_ia; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.diagnostics_ia (id, consultation_id, maladies, recommandations, etat_patient, version_modele, duree_inference_ms, created_at) FROM stdin;
JS3U7XGCUVX1	9LB5G1S9VTW0	[{"nom": "Asthma", "pct": 28.0, "etat": "stable", "recommandations": ["Bronchodilatateurs courte durée (Salbutamol)", "Corticostéroïdes inhalés", "Plan d'action écrit", "Éviction des allergènes", "Contrôle du débit de pointe"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Antécédent d'asthme documenté", "Capacité vitale forcée réduite — FVC = 1.3 L", "Débit de pointe bas — Peak Flow = 1.6 L/min", "Hypoxémie gazeuse — ABG PO₂ anormal", "Dyspnée stade 1/4", "Douleur thoracique présente", "Sueurs nocturnes", "Perte de poids involontaire", "SpO₂ mesurée à 23.5 %"], "examens_suggeres": ["EFR (spirométrie)", "Test de réversibilité", "Tests allergologiques", "Peak-flow"]}, {"nom": "Allergic Rhinitis", "pct": 15.7, "etat": "stable", "recommandations": ["Antihistaminiques 2ème génération", "Corticostéroïdes nasaux", "Éviction des allergènes", "Tests allergologiques", "Désensibilisation possible"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Antécédent d'asthme documenté", "Capacité vitale forcée réduite — FVC = 1.3 L", "Débit de pointe bas — Peak Flow = 1.6 L/min", "Hypoxémie gazeuse — ABG PO₂ anormal", "Dyspnée stade 1/4", "Douleur thoracique présente", "Sueurs nocturnes", "Perte de poids involontaire", "SpO₂ mesurée à 23.5 %"], "examens_suggeres": ["Tests cutanés allergologiques", "IgE spécifiques", "NFS (éosinophiles)"]}, {"nom": "Pneumonia", "pct": 12.7, "etat": "stable", "recommandations": ["Antibiothérapie adaptée (Amoxicilline 1g x 3/j - 7 jours)", "Surveillance saturation O2", "Hydratation abondante (>1.5L/jour)", "Kinésithérapie respiratoire", "Repos strict", "Réévaluation à 48-72h", "Hospitalisation si SpO2 < 92%"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Antécédent d'asthme documenté", "Capacité vitale forcée réduite — FVC = 1.3 L", "Débit de pointe bas — Peak Flow = 1.6 L/min", "Hypoxémie gazeuse — ABG PO₂ anormal", "Dyspnée stade 1/4", "Douleur thoracique présente", "Sueurs nocturnes", "Perte de poids involontaire", "SpO₂ mesurée à 23.5 %"], "examens_suggeres": ["Radiographie thoracique", "NFS-CRP", "Hémocultures", "ECBC", "Gaz du sang si SpO2 < 94%"]}]	["Vérifier la composition des médicaments (certificat halal si disponible)", "Adapter les horaires de prise médicamenteuse pendant le Ramadan", "Consulter un imam si nécessaire pour les cas d'urgence médicale", "Bronchodilatateurs courte durée (Salbutamol)", "Corticostéroïdes inhalés", "Plan d'action écrit", "Éviction des allergènes", "Contrôle du débit de pointe"]	stable	equipe	0	2026-06-16 20:58:53.686413
PTMTDWQGYEXA	0U3FLCO4QI11	[{"nom": "Allergic Rhinitis", "pct": 29.0, "etat": "stable", "recommandations": ["Antihistaminiques 2ème génération", "Corticostéroïdes nasaux", "Éviction des allergènes", "Tests allergologiques", "Désensibilisation possible"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Tabagisme actif confirmé", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Dyspnée stade 1/4", "SpO₂ mesurée à 21.0 %", "Hyperthermie — T° = 45.0 °C"], "examens_suggeres": ["Tests cutanés allergologiques", "IgE spécifiques", "NFS (éosinophiles)"]}, {"nom": "COPD", "pct": 20.7, "etat": "stable", "recommandations": ["Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Tabagisme actif confirmé", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Dyspnée stade 1/4", "SpO₂ mesurée à 21.0 %", "Hyperthermie — T° = 45.0 °C"], "examens_suggeres": ["Spirométrie post-bronchodilatateur", "TDM thoracique", "Gaz du sang", "ECG"]}, {"nom": "COVID-19", "pct": 15.0, "etat": "stable", "recommandations": ["Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Tabagisme actif confirmé", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Dyspnée stade 1/4", "SpO₂ mesurée à 21.0 %", "Hyperthermie — T° = 45.0 °C"], "examens_suggeres": ["PCR SARS-CoV-2", "Scanner thoracique", "NFS-CRP-D-Dimères", "Gaz du sang"]}]	["Antihistaminiques 2ème génération", "Corticostéroïdes nasaux", "Éviction des allergènes", "Tests allergologiques", "Désensibilisation possible"]	stable	equipe	0	2026-06-17 14:42:51.614915
F25DMEACB57Z	85IKTY7A8E5Q	[{"nom": "COVID-19", "pct": 39.0, "etat": "surveille", "recommandations": ["Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"], "criteres_valides": ["Hypercapnie — ABG PCO₂ anormal", "Trouble de l'équilibre acido-basique", "Fièvre documentée — 42.0 °C", "Toux sèche confirmée", "Sueurs nocturnes", "Perte de poids involontaire", "Hyperthermie — T° = 42.0 °C"], "examens_suggeres": ["PCR SARS-CoV-2", "Scanner thoracique", "NFS-CRP-D-Dimères", "Gaz du sang"]}, {"nom": "Bronchitis", "pct": 27.3, "etat": "stable", "recommandations": ["Traitement symptomatique", "Mucolytiques et fluidifiants", "Antibiothérapie si purulent > 7 jours", "Hydratation", "Arrêt du tabac"], "criteres_valides": ["Hypercapnie — ABG PCO₂ anormal", "Trouble de l'équilibre acido-basique", "Fièvre documentée — 42.0 °C", "Toux sèche confirmée", "Sueurs nocturnes", "Perte de poids involontaire", "Hyperthermie — T° = 42.0 °C"], "examens_suggeres": ["Radiographie thoracique", "NFS-CRP", "ECBC si purulent"]}, {"nom": "COPD", "pct": 10.0, "etat": "stable", "recommandations": ["Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"], "criteres_valides": ["Hypercapnie — ABG PCO₂ anormal", "Trouble de l'équilibre acido-basique", "Fièvre documentée — 42.0 °C", "Toux sèche confirmée", "Sueurs nocturnes", "Perte de poids involontaire", "Hyperthermie — T° = 42.0 °C"], "examens_suggeres": ["Spirométrie post-bronchodilatateur", "TDM thoracique", "Gaz du sang", "ECG"]}]	["Vérifier la composition des médicaments (certificat halal si disponible)", "Adapter les horaires de prise médicamenteuse pendant le Ramadan", "Consulter un imam si nécessaire pour les cas d'urgence médicale", "Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"]	surveille	equipe	0	2026-06-18 16:48:30.502434
1MJDHPHVW8GN	MFFAIT4M5NG0	[{"nom": "COPD", "pct": 27.3, "etat": "stable", "recommandations": ["Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Fièvre documentée — 40.0 °C", "SpO₂ mesurée à 56.0 %", "Hyperthermie — T° = 40.0 °C"], "examens_suggeres": ["Spirométrie post-bronchodilatateur", "TDM thoracique", "Gaz du sang", "ECG"]}, {"nom": "Allergic Rhinitis", "pct": 23.3, "etat": "stable", "recommandations": ["Antihistaminiques 2ème génération", "Corticostéroïdes nasaux", "Éviction des allergènes", "Tests allergologiques", "Désensibilisation possible"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Fièvre documentée — 40.0 °C", "SpO₂ mesurée à 56.0 %", "Hyperthermie — T° = 40.0 °C"], "examens_suggeres": ["Tests cutanés allergologiques", "IgE spécifiques", "NFS (éosinophiles)"]}, {"nom": "COVID-19", "pct": 18.3, "etat": "stable", "recommandations": ["Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Fièvre documentée — 40.0 °C", "SpO₂ mesurée à 56.0 %", "Hyperthermie — T° = 40.0 °C"], "examens_suggeres": ["PCR SARS-CoV-2", "Scanner thoracique", "NFS-CRP-D-Dimères", "Gaz du sang"]}]	["Privilégier les alternatives non sanguines (érythropoïétine, fer IV)", "Techniques chirurgicales d'épargne sanguine si intervention prévue", "Informer toute l'équipe soignante de cette restriction", "Documenter le refus signé dans le dossier médical", "Consulter le comité d'éthique si situation d'urgence vitale", "Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"]	stable	equipe	0	2026-06-18 18:22:51.84088
Q04FPPCF3TG4	V14MF8MZ4ORN	[{"nom": "COPD", "pct": 22.7, "etat": "stable", "recommandations": ["Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Fièvre documentée — 45.0 °C", "Toux sèche confirmée", "Dyspnée stade 1/4", "Douleur thoracique présente", "Wheezing ausculté", "Sueurs nocturnes", "Perte de poids involontaire", "SpO₂ mesurée à 78.0 %", "Hyperthermie — T° = 45.0 °C"], "examens_suggeres": ["Spirométrie post-bronchodilatateur", "TDM thoracique", "Gaz du sang", "ECG"]}, {"nom": "Allergic Rhinitis", "pct": 20.0, "etat": "stable", "recommandations": ["Antihistaminiques 2ème génération", "Corticostéroïdes nasaux", "Éviction des allergènes", "Tests allergologiques", "Désensibilisation possible"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Fièvre documentée — 45.0 °C", "Toux sèche confirmée", "Dyspnée stade 1/4", "Douleur thoracique présente", "Wheezing ausculté", "Sueurs nocturnes", "Perte de poids involontaire", "SpO₂ mesurée à 78.0 %", "Hyperthermie — T° = 45.0 °C"], "examens_suggeres": ["Tests cutanés allergologiques", "IgE spécifiques", "NFS (éosinophiles)"]}, {"nom": "COVID-19", "pct": 17.7, "etat": "stable", "recommandations": ["Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"], "criteres_valides": ["Hypoxémie confirmée (SpO₂ < 94%)", "Hypoxémie gazeuse — ABG PO₂ anormal", "Hypercapnie — ABG PCO₂ anormal", "Fièvre documentée — 45.0 °C", "Toux sèche confirmée", "Dyspnée stade 1/4", "Douleur thoracique présente", "Wheezing ausculté", "Sueurs nocturnes", "Perte de poids involontaire", "SpO₂ mesurée à 78.0 %", "Hyperthermie — T° = 45.0 °C"], "examens_suggeres": ["PCR SARS-CoV-2", "Scanner thoracique", "NFS-CRP-D-Dimères", "Gaz du sang"]}]	["Privilégier les alternatives non sanguines (érythropoïétine, fer IV)", "Techniques chirurgicales d'épargne sanguine si intervention prévue", "Informer toute l'équipe soignante de cette restriction", "Documenter le refus signé dans le dossier médical", "Consulter le comité d'éthique si situation d'urgence vitale", "Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"]	critique	equipe	0	2026-06-25 18:25:36.34471
1ZBH286RBFLT	TRHIB029EFD2	[{"nom": "COVID-19", "pct": 32.7, "etat": "surveille", "recommandations": ["Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"], "criteres_valides": ["Douleur thoracique présente"], "examens_suggeres": ["PCR SARS-CoV-2", "Scanner thoracique", "NFS-CRP-D-Dimères", "Gaz du sang"]}, {"nom": "Tuberculosis", "pct": 24.7, "etat": "stable", "recommandations": ["Déclaration obligatoire aux autorités sanitaires", "Traitement DOTS : Rifampicine + Isoniazide + Pyrazinamide + Éthambutol", "Isolement respiratoire", "Enquête autour du cas", "Durée minimale 6 mois"], "criteres_valides": ["Douleur thoracique présente"], "examens_suggeres": ["Bacilloscopie x 3", "Culture BK", "IDR tuberculine", "TDM thoracique"]}, {"nom": "COPD", "pct": 18.0, "etat": "stable", "recommandations": ["Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"], "criteres_valides": ["Douleur thoracique présente"], "examens_suggeres": ["Spirométrie post-bronchodilatateur", "TDM thoracique", "Gaz du sang", "ECG"]}]	["Vérifier la composition des médicaments (certificat halal si disponible)", "Adapter les horaires de prise médicamenteuse pendant le Ramadan", "Consulter un imam si nécessaire pour les cas d'urgence médicale", "Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"]	surveille	equipe	0	2026-07-02 08:51:47.94599
\.


--
-- Data for Name: documents_medecin; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.documents_medecin (id, medecin_id, type_document, url_fichier, nom_fichier, taille_octets, mime_type, created_at, statut, motif_rejet) FROM stdin;
XHZGRCGRVCNW	PNEU-3918267	diplome_specialisation	uploads\\PNEU-3918267\\documents\\diplome_specialisation.pdf	Architecture de deploiment de deelivx (2).pdf	77415	application/pdf	2026-06-15 20:01:39.173061	en_attente	\N
OMZX03NG12DF	PNEU-3918267	diplome_medecine	uploads\\PNEU-3918267\\documents\\diplome_medecine.pdf	Pratique Professionnelle 1 -  Data Analysis sur Excel.pdf	283254	application/pdf	2026-06-15 20:01:39.173066	en_attente	\N
LTKIOHTFGNJ4	PNEU-3918267	inscription_ordre	uploads\\PNEU-3918267\\documents\\inscription_ordre.pdf	Diagramme sans nom.drawio.pdf	1605	application/pdf	2026-06-15 20:01:39.17307	en_attente	\N
SKAWXK0CIFXQ	PNEU-3918267	autorisation_exercice	uploads\\PNEU-3918267\\documents\\autorisation_exercice.pdf	un-rien-peut-tout-changer.pdf	3749031	application/pdf	2026-06-15 20:01:39.173073	en_attente	\N
DU7D3XFQ9KV2	PNEU-3918267	carte_professionnelle	uploads\\PNEU-3918267\\documents\\carte_professionnelle.pdf	SOP-_HOW_THE_SERVICE_PROVIDER_CAN_SETUP_HIS_OWN_CALENDAR_AND_GENERATE_INVOICES.pdf	1221858	application/pdf	2026-06-15 20:01:39.173076	en_attente	\N
4GJSX04ZAFDO	PNEU-3918267	cni	uploads\\PNEU-3918267\\documents\\cni.pdf	un-rien-peut-tout-changer.pdf	3749031	application/pdf	2026-06-15 20:01:39.173079	en_attente	\N
SKXGM3YO6CJS	PNEU-6888059	diplome_specialisation	uploads\\PNEU-6888059\\documents\\diplome_specialisation.pdf	8. Activité 8.pdf	223741	application/pdf	2026-06-16 20:23:41.250253	en_attente	\N
E0AH3N0YOGZ5	PNEU-6888059	diplome_medecine	uploads\\PNEU-6888059\\documents\\diplome_medecine.lck	.ClassDiagram_PneumoIa.vpp.lck	0	application/octet-stream	2026-06-16 20:23:41.250266	en_attente	\N
PAOM7OIOZTC9	PNEU-6888059	inscription_ordre	uploads\\PNEU-6888059\\documents\\inscription_ordre.docx	TPCLOUDSUPABASE.docx	18296	application/vnd.openxmlformats-officedocument.wordprocessingml.document	2026-06-16 20:23:41.250274	en_attente	\N
DCBCSXVRS6EZ	PNEU-6888059	autorisation_exercice	uploads\\PNEU-6888059\\documents\\autorisation_exercice.xlsx	refusees_2026-06-07.xlsx	17583	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	2026-06-16 20:23:41.250283	en_attente	\N
IICDVK9D6L21	PNEU-6888059	carte_professionnelle	uploads\\PNEU-6888059\\documents\\carte_professionnelle.png	lanalyse-des-donnees.png	28227	image/png	2026-06-16 20:23:41.250292	en_attente	\N
FCZRG8T2D39B	PNEU-6888059	cni	uploads\\PNEU-6888059\\documents\\cni.txt	twilio_2FA_recovery_code.txt	24	text/plain	2026-06-16 20:23:41.250298	en_attente	\N
WNHOJAV9WK6Z	PNEU-3318326	diplome_specialisation	uploads\\PNEU-3318326\\documents\\diplome_specialisation.pdf	bilan_85IKTY7A8E5Q.pdf	14	application/pdf	2026-06-18 19:42:08.002692	en_attente	\N
WMFKQ548X0RY	PNEU-3318326	diplome_medecine	uploads\\PNEU-3318326\\documents\\diplome_medecine.csv	audit_2026-05-07.csv	825	text/csv	2026-06-18 19:42:08.002708	en_attente	\N
1LMUBG0SXX6J	PNEU-3318326	inscription_ordre	uploads\\PNEU-3318326\\documents\\inscription_ordre.png	LOGODocker.png	4213	image/png	2026-06-18 19:42:08.002719	en_attente	\N
EM9Y9PEEC59N	PNEU-3318326	autorisation_exercice	uploads\\PNEU-3318326\\documents\\autorisation_exercice.docx	PT_LICENCE1-1.docx	1418175	application/vnd.openxmlformats-officedocument.wordprocessingml.document	2026-06-18 19:42:08.002729	en_attente	\N
DQ74EJTMXGLZ	PNEU-3318326	carte_professionnelle	uploads\\PNEU-3318326\\documents\\carte_professionnelle.sql	todo-list.sql	578	application/octet-stream	2026-06-18 19:42:08.002743	en_attente	\N
LMGOYK7C0MTT	PNEU-3318326	cni	uploads\\PNEU-3318326\\documents\\cni.png	Figure_1.png	178697	image/png	2026-06-18 19:42:08.002766	en_attente	\N
CA6A1LRGYD8Z	PNEU-2997228	diplome_specialisation	uploads\\PNEU-2997228\\documents\\diplome_specialisation.pdf	Receipt-2089-8693-2630.pdf	32437	application/pdf	2026-06-28 19:40:22.410597	en_attente	\N
1GLZHXRXLZTI	PNEU-2997228	diplome_medecine	uploads\\PNEU-2997228\\documents\\diplome_medecine.docx	ITPath360 quiz Kubernetes.docx	23631	application/vnd.openxmlformats-officedocument.wordprocessingml.document	2026-06-28 19:40:22.410613	en_attente	\N
15C0FU68U024	PNEU-2997228	inscription_ordre	uploads\\PNEU-2997228\\documents\\inscription_ordre.pdf	cours-securite-informatique-et-cryptographie-DUT2_GI2.pdf	3406275	application/pdf	2026-06-28 19:40:22.410619	en_attente	\N
A2KN68QF6AOZ	PNEU-2997228	autorisation_exercice	uploads\\PNEU-2997228\\documents\\autorisation_exercice.pdf	MAYA DISNEY OLIVE-_DEV APP DIST_TP1_CS7.pdf	1288408	application/pdf	2026-06-28 19:40:22.410622	en_attente	\N
VZ1DQ36PSFT4	PNEU-2997228	carte_professionnelle	uploads\\PNEU-2997228\\documents\\carte_professionnelle.pdf	Activité 7, CI CD .pdf	595828	application/pdf	2026-06-28 19:40:22.410626	en_attente	\N
7E8OVTNX0GCM	PNEU-2997228	cni	uploads\\PNEU-2997228\\documents\\cni.docx	Maya expose.docx	40530	application/vnd.openxmlformats-officedocument.wordprocessingml.document	2026-06-28 19:40:22.410631	en_attente	\N
HVJIGU5XKIGP	PNEU-1772790	diplome_specialisation	uploads\\PNEU-1772790\\documents\\diplome_specialisation.docx	mon rapport.docx	1574409	application/vnd.openxmlformats-officedocument.wordprocessingml.document	2026-07-01 22:36:34.272793	en_attente	\N
I0HQGJ3U7HAZ	PNEU-1772790	diplome_medecine	uploads\\PNEU-1772790\\documents\\diplome_medecine.pdf	ClassDiagram_GestionDesAccesBoutiques.pdf	27176	application/pdf	2026-07-01 22:36:34.272809	en_attente	\N
LGZHPESMQ7FW	PNEU-1772790	inscription_ordre	uploads\\PNEU-1772790\\documents\\inscription_ordre.pdf	quitus.pdf	20255	application/pdf	2026-07-01 22:36:34.272813	en_attente	\N
Q5QP94FC22N5	PNEU-1772790	autorisation_exercice	uploads\\PNEU-1772790\\documents\\autorisation_exercice.docx	PT_LICENCE1-1 (1).docx	1418175	application/vnd.openxmlformats-officedocument.wordprocessingml.document	2026-07-01 22:36:34.272819	en_attente	\N
W6GHNUXWVGBY	PNEU-1772790	carte_professionnelle	uploads\\PNEU-1772790\\documents\\carte_professionnelle.pdf	MY RESUME.pdf	962371	application/pdf	2026-07-01 22:36:34.272824	en_attente	\N
F69OL45F9PCI	PNEU-1772790	cni	uploads\\PNEU-1772790\\documents\\cni.pdf	8. Activité 8.pdf	223741	application/pdf	2026-07-01 22:36:34.272828	en_attente	\N
\.


--
-- Data for Name: faq_publiees; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.faq_publiees (id, admin_id, question, reponse, categorie, publie, nb_vues, created_at, updated_at) FROM stdin;
HDX9CUYBH8BG	OBG8EN6SN1OY	uu	ll	Autre	t	0	2026-06-28 21:19:54.748697	\N
6BSR1YZE5O3Y	OBG8EN6SN1OY	jjjjj	mmmm	Autre	t	0	2026-07-01 23:07:44.334614	\N
\.


--
-- Data for Name: feedbacks_ia; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.feedbacks_ia (id, diagnostic_id, medecin_id, concordance, diagnostic_final, commentaire, created_at) FROM stdin;
UM2IJGIEBA01	JS3U7XGCUVX1	PNEU-6888059	\N	Asthma	Couleur de yeux jaune moutarde , chaleur et douleur au touche du thorax 	2026-06-16 21:02:48.03053
O4RCQ1C0AVX7	F25DMEACB57Z	PNEU-6888059	\N	Bronchitis	yeux jonatre 	2026-06-18 16:51:15.26702
HYT2K6FWN0MD	1MJDHPHVW8GN	PNEU-6888059	t	COPD		2026-06-18 18:28:44.784074
7G9XJB5W366H	Q04FPPCF3TG4	PNEU-6888059	t	Allergic Rhinitis		2026-06-25 18:29:45.352539
GIQCBSSE5ET1	1ZBH286RBFLT	PNEU-1772790	f		Yeux jonatre , peau matte	2026-07-02 09:32:42.066652
\.


--
-- Data for Name: likes_commentaires; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.likes_commentaires (id, commentaire_id, auteur_type, auteur_id) FROM stdin;
\.


--
-- Data for Name: likes_messages_equipe; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.likes_messages_equipe (id, message_id, auteur_type, auteur_id) FROM stdin;
\.


--
-- Data for Name: medecins; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.medecins (id, civilite, nom, prenom, email, password_hash, specialite, numero_rpps, etablissement, photo_url, telephone, adresse, bio, linkedin, website, statut, motif_rejet, valide_par, valide_le, activation_token, activation_expires, created_at, preferences, code_referent, code_referent_actif, ville, suspension_raison, suspension_duree, suspension_par, suspension_le, statut_precedent, supprime_le, supprime_par, relance_sent, relance_at, updated_at, rejete_par, derniere_connexion) FROM stdin;
PNEU-1772790	Dr	DeLamoir	Brithnette	mayadisney76+5@gmail.com	$2b$12$.IT1kYw11skaVcw/Oyxw7u5gzu./U40kn5NyIrNDZTv9DGcUqfGja	Pneumologie	12345678901	Chu de Douala	/uploads/PNEU-1772790/photo_profil.jpg	6 34 12 89 53	Extreme Nord	God's Hands	\N	\N	valide	\N	OBG8EN6SN1OY	2026-07-01 22:39:45.439681	SQaPihvK7gUtny-lT3wr6PsuDx_7PM8uFx6QXdC75TY	2026-07-08 22:39:45.439648	2026-07-01 22:36:34.180493	{}	AS-3270J	t	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	2026-07-03 06:49:45.721799	\N	2026-07-03 06:49:45.720304
PNEU-3318326	Mme	Paule	Paule	pougoumpaule@gmail.com	$2b$12$A/JshBtOXLAln2Fdbmq3Su2lGNFsnx9mAKAtFO6W9rH.biS45RzyG	Pneumologie	1234567891008	Polycliniques les soigneurrs	\N	+237 56 89 09 34 	Garoua	\N	\N	\N	corbeille	\N	OBG8EN6SN1OY	2026-06-18 19:45:20.210301	S-B0yCl-o_sGRfMwTIsanIqPFHDdnjHIplHqeKRyWTA	2026-06-25 19:45:20.210255	2026-06-18 19:42:07.846282	{}	AS-WI4P0	t	\N	\N	\N	\N	\N	valide	2026-06-27 14:50:05.768601	OBG8EN6SN1OY	f	\N	2026-06-27 14:50:05.800346	\N	2026-06-18 19:46:09.493144
PNEU-6888059	Mme	Sydney Maya	GRILL	mayadisney76@gmail.com	$2b$12$oIbKWF7CzbmbthH2nlX7LOaviAd71it30GkEIoM4Q8LBe1QZiNttq	Pneumologie	123456789002	Hopital de reference 	\N	+237 656616801	Yaounde	Sauver des vies  j'ai fais de cela une passion	\N	\N	valide	\N	OBG8EN6SN1OY	2026-06-16 20:37:43.201299	lyOCpVn6IrcmUl_b8d8wW2p6sJsFBC1dM1q-XGicz3o	2026-06-23 20:37:43.201178	2026-06-16 20:23:41.141611	{}	AS-2ZHCX	t	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	2026-07-04 13:11:28.338746	\N	2026-07-04 13:11:28.336342
PNEU-2997228	Dr	DALRILL	Pirout	mayadisney76+4@gmail.com	$2b$12$Erjy1.GtWVpSJvdOTaUkouXoFJ0v1JkwcEdRn2.jNzutV2DJ24j7K	Pneumologie	12345678910	Hopital les sappeurs 	/uploads/PNEU-2997228/photo_profil.jpg	6 58 26 01 14	Est	Everything in god's hand	\N	\N	corbeille	Documents flous / illisibles : k neden ;klllllllllllllllllllllllllllnndwnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnc	\N	\N	\N	\N	2026-06-28 19:40:22.311597	{}	AS-W6NVL	t	\N	\N	\N	\N	\N	rejete	2026-06-28 20:09:11.696417	OBG8EN6SN1OY	f	\N	2026-06-28 20:09:11.697695	OBG8EN6SN1OY	\N
PNEU-3918267	Mme	Maya	Disney Olive	mayadisneyolive21@gmail.com	$2b$12$jVxED6zHvZ08P/R9VjpOBOyL96NX2hqI8ec.AeHTnl8h6LeM5xzlS	Pneumologie	123456789010	AD LUCEM	\N	+237 656616801	DOUALA,CAMEROUN	Sauver desvies	\N	\N	corbeille	N° CNOM invalide ou introuvable : Votre CNI arrive bientot a inspiration veillez , fournis un plus valide.	OBG8EN6SN1OY	2026-06-15 20:25:30.021262	9lQPYDh3uWxhiz41uu82EarYjqHa5F8X-xUHfvLu7j8	2026-06-22 20:25:30.021222	2026-06-15 20:01:39.099576	{}	AS-GZQA1	t	\N	\N	\N	\N	\N	rejete	2026-06-23 22:25:17.655005	\N	t	2026-06-16 18:44:08.410724	2026-06-23 22:25:17.658252	\N	\N
PNEU-8414821	\N	TEST	Docteur	docteur.test@pneumoia.com	$2b$12$QzuFemC01agQGerP4lePI.vLqq1dfh96q4kX1zGBCz8L4ynsWbgne	Pneumologie	\N	\N	\N	\N	\N	\N	\N	\N	valide	\N	\N	\N	\N	\N	2026-07-08 14:19:44.161609	{"langue": "fr", "compactView": true}	AS-FGHUD	t	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	2026-07-09 11:17:30.775393	\N	\N
\.


--
-- Data for Name: membres_communaute; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.membres_communaute (id, communaute_id, medecin_id, role, statut, joined_at) FROM stdin;
\.


--
-- Data for Name: messages_equipe; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.messages_equipe (id, medecin_referent_id, auteur_type, auteur_medecin_id, auteur_aide_id, parent_id, contenu, type_msg, pinned, likes_count, created_at) FROM stdin;
MSG-QPV2EC2SSW	PNEU-6888059	medecin	PNEU-6888059	\N	\N	jjjjjj	info	f	0	2026-07-02 11:19:10.203117
MSG-9HCFTK9BNM	PNEU-8414821	medecin	PNEU-8414821	\N	\N	Bien reçu, merci.	rapport	f	0	2026-07-08 22:21:54.765083
MSG-YPCVNWGU3M	PNEU-8414821	medecin	PNEU-8414821	\N	\N	Bien reçu, merci.	rapport	f	0	2026-07-08 22:23:29.738811
MSG-12E0YX78BL	PNEU-8414821	medecin	PNEU-8414821	\N	\N	Bien reçu, merci.	rapport	f	0	2026-07-09 10:33:25.455927
MSG-2B64N80HYN	PNEU-8414821	medecin	PNEU-8414821	\N	\N	Bien reçu, merci.	rapport	f	0	2026-07-09 11:15:26.35406
MSG-V4ZNCUVQG9	PNEU-8414821	medecin	PNEU-8414821	\N	\N	Bien reçu, merci.	rapport	f	0	2026-07-09 11:17:30.922521
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.notifications (id, destinataire_id, type_dest, type_notif, titre, message, meta, lu, created_at) FROM stdin;
NJZ19CDM8YFL	Y8P0APWTC4Y0	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr Disney Olive Maya	Dr Disney Olive Maya (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-3918267.	{"lien": "/admin/demandes/PNEU-3918267", "medecin_id": "PNEU-3918267"}	f	2026-06-15 20:01:39.209267
B0U02GH93GM3	Y8P0APWTC4Y0	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr GRILL Sydney Maya	Dr GRILL Sydney Maya (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-6888059.	{"lien": "/admin/demandes/PNEU-6888059", "medecin_id": "PNEU-6888059"}	f	2026-06-16 20:23:41.338752
OELODMAJ6WR2	AIDE-7829840	aide_soignant	validation	Compte validé	Mme GRILL Sydney Maya a approuvé votre compte. Vous pouvez maintenant accéder à toutes vos fonctionnalités.	{"lien": "/aide/dashboard"}	f	2026-06-17 14:22:37.110044
45OEGM8H9MCP	AIDE-7829840	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. GRILL Sydney Maya a modifié le dossier de BRUNO KELIEY.	{"lien": "/aide/patients", "patient_id": "Q7D9ARPMBNWG"}	f	2026-06-25 18:13:21.082226
4Y7JLF2XQLYF	AIDE-9233662	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. GRILL Sydney Maya a modifié le dossier de BRUNO KELIEY.	{"lien": "/aide/patients", "patient_id": "Q7D9ARPMBNWG"}	f	2026-06-25 18:13:21.086831
NACR22LCO2AG	AIDE-5375941	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. GRILL Sydney Maya a modifié le dossier de BRUNO KELIEY.	{"lien": "/aide/patients", "patient_id": "Q7D9ARPMBNWG"}	f	2026-06-25 18:13:21.08992
VZVFKZ4OT099	Y8P0APWTC4Y0	admin	nouvelle_requete_medecin	Nouvelle requête — IA	Dr. GRILL Sydney Maya a soumis une requête : IA	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-6888059", "requete_id": "REQ-P0A4CBKQF4"}	f	2026-06-25 18:33:17.533149
VQM138BSK28K	AIDE-7829840	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. GRILL Sydney Maya a modifié le dossier de Sophie Claire WENE.	{"lien": "/aide/patients", "patient_id": "CT7V6LZQO2SV"}	f	2026-06-18 16:41:04.052398
HGVD526IMQB6	AIDE-7829840	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. GRILL Sydney Maya a modifié le dossier de Sophie Claire WENE.	{"lien": "/aide/patients", "patient_id": "MQO58PFGVZLC"}	f	2026-06-18 16:41:04.069412
SKJYJP9HZFHZ	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — IA	Dr. GRILL Sydney Maya a soumis une requête : IA	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-6888059", "requete_id": "REQ-P0A4CBKQF4"}	f	2026-06-25 18:33:17.5346
MLIU065ULNSY	PNEU-6888059	medecin	aide_nouveau_patient	Nouveau patient créé	RAFF RAFF a créé le dossier de BRUNO KELIEY.	{"lien": "/medecin/patients"}	t	2026-06-25 18:07:49.868932
0UCUQIVDWJRW	PNEU-6888059	medecin	requete_traitee	Votre requête a été traitée	Votre requête « IA » a reçu une réponse de l'administrateur.	{"lien": "/medecin/commentaires", "requete_id": "REQ-P0A4CBKQF4"}	t	2026-06-25 18:35:07.223781
FILGCMQXIR4Y	PNEU-6888059	medecin	faq_reponse	L'administration PneumoIA a répondu à votre question	Votre question : Comment publier?\n\nRéponse : gggggg	{"lien": "/medecin/notifications", "question_id": "QST-O27JWEKI3I"}	t	2026-06-25 18:37:27.901166
QL7HOW80UY9U	PNEU-6888059	medecin	temoignage_supprime	Votre témoignage a été retiré	L'administrateur a supprimé votre témoignage de la page d'accueil. Raison : nvnm	{"lien": "/medecin/commentaires"}	t	2026-06-25 18:53:19.457393
ACOBOFY8RH95	PNEU-6888059	medecin	temoignage_supprime	Votre témoignage a été retiré	L'administrateur a supprimé votre témoignage de la page d'accueil.	{"lien": "/medecin/commentaires"}	t	2026-06-25 18:55:37.788727
O6LC4KIU8F7T	PNEU-6888059	medecin	temoignage_supprime	Votre témoignage a été retiré	L'administrateur a supprimé votre témoignage de la page d'accueil.	{"lien": "/medecin/commentaires"}	t	2026-06-25 18:55:37.78917
P47OZVQXR3MD	PNEU-6888059	medecin	requete_statut	Requête mise à jour — Fermée	Votre requête « ff » est maintenant : Fermée.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:25:29.943895
O9NMYZXS9DDT	PNEU-6888059	medecin	requete_statut	Requête mise à jour — En cours de traitement	Votre requête « ff » est maintenant : En cours de traitement.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:25:30.063051
89F0EYKVQMLY	PNEU-6888059	medecin	requete_statut	Requête mise à jour — En cours de traitement	Votre requête « ff » est maintenant : En cours de traitement.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:25:30.104986
ZL96NEJZBLF4	AIDE-7829840	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. GRILL Sydney Maya a modifié le dossier de NINA Thomsom RIKA.	{"lien": "/aide/patients", "patient_id": "VUDFTD98XREM"}	f	2026-06-18 18:22:50.733382
K8CRYWYXROLR	AIDE-7829840	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. GRILL Sydney Maya a modifié le dossier de NINA Thomsom RIKA.	{"lien": "/aide/patients", "patient_id": "VUDFTD98XREM"}	f	2026-06-18 18:22:50.761847
TP5DDQX3IJ86	Y8P0APWTC4Y0	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr Paule Paule	Dr Paule Paule (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-3318326.	{"lien": "/admin/demandes/PNEU-3318326", "medecin_id": "PNEU-3318326"}	f	2026-06-18 19:42:08.110555
784YQ15YJTGU	Y8P0APWTC4Y0	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr Pougoum Paule	Dr Pougoum Paule (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-0936914.	{"lien": "/admin/demandes/PNEU-0936914", "medecin_id": "PNEU-0936914"}	f	2026-06-22 15:31:12.826672
0C2HZZLYCFFF	Y8P0APWTC4Y0	admin	nouvelle_requete_medecin	Nouvelle requête — ff	Dr. GRILL Sydney Maya a soumis une requête : ff	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-6888059", "requete_id": "REQ-QMZ1W34UJ5"}	f	2026-06-23 16:07:58.825188
R8CKOI9FPPFV	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — ff	Dr. GRILL Sydney Maya a soumis une requête : ff	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-6888059", "requete_id": "REQ-QMZ1W34UJ5"}	f	2026-06-23 16:07:58.826027
GRXVOLRHXR7V	Y8P0APWTC4Y0	admin	nouvelle_requete_medecin	Nouvelle requête — IA derange	Dr. GRILL Sydney Maya a soumis une requête : IA derange	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-6888059", "requete_id": "REQ-24OX4ZIEFK"}	f	2026-06-23 16:24:52.45082
SMQVJL6BRDAF	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — IA derange	Dr. GRILL Sydney Maya a soumis une requête : IA derange	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-6888059", "requete_id": "REQ-24OX4ZIEFK"}	f	2026-06-23 16:24:52.45083
DJUX5QLXYCNV	Y8P0APWTC4Y0	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr Disneyolive  Maya	Dr Disneyolive  Maya (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-6211934.	{"lien": "/admin/demandes/PNEU-6211934", "medecin_id": "PNEU-6211934"}	f	2026-06-23 18:09:57.780171
D0KK1LV3H0RA	Y8P0APWTC4Y0	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr TOmys Meli 	Dr TOmys Meli  (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-0769816.	{"lien": "/admin/demandes/PNEU-0769816", "medecin_id": "PNEU-0769816"}	f	2026-06-23 22:07:37.438003
TC6OQW2YCF0A	AIDE-9233662	aide_soignant	validation	Compte validé	Mme GRILL Sydney Maya a approuvé votre compte. Vous pouvez maintenant accéder à toutes vos fonctionnalités.	{"lien": "/aide/dashboard"}	f	2026-06-25 18:01:33.654185
V6ASOASB9DL6	AIDE-5375941	aide_soignant	validation	Compte validé	Mme GRILL Sydney Maya a approuvé votre compte. Vous pouvez maintenant accéder à toutes vos fonctionnalités.	{"lien": "/aide/dashboard"}	f	2026-06-25 18:04:51.495292
1KEYX2BD9B3B	Y8P0APWTC4Y0	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr Pirout DALRILL	Dr Pirout DALRILL (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-2997228.	{"lien": "/admin/demandes/PNEU-2997228", "medecin_id": "PNEU-2997228"}	f	2026-06-28 19:40:22.502521
A6RQ7F81NG9A	OBG8EN6SN1OY	admin	nouvelle_inscription_medecin	Nouvelle demande d'accès — Dr Brithnette DeLamoir	Dr Brithnette DeLamoir (Pneumologie) a soumis une demande d'accès à la plateforme. Identifiant : PNEU-1772790.	{"lien": "/admin/demandes/PNEU-1772790", "medecin_id": "PNEU-1772790"}	f	2026-07-01 22:36:34.37779
AE8X2ZLKONDD	AIDE-1180204	aide_soignant	validation	Compte validé	Dr Brithnette DeLamoir a approuvé votre compte. Vous pouvez maintenant accéder à toutes vos fonctionnalités.	{"lien": "/aide/dashboard"}	f	2026-07-01 22:54:45.294104
SM5QC8H4YX9J	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — jjjjdcjj : IA	Dr. Brithnette DeLamoir a soumis une requête : jjjjdcjj : IA	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-1772790", "requete_id": "REQ-UJYEBRX1PP"}	f	2026-07-01 23:14:39.45812
XC0W8XRRLBZF	AIDE-5828352	aide_soignant	validation	Compte validé	Dr Brithnette DeLamoir a approuvé votre compte. Vous pouvez maintenant accéder à toutes vos fonctionnalités.	{"lien": "/aide/dashboard"}	t	2026-07-02 08:25:49.595798
7Z7ENXB8S1RO	AIDE-5828352	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. Brithnette DeLamoir a modifié le dossier de Hibrahim STIRFF.	{"lien": "/aide/patients", "patient_id": "DGCOG3YQNGWM"}	f	2026-07-02 08:36:21.80022
EF8269XZ9WJW	PNEU-6888059	medecin	temoignage_supprime	Votre témoignage a été retiré	L'administrateur a supprimé votre témoignage de la page d'accueil. Raison : cwdw	{"lien": "/medecin/commentaires"}	t	2026-06-18 18:05:09.958775
CY52EUJEF7IZ	PNEU-6888059	medecin	faq_reponse	L'administration PneumoIA a répondu à votre question	Votre question : jjjrjejrge\n\nRéponse : jjjjj	{"lien": "/medecin/notifications", "question_id": "QST-JWDUVWEIR2"}	t	2026-06-19 16:10:48.416493
L5SLS80VX15I	PNEU-6888059	medecin	aide_demande	Nouvelle demande d'aide soignant	maya olive (mayadisney76@gmail.com) souhaite rejoindre votre équipe.	{"lien": "/medecin/parametres"}	t	2026-06-19 17:57:30.759188
DN6A0AMU9OTR	PNEU-6888059	medecin	requete_traitee	Votre requête a été traitée	Votre requête « ff » a reçu une réponse de l'administrateur.	{"lien": "/medecin/requetes", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:08:36.815444
ANBMTKKT3WML	PNEU-6888059	medecin	requete_statut	Requête mise à jour — Résolue	Votre requête « ff » est maintenant : Résolue.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:23:10.430764
VOQK6Z4ZC7JX	PNEU-6888059	medecin	requete_statut	Requête mise à jour — En cours de traitement	Votre requête « IA derange » est maintenant : En cours de traitement.	{"lien": "/medecin/commentaires", "requete_id": "REQ-24OX4ZIEFK"}	t	2026-06-23 16:25:13.105539
VVP2YYXVVY1Q	PNEU-6888059	medecin	requete_statut	Requête mise à jour — Résolue	Votre requête « IA derange » est maintenant : Résolue.	{"lien": "/medecin/commentaires", "requete_id": "REQ-24OX4ZIEFK"}	t	2026-06-23 16:25:16.400878
06CSEJVGJAHX	PNEU-6888059	medecin	requete_statut	Requête mise à jour — Fermée	Votre requête « IA derange » est maintenant : Fermée.	{"lien": "/medecin/commentaires", "requete_id": "REQ-24OX4ZIEFK"}	t	2026-06-23 16:25:21.063343
HPW86ELLY7QZ	PNEU-6888059	medecin	requete_statut	Requête mise à jour — Fermée	Votre requête « ff » est maintenant : Fermée.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:25:25.855345
YI54SGN7FZ1C	PNEU-6888059	medecin	requete_statut	Requête mise à jour — Fermée	Votre requête « ff » est maintenant : Fermée.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:25:25.988102
EH1RREKN6KQ4	PNEU-6888059	medecin	requete_statut	Requête mise à jour — En cours de traitement	Votre requête « ff » est maintenant : En cours de traitement.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:25:26.011374
LJFALBZGI5X5	PNEU-6888059	medecin	faq_reponse	L'administration PneumoIA a répondu à votre question	Votre question : jjj\n\nRéponse : kkkk	{"lien": "/medecin/notifications", "question_id": "QST-VUNYQFZ1AO"}	t	2026-06-28 20:35:40.129573
SXLAGYOHE4N5	PNEU-6888059	medecin	faq_reponse	L'administration PneumoIA a répondu à votre question	Votre question : uu\n\nRéponse : ll	{"lien": "/medecin/notifications", "question_id": "QST-1ZVMSLNR3F"}	t	2026-06-28 21:19:44.886732
S3SUJ90WGM6A	PNEU-6888059	medecin	temoignage_supprime	Votre témoignage a été retiré	L'administrateur a supprimé votre témoignage de la page d'accueil. Raison : llll	{"lien": "/medecin/commentaires"}	t	2026-07-01 23:10:45.527421
FWPFFRTOQXN3	PNEU-6888059	medecin	temoignage_supprime	Votre témoignage a été retiré	L'administrateur a supprimé votre témoignage de la page d'accueil. Raison : mmmm	{"lien": "/medecin/commentaires"}	t	2026-07-01 23:10:51.260612
H4GQ4OO2KJKQ	PNEU-1772790	medecin	aide_demande	Nouvelle demande d'aide soignant	Dawn CLARA (mayadisnneyolive+@gmail.com) souhaite rejoindre votre équipe.	{"lien": "/medecin/parametres"}	t	2026-07-01 22:54:38.33414
FWRSFRJJ3UP6	PNEU-1772790	medecin	requete_traitee	Votre requête a été traitée	Votre requête « jjjjdcjj : IA » a reçu une réponse de l'administrateur.	{"lien": "/medecin/commentaires", "requete_id": "REQ-UJYEBRX1PP"}	t	2026-07-01 23:16:05.735844
XNVXHS3XRENY	PNEU-1772790	medecin	faq_reponse	L'administration PneumoIA a répondu à votre question	Votre question : jjjjj\n\nRéponse : mmmm	{"lien": "/medecin/notifications", "question_id": "QST-NYZOVCHNDY"}	t	2026-07-01 23:07:25.452789
KUG46XYZEJYF	PNEU-1772790	medecin	temoignage_supprime	Votre témoignage a été retiré	L'administrateur a supprimé votre témoignage de la page d'accueil. Raison : mkk	{"lien": "/medecin/commentaires"}	t	2026-07-01 23:10:39.747342
339Y4OR3GR75	PNEU-1772790	medecin	aide_demande	Nouvelle demande d'aide soignant	Maya Soignante (mayadisneyolive21+@gmail.com) souhaite rejoindre votre équipe.	{"lien": "/medecin/parametres"}	t	2026-07-02 08:25:36.305502
L56PZGT6EAE8	PNEU-6888059	medecin	requete_traitee	Votre requête a été traitée	Votre requête « IA derange » a reçu une réponse de l'administrateur.	{"lien": "/medecin/commentaires", "requete_id": "REQ-24OX4ZIEFK"}	t	2026-06-23 16:25:47.178586
9MGK43BF8JH1	PNEU-6888059	medecin	requete_statut	Requête mise à jour — Fermée	Votre requête « ff » est maintenant : Fermée.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:26:33.285513
QOU0K4KH9KS3	PNEU-6888059	medecin	aide_demande	Nouvelle demande d'aide soignant	RAFF RAFF (mayadisney76+2@gmail.com) souhaite rejoindre votre équipe.	{"lien": "/medecin/parametres"}	t	2026-06-25 18:01:19.206959
8UDCQW03A3V0	PNEU-6888059	medecin	requete_statut	Requête mise à jour — En cours de traitement	Votre requête « ff » est maintenant : En cours de traitement.	{"lien": "/medecin/commentaires", "requete_id": "REQ-QMZ1W34UJ5"}	t	2026-06-23 16:26:34.715931
1HWXFT872T0G	AIDE-7829840	aide_soignant	nouveau_message_medecin	Message du médecin référent	Dr. GRILL Sydney Maya a posté un message dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-02 11:19:10.227222
UQROD6M3Q4C5	AIDE-9233662	aide_soignant	nouveau_message_medecin	Message du médecin référent	Dr. GRILL Sydney Maya a posté un message dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-02 11:19:10.242853
4OECNVJJ2TSN	AIDE-5375941	aide_soignant	nouveau_message_medecin	Message du médecin référent	Dr. GRILL Sydney Maya a posté un message dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-02 11:19:10.244237
0543BB35AAHS	AIDE-7829840	aide_soignant	nouveau_post	Nouvelle publication	Dr. GRILL Sydney Maya a publié « mmmmm ».	{"lien": "/aide/publications", "pub_id": "LE3ISCR74GNE"}	f	2026-07-02 11:19:54.099044
NM45XMVFE1UW	AIDE-9233662	aide_soignant	nouveau_post	Nouvelle publication	Dr. GRILL Sydney Maya a publié « mmmmm ».	{"lien": "/aide/publications", "pub_id": "LE3ISCR74GNE"}	f	2026-07-02 11:19:54.10046
A7NUYJ018NSI	AIDE-5375941	aide_soignant	nouveau_post	Nouvelle publication	Dr. GRILL Sydney Maya a publié « mmmmm ».	{"lien": "/aide/publications", "pub_id": "LE3ISCR74GNE"}	f	2026-07-02 11:19:54.101864
BOEUFVIOXLO3	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. GRILL Sydney Maya	« mmmmm » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "LE3ISCR74GNE"}	f	2026-07-02 11:19:54.109321
UA0WATW0AP2O	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — kkk	Dr. GRILL Sydney Maya a soumis une requête : kkk	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-6888059", "requete_id": "REQ-1LUMJFBIC2"}	f	2026-07-02 11:23:45.162899
HYDOK31NNS80	AIDE-5828352	aide_soignant	nouveau_commentaire	Votre médecin a commenté une publication	Dr. Brithnette DeLamoir a commenté la publication « mmmmm ».	{"lien": "/aide/commentaires"}	f	2026-07-02 11:26:43.70463
ZT5DDVMI2KK2	PNEU-6888059	medecin	nouveau_commentaire	Nouveau commentaire sur votre publication	Dr. Brithnette DeLamoir a commenté votre publication « mmmmm ».	{"lien": "/medecin/commentaires"}	t	2026-07-02 11:26:43.68383
YMA4AGO1CYLU	PNEU-1772790	medecin	aide_nouveau_patient	Nouveau patient créé	Maya Soignante a créé le dossier de Hibrahim STIRFF.	{"lien": "/medecin/patients"}	t	2026-07-02 08:30:35.910194
2XYU394OP0N2	AIDE-7829840	aide_soignant	nouveau_post	Nouvelle publication	Dr. GRILL Sydney Maya a publié « j'aimerais obtenir le dossier du patient Hibrahim stirff ».	{"lien": "/aide/publications", "pub_id": "FG3S0881FFO1"}	f	2026-07-03 06:51:25.650083
J2UNEHA4198T	AIDE-9233662	aide_soignant	nouveau_post	Nouvelle publication	Dr. GRILL Sydney Maya a publié « j'aimerais obtenir le dossier du patient Hibrahim stirff ».	{"lien": "/aide/publications", "pub_id": "FG3S0881FFO1"}	f	2026-07-03 06:51:25.652906
9IJ00M40B108	AIDE-5375941	aide_soignant	nouveau_post	Nouvelle publication	Dr. GRILL Sydney Maya a publié « j'aimerais obtenir le dossier du patient Hibrahim stirff ».	{"lien": "/aide/publications", "pub_id": "FG3S0881FFO1"}	f	2026-07-03 06:51:25.65425
3FIBX7E7ZFSS	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. GRILL Sydney Maya	« j'aimerais obtenir le dossier du patient Hibrahim stirff » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "FG3S0881FFO1"}	f	2026-07-03 06:51:25.657474
HM6ZDKZ4PAD4	OBG8EN6SN1OY	admin	deblocage_compte	Demande de déblocage de compte	Dr. GRILL Sydney Maya (mayadisney76@gmail.com) demande le déblocage de son compte suspendu via email. Consultez la page Comptes suspendus pour traiter cette demande.	{"actionLink": "/administrateur/suspendus", "medecin_id": "PNEU-6888059", "medecin_nom": "GRILL Sydney Maya"}	f	2026-07-03 07:34:34.975936
MO79UKCM7VK1	OBG8EN6SN1OY	admin	deblocage_compte	Demande de déblocage de compte	Dr. GRILL Sydney Maya (mayadisney76@gmail.com) demande le déblocage de son compte suspendu via email. Consultez la page Comptes suspendus pour traiter cette demande.	{"actionLink": "/administrateur/suspendus", "medecin_id": "PNEU-6888059", "medecin_nom": "GRILL Sydney Maya"}	f	2026-07-03 07:34:34.992088
LF09XB76UXCO	PNEU-6888059	medecin	requete_traitee	Votre requête a été traitée	Votre requête « Demande de déblocage de compte » a reçu une réponse de l'administrateur.	{"lien": "/medecin/commentaires", "requete_id": "REQ-A7AM6YTGQK"}	f	2026-07-03 07:55:15.875379
APNF580N7GQ9	PNEU-6888059	medecin	requete_traitee	Votre requête a été traitée	Votre requête « Demande de déblocage de compte » a reçu une réponse de l'administrateur.	{"lien": "/medecin/commentaires", "requete_id": "REQ-GKJO6Z5STJ"}	f	2026-07-03 07:55:15.877491
F6E5Z5XQH44O	OBG8EN6SN1OY	admin	deblocage_compte	Demande de déblocage de compte	Dr. GRILL Sydney Maya (mayadisney76@gmail.com) demande le déblocage de son compte suspendu via email. Consultez la page Comptes suspendus pour traiter cette demande.	{"actionLink": "/administrateur/suspendus", "medecin_id": "PNEU-6888059", "medecin_nom": "GRILL Sydney Maya"}	f	2026-07-04 13:06:34.990207
QTY12TBWJ2J8	OBG8EN6SN1OY	admin	deblocage_compte	Demande de déblocage de compte	Dr. GRILL Sydney Maya (mayadisney76@gmail.com) demande le déblocage de son compte suspendu via email. Consultez la page Comptes suspendus pour traiter cette demande.	{"actionLink": "/administrateur/suspendus", "medecin_id": "PNEU-6888059", "medecin_nom": "GRILL Sydney Maya"}	f	2026-07-04 13:06:34.99118
J4UDALDUOQ1G	PNEU-6888059	medecin	requete_traitee	Votre requête a été traitée	Votre requête « Demande de déblocage de compte » a reçu une réponse de l'administrateur.	{"lien": "/medecin/commentaires", "requete_id": "REQ-8JT11KTECJ"}	f	2026-07-04 13:07:38.269758
GF50M67Y0RRO	AIDE-2609616	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. Docteur TEST a modifié le dossier de Jean-Pierre DUPONT.	{"lien": "/aide/patients", "patient_id": "SY6XXQE5NJKG"}	f	2026-07-09 11:15:26.660707
NCXLHVDR2OOS	AIDE-2609616	aide_soignant	nouveau_post	Nouvelle publication	Dr. Docteur TEST a publié « Test publication pneumonie ».	{"lien": "/aide/publications", "pub_id": "S05MT84X2SXV"}	f	2026-07-09 11:15:26.944174
LS1FJYKWMKL8	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "S05MT84X2SXV"}	f	2026-07-09 11:15:26.946749
KP8SN39S6XQ6	AIDE-2609616	aide_soignant	nouveau_commentaire	Votre médecin a commenté une publication	Dr. Docteur TEST a commenté la publication « Test publication pneumonie ».	{"lien": "/aide/commentaires"}	f	2026-07-09 11:15:27.002728
U1DX70TAKTWN	OBG8EN6SN1OY	admin	compte_bloque_tentatives	Compte médecin bloqué — tentatives suspectes	Le compte de Dr. GRILL Sydney Maya (mayadisney76@gmail.com) a été suspendu après 3 tentatives OTP incorrectes lors de la réinitialisation du mot de passe.	{"email": "mayadisney76@gmail.com", "actionLink": "/administrateur/suspendus", "medecin_id": "PNEU-6888059", "medecin_nom": "GRILL Sydney Maya"}	t	2026-07-03 07:34:00.808216
4ZIZ1ZD8XAY0	OBG8EN6SN1OY	admin	compte_bloque_tentatives	Compte médecin bloqué — tentatives suspectes	Le compte de Dr. GRILL Sydney Maya (mayadisney76@gmail.com) a été suspendu après 3 tentatives OTP incorrectes lors de la réinitialisation du mot de passe.	{"email": "mayadisney76@gmail.com", "actionLink": "/administrateur/suspendus", "medecin_id": "PNEU-6888059", "medecin_nom": "GRILL Sydney Maya"}	t	2026-07-04 12:59:56.730524
U24MW9TK1U00	PNEU-6888059	medecin	compte_reactive	Votre compte a été réactivé	Votre compte PneumoIA a été réactivé par l'administrateur. Vous pouvez de nouveau vous connecter à la plateforme.	{"actionLink": "/"}	f	2026-07-04 13:07:34.762457
VOVR34IPS9FQ	PNEU-6888059	medecin	requete_traitee	Votre requête a été traitée	Votre requête « Demande de déblocage de compte » a reçu une réponse de l'administrateur.	{"lien": "/medecin/commentaires", "requete_id": "REQ-MJDCXG9UGL"}	f	2026-07-04 13:07:38.268729
3YN3QUI8T45S	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "8C1409U6CU0L"}	f	2026-07-08 21:37:24.923199
7807B3BYM87W	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-24PNUR1J1A"}	f	2026-07-08 21:37:25.131112
JCI2LPKS2V3U	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "JG62NWAVCFTU"}	f	2026-07-08 21:38:08.079214
N2PQB498PXAD	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-M2BP9VMXHR"}	f	2026-07-08 21:38:08.241343
MK4847ZTM6NL	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "P724CQJ3YYX6"}	f	2026-07-08 21:43:55.231456
EP55Y0LUAOND	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-U9K0KLM9QF"}	f	2026-07-08 21:43:55.480641
ZJCYFRYUYAG9	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "UR9TQU74SFCA"}	f	2026-07-08 22:15:15.369908
0ULE69D5RIFF	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-5DBL7NK770"}	f	2026-07-08 22:15:15.547997
NEVT02LIDSJY	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "KO28C36UAMJ7"}	f	2026-07-08 22:21:55.650488
Z78H7F1F6DF5	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-HUK9BOV0HR"}	f	2026-07-08 22:21:55.949809
103JNOW758Z2	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "5CMZY4HG8SHH"}	f	2026-07-08 22:23:30.628655
LJHGSB3B104Y	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-SN7MPAH14S"}	f	2026-07-08 22:23:30.929911
OZLP8SHWPN4C	AIDE-2609616	aide_soignant	nouveau_message_medecin	Message du médecin référent	Dr. Docteur TEST a posté un message dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-09 10:33:25.423104
TBV9AS32B6BT	AIDE-2609616	aide_soignant	nouveau_commentaire	Réponse du médecin référent	Dr. Docteur TEST a répondu dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-09 10:33:25.461881
EFRLZFM9N6BK	AIDE-2609616	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. Docteur TEST a modifié le dossier de Jean-Pierre DUPONT.	{"lien": "/aide/patients", "patient_id": "AXWG7VQ76BBU"}	f	2026-07-09 10:33:25.905758
EPJO9P36ADNH	AIDE-2609616	aide_soignant	nouveau_post	Nouvelle publication	Dr. Docteur TEST a publié « Test publication pneumonie ».	{"lien": "/aide/publications", "pub_id": "17RXW3HTO1O3"}	f	2026-07-09 10:33:26.168636
7888309LQOMV	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "17RXW3HTO1O3"}	f	2026-07-09 10:33:26.172737
4XDSV8OQCMLA	AIDE-2609616	aide_soignant	nouveau_commentaire	Votre médecin a commenté une publication	Dr. Docteur TEST a commenté la publication « Test publication pneumonie ».	{"lien": "/aide/commentaires"}	f	2026-07-09 10:33:26.25352
WCGN49Q79NI7	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-KWM2300HT0"}	f	2026-07-09 10:33:26.449048
IX8BY9DOF383	AIDE-2609616	aide_soignant	nouveau_message_medecin	Message du médecin référent	Dr. Docteur TEST a posté un message dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-09 11:15:26.325562
ZXDXUFPICC6Z	AIDE-2609616	aide_soignant	nouveau_commentaire	Réponse du médecin référent	Dr. Docteur TEST a répondu dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-09 11:15:26.357732
8ROKXRR4FBSH	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-10QG71JK2S"}	f	2026-07-09 11:15:27.110014
RCTNQUWKW9IJ	AIDE-2609616	aide_soignant	nouveau_message_medecin	Message du médecin référent	Dr. Docteur TEST a posté un message dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-09 11:17:30.877046
FB8KXOI98IB4	AIDE-2609616	aide_soignant	nouveau_commentaire	Réponse du médecin référent	Dr. Docteur TEST a répondu dans le canal équipe.	{"lien": "/aide/commentaires"}	f	2026-07-09 11:17:30.926196
TA0OK0I3EVSC	AIDE-2609616	aide_soignant	aide_modif_patient	Dossier patient modifié	Dr. Docteur TEST a modifié le dossier de Jean-Pierre DUPONT.	{"lien": "/aide/patients", "patient_id": "AL4Q7NBH9RL0"}	f	2026-07-09 11:17:31.421368
Z1ZLHW6R23IB	AIDE-2609616	aide_soignant	nouveau_post	Nouvelle publication	Dr. Docteur TEST a publié « Test publication pneumonie ».	{"lien": "/aide/publications", "pub_id": "GQTA5SS55RJZ"}	f	2026-07-09 11:17:31.747109
I73CLHW6PAHT	OBG8EN6SN1OY	admin	nouvelle_publication	Nouvelle publication — Dr. Docteur TEST	« Test publication pneumonie » (discussion)	{"lien": "/administrateur/commentaires", "pub_id": "GQTA5SS55RJZ"}	f	2026-07-09 11:17:31.750556
KVG0L310GEMV	AIDE-2609616	aide_soignant	nouveau_commentaire	Votre médecin a commenté une publication	Dr. Docteur TEST a commenté la publication « Test publication pneumonie ».	{"lien": "/aide/commentaires"}	f	2026-07-09 11:17:31.837987
7VJRX1OCGSBC	OBG8EN6SN1OY	admin	nouvelle_requete_medecin	Nouvelle requête — Problème de connexion	Dr. Docteur TEST a soumis une requête : Problème de connexion	{"lien": "/administrateur/requetes", "medecin_id": "PNEU-8414821", "requete_id": "REQ-IGNWEA4M1W"}	f	2026-07-09 11:17:32.3756
\.


--
-- Data for Name: otp_codes; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.otp_codes (id, medecin_id, code, expires_at, used, created_at, purpose, fail_count) FROM stdin;
29SD0MFSXIWV	PNEU-3918267	593702	2026-06-15 20:40:43.157793	f	2026-06-15 20:35:43.165482	login	0
UD3TF1P9VKKQ	PNEU-3918267	105058	2026-06-16 04:29:34.301834	t	2026-06-16 04:24:34.391882	reset	0
TUVPCSS611O4	PNEU-3918267	810188	2026-06-16 05:02:30.135284	t	2026-06-16 04:57:33.789546	reset	0
XGYOOZQYG68N	PNEU-3918267	593053	2026-06-16 05:03:55.910563	t	2026-06-16 04:58:55.916646	login	0
TCZGTOTMZTJ1	PNEU-3918267	972973	2026-06-16 10:40:24.396515	t	2026-06-16 10:35:24.458021	login	0
SO51CULLQZ8B	PNEU-6888059	404689	2026-06-16 20:44:27.928819	t	2026-06-16 20:39:27.943642	login	0
Q8I4BCG8359Y	PNEU-6888059	778640	2026-06-17 05:27:43.617984	t	2026-06-17 05:22:43.679049	login	0
CVCPD20A7RCX	PNEU-6888059	995008	2026-06-17 06:12:42.346329	f	2026-06-17 06:07:42.495133	login	0
726I6S0EOF2M	PNEU-6888059	137224	2026-06-17 06:14:39.357678	f	2026-06-17 06:09:39.362238	login	0
8PZUIN0F5C4V	PNEU-6888059	225324	2026-06-17 06:14:41.465491	t	2026-06-17 06:09:41.469276	login	0
OTMDLI0D9K7E	PNEU-6888059	568875	2026-06-17 13:36:10.904686	f	2026-06-17 13:31:10.978604	login	0
O1HTY54JHL0K	PNEU-6888059	178131	2026-06-17 13:37:30.514626	f	2026-06-17 13:32:30.516657	login	0
7Z4LR2ZZ2LRV	PNEU-6888059	653714	2026-06-17 13:38:17.557204	t	2026-06-17 13:33:17.557997	login	0
G7O0TF8BANM0	PNEU-6888059	902818	2026-06-17 14:43:43.251662	t	2026-06-17 14:38:43.259923	login	0
A1JNO6WD4OEY	PNEU-6888059	968933	2026-06-17 16:09:15.936428	t	2026-06-17 16:04:16.038989	login	0
UWG1EZSK2EJ0	PNEU-6888059	624498	2026-06-17 16:45:39.886028	t	2026-06-17 16:40:39.941582	login	0
489C3MJJXD8M	PNEU-6888059	583458	2026-06-17 17:54:16.335635	t	2026-06-17 17:49:16.362971	login	0
UXHE6ZU9WQDU	PNEU-6888059	796768	2026-06-17 19:50:04.994048	t	2026-06-17 19:45:05.004684	login	0
1HG3TJRU9S0C	PNEU-6888059	597770	2026-06-17 20:12:34.514035	t	2026-06-17 20:07:34.588898	login	0
Y2G6T79TLUUE	PNEU-6888059	788008	2026-06-18 16:21:14.526843	t	2026-06-18 16:16:14.562825	login	0
6DY0FDPRTZKN	PNEU-6888059	317150	2026-06-18 17:34:49.24315	t	2026-06-18 17:29:49.254757	login	0
12188ZWRGXOA	PNEU-6888059	499341	2026-06-18 18:39:01.608644	t	2026-06-18 18:34:01.62727	login	0
CENZP0A6BS8U	PNEU-3318326	582208	2026-06-18 19:50:51.250583	t	2026-06-18 19:45:51.257994	login	0
M2P2THKBV5RN	PNEU-6888059	191895	2026-06-19 19:57:27.37174	t	2026-06-19 19:52:27.374514	login	0
CX77CX50NH8Y	PNEU-6888059	728664	2026-06-23 11:42:57.356455	t	2026-06-23 11:37:57.361936	login	0
7Q9NV2S278K9	PNEU-3318326	328532	2026-06-18 20:08:02.983102	t	2026-06-18 20:03:02.997321	reset	3
O7SS07WG6WAT	PNEU-3318326	650537	2026-06-18 20:09:45.571698	t	2026-06-18 20:04:45.574363	reset	0
O5CKQWWV9AM7	PNEU-3318326	194317	2026-06-18 20:16:07.643098	f	2026-06-18 20:11:07.655033	login	0
D5YM4ILXZZAW	PNEU-6888059	812081	2026-06-18 20:50:07.841168	t	2026-06-18 20:45:07.842975	login	0
CYVNB3PB9T92	PNEU-6888059	912755	2026-06-19 16:14:11.05593	t	2026-06-19 16:09:11.117004	login	0
QXI23PGO138O	PNEU-6888059	895167	2026-06-23 15:20:33.412472	f	2026-06-23 15:15:33.434455	login	0
Y0WUSIPYNYGI	PNEU-6888059	018912	2026-06-23 15:22:55.737826	t	2026-06-23 15:17:55.738974	login	0
4HHR29CUUTEQ	PNEU-6888059	932196	2026-06-19 17:48:54.243871	f	2026-06-19 17:43:54.29311	login	4
A0R8IAJ0L80A	PNEU-6888059	620005	2026-06-19 17:55:44.869305	f	2026-06-19 17:50:44.871586	login	0
QSN3GQCRF06S	PNEU-6888059	959136	2026-06-19 17:56:35.418074	f	2026-06-19 17:51:35.419986	login	0
8BJ6L7HZF7VN	PNEU-6888059	482350	2026-06-19 17:56:36.538179	f	2026-06-19 17:51:36.539196	login	0
TY182CQK05AA	PNEU-6888059	463790	2026-06-19 17:59:05.888253	t	2026-06-19 17:54:05.89864	login	0
3JY8Y6J4PFSM	PNEU-6888059	753310	2026-06-19 19:12:03.79163	t	2026-06-19 19:07:03.831695	login	0
THQZNZFEDO1B	PNEU-6888059	240892	2026-06-19 19:54:58.52562	f	2026-06-19 19:49:58.546108	login	0
X0OQ5OS9VUJ8	PNEU-6888059	127861	2026-07-02 11:04:37.410827	t	2026-07-02 10:59:37.461066	login	0
WVZO8A44KF42	PNEU-6888059	600782	2026-06-25 17:56:28.625085	f	2026-06-25 17:51:28.639375	login	0
Z5HKRB892JYU	PNEU-6888059	231232	2026-06-25 17:57:47.972257	t	2026-06-25 17:52:47.973144	login	0
X3MUS6FYPKGX	PNEU-3318326	410280	2026-06-18 20:12:36.225619	t	2026-06-18 20:07:36.226787	reset	0
E534T7WJZF20	PNEU-3318326	800057	2026-06-25 18:00:07.207445	t	2026-06-25 17:55:07.213599	reset	0
RNJVVM7AEBLE	PNEU-3318326	007387	2026-06-25 18:03:20.489024	f	2026-06-25 17:58:20.489753	reset	0
ZVE798LIZODG	PNEU-6888059	161332	2026-06-25 18:15:47.323608	t	2026-06-25 18:10:47.333284	login	0
P4Y7UUQBGRIU	PNEU-6888059	151521	2026-06-25 18:26:07.033722	t	2026-06-25 18:21:07.040635	login	0
DCNY7UQGXD8V	PNEU-6888059	725817	2026-06-26 19:12:32.991981	f	2026-06-26 19:07:33.174995	login	0
SSA2JJ98T2B1	PNEU-6888059	872327	2026-06-26 19:13:16.349458	t	2026-06-26 19:08:16.351464	login	0
2XQB1HUVCC2Q	PNEU-6888059	720671	2026-06-28 20:38:25.33985	t	2026-06-28 20:33:25.361104	login	0
29H5HE87EXDA	PNEU-1772790	456949	2026-07-01 22:47:04.699287	t	2026-07-01 22:42:04.70255	login	0
9M9HKJ1PWF9C	PNEU-1772790	295368	2026-07-02 08:14:13.058648	f	2026-07-02 08:09:13.115603	login	0
EI8GD6YHEW7P	PNEU-1772790	324468	2026-07-02 08:16:31.741209	f	2026-07-02 08:11:31.744253	login	0
S1H5WQA4M82X	PNEU-6888059	761310	2026-07-02 08:16:55.397704	f	2026-07-02 08:11:55.398633	login	0
AFPV0CBCESYH	PNEU-1772790	802459	2026-07-02 11:05:36.499952	t	2026-07-02 11:00:36.501446	login	0
H63HBYOSUT9X	PNEU-6888059	787446	2026-07-02 11:17:51.324464	t	2026-07-02 11:12:51.325338	login	0
X1FFNSMWFWH7	PNEU-1772790	628093	2026-07-02 08:17:13.512531	f	2026-07-02 08:12:13.513313	login	8
VTXTXKD4R5EK	PNEU-1772790	372530	2026-07-02 08:25:42.709195	t	2026-07-02 08:20:42.710379	login	0
E8H1X3QW76U5	PNEU-1772790	214433	2026-07-02 08:40:15.17348	t	2026-07-02 08:35:15.17558	login	0
24PF58UI4YOM	PNEU-1772790	220249	2026-07-02 09:31:38.433137	t	2026-07-02 09:26:38.453151	login	0
A6DPYT9YJLP1	PNEU-6888059	131421	2026-07-02 09:40:57.78718	t	2026-07-02 09:35:57.789119	login	0
Q8Q0O0C38L41	PNEU-6888059	541860	2026-07-02 11:20:00.87305	t	2026-07-02 11:15:00.875343	login	0
CW9JGTXMSDF6	PNEU-1772790	460407	2026-07-02 11:30:50.410075	t	2026-07-02 11:25:50.410627	login	0
76F1Q05YVUQ8	PNEU-6888059	230287	2026-07-02 11:33:10.764248	t	2026-07-02 11:28:10.766999	login	0
Z2GFRLW6XHS4	PNEU-1772790	751733	2026-07-02 13:07:44.731822	f	2026-07-02 13:02:44.745864	login	0
70LI34MBF3Z2	PNEU-1772790	567112	2026-07-02 13:08:07.489214	f	2026-07-02 13:03:07.491912	login	4
D1BYNYS734D4	PNEU-1772790	356715	2026-07-02 13:20:14.743259	t	2026-07-02 13:15:14.743916	reset	0
BO2BRMIEX8AM	PNEU-1772790	110059	2026-07-02 13:20:42.191139	f	2026-07-02 13:15:42.194603	reset	0
5YLEJ55GZ29R	PNEU-6888059	456762	2026-07-02 13:07:13.96639	t	2026-07-02 13:02:13.982263	reset	0
2V42NYZEBB2N	PNEU-6888059	283383	2026-07-02 21:41:42.262581	t	2026-07-02 21:36:42.277955	login	0
ON204JABX01K	PNEU-6888059	239499	2026-07-03 05:29:47.632529	t	2026-07-03 05:24:47.675462	reset	3
YSXI31W48QUZ	PNEU-1772790	635944	2026-07-03 06:35:54.389318	t	2026-07-03 06:30:54.497311	login	0
ABG9Z6Y7FUB9	PNEU-6888059	349728	2026-07-03 06:52:57.205862	t	2026-07-03 06:47:57.220773	login	0
EKU5ZWELNSQI	PNEU-1772790	517564	2026-07-03 06:54:26.728108	t	2026-07-03 06:49:26.729729	login	0
2L2U23GVUHQX	PNEU-6888059	209148	2026-07-03 06:58:19.496336	f	2026-07-03 06:53:19.497255	login	0
68W5BXBYZ2M2	PNEU-6888059	880667	2026-07-03 06:57:13.971799	t	2026-07-03 06:52:13.973909	reset	3
MO6IQYA48XII	PNEU-6888059	181759	2026-07-03 06:58:34.424227	t	2026-07-03 06:53:34.42638	reset	3
99KSHU20SKTY	PNEU-6888059	654730	2026-07-03 06:59:11.525817	t	2026-07-03 06:54:11.526841	reset	3
KYWPND9H20AO	PNEU-6888059	700363	2026-07-03 07:12:23.342679	f	2026-07-03 07:07:23.345678	login	0
UNKGHMIHFZXF	PNEU-6888059	521076	2026-07-03 07:14:56.601194	f	2026-07-03 07:09:56.604624	login	0
HUD9P1M1F6ZZ	PNEU-6888059	651149	2026-07-03 07:07:55.400905	t	2026-07-03 07:02:55.408143	reset	3
OO3MQIQWZD08	PNEU-6888059	237266	2026-07-03 07:16:37.784433	f	2026-07-03 07:11:37.786258	login	0
9YYIFEL3SK6R	PNEU-6888059	314720	2026-07-03 07:15:12.263354	t	2026-07-03 07:10:12.266631	reset	3
Q1CRC27J240L	PNEU-6888059	590896	2026-07-03 07:23:00.288927	f	2026-07-03 07:18:00.290091	login	0
YQM4D4YJCP5E	PNEU-6888059	632853	2026-07-03 07:22:23.939107	t	2026-07-03 07:17:23.95455	reset	3
7ORWD1QJSJP8	PNEU-6888059	452517	2026-07-03 07:28:38.655461	f	2026-07-03 07:23:38.656869	login	0
FMG6P0AD93SD	PNEU-6888059	623958	2026-07-03 07:28:04.941108	t	2026-07-03 07:23:04.942884	reset	3
OBUHA0UOXKCC	PNEU-6888059	108292	2026-07-03 07:38:44.840117	t	2026-07-03 07:33:44.843366	reset	3
GXJ39N3229J6	PNEU-6888059	171846	2026-07-04 13:04:27.514111	t	2026-07-04 12:59:27.519637	reset	3
10186KAYWW6Y	PNEU-6888059	719864	2026-07-04 13:13:32.886313	f	2026-07-04 13:08:32.889442	login	0
MS1W77CPD5DG	PNEU-6888059	152228	2026-07-04 13:14:21.384898	f	2026-07-04 13:09:21.387088	login	0
VRV88LYJ1PNU	PNEU-6888059	623389	2026-07-04 13:14:58.711936	t	2026-07-04 13:09:58.715558	login	0
\.


--
-- Data for Name: parametres; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.parametres (id, cle, valeur, updated_at) FROM stdin;
\.


--
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.patients (id, nom, prenom, civilite, date_naissance, sexe, groupe_sanguin, religion, telephone, email, adresse, profession, personne_a_contacter, telephone_urgence, allergies, antecedents, created_by, created_at, updated_at, deleted_at, deleted_by, aide_id, created_by_aide) FROM stdin;
LYJES29AB9IF	LESLIE	CORAILLE	Mme	2000-01-16	F	O+	catholique	+237 656066898	LeslieCoraille@gmail.com	Douala 	Comptable	\N	\N	["Aspirine", "anti-inflammatoire"]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": true, "hepatite_c": true, "tuberculose": false, "hypertension": true, "cancer_poumon": true, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "", "allergie_medicaments": "", "exposition_professionnelle": ""}	PNEU-3918267	2026-06-16 05:03:59.466702	2026-06-16 05:05:40.52133	\N	\N	\N	\N
SORB1HEPGCNB	LILA	HASSANE	Mme	2000-06-06	F	\N	musulman	656690987	\N	Douala , Bonamoussadi	Comptable	M. Houram kirash	650899076	[]	{"vih": false, "bpco": true, "alcool": false, "asthme": true, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": true, "hypertension": true, "cancer_poumon": true, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun", "allergie_medicaments": "Aspirine , anti-douleur", "exposition_professionnelle": ""}	PNEU-6888059	2026-06-16 20:47:37.093313	2026-06-16 20:48:33.745452	\N	\N	\N	\N
97Z8C325B8LH	YUYU	loli	M	1999-10-09	M	O-	autres	654342321	\N	yaounde	enseignant	\N	\N	["aucune"]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": true, "hypertension": true, "cancer_poumon": false, "duree_tabagisme": 7, "profession_risque": false, "cigarettes_par_jour": 7, "traitement_en_cours": "aucun ", "allergie_medicaments": "Aucun", "exposition_professionnelle": ""}	PNEU-6888059	2026-06-17 14:32:41.406339	2026-06-17 14:33:37.33434	\N	\N	AIDE-7829840	\N
CT7V6LZQO2SV	WENE	Sophie Claire	Mme	2005-03-13	F	B+	protestant	656789034	\N	Jouvence	Etudiante	Magne keke niam	656 876312	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun", "allergie_medicaments": "", "exposition_professionnelle": ""}	PNEU-6888059	2026-06-18 16:41:03.797765	2026-06-18 16:41:03.969301	\N	\N	\N	\N
MQO58PFGVZLC	WENE	Sophie Claire	Mme	2005-03-13	F	B+	protestant	656789034	\N	Jouvence	Etudiante	Magne keke niam	656 876312	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun", "allergie_medicaments": "", "exposition_professionnelle": ""}	PNEU-6888059	2026-06-18 16:41:03.813522	2026-06-18 16:41:03.97054	\N	\N	\N	\N
CDM985JJ78RJ	UYRRYIU	,jhgm	Mme	2000-10-23	F	AB+	musulman	652541423	\N	douala	mineur	hellllo	678998877	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": true, "diabete": false, "typhoide": true, "paludisme": true, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "", "allergie_medicaments": "", "exposition_professionnelle": ""}	PNEU-6888059	2026-06-18 16:44:51.712951	2026-06-18 16:45:05.719778	\N	\N	\N	\N
VUDFTD98XREM	RIKA	NINA Thomsom	M	1999-03-03	M	A-	temoin_jehovah	6 56 61 67 89	\N	Rue TWEEEL	Enseignante	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": false, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "aucun ", "allergie_medicaments": "aucun ", "exposition_professionnelle": ""}	PNEU-6888059	2026-06-18 18:12:39.12734	2026-06-18 18:12:39.476572	\N	\N	\N	\N
DGCOG3YQNGWM	STIRFF	Hibrahim	M	1989-09-13	M	AB-	musulman	6 56 34 21 45	hibrahimstirff@gmail.com	Extreme-Nord , nourrah	Commecant	\N	\N	["Arachide", "huile rouge"]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": true, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": "Aucun", "allergie_medicaments": "Aucun", "exposition_professionnelle": ""}	PNEU-1772790	2026-07-02 08:30:35.895835	2026-07-02 08:36:55.651157	\N	\N	AIDE-5828352	AIDE-5828352
H2XSG6PROW2B	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 14:19:44.300182	2026-07-08 14:19:44.542635	\N	\N	\N	\N
Q7D9ARPMBNWG	KELIEY	BRUNO	M	1992-03-04	M	O-	temoin_jehovah	645567687	brunokeliey@gmail.com	Douala	Agriculteur	\N	\N	["arachide", "peniceline"]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "prochain_suivi": "2026-07-08", "duree_tabagisme": 0, "profession_risque": true, "cigarettes_par_jour": 0, "traitement_en_cours": "Aucun", "allergie_medicaments": "arachide , peniceline", "exposition_professionnelle": ""}	PNEU-6888059	2026-06-25 18:07:49.852467	2026-06-25 18:31:00.328657	\N	\N	AIDE-5375941	AIDE-5375941
3WDN51B9ID8L	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 21:31:23.238368	2026-07-08 21:31:23.504419	\N	\N	\N	\N
KYQ5H18K2J6A	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 14:19:44.783846	2026-07-08 14:19:45.097576	\N	\N	\N	\N
OAJWRB9JDMLL	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 21:31:23.734913	2026-07-08 21:31:24.046543	\N	\N	\N	\N
6SG43ENX8UFN	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 21:37:23.512109	2026-07-08 21:37:23.813331	\N	\N	\N	\N
Q8RYBFYTMZP0	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 21:37:24.4805	2026-07-08 21:37:24.736829	\N	\N	\N	\N
DJ29ZR3V6O0Y	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 21:38:06.52578	2026-07-08 21:38:06.924854	\N	\N	\N	\N
AXWG7VQ76BBU	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-09 10:33:25.820611	2026-07-09 10:33:26.022903	\N	\N	\N	\N
PDT4ISG0HHSS	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 21:38:07.643807	2026-07-08 21:38:07.919322	\N	\N	\N	\N
7CEO9TIE3HWK	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 21:43:53.491817	2026-07-08 21:43:53.882942	\N	\N	\N	\N
OH83J7BC5FNG	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-09 11:17:30.24406	2026-07-09 11:17:30.439056	\N	\N	\N	\N
ET6GSOBK5I0I	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 21:43:54.64604	2026-07-08 21:43:54.942006	\N	\N	\N	\N
489MI5ZW3VIW	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 22:15:13.758631	2026-07-08 22:15:14.133297	\N	\N	\N	\N
HKXMFGMWS2AK	BENTEST	Alice-M	Mme	\N	F	\N	\N	+237600000099	\N	\N	\N	\N	\N	[]	{"diabete": false, "hypertension": true}	PNEU-8414821	2026-07-09 11:14:59.188211	2026-07-09 11:14:59.388498	\N	\N	AIDE-2609616	AIDE-2609616
L295VBU0Q3A1	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 22:15:14.875642	2026-07-08 22:15:15.171716	\N	\N	\N	\N
6NR18SGF5RDV	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 22:21:53.913799	2026-07-08 22:21:54.156812	\N	\N	\N	\N
BCT82NL034GE	BENTEST	Alice-M	Mme	\N	F	\N	\N	+237600000099	\N	\N	\N	\N	\N	[]	{"diabete": false, "hypertension": true}	PNEU-8414821	2026-07-09 11:15:24.87926	2026-07-09 11:15:25.107837	\N	\N	AIDE-2609616	AIDE-2609616
CNZ5NKNRIJ27	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 22:21:55.236803	2026-07-08 22:21:55.467241	\N	\N	\N	\N
5MAKB9OPJ5B3	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-08 22:23:28.656196	2026-07-08 22:23:28.886846	\N	\N	\N	\N
BD4PYCC2705B	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-09 11:15:25.916006	2026-07-09 11:15:26.039149	\N	\N	\N	\N
UFEV9MBWHCWN	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-08 22:23:30.178937	2026-07-08 22:23:30.435966	\N	\N	\N	\N
2OKLME8F1Z2T	BENTEST	Alice-M	Mme	\N	F	\N	\N	+237600000099	\N	\N	\N	\N	\N	[]	{"diabete": false, "hypertension": true}	PNEU-8414821	2026-07-09 10:33:23.170886	2026-07-09 10:33:23.375359	\N	\N	AIDE-2609616	AIDE-2609616
AI15S1DRRWDF	MARTIN	Sophie	Mme	\N	F	\N	\N	+237600000002	\N	\N	\N	\N	\N	[]	{"vih": false, "bpco": false, "alcool": false, "asthme": false, "covid19": false, "diabete": true, "typhoide": false, "paludisme": false, "tabagisme": "non-fumeur", "hepatite_b": false, "hepatite_c": false, "tuberculose": false, "hypertension": false, "cancer_poumon": false, "duree_tabagisme": 0, "profession_risque": false, "cigarettes_par_jour": 0, "traitement_en_cours": null, "allergie_medicaments": null, "exposition_professionnelle": null}	PNEU-8414821	2026-07-09 10:33:24.852776	2026-07-09 10:33:25.028871	\N	\N	\N	\N
AL4Q7NBH9RL0	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-09 11:17:31.319292	2026-07-09 11:17:31.555879	\N	\N	\N	\N
SY6XXQE5NJKG	DUPONT	Jean-Pierre	M	\N	M	\N	\N	+237600000001	\N	\N	\N	\N	\N	[]	{}	PNEU-8414821	2026-07-09 11:15:26.606501	2026-07-09 11:15:26.781683	\N	\N	\N	\N
F7D66KKRU26D	BENTEST	Alice-M	Mme	\N	F	\N	\N	+237600000099	\N	\N	\N	\N	\N	[]	{"diabete": false, "hypertension": true}	PNEU-8414821	2026-07-09 11:17:28.934403	2026-07-09 11:17:29.290511	\N	\N	AIDE-2609616	AIDE-2609616
\.


--
-- Data for Name: publications; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.publications (id, communaute_id, auteur_id, consultation_id, titre, contenu, type, tags, nb_commentaires, nb_reactions, created_at, ressource_id) FROM stdin;
LE3ISCR74GNE	\N	PNEU-6888059	\N	mmmmm	hhhhh	discussion	[]	1	0	2026-07-02 11:19:54.08855	\N
F9T8W1RFKZT6	\N	PNEU-1772790	\N	COPD	JJJJJJ	cas_clinique	[]	0	0	2026-07-03 06:32:33.521276	RES-3959912
FG3S0881FFO1	\N	PNEU-6888059	\N	j'aimerais obtenir le dossier du patient Hibrahim stirff	hhhhhh	discussion	[]	0	0	2026-07-03 06:51:25.627183	\N
9I8HV06QQ44P	\N	PNEU-1772790	\N	nn	mm	cas_clinique	[]	0	0	2026-07-03 06:58:05.396738	RES-1994837
8C1409U6CU0L	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	0	2026-07-08 21:37:24.91445	\N
JG62NWAVCFTU	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	0	2026-07-08 21:38:08.0716	\N
P724CQJ3YYX6	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	1	2026-07-08 21:43:55.219963	\N
UR9TQU74SFCA	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	1	2026-07-08 22:15:15.3612	\N
KO28C36UAMJ7	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	1	2026-07-08 22:21:55.643333	\N
5CMZY4HG8SHH	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	1	2026-07-08 22:23:30.619553	\N
17RXW3HTO1O3	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	1	2026-07-09 10:33:26.16339	\N
S05MT84X2SXV	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	1	2026-07-09 11:15:26.940702	\N
GQTA5SS55RJZ	\N	PNEU-8414821	\N	Test publication pneumonie	Discussion sur la pneumonie bactérienne.	discussion	["pneumonie", "bacterie"]	1	1	2026-07-09 11:17:31.742601	\N
\.


--
-- Data for Name: questions_admin; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.questions_admin (id, medecin_id, titre, message, statut, reponse, created_at, repondu_at) FROM stdin;
QST-JWDUVWEIR2	PNEU-6888059	jjjrjejrge	ewqvwqd	publiee_faq	jjjjj	2026-06-19 16:09:59.173389	2026-06-19 16:11:28.222759
QST-50AWM4WKNI	PNEU-6888059	Comment archiver un document patient ?	J'ai essaye d'appuie sur le bouton archive mais rien ne donne	publiee_faq	Veiller double cliquer sur le bouton.Et tout fonctionnera comme il faut.	2026-06-18 17:04:38.830121	2026-06-23 16:49:12.392692
QST-1ZVQ6BVV0K	PNEU-6888059	nn ,m ,m m,dsvsfv	wvwevqewvveVE; d;vm x/	publiee_faq	kdbv vrbdhhhhhdhwhrhdhvbrj wrdv	2026-06-17 16:05:07.088366	2026-06-23 16:49:13.57163
QST-O27JWEKI3I	PNEU-6888059	Comment publier?	ghhkwkkbecw	publiee_faq	gggggg	2026-06-25 18:37:02.018661	2026-06-25 18:37:33.798175
QST-VUNYQFZ1AO	PNEU-6888059	jjj	jjjjjjjjjjjjjjjjjjjjjjjjjjjjjhahhHWY2D1YT	publiee_faq	kkkk	2026-06-28 20:35:10.08159	2026-06-28 20:52:52.775661
QST-1ZVMSLNR3F	PNEU-6888059	uu	ookuyrte	publiee_faq	ll	2026-06-28 21:19:14.185638	2026-06-28 21:19:54.747712
QST-NYZOVCHNDY	PNEU-1772790	jjjjj	jjjj	publiee_faq	mmmm	2026-07-01 23:07:03.519465	2026-07-01 23:07:44.333032
QST-FS9H5A8JN9	PNEU-8414821	Comment modifier mon profil ?	Je n'arrive pas à modifier ma photo de profil.	en_attente	\N	2026-07-08 22:21:55.798329	\N
QST-51FS63C6QO	PNEU-8414821	Comment modifier mon profil ?	Je n'arrive pas à modifier ma photo de profil.	en_attente	\N	2026-07-08 22:23:30.785917	\N
QST-0HSL939YGO	PNEU-8414821	Comment modifier mon profil ?	Je n'arrive pas à modifier ma photo de profil.	en_attente	\N	2026-07-09 10:33:26.293984	\N
QST-SGE1KQQ07N	PNEU-8414821	Comment modifier mon profil ?	Je n'arrive pas à modifier ma photo de profil.	en_attente	\N	2026-07-09 11:15:27.027603	\N
QST-UP3DRBIDXG	PNEU-8414821	Comment modifier mon profil ?	Je n'arrive pas à modifier ma photo de profil.	en_attente	\N	2026-07-09 11:17:32.139468	\N
\.


--
-- Data for Name: questions_medecins; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.questions_medecins (id, medecin_id, question, categorie, statut, reponse, repondu_par, repondu_le, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: reactions; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.reactions (id, publication_id, medecin_id, type) FROM stdin;
CGFK8B71C7SA	P724CQJ3YYX6	PNEU-8414821	utile
ZPM5VBCMJFSR	UR9TQU74SFCA	PNEU-8414821	utile
5D0NSZHY2OOT	KO28C36UAMJ7	PNEU-8414821	utile
DYW8QAK7G3ZA	5CMZY4HG8SHH	PNEU-8414821	utile
2YBPG7FWOEU6	17RXW3HTO1O3	PNEU-8414821	utile
B6OZCFJM3E99	S05MT84X2SXV	PNEU-8414821	utile
E9NK3MDJIW3V	GQTA5SS55RJZ	PNEU-8414821	utile
\.


--
-- Data for Name: requetes_medecins; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.requetes_medecins (id, medecin_id, nom_medecin, email_medecin, titre, categorie, description, statut, action_admin, reponse_admin, repondu_par, repondu_le, created_at, traite_le) FROM stdin;
REQ-IGNWEA4M1W	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-09 11:17:32.341922	\N
REQ-UJYEBRX1PP	PNEU-1772790	Dr Brithnette DeLamoir	mayadisney76+5@gmail.com	jjjjdcjj : IA	autre	Le modele ne cesse de repondre de maniere bizarre	resolu	Problème en cours de résolution	Problème en cours de résolution	OBG8EN6SN1OY	2026-07-01 23:17:31.518556	2026-07-01 23:14:39.448678	2026-07-01 23:17:31.518556
REQ-1LUMJFBIC2	PNEU-6888059	Mme GRILL Sydney Maya	mayadisney76@gmail.com	kkk	autre	kkkk	en_attente	\N	\N	\N	\N	2026-07-02 11:23:45.147049	\N
REQ-A7AM6YTGQK	PNEU-6888059	Dr. GRILL Sydney Maya	mayadisney76@gmail.com	Demande de déblocage de compte	probleme_acces	Mon compte a été bloqué automatiquement suite à plusieurs tentatives OTP incorrectes.\nMotif du blocage : Compte bloqué – 3 tentatives OTP incorrectes lors de la réinitialisation du mot de passe.\nJe demande le rétablissement de mon accès à la plateforme PneumoIA.	resolu	Compte débloqué	Votre compte est déjà actif. Cette demande a été clôturée par l'administrateur.	OBG8EN6SN1OY	2026-07-03 07:55:15.874861	2026-07-03 07:34:34.972407	2026-07-03 07:55:15.874861
REQ-GKJO6Z5STJ	PNEU-6888059	Dr. GRILL Sydney Maya	mayadisney76@gmail.com	Demande de déblocage de compte	probleme_acces	Mon compte a été bloqué automatiquement suite à plusieurs tentatives OTP incorrectes.\nMotif du blocage : Compte bloqué – 3 tentatives OTP incorrectes lors de la réinitialisation du mot de passe.\nJe demande le rétablissement de mon accès à la plateforme PneumoIA.	resolu	Compte débloqué	Votre compte est déjà actif. Cette demande a été clôturée par l'administrateur.	OBG8EN6SN1OY	2026-07-03 07:55:15.876051	2026-07-03 07:34:34.961486	2026-07-03 07:55:15.876051
REQ-MJDCXG9UGL	PNEU-6888059	Dr. GRILL Sydney Maya	mayadisney76@gmail.com	Demande de déblocage de compte	probleme_acces	Mon compte a été bloqué automatiquement suite à plusieurs tentatives OTP incorrectes.\nMotif du blocage : Compte bloqué – 3 tentatives OTP incorrectes lors de la réinitialisation du mot de passe.\nJe demande le rétablissement de mon accès à la plateforme PneumoIA.	resolu	Compte débloqué	Votre compte a été réactivé par l'administrateur. Vous pouvez vous reconnecter.	OBG8EN6SN1OY	2026-07-04 13:07:38.268351	2026-07-04 13:06:34.982919	2026-07-04 13:07:38.268351
REQ-8JT11KTECJ	PNEU-6888059	Dr. GRILL Sydney Maya	mayadisney76@gmail.com	Demande de déblocage de compte	probleme_acces	Mon compte a été bloqué automatiquement suite à plusieurs tentatives OTP incorrectes.\nMotif du blocage : Compte bloqué – 3 tentatives OTP incorrectes lors de la réinitialisation du mot de passe.\nJe demande le rétablissement de mon accès à la plateforme PneumoIA.	resolu	Compte débloqué	Votre compte a été réactivé par l'administrateur. Vous pouvez vous reconnecter.	OBG8EN6SN1OY	2026-07-04 13:07:38.269408	2026-07-04 13:06:34.981798	2026-07-04 13:07:38.269408
REQ-24PNUR1J1A	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-08 21:37:25.091871	\N
REQ-M2BP9VMXHR	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-08 21:38:08.215924	\N
REQ-U9K0KLM9QF	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-08 21:43:55.447564	\N
REQ-5DBL7NK770	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-08 22:15:15.519209	\N
REQ-HUK9BOV0HR	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-08 22:21:55.919724	\N
REQ-SN7MPAH14S	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-08 22:23:30.907748	\N
REQ-KWM2300HT0	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-09 10:33:26.423206	\N
REQ-10QG71JK2S	PNEU-8414821	Dr. Docteur TEST	docteur.test@pneumoia.com	Problème de connexion	probleme_acces	Je n'arrive pas à accéder au module de diagnostic.	en_attente	\N	\N	\N	\N	2026-07-09 11:15:27.094331	\N
\.


--
-- Data for Name: ressources_medicales; Type: TABLE DATA; Schema: public; Owner: pneumo_user
--

COPY public.ressources_medicales (id, medecin_id, titre, resume, contenu, pdf_url, pathologie, tags, niveau, nb_telechargements, nb_vues, publie, created_at, updated_at) FROM stdin;
RES-1866265	PNEU-6888059	Sysmtome d'asthme semblable a un diabete	J'ai recu un patient qui prentait tout ls sysmtome d'une personne attente d'un diabete , mais si on regarde de point du vu eloigne ce patient souffre d'asthme.		\N	Asthme	[]	Spécialiste	0	1	t	2026-06-17 05:32:46.591241	2026-06-25 19:08:34.402847
RES-1994837	PNEU-1772790	nn	mm	jjj	\N	Tuberculose	[]	3ème année	0	0	t	2026-07-03 06:58:05.389298	\N
RES-3959912	PNEU-1772790	COPD	JJJJJJ	WQXjllvaW	uploads\\ressources\\RES-3959912\\document.pdf	Tuberculose	[]	3ème année	1	1	t	2026-07-03 06:32:24.28765	2026-07-03 07:16:10.09628
\.


--
-- Name: acces_patient acces_patient_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.acces_patient
    ADD CONSTRAINT acces_patient_pkey PRIMARY KEY (id);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- Name: aides_soignants aides_soignants_email_key; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.aides_soignants
    ADD CONSTRAINT aides_soignants_email_key UNIQUE (email);


--
-- Name: aides_soignants aides_soignants_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.aides_soignants
    ADD CONSTRAINT aides_soignants_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: avis_medecins avis_medecins_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.avis_medecins
    ADD CONSTRAINT avis_medecins_pkey PRIMARY KEY (id);


--
-- Name: avis_patient avis_patient_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.avis_patient
    ADD CONSTRAINT avis_patient_pkey PRIMARY KEY (id);


--
-- Name: avis avis_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.avis
    ADD CONSTRAINT avis_pkey PRIMARY KEY (id);


--
-- Name: cas_cliniques_publics cas_cliniques_publics_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.cas_cliniques_publics
    ADD CONSTRAINT cas_cliniques_publics_pkey PRIMARY KEY (id);


--
-- Name: commentaires commentaires_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.commentaires
    ADD CONSTRAINT commentaires_pkey PRIMARY KEY (id);


--
-- Name: communautes communautes_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.communautes
    ADD CONSTRAINT communautes_pkey PRIMARY KEY (id);


--
-- Name: consultations consultations_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.consultations
    ADD CONSTRAINT consultations_pkey PRIMARY KEY (id);


--
-- Name: diagnostics_ia diagnostics_ia_consultation_id_key; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.diagnostics_ia
    ADD CONSTRAINT diagnostics_ia_consultation_id_key UNIQUE (consultation_id);


--
-- Name: diagnostics_ia diagnostics_ia_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.diagnostics_ia
    ADD CONSTRAINT diagnostics_ia_pkey PRIMARY KEY (id);


--
-- Name: documents_medecin documents_medecin_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.documents_medecin
    ADD CONSTRAINT documents_medecin_pkey PRIMARY KEY (id);


--
-- Name: faq_publiees faq_publiees_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.faq_publiees
    ADD CONSTRAINT faq_publiees_pkey PRIMARY KEY (id);


--
-- Name: feedbacks_ia feedbacks_ia_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.feedbacks_ia
    ADD CONSTRAINT feedbacks_ia_pkey PRIMARY KEY (id);


--
-- Name: likes_commentaires likes_commentaires_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.likes_commentaires
    ADD CONSTRAINT likes_commentaires_pkey PRIMARY KEY (id);


--
-- Name: likes_messages_equipe likes_messages_equipe_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.likes_messages_equipe
    ADD CONSTRAINT likes_messages_equipe_pkey PRIMARY KEY (id);


--
-- Name: medecins medecins_code_referent_key; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_code_referent_key UNIQUE (code_referent);


--
-- Name: medecins medecins_email_key; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_email_key UNIQUE (email);


--
-- Name: medecins medecins_numero_rpps_key; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_numero_rpps_key UNIQUE (numero_rpps);


--
-- Name: medecins medecins_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_pkey PRIMARY KEY (id);


--
-- Name: membres_communaute membres_communaute_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.membres_communaute
    ADD CONSTRAINT membres_communaute_pkey PRIMARY KEY (id);


--
-- Name: messages_equipe messages_equipe_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.messages_equipe
    ADD CONSTRAINT messages_equipe_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: otp_codes otp_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.otp_codes
    ADD CONSTRAINT otp_codes_pkey PRIMARY KEY (id);


--
-- Name: parametres parametres_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.parametres
    ADD CONSTRAINT parametres_pkey PRIMARY KEY (id);


--
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- Name: publications publications_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.publications
    ADD CONSTRAINT publications_pkey PRIMARY KEY (id);


--
-- Name: questions_admin questions_admin_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.questions_admin
    ADD CONSTRAINT questions_admin_pkey PRIMARY KEY (id);


--
-- Name: questions_medecins questions_medecins_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.questions_medecins
    ADD CONSTRAINT questions_medecins_pkey PRIMARY KEY (id);


--
-- Name: reactions reactions_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_pkey PRIMARY KEY (id);


--
-- Name: requetes_medecins requetes_medecins_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.requetes_medecins
    ADD CONSTRAINT requetes_medecins_pkey PRIMARY KEY (id);


--
-- Name: ressources_medicales ressources_medicales_pkey; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.ressources_medicales
    ADD CONSTRAINT ressources_medicales_pkey PRIMARY KEY (id);


--
-- Name: acces_patient uq_acces_medecin_patient; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.acces_patient
    ADD CONSTRAINT uq_acces_medecin_patient UNIQUE (patient_id, medecin_demandeur_id);


--
-- Name: likes_commentaires uq_like_com_auteur; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.likes_commentaires
    ADD CONSTRAINT uq_like_com_auteur UNIQUE (commentaire_id, auteur_id);


--
-- Name: likes_messages_equipe uq_like_msg_auteur; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.likes_messages_equipe
    ADD CONSTRAINT uq_like_msg_auteur UNIQUE (message_id, auteur_id);


--
-- Name: membres_communaute uq_membre_communaute; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.membres_communaute
    ADD CONSTRAINT uq_membre_communaute UNIQUE (communaute_id, medecin_id);


--
-- Name: reactions uq_reaction_medecin_publication; Type: CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT uq_reaction_medecin_publication UNIQUE (publication_id, medecin_id);


--
-- Name: idx_patients_aide; Type: INDEX; Schema: public; Owner: pneumo_user
--

CREATE INDEX idx_patients_aide ON public.patients USING btree (created_by_aide);


--
-- Name: ix_admins_email; Type: INDEX; Schema: public; Owner: pneumo_user
--

CREATE UNIQUE INDEX ix_admins_email ON public.admins USING btree (email);


--
-- Name: ix_admins_phone; Type: INDEX; Schema: public; Owner: pneumo_user
--

CREATE INDEX ix_admins_phone ON public.admins USING btree (phone);


--
-- Name: ix_parametres_cle; Type: INDEX; Schema: public; Owner: pneumo_user
--

CREATE UNIQUE INDEX ix_parametres_cle ON public.parametres USING btree (cle);


--
-- Name: acces_patient acces_patient_medecin_demandeur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.acces_patient
    ADD CONSTRAINT acces_patient_medecin_demandeur_id_fkey FOREIGN KEY (medecin_demandeur_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: acces_patient acces_patient_medecin_proprietaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.acces_patient
    ADD CONSTRAINT acces_patient_medecin_proprietaire_id_fkey FOREIGN KEY (medecin_proprietaire_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: acces_patient acces_patient_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.acces_patient
    ADD CONSTRAINT acces_patient_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id) ON DELETE CASCADE;


--
-- Name: aides_soignants aides_soignants_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.aides_soignants
    ADD CONSTRAINT aides_soignants_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: audit_logs audit_logs_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE SET NULL;


--
-- Name: avis avis_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.avis
    ADD CONSTRAINT avis_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: avis_medecins avis_medecins_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.avis_medecins
    ADD CONSTRAINT avis_medecins_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: avis_patient avis_patient_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.avis_patient
    ADD CONSTRAINT avis_patient_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: avis_patient avis_patient_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.avis_patient
    ADD CONSTRAINT avis_patient_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id) ON DELETE CASCADE;


--
-- Name: cas_cliniques_publics cas_cliniques_publics_auteur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.cas_cliniques_publics
    ADD CONSTRAINT cas_cliniques_publics_auteur_id_fkey FOREIGN KEY (auteur_id) REFERENCES public.medecins(id) ON DELETE SET NULL;


--
-- Name: commentaires commentaires_auteur_aide_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.commentaires
    ADD CONSTRAINT commentaires_auteur_aide_id_fkey FOREIGN KEY (auteur_aide_id) REFERENCES public.aides_soignants(id) ON DELETE RESTRICT;


--
-- Name: commentaires commentaires_auteur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.commentaires
    ADD CONSTRAINT commentaires_auteur_id_fkey FOREIGN KEY (auteur_id) REFERENCES public.medecins(id) ON DELETE RESTRICT;


--
-- Name: commentaires commentaires_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.commentaires
    ADD CONSTRAINT commentaires_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.commentaires(id) ON DELETE CASCADE;


--
-- Name: commentaires commentaires_publication_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.commentaires
    ADD CONSTRAINT commentaires_publication_id_fkey FOREIGN KEY (publication_id) REFERENCES public.publications(id) ON DELETE CASCADE;


--
-- Name: communautes communautes_createur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.communautes
    ADD CONSTRAINT communautes_createur_id_fkey FOREIGN KEY (createur_id) REFERENCES public.medecins(id) ON DELETE RESTRICT;


--
-- Name: consultations consultations_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.consultations
    ADD CONSTRAINT consultations_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE RESTRICT;


--
-- Name: consultations consultations_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.consultations
    ADD CONSTRAINT consultations_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id) ON DELETE RESTRICT;


--
-- Name: diagnostics_ia diagnostics_ia_consultation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.diagnostics_ia
    ADD CONSTRAINT diagnostics_ia_consultation_id_fkey FOREIGN KEY (consultation_id) REFERENCES public.consultations(id) ON DELETE CASCADE;


--
-- Name: documents_medecin documents_medecin_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.documents_medecin
    ADD CONSTRAINT documents_medecin_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: faq_publiees faq_publiees_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.faq_publiees
    ADD CONSTRAINT faq_publiees_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.admins(id) ON DELETE SET NULL;


--
-- Name: feedbacks_ia feedbacks_ia_diagnostic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.feedbacks_ia
    ADD CONSTRAINT feedbacks_ia_diagnostic_id_fkey FOREIGN KEY (diagnostic_id) REFERENCES public.diagnostics_ia(id) ON DELETE CASCADE;


--
-- Name: feedbacks_ia feedbacks_ia_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.feedbacks_ia
    ADD CONSTRAINT feedbacks_ia_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: likes_commentaires likes_commentaires_commentaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.likes_commentaires
    ADD CONSTRAINT likes_commentaires_commentaire_id_fkey FOREIGN KEY (commentaire_id) REFERENCES public.commentaires(id) ON DELETE CASCADE;


--
-- Name: likes_messages_equipe likes_messages_equipe_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.likes_messages_equipe
    ADD CONSTRAINT likes_messages_equipe_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages_equipe(id) ON DELETE CASCADE;


--
-- Name: medecins medecins_rejete_par_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_rejete_par_fkey FOREIGN KEY (rejete_par) REFERENCES public.admins(id) ON DELETE SET NULL;


--
-- Name: medecins medecins_supprime_par_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_supprime_par_fkey FOREIGN KEY (supprime_par) REFERENCES public.admins(id) ON DELETE SET NULL;


--
-- Name: medecins medecins_suspension_par_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_suspension_par_fkey FOREIGN KEY (suspension_par) REFERENCES public.admins(id) ON DELETE SET NULL;


--
-- Name: medecins medecins_valide_par_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.medecins
    ADD CONSTRAINT medecins_valide_par_fkey FOREIGN KEY (valide_par) REFERENCES public.admins(id) ON DELETE SET NULL;


--
-- Name: membres_communaute membres_communaute_communaute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.membres_communaute
    ADD CONSTRAINT membres_communaute_communaute_id_fkey FOREIGN KEY (communaute_id) REFERENCES public.communautes(id) ON DELETE CASCADE;


--
-- Name: membres_communaute membres_communaute_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.membres_communaute
    ADD CONSTRAINT membres_communaute_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: messages_equipe messages_equipe_auteur_aide_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.messages_equipe
    ADD CONSTRAINT messages_equipe_auteur_aide_id_fkey FOREIGN KEY (auteur_aide_id) REFERENCES public.aides_soignants(id) ON DELETE SET NULL;


--
-- Name: messages_equipe messages_equipe_auteur_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.messages_equipe
    ADD CONSTRAINT messages_equipe_auteur_medecin_id_fkey FOREIGN KEY (auteur_medecin_id) REFERENCES public.medecins(id) ON DELETE SET NULL;


--
-- Name: messages_equipe messages_equipe_medecin_referent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.messages_equipe
    ADD CONSTRAINT messages_equipe_medecin_referent_id_fkey FOREIGN KEY (medecin_referent_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: messages_equipe messages_equipe_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.messages_equipe
    ADD CONSTRAINT messages_equipe_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.messages_equipe(id) ON DELETE CASCADE;


--
-- Name: otp_codes otp_codes_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.otp_codes
    ADD CONSTRAINT otp_codes_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: patients patients_aide_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_aide_id_fkey FOREIGN KEY (aide_id) REFERENCES public.aides_soignants(id) ON DELETE SET NULL;


--
-- Name: patients patients_created_by_aide_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_created_by_aide_fkey FOREIGN KEY (created_by_aide) REFERENCES public.aides_soignants(id) ON DELETE SET NULL;


--
-- Name: patients patients_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.medecins(id) ON DELETE SET NULL;


--
-- Name: patients patients_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.medecins(id) ON DELETE SET NULL;


--
-- Name: publications publications_auteur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.publications
    ADD CONSTRAINT publications_auteur_id_fkey FOREIGN KEY (auteur_id) REFERENCES public.medecins(id) ON DELETE RESTRICT;


--
-- Name: publications publications_communaute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.publications
    ADD CONSTRAINT publications_communaute_id_fkey FOREIGN KEY (communaute_id) REFERENCES public.communautes(id) ON DELETE CASCADE;


--
-- Name: publications publications_consultation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.publications
    ADD CONSTRAINT publications_consultation_id_fkey FOREIGN KEY (consultation_id) REFERENCES public.consultations(id) ON DELETE SET NULL;


--
-- Name: publications publications_ressource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.publications
    ADD CONSTRAINT publications_ressource_id_fkey FOREIGN KEY (ressource_id) REFERENCES public.ressources_medicales(id) ON DELETE SET NULL;


--
-- Name: questions_admin questions_admin_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.questions_admin
    ADD CONSTRAINT questions_admin_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: questions_medecins questions_medecins_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.questions_medecins
    ADD CONSTRAINT questions_medecins_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE SET NULL;


--
-- Name: questions_medecins questions_medecins_repondu_par_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.questions_medecins
    ADD CONSTRAINT questions_medecins_repondu_par_fkey FOREIGN KEY (repondu_par) REFERENCES public.admins(id) ON DELETE SET NULL;


--
-- Name: reactions reactions_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- Name: reactions reactions_publication_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_publication_id_fkey FOREIGN KEY (publication_id) REFERENCES public.publications(id) ON DELETE CASCADE;


--
-- Name: ressources_medicales ressources_medicales_medecin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pneumo_user
--

ALTER TABLE ONLY public.ressources_medicales
    ADD CONSTRAINT ressources_medicales_medecin_id_fkey FOREIGN KEY (medecin_id) REFERENCES public.medecins(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 8R3ilzTlhSaSzsdSC8ablWktObZLD3Fdy2Xaw1xyEhReuXlHCGX1g33fIru9ih5

