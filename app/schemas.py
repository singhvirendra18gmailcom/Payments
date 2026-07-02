from pydantic import BaseModel, EmailStr , Field

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=72
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=72
    )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class PaymentExplainRequest(BaseModel):
    message_type: str
    content: str

class ChatRequest(BaseModel):
    question: str