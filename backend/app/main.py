import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
import app.models  # Ensures models are loaded
from app.routes import auth, analysis, saved_results

# Create all database tables safely (no-op or caught if read-only)
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(
    title="AI Stylist API",
    description="Personalised Fashion Harmony API powered by Computer Vision & Colour Theory",
    version="1.0.0"
)

# Cross-Origin Resource Sharing for Flutter Web & Mobile
# Using allow_origin_regex ensures Starlette reflects the actual requesting Origin
# (e.g., http://localhost:3000, https://aistylist-mu.vercel.app) satisfying browser CORS rules.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Ensure upload directories exist and mount static route safely
for dir_path in (settings.UPLOAD_DIR, settings.OUTFIT_IMAGE_DIR, settings.VIRTUAL_TRYON_DIR):
    try:
        os.makedirs(dir_path, exist_ok=True)
    except OSError:
        pass

try:
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
except Exception:
    pass


@app.on_event("startup")
async def startup_system_check():
    import sys
    from app.services.virtual_tryon_provider import get_virtual_tryon_provider

    vton = get_virtual_tryon_provider()
    app.state.vton_provider = vton

    gpu_avail = False
    gpu_name = "Not Available"
    vram_str = "N/A"
    torch_version = "Not Loaded"

    # Only inspect PyTorch / CUDA when VTON is enabled and local
    if settings.VTON_PROVIDER == "local" and settings.VTON_ENABLED:
        try:
            import torch
            torch_version = torch.__version__
            gpu_avail = torch.cuda.is_available()
            gpu_name = torch.cuda.get_device_name(0) if gpu_avail else "Not Available"
            if gpu_avail:
                try:
                    total_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
                    vram_str = f"{total_gb:.1f} GB"
                except Exception:
                    pass
        except (ImportError, Exception):
            torch_version = "Unavailable (Serverless/CPU Mode)"

    gemini_status = "Connected" if (settings.GEMINI_ENABLED and settings.GEMINI_API_KEY) else "Not Configured"
    vton_ready = getattr(getattr(vton, "local_provider", None), "is_ready", False)

    print("=" * 64)
    print("                    AI STYLIST SYSTEM CHECK")
    print("=" * 64)
    print(f"  Python:              {sys.version.split()[0]}")
    print(f"  PyTorch:             {torch_version}")
    print(f"  CUDA:                {'Available' if gpu_avail else 'Unavailable'}")
    print(f"  GPU:                 {gpu_name}")
    print(f"  VRAM:                {vram_str}")
    print(f"  VTON Provider:       {settings.VTON_PROVIDER}")
    print(f"  FASHN VTON Status:   {'Ready' if vton_ready else ('Disabled' if not settings.VTON_ENABLED else 'Standby')}")
    print(f"  Gemini Vision:       {gemini_status} ({settings.GEMINI_MODEL})")
    print(f"  Try-On Max Looks:    {settings.TRYON_MAX_LOOKS}")
    print("=" * 64)


# Mount API Routers
app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(saved_results.router)


@app.get("/")
@app.get("/health")
def root():
    return {
        "status": "ok",
        "service": "AI Stylist – Personalised Fashion Harmony API",
        "version": "1.0.0",
        "vton_provider": settings.VTON_PROVIDER,
        "vton_enabled": settings.VTON_ENABLED,
        "docs": "/docs"
    }
