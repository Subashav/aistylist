"""
Virtual Try-On Provider Interface & Delegation
==============================================
Defines the clean VirtualTryOnProvider abstraction.
Provides FASHNVTONLocalProvider as the primary virtual try-on engine for Phase 1.
Ensures product honesty:
  - Returns result_type: "actual_try_on" when FASHN VTON generates the image.
  - Returns result_type: "outfit_preview" when fallback preview is used.
  - Returns result_type: "unavailable" when try-on fails without silent fake results.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging

from PIL import Image

from app.config import settings
from app.services.fashn_vton_local_provider import FASHNVTONLocalProvider
from app.services.try_on_provider import PersonalizedTryOnCompositor

logger = logging.getLogger(__name__)


class VirtualTryOnProvider(ABC):
    """
    Abstract interface for Virtual Try-On services.
    Enables swapping between local FASHN VTON and future remote/cloud providers.
    """

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
                "result_type": "actual_try_on" | "outfit_preview" | "unavailable",
                "image_url": Optional[str],
                "provider": str,
                "category": str,
                "execution_time_seconds": Optional[float],
                "message": Optional[str]
            }
        """
        pass


class DefaultVirtualTryOnProvider(VirtualTryOnProvider):
    """
    Default Phase 1 Virtual Try-On Provider.
    Primary: FASHN VTON v1.5 local GPU execution.
    Fallback: PersonalizedTryOnCompositor (clearly labeled as outfit_preview).
    """

    def __init__(self, local_vton_provider: Optional[FASHNVTONLocalProvider] = None):
        self.local_provider = local_vton_provider or FASHNVTONLocalProvider()
        self.compositor_fallback = PersonalizedTryOnCompositor()

    async def generate_try_on(
        self,
        person_image: Union[str, Path, bytes, Image.Image],
        garment_image: Union[str, Path, bytes, Image.Image],
        category: str,
        styling_context: Optional[Dict[str, Any]] = None,
        allow_fallback_preview: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        # 1. Attempt Local FASHN VTON
        if settings.VTON_ENABLED:
            vton_res = await self.local_provider.generate_try_on(
                person_image=person_image,
                garment_image=garment_image,
                category=category,
                styling_context=styling_context,
                **kwargs,
            )

            if vton_res.get("success") and vton_res.get("image_url"):
                return vton_res

            logger.warning("FASHN VTON returned non-success: %s", vton_res.get("message"))
            if not allow_fallback_preview:
                return vton_res

        # 2. Transparent Fallback Preview if allowed and needed
        logger.info("Using AI Outfit Preview compositor fallback.")
        try:
            user_path = Path(person_image) if isinstance(person_image, (str, Path)) else None
            garment_path = Path(garment_image) if isinstance(garment_image, (str, Path)) else None
            outfit = styling_context if styling_context else {"title": "Casual Classic"}

            preview_url = self.compositor_fallback.generate(
                outfit=outfit,
                detected_colour_hex=kwargs.get("detected_colour_hex", "#000000"),
                detected_colour_shade=kwargs.get("detected_colour_shade", "Classic"),
                detected_clothing_type=category,
                output_dir=settings.VIRTUAL_TRYON_DIR,
                user_image_path=user_path,
                garment_image_path=garment_path,
                semantic_data=kwargs.get("semantic_data"),
            )

            return {
                "success": True,
                "result_type": "outfit_preview",
                "image_url": preview_url,
                "provider": "preview_compositor",
                "category": category,
                "message": "FASHN VTON unavailable; generated AI Outfit Preview.",
            }
        except Exception as comp_err:
            logger.error("Compositor fallback failed: %s", comp_err)
            return {
                "success": False,
                "result_type": "unavailable",
                "image_url": None,
                "provider": "none",
                "category": category,
                "error_code": "VTON_UNAVAILABLE",
                "message": f"Virtual try-on unavailable: {comp_err}",
            }


# Global singleton instance
_vton_singleton: Optional[DefaultVirtualTryOnProvider] = None


def get_virtual_tryon_provider() -> DefaultVirtualTryOnProvider:
    global _vton_singleton
    if _vton_singleton is None:
        _vton_singleton = DefaultVirtualTryOnProvider()
    return _vton_singleton
