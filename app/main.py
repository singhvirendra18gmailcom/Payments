import os
import time

from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AI_PROVIDER,
    ALGORITHM,
    DATABASE_URL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SECRET_KEY,
)
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

AI_UNAVAILABLE_MESSAGE = "AI service is currently unavailable. Please try again later."
SUPPORTED_AI_PROVIDERS = {"gemini", "local"}
SUPPORTED_JWT_ALGORITHMS = {"HS256"}
PLACEHOLDER_GEMINI_KEYS = {
    "test_api_key_for_local_and_ci",
    "your_gemini_api_key",
}


def validate_configuration() -> None:
    errors = []
    warnings = []

    if not SECRET_KEY or not SECRET_KEY.strip():
        errors.append("SECRET_KEY is required")

    if ALGORITHM not in SUPPORTED_JWT_ALGORITHMS:
        errors.append(
            f"ALGORITHM must be one of {sorted(SUPPORTED_JWT_ALGORITHMS)}"
        )

    if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
        errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0")

    if not DATABASE_URL or not DATABASE_URL.strip():
        errors.append("DATABASE_URL is required")

    if AI_PROVIDER.lower().strip() not in SUPPORTED_AI_PROVIDERS:
        errors.append(
            f"AI_PROVIDER must be one of {sorted(SUPPORTED_AI_PROVIDERS)}"
        )

    if AI_PROVIDER.lower().strip() == "gemini":
        if not GEMINI_MODEL or not GEMINI_MODEL.strip():
            errors.append("GEMINI_MODEL is required when AI_PROVIDER=gemini")

        if not GEMINI_API_KEY or not GEMINI_API_KEY.strip():
            errors.append("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        elif GEMINI_API_KEY in PLACEHOLDER_GEMINI_KEYS:
            warnings.append(
                "GEMINI_API_KEY is using a placeholder value; "
                "Gemini API calls will fail until a real key is configured"
            )

    for warning in warnings:
        logger.warning(f"Configuration warning: {warning}")

    if errors:
        message = "; ".join(errors)
        logger.error(f"Configuration validation failed: {message}")
        raise RuntimeError(message)

    logger.info("Configuration validation passed")


def ai_error_response(error: str | None = None) -> JSONResponse:
    content = {
        "status": "error",
        "provider": AI_PROVIDER,
        "message": AI_UNAVAILABLE_MESSAGE,
    }

    if error:
        content["error"] = error

    return JSONResponse(status_code=503, content=content)


@app.on_event("startup")
def validate_app_configuration():
    validate_configuration()


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

    try:
        explanation = explain_payment(request.message_type, request.content)
    except ValueError as ex:
        logger.warning(f"Invalid payment explain request: {ex}")
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        logger.exception("Payment explanation API failed")
        return ai_error_response(str(ex))

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

    try:
        answer = answer_question(request.question)
    except ValueError as ex:
        logger.warning(f"Invalid chat request: {ex}")
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        logger.exception("Chat API failed")
        return ai_error_response(str(ex))

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
    logger.info("AI chat endpoint called")

    try:
        ai_service = get_ai_service()
        answer = ai_service.ask(request.question)
    except ValueError as ex:
        logger.warning(f"Invalid AI chat request: {ex}")
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        logger.exception("AI chat API failed")
        return ai_error_response(str(ex))

    return {
        "question": request.question,
        "answer": answer
    }


@app.post("/payments/explain-ai")
def explain_payment_ai(request: PaymentExplainRequest):
    logger.info("AI payment explain endpoint called")

    try:
        ai_service = get_ai_service()
        payment_service = PaymentService(ai_service)
        explanation = payment_service.explain_payment_message(
            request.message_type,
            request.content
        )
    except ValueError as ex:
        logger.warning(f"Invalid AI payment explain request: {ex}")
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        logger.exception("AI payment explanation API failed")
        return ai_error_response(str(ex))

    return {
        "message_type": request.message_type,
        "explanation": explanation
    }


@app.get("/ai/health")
def ai_health():
    logger.info("AI health endpoint called")

    try:
        ai_service = get_ai_service()
        available = ai_service.health_check()
    except Exception as ex:
        logger.exception("AI health check failed")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "provider": AI_PROVIDER,
                "available": False,
                "error": str(ex),
            },
        )

    status_code = 200 if available else 503
    status = "healthy" if available else "unhealthy"

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "provider": AI_PROVIDER,
            "available": available,
        },
    )
