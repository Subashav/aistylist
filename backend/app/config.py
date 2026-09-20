import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="allow",
    )

    SECRET_KEY: str = "ai_stylist_super_secret_jwt_key_2026_fashion_harmony"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'ai_stylist.db'}"
    UPLOAD_DIR: Path = (BASE_DIR / "uploads").resolve()
    # Sub-directory for AI-composed outfit recommendation images
    OUTFIT_IMAGE_DIR: Path = (BASE_DIR / "uploads" / "outfit_recommendations").resolve()
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

    # Virtual Try-On Provider: "local" (default for Windows GPU) or "disabled"
    VTON_PROVIDER: str = os.getenv("VTON_PROVIDER", "local")
    VTON_ENABLED: bool = True
    VTON_MODEL_NAME: str = "FASHN VTON v1.5"
    VTON_WEIGHTS_DIR: Path = (BASE_DIR / "weights").resolve()
    TRYON_MAX_LOOKS: int = 2  # 2 personalized try-on images; remaining are complete outfit & material guides
    VIRTUAL_TRYON_DIR: Path = (BASE_DIR / "uploads" / "virtual_tryon").resolve()

settings = Settings()

if settings.VTON_PROVIDER == "disabled":
    settings.VTON_ENABLED = False

for directory in (settings.UPLOAD_DIR, settings.OUTFIT_IMAGE_DIR, settings.VIRTUAL_TRYON_DIR, settings.VTON_WEIGHTS_DIR):
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError:
        pass


