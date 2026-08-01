from pydantic import BaseModel, EmailStr , Field,  ConfigDict

from datetime import datetime


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

class DocumentUploadResponse(BaseModel):
    id: int
    original_filename: str
    content_type: str
    file_size: int
    processing_status: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)