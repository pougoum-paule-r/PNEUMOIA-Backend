from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class OTPVerifyRequest(BaseModel):
    # medecin_id est un String(15) format PNEU-XXXXXXX (pas un UUID)
    medecin_id: str
    code:       str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"

class MessageResponse(BaseModel):
    message:    str
    medecin_id: str | None = None   # présent seulement après /login
    email_sent: bool | None = None  # False si l'envoi d'email OTP a échoué