from pydantic import BaseModel, EmailStr, field_validator, model_validator
import re


class LoginSchema(BaseModel):
    email:    EmailStr
    password: str
    phone:    str

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^\+\d{8,15}$", cleaned):
            raise ValueError("Numéro invalide. Format attendu : +237XXXXXXXXX")
        return cleaned


class ResetRequestSchema(BaseModel):
    email: EmailStr
    phone: str

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^\+\d{8,15}$", cleaned):
            raise ValueError("Numéro invalide. Format attendu : +237XXXXXXXXX")
        return cleaned


class ResetConfirmSchema(BaseModel):
    email:            EmailStr
    otp:              str
    new_password:     str
    confirm_password: str

    @field_validator("otp")
    @classmethod
    def otp_format(cls, v: str) -> str:
        if not re.match(r"^\d{6}$", v):
            raise ValueError("Le code OTP doit contenir exactement 6 chiffres.")
        return v

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Minimum 8 caractères.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Au moins une majuscule requise.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Au moins un chiffre requis.")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetConfirmSchema":
        if self.new_password != self.confirm_password:
            raise ValueError("Les mots de passe ne correspondent pas.")
        return self


class RefusRequestSchema(BaseModel):
    motif: str

    @field_validator("motif")
    @classmethod
    def motif_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le motif ne peut pas être vide.")
        return v.strip()