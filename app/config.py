from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "test_secret_key_for_local_and_ci"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./payment_assistant.db"
)

AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "gemini"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "test_api_key_for_local_and_ci"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)
