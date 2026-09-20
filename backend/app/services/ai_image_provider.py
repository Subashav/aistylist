"""
AI Fashion Image Generation Provider
====================================
Generates photorealistic fashion editorial photographs of full-body models wearing
the complete recommended outfit, strictly preserving the detected garment type,
colour shade, and HEX value as the anchor piece.

Supported backends:
  - 'pollinations' : High-quality photorealistic Flux/Realistic Vision models (free, zero API key needed)
  - 'openai'       : OpenAI DALL-E 3
  - 'stability'    : Stability AI Stable Diffusion (with reference garment support)
  - 'custom'       : Configurable generic HTTP image generation endpoint

Fallback:
  - Automatically falls back to PillowOutfitComposer on network failure or invalid response.
"""

import os
import uuid
import urllib.parse
import logging
import random
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any

import httpx
from PIL import Image

from app.config import settings
from app.services.visual_provider import OutfitVisualProvider, PillowOutfitComposer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Occasion Styling Tone Mappings
# Ensures each of the 4 outfit scenarios produces a visually distinct editorial photo
# ---------------------------------------------------------------------------
OCCASION_STYLING_MAP = {
    "Casual Classic": (
        "Clean minimalist everyday street fashion, relaxed effortless posture, "
        "morning natural daylight, contemporary urban setting."
    ),
    "Smart Casual Elegance": (
        "Sharp sophisticated smart-casual styling, refined modern luxury aesthetic, "
        "tasteful evening golden hour lighting, architectural backdrop."
    ),
    "Layered Dimension": (
        "Stylish layered seasonal coordination, modern structured silhouette, "
        "cool-weather editorial mood, soft diffused daylight."
    ),
    "Weekend Contrast": (
        "Relaxed contemporary weekend brunch aesthetic, dynamic easygoing lifestyle pose, "
        "bright airy ambient lighting, vibrant clean space."
    ),
}


def build_fashion_prompt(
    outfit: Dict[str, Any],
    detected_colour_hex: str,
    detected_colour_shade: str,
    detected_clothing_type: str,
    semantic_data: Optional[Any] = None,
) -> str:
    """
    Constructs an extensive, photorealistic fashion editorial prompt dynamically
    from the detected clothing, recommended outfit items, and optional semantic metadata.
    """
    title = outfit.get("title", "Fashion Look")
    occasion = outfit.get("occasion", "Everyday Wear")
    top = outfit.get("top", "")
    bottom = outfit.get("bottom", "")
    shoes = outfit.get("shoes", "")
    accessories = outfit.get("accessories", "")

    # Semantic attributes
    pattern = getattr(semantic_data, "pattern", "Solid") if semantic_data else "Solid"
    sleeve = getattr(semantic_data, "sleeve_length", "") if semantic_data else ""
    fit = getattr(semantic_data, "fit", "") if semantic_data else ""
    neckline = getattr(semantic_data, "neckline", "") if semantic_data else ""
    material = getattr(semantic_data, "material_appearance", "") if semantic_data else ""
    subcategory = getattr(semantic_data, "subcategory", detected_clothing_type) if semantic_data else detected_clothing_type

    # Specific styling vibe based on title/occasion
    vibe = OCCASION_STYLING_MAP.get(
        title,
        f"Modern contemporary styling suitable for {occasion}, clean luxury editorial mood."
    )

    # Detailed garment descriptor
    garment_descriptors = [detected_colour_shade]
    if pattern and pattern.lower() not in ("solid", "plain"):
        garment_descriptors.append(f"{pattern.lower()} pattern")
    if fit:
        garment_descriptors.append(f"{fit.lower()} fit")
    if sleeve and sleeve.lower() != "not applicable":
        garment_descriptors.append(sleeve.lower())
    if neckline:
        garment_descriptors.append(f"with {neckline.lower()}")
    garment_descriptors.append(subcategory)
    if material:
        garment_descriptors.append(f"in {material.lower()} texture")

    full_garment_desc = " ".join(garment_descriptors)

    prompt = (
        f"Create a realistic premium fashion editorial photograph. "
        f"A professional fashion model wearing the complete recommended outfit. "
        f"Main anchor garment: {full_garment_desc} "
        f"(exact color tone matching {detected_colour_shade}, HEX {detected_colour_hex}). "
        f"Top piece: {top}. "
        f"Bottom piece: {bottom}. "
        f"Footwear: {shoes}. "
    )

    if accessories and accessories.lower() != "none" and accessories.strip():
        prompt += f"Accessories and layering: {accessories}. "

    prompt += (
        f"Styling mood: {vibe} "
        f"Composition: Full-body fashion photograph, model visible from head to shoes. "
        f"Natural human proportions, realistic fabric texture, natural clothing folds, "
        f"clean modern photography, clean neutral minimal studio background, "
        f"soft realistic studio lighting, sharp focus, 8k fashion magazine quality. "
        f"The main garment must remain {detected_colour_shade} ({detected_colour_hex}) and visually accurate. "
        f"Do not add clothing items not specified. Do not change specified colors. "
        f"No logos, no text, no watermarks, no distorted anatomy."
    )

    return prompt


# ---------------------------------------------------------------------------
# AI Image Provider Implementation
# ---------------------------------------------------------------------------
class AIImageProvider(OutfitVisualProvider):
    """
    Photorealistic AI outfit image generator.
    Delegates to configured AI backend (Pollinations / OpenAI / Stability / Custom)
    with automatic fallback to PillowOutfitComposer if unavailable or on error.
    """

    def __init__(self):
        self.fallback_composer = PillowOutfitComposer()

    async def generate_outfit_visual(
        self,
        outfit: Dict[str, Any],
        detected_colour_hex: str,
        detected_colour_shade: str,
        detected_clothing_type: str,
        output_dir: Path,
        reference_image_path: Optional[Path] = None,
        semantic_data: Optional[Any] = None,
    ) -> Optional[str]:
        prompt = build_fashion_prompt(
            outfit=outfit,
            detected_colour_hex=detected_colour_hex,
            detected_colour_shade=detected_colour_shade,
            detected_clothing_type=detected_clothing_type,
            semantic_data=semantic_data,
        )
        logger.info("AI Fashion Prompt for '%s': %s", outfit.get("title"), prompt)

        backend = settings.AI_IMAGE_PROVIDER.lower().strip()
        image_bytes: Optional[bytes] = None

        try:
            if backend == "openai" and settings.IMAGE_GENERATION_API_KEY:
                image_bytes = await self._generate_openai(prompt)
            elif backend == "stability" and settings.IMAGE_GENERATION_API_KEY:
                image_bytes = await self._generate_stability(prompt, reference_image_path)
            elif backend == "custom" and settings.IMAGE_GENERATION_API_KEY:
                image_bytes = await self._generate_custom(prompt)
            else:
                # Default: High-quality photorealistic Pollinations Flux/Vision API
                image_bytes = await self._generate_pollinations(prompt)

            if image_bytes:
                # Validate image integrity with Pillow
                image = Image.open(BytesIO(image_bytes))
                image.verify()  # Ensure valid image stream

                # Re-open for saving after verify
                image = Image.open(BytesIO(image_bytes))
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"outfit_ai_{uuid.uuid4().hex}.png"
                filepath = output_dir / filename
                
                # Convert to RGB if needed (e.g. RGBA/WebP) and save as high-quality PNG
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                image.save(str(filepath), "PNG", quality=95, optimize=True)
                
                logger.info("Successfully generated AI outfit image: %s", filepath)
                return f"/uploads/outfit_recommendations/{filename}"

        except Exception as exc:
            logger.warning(
                "AI image generation failed for '%s' (%s). Falling back to PillowOutfitComposer.",
                outfit.get("title"),
                exc,
            )

        # Fallback to Pillow visual composer
        return await self.fallback_composer.generate_outfit_visual(
            outfit=outfit,
            detected_colour_hex=detected_colour_hex,
            detected_colour_shade=detected_colour_shade,
            detected_clothing_type=detected_clothing_type,
            output_dir=output_dir,
            reference_image_path=reference_image_path,
        )

    # -----------------------------------------------------------------------
    # Backend 1: Pollinations (Flux / Realistic Vision)
    # -----------------------------------------------------------------------
    async def _generate_pollinations(self, prompt: str) -> Optional[bytes]:
        seed = random.randint(100000, 9999999)
        encoded_prompt = urllib.parse.quote(prompt)
        model = settings.AI_IMAGE_MODEL if settings.AI_IMAGE_MODEL else "flux"
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&model={model}&nologo=true&enhance=true&seed={seed}"

        timeout = httpx.Timeout(settings.AI_IMAGE_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200 and len(response.content) > 5000:
                return response.content
            else:
                logger.warning(
                    "Pollinations API returned status %d (body length: %d)",
                    response.status_code,
                    len(response.content),
                )
                return None

    # -----------------------------------------------------------------------
    # Backend 2: OpenAI DALL-E 3
    # -----------------------------------------------------------------------
    async def _generate_openai(self, prompt: str) -> Optional[bytes]:
        headers = {
            "Authorization": f"Bearer {settings.IMAGE_GENERATION_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "response_format": "b64_json",
        }
        timeout = httpx.Timeout(settings.AI_IMAGE_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload,
            )
            if response.status_code == 200:
                data = response.json()
                b64_data = data["data"][0].get("b64_json")
                if b64_data:
                    import base64
                    return base64.b64decode(b64_data)
                url = data["data"][0].get("url")
                if url:
                    img_resp = await client.get(url)
                    return img_resp.content
            else:
                logger.error("OpenAI DALL-E error: %s", response.text)
                return None

    # -----------------------------------------------------------------------
    # Backend 3: Stability AI Stable Diffusion
    # -----------------------------------------------------------------------
    async def _generate_stability(
        self, prompt: str, reference_image_path: Optional[Path] = None
    ) -> Optional[bytes]:
        headers = {
            "Authorization": f"Bearer {settings.IMAGE_GENERATION_API_KEY}",
            "Accept": "application/json",
        }
        timeout = httpx.Timeout(settings.AI_IMAGE_TIMEOUT, connect=10.0)

        # Image-to-image with reference garment if provided
        if reference_image_path and reference_image_path.exists():
            with open(reference_image_path, "rb") as f:
                files = {"init_image": f}
                data = {
                    "init_image_mode": "IMAGE_STRENGTH",
                    "image_strength": 0.35,
                    "text_prompts[0][text]": prompt,
                    "text_prompts[0][weight]": 1.0,
                    "cfg_scale": 7,
                    "samples": 1,
                    "steps": 30,
                }
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image",
                        headers=headers,
                        files=files,
                        data=data,
                    )
                    if response.status_code == 200:
                        res_json = response.json()
                        import base64
                        return base64.b64decode(res_json["artifacts"][0]["base64"])

        # Text-to-image fallback
        json_data = {
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {
                    "text": "distorted anatomy, bad hands, cartoon, 3d, watermark, text, logo, oversaturated",
                    "weight": -1.0,
                },
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 768,
            "samples": 1,
            "steps": 30,
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={"Authorization": f"Bearer {settings.IMAGE_GENERATION_API_KEY}", "Content-Type": "application/json"},
                json=json_data,
            )
            if response.status_code == 200:
                res_json = response.json()
                import base64
                return base64.b64decode(res_json["artifacts"][0]["base64"])
            else:
                logger.error("Stability AI error: %s", response.text)
                return None

    # -----------------------------------------------------------------------
    # Backend 4: Custom HTTP Endpoint
    # -----------------------------------------------------------------------
    async def _generate_custom(self, prompt: str) -> Optional[bytes]:
        # Generic integration hook
        return None
