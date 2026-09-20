import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting AI Stylist Backend on http://127.0.0.1:{settings.PORT}")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
