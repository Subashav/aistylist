"""
Gemini Image Generation Provider (Virtual Try-On)
=================================================
Executes multimodal virtual try-on image generation using Google Gemini
(e.g., gemini-3.1-flash-image) with dual image references (person + garment).
"""

import os
import uuid
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from io import BytesIO

import httpx
from PIL import Image

from app.config import settings
from app.services.tryon_prompt_builder import build_gemini_tryon_prompt

logger = logging.getLogger(__name__)


class GeminiImageProvider:
    """
    Client for Gemini Image Generation API (gemini-3.1-flash-image).
    Passes user portrait and garment reference images with controlled styling instructions.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_IMAGE_MODEL
        self.timeout = settings.GEMINI_IMAGE_TIMEOUT
        self.output_dir = settings.VIRTUAL_TRYON_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _encode_image(self, image_input: Union[str, Path, bytes, Image.Image]) -> tuple[str, str]:
        """
        Converts image input to base64 string and mime type.
        Resizes large images if needed to stay within optimal token limits.
        """
        if isinstance(image_input, (str, Path)):
            path = Path(image_input)
            if not path.exists():
                raise FileNotFoundError(f"Reference image not found: {path}")
            with Image.open(path) as img:
                img_rgb = img.convert("RGB")
                # Optimize dimensions for prompt reference
                if max(img_rgb.size) > 1024:
                    img_rgb.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                buf = BytesIO()
                img_rgb.save(buf, format="JPEG", quality=90)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                return b64, "image/jpeg"

        elif isinstance(image_input, bytes):
            with Image.open(BytesIO(image_input)) as img:
                img_rgb = img.convert("RGB")
                if max(img_rgb.size) > 1024:
                    img_rgb.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                buf = BytesIO()
                img_rgb.save(buf, format="JPEG", quality=90)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                return b64, "image/jpeg"

        elif isinstance(image_input, Image.Image):
            img_rgb = image_input.convert("RGB")
            if max(img_rgb.size) > 1024:
                img_rgb.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            buf = BytesIO()
            img_rgb.save(buf, format="JPEG", quality=90)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return b64, "image/jpeg"

        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    async def generate_tryon(
        self,
        person_image: Union[str, Path, bytes, Image.Image],
        garment_image: Union[str, Path, bytes, Image.Image],
        outfit: Dict[str, Any],
        detected_colour_shade: str = "Classic",
        detected_colour_hex: str = "#000000",
        category: str = "T-shirt",
        user_persona: Optional[str] = None,
        semantic_data: Optional[Any] = None,
        styling_instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calls Gemini Image Generation model with Person + Garment references.
        Returns:
            {
                "success": bool,
                "image_url": str,
                "provider": "gemini",
                "model": "gemini-3.1-flash-image",
                "try_on_type": "gemini_personalized_try_on" | "outfit_preview",
                "error": Optional[str]
            }
        """
        if not settings.GEMINI_IMAGE_ENABLED or not self.api_key:
            logger.warning("Gemini Image generation disabled or missing API key.")
            return {
                "success": False,
                "image_url": None,
                "provider": "gemini",
                "model": self.model,
                "try_on_type": "outfit_preview",
                "error": "Gemini Image API is disabled or unconfigured",
            }

        prompt = build_gemini_tryon_prompt(
            outfit=outfit,
            detected_colour_shade=detected_colour_shade,
            detected_colour_hex=detected_colour_hex,
            detected_clothing_type=category,
            user_persona=user_persona,
            semantic_data=semantic_data,
            styling_instructions=styling_instructions,
        )

        try:
            person_b64, person_mime = self._encode_image(person_image)
            garment_b64, garment_mime = self._encode_image(garment_image)

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inlineData": {
                                    "mimeType": person_mime,
                                    "data": person_b64,
                                }
                            },
                            {
                                "inlineData": {
                                    "mimeType": garment_mime,
                                    "data": garment_b64,
                                }
                            },
                        ]
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["IMAGE"],
                },
            }

            logger.info("Requesting Gemini Try-On from model: %s for '%s'", self.model, outfit.get("title"))

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)

            if resp.status_code != 200:
                err_data = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
                err_msg = err_data.get("error", {}).get("message", resp.text[:200])
                logger.warning("Gemini Image API returned status %s: %s", resp.status_code, err_msg)
                return {
                    "success": False,
                    "image_url": None,
                    "provider": "gemini",
                    "model": self.model,
                    "try_on_type": "outfit_preview",
                    "error": f"Gemini API {resp.status_code}: {err_msg}",
                }

            result_data = resp.json()
            candidates = result_data.get("candidates", [])
            if not candidates:
                logger.warning("No candidates returned in Gemini Image response: %s", result_data)
                return {
                    "success": False,
                    "image_url": None,
                    "provider": "gemini",
                    "model": self.model,
                    "try_on_type": "outfit_preview",
                    "error": "No image candidates generated",
                }

            parts = candidates[0].get("content", {}).get("parts", [])
            image_bytes = None
            for p in parts:
                inline = p.get("inlineData")
                if inline and inline.get("data"):
                    image_bytes = base64.b64decode(inline["data"])
                    break

            if not image_bytes:
                logger.warning("No inline image data found in Gemini parts: %s", [list(p.keys()) for p in parts])
                return {
                    "success": False,
                    "image_url": None,
                    "provider": "gemini",
                    "model": self.model,
                    "try_on_type": "outfit_preview",
                    "error": "No image bytes returned in candidate content",
                }

            # Save generated image
            filename = f"look_{uuid.uuid4().hex}.png"
            filepath = self.output_dir / filename
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            logger.info("Saved Gemini Try-On image to: %s", filepath)

            return {
                "success": True,
                "image_url": f"/uploads/virtual_tryon/{filename}",
                "provider": "gemini",
                "model": self.model,
                "try_on_type": "gemini_personalized_try_on",
                "error": None,
            }

        except Exception as exc:
            logger.error("Error during Gemini try-on generation: %s", exc, exc_info=True)
            return {
                "success": False,
                "image_url": None,
                "provider": "gemini",
                "model": self.model,
                "try_on_type": "outfit_preview",
                "error": str(exc),
            }
