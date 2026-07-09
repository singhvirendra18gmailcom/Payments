import os
import time

from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from app.logger import logger
from app.services.ai_factory import get_ai_service
from app.services.payment_service import PaymentService


from .database import Base, engine
from .models import User
from .schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    PaymentExplainRequest,
    ChatRequest
)
from .auth import (
    get_db,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from .payment_service import explain_payment, answer_question

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Payment Assistant")

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    client_host = request.client.host if request.client else "unknown"

    logger.info(
        f"Request started: {request.method} {request.url.path} "
        f"from {client_host}"
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.exception(
            f"Request failed: {request.method} {request.url.path} "
            f"after {duration_ms:.2f}ms"
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        f"Response completed: {request.method} {request.url.path} "
        f"status={response.status_code} duration={duration_ms:.2f}ms"
    )

    return response

@app.get("/health")
def health():
    logger.info("Health endpoint called")
    return {
        "status": "ok",
        "app": "AI Payment Assistant"
    }

@app.post("/auth/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    logger.info("user registration endpoint called")
    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(
        f"User registered successfully: {user.email}"
    )
    return {
        "message": "User registered successfully",
        "email": user.email
    }

@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt: {request.email}")
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        logger.warning(
            f"Login failed: User not found: {request.email}"
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user.hashed_password):
        logger.warning(
            f"Login failed: Invalid Email or password: {request.email}"
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    logger.info("user me endpoint called")
    return {
        "name": current_user.name,
        "email": current_user.email
    }

@app.post("/payments/explain")
def payment_explain(
    request: PaymentExplainRequest,
    current_user: User = Depends(get_current_user)
):
    logger.info("payment explain endpoint called")
    explanation = explain_payment(request.message_type, request.content)

    return {
        "message_type": request.message_type,
        "explanation": explanation
    }

@app.post("/chat/ask")
def chat_ask(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    logger.info("chat ask endpoint called")
    answer = answer_question(request.question)

    return {
        "question": request.question,
        "answer": answer
    }

@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    logger.info("document uplaod endpoint called")
    allowed_extensions = [".pdf", ".txt", ".docx"]
    filename = file.filename

    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and DOCX files are allowed"
        )

    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())
    logger.info(
        f"File uploaded by {current_user.email}: {filename}"
    )
    return {
        "filename": filename,
        "status": "uploaded"
    }

@app.get("/documents")
def list_documents(current_user: User = Depends(get_current_user)):
    logger.info("list all documents endpoint called")
    files = os.listdir(UPLOAD_DIR)

    return [
        {
            "filename": file,
            "type": os.path.splitext(file)[1].replace(".", "")
        }
        for file in files
    ]



@app.post("/chat/ask-ai")
def ask_ai(request: ChatRequest):
    ai_service = get_ai_service()
    answer = ai_service.ask(request.question)

    return {
        "question": request.question,
        "answer": answer
    }


@app.post("/payments/explain-ai")
def explain_payment_ai(request: PaymentExplainRequest):
    ai_service = get_ai_service()
    payment_service = PaymentService(ai_service)

    explanation = payment_service.explain_payment_message(
        request.message_type,
        request.content
    )

    return {
        "message_type": request.message_type,
        "explanation": explanation
    }


@app.get("/ai/health")
def ai_health():
    ai_service = get_ai_service()

    return {
        "provider": "gemini",
        "available": ai_service.health_check()
    }