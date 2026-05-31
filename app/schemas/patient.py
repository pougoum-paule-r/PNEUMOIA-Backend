# app/schemas/patient.py
from pydantic import BaseModel
from typing import Optional
from datetime import date


class PatientCreate(BaseModel):
    civilite:            Optional[str]  = None
    nom:                 str
    prenom:              str
    date_naissance:      Optional[date] = None
    groupe_sanguin:      Optional[str]  = None
    religion:            Optional[str]  = None
    telephone:           Optional[str]  = None
    email:               Optional[str]  = None
    adresse:             Optional[str]  = None
    profession:          Optional[str]  = None
    personne_a_contacter: Optional[str] = None
    telephone_urgence:   Optional[str]  = None
    allergies:           list           = []
    antecedents:         dict           = {}

    model_config = {"from_attributes": True}


class PatientOut(BaseModel):
    id:                  str
    civilite:            Optional[str]
    nom:                 str
    prenom:              str
    date_naissance:      Optional[date]
    sexe:                Optional[str]
    groupe_sanguin:      Optional[str]
    religion:            Optional[str]
    telephone:           Optional[str]
    email:               Optional[str]
    adresse:             Optional[str]
    profession:          Optional[str]
    personne_a_contacter: Optional[str]
    telephone_urgence:   Optional[str]
    allergies:           list
    antecedents:         dict

    model_config = {"from_attributes": True}


class PatientSearchResult(BaseModel):
    id:             str
    nom:            str
    prenom:         str
    civilite:       Optional[str]
    telephone:      Optional[str]
    adresse:        Optional[str]
    date_naissance: Optional[date]

    model_config = {"from_attributes": True}