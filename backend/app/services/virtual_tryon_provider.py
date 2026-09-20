"""
Virtual Try-On Provider Interface & Hierarchy
==============================================
Defines the clean VirtualTryOnProvider abstraction:
1. FASHNVTONLocalProvider: Local NVIDIA RTX GPU workstation (PyTorch + CUDA)
2. ProductionVTONProvider: Production-safe FASHN Cloud REST API (api.fashn.ai)
3. DisabledVirtualTryOnProvider: Structured unavailable response for serverless without GPU/API

Product Honesty:
  - Returns result_type: "actual_try_on" when photorealistic VTON generates the image.
  - Returns result_type: "unavailable" when try-on is unconfigured or unsupported.
  - NEVER returns fake canvas drawings, stock models, or placeholder images.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, Union, Literal
from io import BytesIO
import base64
import time
import asyncio
import logging

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)


def _normalize_category(raw: str) -> Literal["tops", "bottoms", "one-pieces"]:
    c = (raw or "").lower().strip()
    bottoms = ["bottom", "pant", "trouser", "jean", "skirt", "short", "chino", "legging"]
    one_pieces = ["dress", "one-piece", "jumpsuit", "romper", "gown", "suit"]
    if any(b in c for b in bottoms):
        return "bottoms"
    if any(o in c for o in one_pieces):
        return "one-pieces"
    return "tops"


def _image_to_base64_data_url(image_input: Union[str, Path, bytes, Image.Image]) -> str:
    """Converts image input to an optimized data:image/jpeg;base64 URL."""
    if isinstance(image_input, (str, Path)):
        p = Path(image_input)
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {p}")
        with Image.open(p) as img:
            img_rgb = img.convert("RGB")
            if max(img_rgb.size) > 1200:
                img_rgb.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            buf = BytesIO()
            img_rgb.save(buf, format="JPEG", quality=90)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"

    elif isinstance(image_input, bytes):
        with Image.open(BytesIO(image_input)) as img:
            img_rgb = img.convert("RGB")
            if max(img_rgb.size) > 1200:
                img_rgb.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            buf = BytesIO()
            img_rgb.save(buf, format="JPEG", quality=90)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"

    elif isinstance(image_input, Image.Image):
        img_rgb = image_input.convert("RGB")
        if max(img_rgb.size) > 1200:
            img_rgb.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img_rgb.save(buf, format="JPEG", quality=90)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    raise ValueError(f"Unsupported image input type: {type(image_input)}")


class VirtualTryOnProvider(ABC):
    """Abstract base class for all Virtual Try-On implementations."""

    @abstractmethod
    async def generate_try_on(
        self,
        person_image: Union[str, Path, bytes, Image.Image],
        garment_image: Union[str, Path, bytes, Image.Image],
        category: str,
        styling_context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Executes virtual try-on and returns:
            {
                "success": bool,
                "result_type": "actual_try_on" | "unavailable",
                "image_url": Optional[str],
                "provider": str,
                "category": str,
                "execution_time_seconds": Optional[float],
                "message": Optional[str],
                "error_code": Optional[str]
            }
        """
        pass


class DisabledVirtualTryOnProvider(VirtualTryOnProvider):
    """
    Provider used when VTON is explicitly disabled or unconfigured in serverless.
    Returns an honest, structured 'unavailable' result instead of fake try-on images.
    """

    def __init__(self, message: Optional[str] = None):
        self.is_ready = False
        self.message = message or "Virtual Try-On is currently unavailable in this deployment (requires local GPU workstation or FASHN Cloud API key)."

    async def generate_try_on(
        self,
        person_image: Union[str, Path, bytes, Image.Image],
        garment_image: Union[str, Path, bytes, Image.Image],
        category: str,
        styling_context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        return {
            "success": False,
            "result_type": "unavailable",
            "image_url": None,
            "provider": "disabled",
            "category": category,
            "error_code": "VTON_DISABLED",
            "message": self.message,
        }


class ProductionVTONProvider(VirtualTryOnProvider):
    """
    Production-safe Virtual Try-On Provider via the official FASHN Cloud REST API.
    Used on Vercel and cloud deployments without a local GPU.
    Submits jobs to FASHN's cloud GPU infrastructure and returns permanent public HTTPS URLs.
    """

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "FASHN_API_KEY", "")
        self.api_url = (api_url or getattr(settings, "FASHN_API_URL", "https://api.fashn.ai/v1")).rstrip("/")
        self.timeout = getattr(settings, "FASHN_API_TIMEOUT", 60)
        self.is_ready = bool(self.api_key)

    async def generate_try_on(
        self,
        person_image: Union[str, Path, bytes, Image.Image],
        garment_image: Union[str, Path, bytes, Image.Image],
        category: str,
        styling_context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()

        if not self.api_key:
            logger.info("Production VTON called without FASHN_API_KEY. Returning structured unavailable status.")
            return {
                "success": False,
                "result_type": "unavailable",
                "image_url": None,
                "provider": "fashn_api_unconfigured",
                "category": category,
                "error_code": "PRODUCTION_VTON_API_KEY_REQUIRED",
                "message": "Production Virtual Try-On requires FASHN_API_KEY configured in environment variables, or local GPU workstation.",
            }

        norm_cat = _normalize_category(category)

        try:
            person_url = _image_to_base64_data_url(person_image)
            garment_url = _image_to_base64_data_url(garment_image)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            run_payload = {
                "model_image": person_url,
                "garment_image": garment_url,
                "category": norm_cat,
                "mode": "balanced",
                "nsfw_filter": True,
            }

            logger.info("Submitting try-on request to FASHN Cloud API: %s/run (category: %s)", self.api_url, norm_cat)

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(f"{self.api_url}/run", headers=headers, json=run_payload)

            if resp.status_code not in (200, 201):
                err_text = resp.text[:250]
                logger.error("FASHN API submission failed with HTTP %d: %s", resp.status_code, err_text)
                return {
                    "success": False,
                    "result_type": "unavailable",
                    "image_url": None,
                    "provider": "fashn_api",
                    "category": category,
                    "error_code": f"FASHN_API_{resp.status_code}",
                    "message": f"FASHN Cloud API error: {err_text}",
                }

            run_data = resp.json()
            pred_id = run_data.get("id")
            if not pred_id:
                raise ValueError(f"FASHN API did not return job ID: {run_data}")

            # Poll for completion
            poll_url = f"{self.api_url}/status/{pred_id}"
            deadline = time.time() + self.timeout

            async with httpx.AsyncClient(timeout=10.0) as client:
                while time.time() < deadline:
                    await asyncio.sleep(2.5)
                    poll_resp = await client.get(poll_url, headers=headers)
                    if poll_resp.status_code == 200:
                        status_data = poll_resp.json()
                        job_status = status_data.get("status")

                        if job_status == "completed":
                            output_urls = status_data.get("output", [])
                            if output_urls and isinstance(output_urls, list) and output_urls[0]:
                                out_img = output_urls[0]
                                elapsed = round(time.perf_counter() - t0, 2)
                                logger.info("FASHN Cloud VTON completed successfully in %.2fs: %s", elapsed, out_img)
                                return {
                                    "success": True,
                                    "result_type": "actual_try_on",
                                    "image_url": out_img,
                                    "provider": "fashn_cloud_api",
                                    "category": category,
                                    "execution_time_seconds": elapsed,
                                    "message": "Actual try-on generated via FASHN Cloud GPU service.",
                                }
                            break

                        elif job_status == "failed":
                            error_msg = status_data.get("error") or "FASHN inference job failed"
                            logger.error("FASHN Cloud VTON job %s failed: %s", pred_id, error_msg)
                            return {
                                "success": False,
                                "result_type": "unavailable",
                                "image_url": None,
                                "provider": "fashn_cloud_api",
                                "category": category,
                                "error_code": "FASHN_JOB_FAILED",
                                "message": error_msg,
                            }

            return {
                "success": False,
                "result_type": "unavailable",
                "image_url": None,
                "provider": "fashn_cloud_api",
                "category": category,
                "error_code": "FASHN_TIMEOUT",
                "message": f"FASHN Cloud API job timed out after {self.timeout} seconds.",
            }

        except Exception as exc:
            logger.error("ProductionVTONProvider exception: %s", exc, exc_info=True)
            return {
                "success": False,
                "result_type": "unavailable",
                "image_url": None,
                "provider": "fashn_cloud_api",
                "category": category,
                "error_code": "VTON_EXCEPTION",
                "message": f"Virtual try-on error: {exc}",
            }


class DefaultVirtualTryOnProvider(VirtualTryOnProvider):
    """
    Local GPU Virtual Try-On Provider.
    Primary: FASHN VTON v1.5 local NVIDIA GPU execution (lazy-loaded).
    Fallback: DisabledVirtualTryOnProvider (when local GPU or torch unavailable).
    """

    def __init__(self, local_vton_provider: Optional[Any] = None):
        self._local_provider = local_vton_provider

    @property
    def local_provider(self):
        if self._local_provider is None:
            if settings.VTON_PROVIDER == "disabled" or not settings.VTON_ENABLED:
                self._local_provider = DisabledVirtualTryOnProvider()
            else:
                try:
                    from app.services.fashn_vton_local_provider import FASHNVTONLocalProvider
                    self._local_provider = FASHNVTONLocalProvider()
                except Exception as exc:
                    logger.warning("FASHN VTON local provider unavailable (%s); using Disabled provider.", exc)
                    self._local_provider = DisabledVirtualTryOnProvider()
        return self._local_provider

    async def generate_try_on(
        self,
        person_image: Union[str, Path, bytes, Image.Image],
        garment_image: Union[str, Path, bytes, Image.Image],
        category: str,
        styling_context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        if settings.VTON_ENABLED and settings.VTON_PROVIDER == "local":
            return await self.local_provider.generate_try_on(
                person_image=person_image,
                garment_image=garment_image,
                category=category,
                styling_context=styling_context,
                **kwargs,
            )

        return {
            "success": False,
            "result_type": "unavailable",
            "image_url": None,
            "provider": "disabled",
            "category": category,
            "error_code": "VTON_UNAVAILABLE",
            "message": "Local GPU Virtual Try-On is disabled or unconfigured.",
        }


# Global singleton instance
_vton_singleton: Optional[VirtualTryOnProvider] = None


def get_virtual_tryon_provider() -> VirtualTryOnProvider:
    global _vton_singleton
    if _vton_singleton is None:
        from app.config import IS_SERVERLESS
        prov = (settings.VTON_PROVIDER or "auto").lower().strip()
        if prov == "production":
            _vton_singleton = ProductionVTONProvider()
        elif prov == "auto":
            if IS_SERVERLESS:
                _vton_singleton = ProductionVTONProvider()
            elif settings.VTON_ENABLED:
                _vton_singleton = DefaultVirtualTryOnProvider()
            else:
                _vton_singleton = DisabledVirtualTryOnProvider()
        elif prov == "local":
            if IS_SERVERLESS:
                _vton_singleton = ProductionVTONProvider()
            elif settings.VTON_ENABLED:
                _vton_singleton = DefaultVirtualTryOnProvider()
            else:
                _vton_singleton = DisabledVirtualTryOnProvider()
        elif prov == "disabled":
            _vton_singleton = DisabledVirtualTryOnProvider()
        else:
            _vton_singleton = DisabledVirtualTryOnProvider()
    return _vton_singleton
