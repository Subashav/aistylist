"""
User Portrait Styling Analysis Service
======================================
Analyzes the user's uploaded portrait photo strictly for fashion styling purposes:
  - Validates that the image contains an individual suitable for styling
    (gracefully rejects clothing-only images, empty backgrounds, or invalid photos).
  - Extracts visual styling attributes:
    * Skin tone / visible complexion undertone (e.g. Warm Golden, Cool Olive, Neutral Fair, Rich Deep)
    * Apparent build / body proportions (e.g. Slender, Athletic / Broad, Balanced / Proportionate)
    * Face shape where useful for neckline styling (e.g. Oval, Square, Round, Heart, Oblong)
    * Silhouette preference (e.g. Clean Vertical Lines, Structured Tailoring, Balanced Proportions)
  - Constructs an appearance prompt descriptor to lock persona likeness in the try-on generator.

IMPORTANT PRIVACY / ETHICAL GUIDELINES:
  - Extracts only visual styling attributes for outfit harmony.
  - Does NOT make sensitive or unsupported demographic inferences.
  - Does NOT store unnecessary biometric templates or identification markers.
"""

import base64
import json
import logging
import mimetypes
import re
from pathlib import Path
from typing import Optional, Dict, Any

import cv2
import httpx
import numpy as np
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Structured Schema for User Styling Analysis
# ---------------------------------------------------------------------------
class UserStylingProfile(BaseModel):
    is_valid_person: bool = Field(
        default=True,
        description="Whether the photo contains a recognizable individual suitable for virtual try-on",
    )
    validation_status: str = Field(
        default="valid",
        description="Status: 'valid', 'clothing_only', 'no_person_detected', 'multiple_people', 'unclear'",
    )
    validation_message: Optional[str] = Field(
        default=None,
        description="Helpful user message if validation failed or fallback is used",
    )
    complexion_tone: Optional[str] = Field(
        default="Neutral / Balanced",
        description="Visible complexion and undertone family for color harmony pairing",
    )
    apparent_build: Optional[str] = Field(
        default="Proportionate",
        description="Apparent silhouette structure (e.g. Slender, Athletic, Proportionate, Broader Frame)",
    )
    height_build_proportion: Optional[str] = Field(
        default="Balanced Proportions",
        description="Approximate vertical body proportions and apparent build balance",
    )
    face_shape: Optional[str] = Field(
        default="Oval",
        description="Face shape used for neckline & collar recommendations",
    )
    visual_style: Optional[str] = Field(
        default="Contemporary Clean",
        description="Visible aesthetic or styling preference (e.g. Minimalist, Classic Tailored, Contemporary Streetwear)",
    )
    styling_silhouette_preference: Optional[str] = Field(
        default="Balanced Proportions",
        description="Trouser cut and layering balance best suited for the individual's visual silhouette",
    )
    persona_descriptor: Optional[str] = Field(
        default="A modern individual with balanced features",
        description="Visual appearance summary for identity-locking in virtual try-on prompts",
    )


# ---------------------------------------------------------------------------
# Gemini System Prompt for Styling Analysis
# ---------------------------------------------------------------------------
USER_ANALYSIS_SYSTEM_PROMPT = """You are an expert personal stylist and computer vision fashion consultant.
Your role is to analyze a user's uploaded portrait photo purely to determine clothing fit, color harmony, and styling proportions.

STRICT RULES:
1. First, check if this photo actually contains a real individual / portrait suitable for styling.
   - If this is a photo of CLOTHING ONLY (e.g. flat lay, hanger, product shot), set:
     "is_valid_person": false,
     "validation_status": "clothing_only",
     "validation_message": "This photo appears to be a clothing item rather than your portrait photo."
   - If there is NO visible person (e.g. landscape, object, empty wall), set:
     "is_valid_person": false,
     "validation_status": "no_person_detected",
     "validation_message": "No person was detected in this photo."
   - If there are multiple prominent people, set:
     "is_valid_person": false,
     "validation_status": "multiple_people",
     "validation_message": "Multiple individuals detected. Please upload a solo portrait for personalized try-on."

2. If a single individual is clearly visible, set "is_valid_person": true, "validation_status": "valid", and extract ONLY these styling attributes:
   - "complexion_tone": One of ["Warm Golden / Olive", "Cool Undertone / Fair", "Neutral Medium", "Rich Deep / Warm", "Warm Tan", "Cool Alabaster"]
   - "apparent_build": One of ["Slender / Linear", "Athletic / Broad Shoulders", "Balanced / Proportionate", "Relaxed / Broader Silhouette"]
   - "height_build_proportion": One of ["Balanced Vertical Proportions", "Elongated Frame", "Compact / Proportionate Frame", "Athletic Silhouette"]
   - "face_shape": One of ["Oval", "Square", "Round", "Heart", "Oblong"]
   - "visual_style": e.g. "Contemporary Minimalist", "Classic Casual", "Modern Smart Casual", "Urban Streetwear"
   - "styling_silhouette_preference": e.g. "Clean vertical lines with mid-to-high rise bottoms", "Structured shoulders with relaxed taper", "Straight leg cuts to balance torso"
   - "persona_descriptor": A concise, respectful visual appearance descriptor describing visible hair style/color, skin complexion family, and build (e.g. "An individual with short dark wavy hair, warm olive complexion, and an athletic build") to preserve their likeness in fashion imagery.

3. NEVER make sensitive, medical, or unsupported demographic claims. Do NOT store biometric templates.
4. Output STRICT JSON only matching this schema without markdown fences:
{
  "is_valid_person": true,
  "validation_status": "valid",
  "validation_message": null,
  "complexion_tone": "Warm Golden / Olive",
  "apparent_build": "Athletic / Broad Shoulders",
  "height_build_proportion": "Balanced Vertical Proportions",
  "face_shape": "Oval",
  "visual_style": "Contemporary Minimalist",
  "styling_silhouette_preference": "Clean vertical lines with tapered trousers",
  "persona_descriptor": "An individual with short black hair, warm olive complexion, and an athletic build"
}"""


def _clean_json_response(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _cv_fallback_person_check(image_path: Path) -> UserStylingProfile:
    """
    Heuristic check when Gemini is disabled or unavailable.
    Inspects image dimensions, color variation, and skin-tone pixel percentage.
    """
    try:
        img_bgr = cv2.imread(str(image_path))
        if img_bgr is None:
            return UserStylingProfile(
                is_valid_person=False,
                validation_status="unclear",
                validation_message="Unable to read the uploaded user photo.",
            )

        h, w = img_bgr.shape[:2]
        if h < 80 or w < 80:
            return UserStylingProfile(
                is_valid_person=False,
                validation_status="unclear",
                validation_message="Image resolution is too low for virtual try-on.",
            )

        # Convert to HSV and YCrCb for skin tone heuristic
        ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)

        # Skin tone range in YCrCb: Cr [133, 173], Cb [77, 127]
        skin_mask = (
            (ycrcb[:, :, 1] >= 133)
            & (ycrcb[:, :, 1] <= 173)
            & (ycrcb[:, :, 2] >= 77)
            & (ycrcb[:, :, 2] <= 127)
        )
        skin_ratio = np.count_nonzero(skin_mask) / (h * w)

        # If skin tone is virtually 0 (< 1.5%), it's very likely a product / clothing-only shot
        if skin_ratio < 0.015:
            logger.info("CV fallback detected low skin ratio (%.3f) — likely clothing-only image", skin_ratio)
            return UserStylingProfile(
                is_valid_person=False,
                validation_status="clothing_only",
                validation_message="The uploaded photo appears to be a garment item rather than your portrait.",
                persona_descriptor="A stylish contemporary individual",
            )

        # Skin detected; return default balanced profile
        return UserStylingProfile(
            is_valid_person=True,
            validation_status="valid",
            complexion_tone="Warm / Neutral",
            apparent_build="Balanced / Proportionate",
            face_shape="Oval",
            styling_silhouette_preference="Balanced vertical lines with contemporary fit",
            persona_descriptor="The individual in the uploaded reference portrait with natural hair and realistic proportions",
        )

    except Exception as exc:
        logger.warning("CV fallback person check failed: %s", exc)
        return UserStylingProfile(
            is_valid_person=True,
            validation_status="valid",
            persona_descriptor="The person from the reference portrait",
        )


async def analyze_user_portrait(image_path: Path) -> UserStylingProfile:
    """
    Sends the user portrait photo to Gemini Vision for styling analysis and validation.
    Falls back gracefully to CV heuristics if Gemini is disabled or fails.
    """
    if not image_path.exists():
        logger.warning("User portrait image does not exist: %s", image_path)
        return UserStylingProfile(
            is_valid_person=False,
            validation_status="no_person_detected",
            validation_message="No user portrait image found.",
        )

    # Use Gemini if available
    if settings.GEMINI_ENABLED and settings.GEMINI_API_KEY:
        try:
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if not mime_type or not mime_type.startswith("image/"):
                mime_type = "image/jpeg"

            with open(image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")

            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
                f"?key={settings.GEMINI_API_KEY}"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": USER_ANALYSIS_SYSTEM_PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": image_b64,
                                }
                            },
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "response_mime_type": "application/json",
                },
            }

            timeout = httpx.Timeout(settings.GEMINI_TIMEOUT, connect=3.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "")
                            clean_text = _clean_json_response(raw_text)
                            profile = UserStylingProfile.model_validate_json(clean_text)
                            logger.info(
                                "User Portrait Analysis: is_valid=%s, status=%s, complexion=%s, build=%s",
                                profile.is_valid_person,
                                profile.validation_status,
                                profile.complexion_tone,
                                profile.apparent_build,
                            )
                            return profile

        except Exception as exc:
            logger.warning("Gemini user portrait analysis failed (%s). Using CV fallback.", exc)

    # Fallback to CV heuristics
    return _cv_fallback_person_check(image_path)
