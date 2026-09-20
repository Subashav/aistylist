"""
FASHN VTON v1.5 Local Provider
==============================
Executes photorealistic virtual try-on on the local NVIDIA GPU using FASHN VTON v1.5.
Guarded with a sequential execution lock and memory optimization to operate safely
within 4 GB VRAM on an NVIDIA RTX 3050 Laptop GPU.
"""

import os
import sys
import time
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union, Literal
from io import BytesIO

import torch
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

# Global concurrency lock: Strictly 1 inference job on GPU at a time to prevent OOM
VTON_SEMAPHORE = asyncio.Semaphore(1)


def normalize_clothing_category(raw_category: str) -> Literal["tops", "bottoms", "one-pieces"]:
    """
    Maps varied user, CV, or Gemini category names into the 3 categories
    supported by FASHN VTON: 'tops', 'bottoms', 'one-pieces'.
    """
    cat = (raw_category or "").lower().strip()

    bottom_keywords = [
        "bottom", "pant", "jean", "trouser", "chino", "short",
        "skirt", "legging", "sweatpant", "cargo"
    ]
    if any(k in cat for k in bottom_keywords):
        return "bottoms"

    one_piece_keywords = [
        "one-piece", "one_piece", "dress", "jumpsuit", "romper",
        "gown", "overall", "bodysuit"
    ]
    if any(k in cat for k in one_piece_keywords):
        return "one-pieces"

    # Default to tops (t-shirt, shirt, polo, hoodie, jacket, blazer, sweater, top)
    return "tops"


class FASHNVTONLocalProvider:
    """
    Wraps the local FASHN VTON v1.5 pipeline with GPU memory safeguards,
    sequential inference, and output persistence.
    """

    def __init__(self, weights_dir: Optional[Path] = None):
        self.weights_dir = Path(weights_dir) if weights_dir else settings.VTON_WEIGHTS_DIR
        self.output_dir = settings.VIRTUAL_TRYON_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = None
        self._is_ready = False
        self._load_error: Optional[str] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """
        Loads FASHN VTON TryOnPipeline once into memory.
        Sets bfloat16 / fp16 and eval mode.
        """
        if self._is_ready and self.pipeline is not None:
            return

        t0 = time.perf_counter()
        logger.info("Initializing FASHN VTON v1.5 pipeline from %s on device: %s", self.weights_dir, self.device)

        try:
            from app.services.fashn_vton import TryOnPipeline

            self.pipeline = TryOnPipeline(
                weights_dir=str(self.weights_dir),
                device=self.device,
            )
            self._is_ready = True
            self._load_error = None
            elapsed = time.perf_counter() - t0
            logger.info("FASHN VTON v1.5 successfully loaded in %.2fs", elapsed)

        except Exception as e:
            self._is_ready = False
            self._load_error = str(e)
            logger.error("Failed to load FASHN VTON v1.5: %s", e, exc_info=True)

    @property
    def is_ready(self) -> bool:
        return self._is_ready and self.pipeline is not None

    @property
    def load_error(self) -> Optional[str]:
        return self._load_error

    def _load_image(self, img_input: Union[str, Path, bytes, Image.Image]) -> Image.Image:
        """Loads and normalizes an input image to RGB PIL Image."""
        if isinstance(img_input, (str, Path)):
            path = Path(img_input)
            if not path.exists():
                raise FileNotFoundError(f"Input image not found: {path}")
            return Image.open(path).convert("RGB")
        elif isinstance(img_input, bytes):
            return Image.open(BytesIO(img_input)).convert("RGB")
        elif isinstance(img_input, Image.Image):
            return img_input.convert("RGB")
        raise ValueError(f"Unsupported image input type: {type(img_input)}")

    async def generate_try_on(
        self,
        person_image: Union[str, Path, bytes, Image.Image],
        garment_image: Union[str, Path, bytes, Image.Image],
        category: str = "tops",
        styling_context: Optional[Dict[str, Any]] = None,
        num_timesteps: int = 25,
        guidance_scale: float = 1.5,
        seed: int = 42,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Executes one virtual try-on inference safely under the global semaphore.
        """
        if not self.is_ready:
            self.load_model()
            if not self.is_ready:
                return {
                    "success": False,
                    "result_type": "unavailable",
                    "error_code": "VTON_UNAVAILABLE",
                    "message": f"FASHN VTON model is not loaded: {self._load_error}",
                }

        fashn_cat = normalize_clothing_category(category)

        # Acquire lock to ensure only 1 GPU inference at a time
        async with VTON_SEMAPHORE:
            t0 = time.perf_counter()
            try:
                # Run the blocking PyTorch inference in a worker thread
                loop = asyncio.get_running_loop()

                def _run_inference():
                    person_pil = self._load_image(person_image)
                    garment_pil = self._load_image(garment_image)

                    with torch.inference_mode():
                        output = self.pipeline(
                            person_image=person_pil,
                            garment_image=garment_pil,
                            category=fashn_cat,
                            num_samples=1,
                            num_timesteps=num_timesteps,
                            guidance_scale=guidance_scale,
                            seed=seed,
                        )

                    # Free VRAM cache immediately after inference
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

                    return output.images[0]

                result_img = await loop.run_in_executor(None, _run_inference)

                # Save output image
                filename = f"tryon_{uuid.uuid4().hex}.png"
                save_path = self.output_dir / filename
                result_img.save(str(save_path), "PNG", quality=95)

                elapsed = time.perf_counter() - t0
                logger.info("FASHN VTON generated '%s' in %.2fs", filename, elapsed)

                return {
                    "success": True,
                    "result_type": "actual_try_on",
                    "image_url": f"/uploads/virtual_tryon/{filename}",
                    "provider": "fashn_vton_local",
                    "category": fashn_cat,
                    "execution_time_seconds": round(elapsed, 2),
                    "error": None,
                }

            except Exception as err:
                logger.error("Error during FASHN VTON generation: %s", err, exc_info=True)
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                return {
                    "success": False,
                    "result_type": "unavailable",
                    "error_code": "VTON_INFERENCE_ERROR",
                    "message": str(err),
                }
