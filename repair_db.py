"""
Script de reparation des donnees corrompues (caracteres accentues -> ??)
A executer dans le container : docker cp repair_db.py pneumoia_backend:/tmp/ && docker exec pneumoia_backend python /tmp/repair_db.py
"""
import asyncio, sys, json
sys.path.insert(0, '/app')

# Tables de correspondance correctes (depuis le code actuel)
CRITERES = {
    "Pneumonia":         ["Infiltrat alveolaire au scanner", "Hypoxemie (O2 anormal)", "Anomalie des gaz du sang", "Debit expiratoire diminue", "Capacite vitale reduite"],
    "Asthma":            ["Obstruction bronchique reversible", "Antecedents d'asthme", "VEMS/CVF diminue", "Debit de pointe variable", "Reponse aux bronchodilatateurs"],
    "COPD":              ["Obstruction chronique des voies aeriennes", "FEV1/FVC < 0.70", "Tabagisme significatif", "Hyperinflation pulmonaire"],
    "Tuberculosis":      ["Toux chronique productive", "Sueurs nocturnes et amaigrissement", "Infiltrats apicaux au scanner", "Contexte epidemiologique"],
    "COVID-19":          ["Syndrome grippal avec fievre", "Atteinte pulmonaire bilaterale", "Hypoxemie progressive", "Scanner en verre depoli"],
    "Influenza":         ["Debut brutal avec fievre elevee", "Myalgies et arthralgies", "Signes respiratoires superieurs", "Contexte epidemique"],
    "Bronchitis":        ["Toux productive persistante", "Expectorations mucopurulentes", "Auscultation avec ronchi", "Absence d'infiltrat alveolaire"],
    "Lung Cancer":       ["Toux chronique hemoptoique", "Amaigrissement inexplique", "Masse pulmonaire au scanner", "Obstruction bronchique"],
    "Allergic Rhinitis": ["Rhinorrhee claire", "Eternuements en salves", "Obstruction nasale chronique", "Contexte allergique"],
    "Sinusitis":         ["Douleur sinusienne a la pression", "Obstruction nasale", "Secretions purulentes", "Opacite sinusienne"],
    "Cystic Fibrosis":   ["Toux productive chronique", "FVC et VEMS tres diminues", "Test de la sueur positif", "Colonisation bacterienne"],
    "Sleep Apnea":       ["Ronflements nocturnes", "Apnees observees", "Somnolence diurne", "Saturation nocturne diminuee"],
    "Pneumothorax":      ["Douleur thoracique brutale", "Dyspnee aigue", "Silence auscultatoire", "Hypoxemie soudaine"],
    "Common Cold":       ["Rhinorrhee et congestion nasale", "Legere fievre", "Toux seche moderee", "Evolution courte < 10 jours"],
}

# Les vraies valeurs avec accents (depuis diagnostics.py actuel)
CRITERES_CORRECT = {
    "Pneumonia":         ["Infiltrat alvéolaire au scanner", "Hypoxémie (O2 anormal)", "Anomalie des gaz du sang", "Débit expiratoire diminué", "Capacité vitale réduite"],
    "Asthma":            ["Obstruction bronchique réversible", "Antécédents d’asthme", "VEMS/CVF diminué", "Débit de pointe variable", "Réponse aux bronchodilatateurs"],
    "COPD":              ["Obstruction chronique des voies aériennes", "FEV1/FVC < 0.70", "Tabagisme significatif", "Hyperinflation pulmonaire"],
    "Tuberculosis":      ["Toux chronique productive", "Sueurs nocturnes et amaigrissement", "Infiltrats apicaux au scanner", "Contexte épidémiologique"],
    "COVID-19":          ["Syndrome grippal avec fièvre", "Atteinte pulmonaire bilatérale", "Hypoxémie progressive", "Scanner en verre dépoli"],
    "Influenza":         ["Début brutal avec fièvre élevée", "Myalgies et arthralgies", "Signes respiratoires supérieurs", "Contexte épidémique"],
    "Bronchitis":        ["Toux productive persistante", "Expectorations mucopurulentes", "Auscultation avec ronchi", "Absence d'infiltrat alvéolaire"],
    "Lung Cancer":       ["Toux chronique hémoptoïque", "Amaigrissement inexpliqué", "Masse pulmonaire au scanner", "Obstruction bronchique"],
    "Allergic Rhinitis": ["Rhinorrhée claire", "Éternuements en salves", "Obstruction nasale chronique", "Contexte allergique"],
    "Sinusitis":         ["Douleur sinusienne à la pression", "Obstruction nasale", "Sécrétions purulentes", "Opacité sinusienne"],
    "Cystic Fibrosis":   ["Toux productive chronique", "FVC et VEMS très diminués", "Test de la sueur positif", "Colonisation bactérienne"],
    "Sleep Apnea":       ["Ronflements nocturnes", "Apnées observées", "Somnolence diurne", "Saturation nocturne diminuée"],
    "Pneumothorax":      ["Douleur thoracique brutale", "Dyspnée aiguë", "Silence auscultatoire", "Hypoxémie soudaine"],
    "Common Cold":       ["Rhinorrhée et congestion nasale", "Légère fièvre", "Toux sèche modérée", "Évolution courte < 10 jours"],
}

RECOMMANDATIONS_CORRECT = {
    "Pneumonia":         ["Antibiothérapie adaptée (Amoxicilline 1g x 3/j - 7 jours)", "Surveillance saturation O2", "Hydratation abondante (>1.5L/jour)", "Kinésithérapie respiratoire", "Repos strict", "Réévaluation à 48-72h", "Hospitalisation si SpO2 < 92%"],
    "Asthma":            ["Bronchodilatateurs courte durée (Salbutamol)", "Corticostéroïdes inh alés", "Plan d'action écrit", "Éviction des allergènes", "Contrôle du débit de pointe"],
    "COPD":              ["Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"],
    "Tuberculosis":      ["Déclaration obligatoire aux autorités sanitaires", "Traitement DOTS : Rifampicine + Isoniazide + Pyrazinamide + Éthambutol", "Isolement respiratoire", "Enquête autour du cas", "Durée minimale 6 mois"],
    "COVID-19":          ["Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"],
    "Influenza":         ["Antiviraux (Oseltamivir) dans les 48h", "Repos et hydratation", "Antipyrétiques (Paracétamol)", "Éviter l'Aspirine", "Isolement 5 jours"],
    "Bronchitis":        ["Traitement symptomatique", "Mucolytiques et fluidifiants", "Antibiothérapie si purulent > 7 jours", "Hydratation", "Arrêt du tabac"],
    "Lung Cancer":       ["Bilan d'extension urgent (TDM thoraco-abdomino-pelvien)", "Biopsie bronchique", "Consultation oncologie thoracique", "Bilan biologique complet", "Arrêt tabac immédiat"],
    "Allergic Rhinitis": ["Antihistaminiques 2ème génération", "Corticostéroïdes nasaux", "Éviction des allergènes", "Tests allergologiques", "Désensibilisation possible"],
    "Sinusitis":         ["Décongestionnants nasaux (max 5 jours)", "Lavages nasaux sérum physiologique", "Antibiothérapie si bactérienne", "Antalgiques"],
    "Cystic Fibrosis":   ["Kinésithérapie respiratoire quotidienne", "Antibiotiques inh alés", "Enzymes pancéatiques", "Suivi pluridisciplinaire spécialisé"],
    "Sleep Apnea":       ["Polysomnographie pour confirmer", "PPC nocturne", "Perte de poids", "Éviction alcool et sédatifs"],
    "Pneumothorax":      ["Hospitalisation en urgence", "Exsufflation ou drainage pleural", "Surveillance radiologique", "Oxygénothérapie fort débit"],
    "Common Cold":       ["Traitement symptomatique uniquement", "Repos et hydratation", "Paracétamol si fièvre", "Pas d'antibiothérapie (viral)"],
}

EXAMENS_CORRECT = {
    "Pneumonia":         ["Radiographie thoracique", "NFS-CRP", "Hémocultures", "ECBC", "Gaz du sang si SpO2 < 94%"],
    "Asthma":            ["EFR (spirométrie)", "Test de réversibilité", "Tests allergologiques", "Peak-flow"],
    "COPD":              ["Spirométrie post-bronchodilatateur", "TDM thoracique", "Gaz du sang", "ECG"],
    "Tuberculosis":      ["Bacilloscopie x 3", "Culture BK", "IDR tuberculine", "TDM thoracique"],
    "COVID-19":          ["PCR SARS-CoV-2", "Scanner thoracique", "NFS-CRP-D-Dimères", "Gaz du sang"],
    "Influenza":         ["Test rapide grippe", "NFS", "PCR grippe si doute"],
    "Bronchitis":        ["Radiographie thoracique", "NFS-CRP", "ECBC si purulent"],
    "Lung Cancer":       ["TDM thoraco-AP", "PET-scan", "Fibroscopie bronchique", "Biopsie", "Bilan biologique"],
    "Allergic Rhinitis": ["Tests cutanés allergologiques", "IgE spécifiques", "NFS (éosinophiles)"],
    "Sinusitis":         ["TDM des sinus", "NFS-CRP"],
    "Cystic Fibrosis":   ["Test de la sueur", "Génotypage CFTR", "Spirométrie", "ECBC"],
    "Sleep Apnea":       ["Polysomnographie", "Oxymetrie nocturne", "ECG"],
    "Pneumothorax":      ["Radiographie thoracique urgente", "TDM thoracique", "Gaz du sang"],
    "Common Cold":       ["Aucun examen nécessaire en routine"],
}

# Recommandations religieuses
RECO_MUSULMAN = [
    "Vérifier la composition des médicaments (certificat halal si disponible)",
    "Adapter les horaires de prise médicamenteuse pendant le Ramadan",
    "Consulter un imam si nécessaire pour les cas d'urgence médicale",
]

# Criteres dynamiques patterns (remplacer ?? par le bon caractere)
# Basé sur _criteres_depuis_symptomes dans diagnostics.py
PATTERNS = [
    ("Hypox??mie confirm??e", "Hypoxémie confirmée"),
    ("Hypox??mie gazeuse ??? ABG PO??? anormal", "Hypoxémie gazeuse — ABG PO₂ anormal"),
    ("Hypox??mie gazeuse", "Hypoxémie gazeuse"),
    ("Hypox??mie confirm??e (SpO??? < 94%)", "Hypoxémie confirmée (SpO₂ < 94%)"),
    ("Fi??vre document??e ??? 38", "Fièvre documentée ≥ 38"),
    ("SpO??? mesur??e", "SpO₂ mesurée"),
    ("Hyperthermie ??? T?? = ", "Hyperthermie — T° = "),
    ("Tachycardie ??? FC =", "Tachycardie — FC ="),
    ("Tachypn??e ??? FR =", "Tachypnée — FR ="),
    ("D??bit expiratoire diminu??", "Débit expiratoire diminué"),
    ("Capacit?? vitale r??duite", "Capacité vitale réduite"),
    ("Ratio VEMS/CVF diminu??", "Ratio VEMS/CVF diminué"),
    ("D??bit de pointe bas", "Débit de pointe bas"),
    ("Ant??c??dent d'asthme", "Antécédent d'asthme"),
    ("Tabagisme actif ??? facteur aggravant", "Tabagisme actif — facteur aggravant"),
    ("PO??? sanguin anormal", "PO₂ sanguin anormal"),
    ("PCO??? sanguin anormal", "PCO₂ sanguin anormal"),
    ("Anomalie scanographique d??tect??e", "Anomalie scanographique détectée"),
    ("D??claration obligatoire", "Déclaration obligatoire"),
    ("autorit??s sanitaires", "autorités sanitaires"),
    ("??thambutol", "Éthambutol"),
    ("Enqu??te autour du cas", "Enquête autour du cas"),
    ("Dur??e minimale", "Durée minimale"),
    ("V??rifier la composition", "Vérifier la composition"),
    ("m??dicaments", "médicaments"),
    ("Adapter les horaires de prise m??dicamenteuse", "Adapter les horaires de prise médicamenteuse"),
    ("Consulter un imam si n??cessaire", "Consulter un imam si nécessaire"),
    ("m??dicale", "médicale"),
    ("fi??vre", "fièvre"),
    ("fi??vre", "fièvre"),
    ("Hypox??mie", "Hypoxémie"),
    ("??pid??", "épidé"),
    ("bilat??rale", "bilatérale"),
    ("??pidémique", "épidémique"),
    ("??pidémiologique", "épidémiologique"),
    ("diminu??", "diminué"),
    ("r??duite", "réduite"),
    ("r??versible", "réversible"),
]


def fix_string(s):
    if not isinstance(s, str) or '?' not in s:
        return s
    result = s
    for bad, good in PATTERNS:
        result = result.replace(bad, good)
    return result


def fix_list(lst):
    if not lst:
        return lst
    return [fix_string(s) if isinstance(s, str) else s for s in lst]


def fix_maladies(maladies):
    if not maladies:
        return maladies
    fixed = []
    for m in maladies:
        nom = m.get('nom', '')
        new_m = dict(m)
        # Remplacer par les bonnes valeurs si la maladie est connue
        if nom in CRITERES_CORRECT:
            new_m['criteres_valides'] = CRITERES_CORRECT[nom]
        else:
            new_m['criteres_valides'] = fix_list(m.get('criteres_valides', []))

        if nom in RECOMMANDATIONS_CORRECT:
            new_m['recommandations'] = RECOMMANDATIONS_CORRECT[nom]
        else:
            new_m['recommandations'] = fix_list(m.get('recommandations', []))

        if nom in EXAMENS_CORRECT:
            new_m['examens_suggeres'] = EXAMENS_CORRECT[nom]
        else:
            new_m['examens_suggeres'] = fix_list(m.get('examens_suggeres', []))
        fixed.append(new_m)
    return fixed


async def main():
    from app.database import AsyncSessionLocal
    from app.models.diagnostic_ia import DiagnosticIA
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(DiagnosticIA))
        diags = result.scalars().all()
        print(f"Total diagnostics: {len(diags)}")
        updated = 0
        for d in diags:
            changed = False

            # Fix maladies
            orig = d.maladies
            fixed = fix_maladies(orig)
            if fixed != orig:
                d.maladies = fixed
                changed = True

            # Fix recommandations (champ direct)
            if d.recommandations:
                fixed_r = fix_list(d.recommandations)
                if fixed_r != d.recommandations:
                    d.recommandations = fixed_r
                    changed = True

            if changed:
                updated += 1

        await db.commit()
        print(f"Updated: {updated} diagnostic(s)")


asyncio.run(main())
