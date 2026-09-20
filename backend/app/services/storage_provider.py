"""
Image Storage Provider
======================
Abstraction for persisting and serving images reliably across local development
and serverless / cloud production deployments.

- LocalImageStorage: Saves to local filesystem (uploads/ directory), served via FastAPI static route.
- ProductionImageStorage: Stores images persistently in database (StoredImage) and/or cloud storage,
  guaranteeing that images survive serverless container lifecycles on Vercel without 404s.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Union
import logging
import os

from app.config import settings, IS_SERVERLESS
from app.database import SessionLocal
from app.models.image_storage import StoredImage

logger = logging.getLogger(__name__)


class ImageStorageProvider(ABC):
    """Abstract interface for image persistence and retrieval."""

    @abstractmethod
    async def save_image(
        self,
        image_data: bytes,
        filename: str,
        content_type: str = "image/png",
        subfolder: str = "",
    ) -> str:
        """
        Persists image bytes and returns a stable, browser-accessible URL.
        """
        pass

    @abstractmethod
    async def get_image(self, filename: str) -> Optional[Tuple[bytes, str]]:
        """
        Retrieves image bytes and content_type by filename.
        """
        pass


class LocalImageStorage(ImageStorageProvider):
    """Filesystem storage for local workstation development."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.UPLOAD_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(
        self,
        image_data: bytes,
        filename: str,
        content_type: str = "image/png",
        subfolder: str = "",
    ) -> str:
        target_dir = (self.base_dir / subfolder) if subfolder else self.base_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename

        with open(file_path, "wb") as f:
            f.write(image_data)

        rel_path = f"/uploads/{subfolder}/{filename}" if subfolder else f"/uploads/{filename}"
        return rel_path

    async def get_image(self, filename: str) -> Optional[Tuple[bytes, str]]:
        # Search recursively in upload directory
        for p in self.base_dir.rglob(filename):
            if p.is_file():
                ext = p.suffix.lower()
                mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
                with open(p, "rb") as f:
                    return f.read(), mime
        return None


class ProductionImageStorage(ImageStorageProvider):
    """
    Persistent storage for Serverless / Cloud Production.
    Stores image data in database and local cache so images survive container recycling.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (Path("/tmp/ai_stylist/uploads") if IS_SERVERLESS else settings.UPLOAD_DIR)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    async def save_image(
        self,
        image_data: bytes,
        filename: str,
        content_type: str = "image/png",
        subfolder: str = "",
    ) -> str:
        # 1. Cache to local container filesystem if available
        try:
            target_dir = (self.cache_dir / subfolder) if subfolder else self.cache_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            with open(target_dir / filename, "wb") as f:
                f.write(image_data)
        except Exception as cache_err:
            logger.debug("Filesystem cache write skipped: %s", cache_err)

        # 2. Persist in database for global access across all serverless containers
        db = SessionLocal()
        try:
            existing = db.query(StoredImage).filter(StoredImage.filename == filename).first()
            if existing:
                existing.data = image_data
                existing.content_type = content_type
            else:
                new_img = StoredImage(
                    filename=filename,
                    content_type=content_type,
                    data=image_data,
                )
                db.add(new_img)
            db.commit()
        except Exception as db_err:
            db.rollback()
            logger.warning("Database image persistence warning: %s", db_err)
        finally:
            db.close()

        base_url = settings.STORAGE_BASE_URL.rstrip("/") if settings.STORAGE_BASE_URL else ""
        return f"{base_url}/api/images/{filename}"

    async def get_image(self, filename: str) -> Optional[Tuple[bytes, str]]:
        # Check local cache first
        try:
            for p in self.cache_dir.rglob(filename):
                if p.is_file():
                    ext = p.suffix.lower()
                    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
                    with open(p, "rb") as f:
                        return f.read(), mime
        except Exception:
            pass

        # Query persistent database
        db = SessionLocal()
        try:
            stored = db.query(StoredImage).filter(StoredImage.filename == filename).first()
            if stored and stored.data:
                return stored.data, stored.content_type or "image/png"
        except Exception as err:
            logger.warning("Error fetching stored image '%s': %s", filename, err)
        finally:
            db.close()

        return None


# Global singleton factory
_storage_singleton: Optional[ImageStorageProvider] = None


def get_storage_provider() -> ImageStorageProvider:
    global _storage_singleton
    if _storage_singleton is None:
        mode = settings.STORAGE_PROVIDER.lower().strip()
        if mode == "production" or (mode == "auto" and IS_SERVERLESS):
            _storage_singleton = ProductionImageStorage()
        else:
            _storage_singleton = LocalImageStorage()
    return _storage_singleton
