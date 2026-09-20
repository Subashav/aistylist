import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

def _is_writable(path: Path) -> bool:
    try:
        test_file = path / ".write_test"
        with open(test_file, "w") as f:
            f.write("1")
        test_file.unlink(missing_ok=True)
        return True
    except Exception:
        return False

# Detect serverless / read-only filesystem (Vercel, AWS Lambda)
IS_SERVERLESS = bool(
    os.environ.get("VERCEL") or 
    os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or 
    not _is_writable(BASE_DIR)
)

if IS_SERVERLESS:
    DATA_DIR = Path("/tmp/ai_stylist")
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
else:
    DATA_DIR = BASE_DIR


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="allow",
    )

    SECRET_KEY: str = "ai_stylist_super_secret_jwt_key_2026_fashion_harmony"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'ai_stylist.db'}"
    UPLOAD_DIR: Path = (DATA_DIR / "uploads").resolve()
    # Sub-directory for AI-composed outfit recommendation images
    OUTFIT_IMAGE_DIR: Path = (DATA_DIR / "uploads" / "outfit_recommendations").resolve()
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://aistylist-mu.vercel.app",
    ]
    # Visual Provider Settings: 'ai' or 'pillow'
    OUTFIT_VISUAL_PROVIDER: str = "ai"
    # AI Backend: 'pollinations' (free/instant photorealistic flux), 'openai' (DALL-E 3), 'stability', 'custom'
    AI_IMAGE_PROVIDER: str = "pollinations"
    # Optional API key for OpenAI / Stability / Replicate / custom provider
    IMAGE_GENERATION_API_KEY: str = ""
    # Model name
    AI_IMAGE_MODEL: str = "flux"
    # Timeout in seconds for AI image generation requests
    AI_IMAGE_TIMEOUT: int = 35
    # Gemini Vision Semantic Understanding (Reasoning & Styling)
    GEMINI_ENABLED: bool = True
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_TIMEOUT: int = 15

    # Virtual Try-On Provider: "local" (default for Windows GPU), "production" (FASHN Cloud API), or "disabled"
    VTON_PROVIDER: str = os.getenv("VTON_PROVIDER", "local")
    VTON_ENABLED: bool = True
    VTON_MODEL_NAME: str = "FASHN VTON v1.5"
    VTON_WEIGHTS_DIR: Path = (BASE_DIR / "weights").resolve()
    TRYON_MAX_LOOKS: int = 2  # 2 personalized try-on images; remaining are complete outfit & material guides
    VIRTUAL_TRYON_DIR: Path = (DATA_DIR / "uploads" / "virtual_tryon").resolve()

    # Production FASHN Cloud API (https://api.fashn.ai)
    FASHN_API_KEY: str = ""
    FASHN_API_URL: str = "https://api.fashn.ai/v1"
    FASHN_API_TIMEOUT: int = 60

    # Storage Provider: 'auto', 'local', or 'production'
    STORAGE_PROVIDER: str = "auto"
    STORAGE_BASE_URL: str = ""


settings = Settings()

# If serverless/Vercel, guarantee SQLite and uploads point to writable /tmp
if IS_SERVERLESS:
    if "sqlite" in settings.DATABASE_URL:
        settings.DATABASE_URL = f"sqlite:///{DATA_DIR / 'ai_stylist.db'}"
    settings.UPLOAD_DIR = (DATA_DIR / "uploads").resolve()
    settings.OUTFIT_IMAGE_DIR = (DATA_DIR / "uploads" / "outfit_recommendations").resolve()
    settings.VIRTUAL_TRYON_DIR = (DATA_DIR / "uploads" / "virtual_tryon").resolve()

if settings.VTON_PROVIDER == "disabled":
    settings.VTON_ENABLED = False

for directory in (settings.UPLOAD_DIR, settings.OUTFIT_IMAGE_DIR, settings.VIRTUAL_TRYON_DIR, settings.VTON_WEIGHTS_DIR):
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError:
        pass
