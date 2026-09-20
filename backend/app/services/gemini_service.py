"""
Gemini Vision Semantic Garment Analysis Service
===============================================
Extracts rich semantic metadata from garment photos including:
  - Precise subcategory (T-shirt, Polo, Button-Down, Blazer, Hoodie, Jeans...)
  - Pattern recognition (Solid, Striped, Checked, Floral, Graphic...)
  - Fit & Silhouette (Slim, Regular, Relaxed, Oversized, Tailored)
  - Sleeve length & Neckline style
  - Formality & Aesthetic (Casual, Smart Casual, Business Formal, Streetwear)
  - Material texture appearance (Cotton, Denim, Linen, Knit, Leather...)

IMPORTANT:
  - This service does NOT override the OpenCV CV pipeline's measured color (HEX / LAB)
    when CV confidence is high. It enriches understanding of garment architecture.
  - Returns None gracefully on any API error, timeout, or missing key.
"""

import asyncio
import base64
import json
import logging
import mimetypes
import re
from pathlib import Path
from typing import List, Optional, Any, Dict

import httpx
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Structured Pydantic Schema for Garment Semantic Data
# ---------------------------------------------------------------------------
class GarmentAnalysis(BaseModel):
    category: str = Field(
        default="Top",
        description="Major garment class: Top, Bottom, Outerwear, One-Piece, Footwear",
    )
    subcategory: str = Field(
        default="T-shirt",
        description="Specific garment item: T-shirt, Polo Shirt, Button-Down Shirt, Blazer, Hoodie, Sweater, Jacket, Jeans, Chinos, Trousers, Shorts, Dress, etc.",
    )
    pattern: str = Field(
        default="Solid",
        description="Visual fabric pattern: Solid, Striped, Checked / Plaid, Floral, Graphic / Printed, Polka Dot, Textured",
    )
    sleeve_length: str = Field(
        default="Short Sleeve",
        description="Sleeve structure: Short Sleeve, Long Sleeve, Sleeveless, 3/4 Sleeve, Not Applicable",
    )
    neckline: str = Field(
        default="Crewneck",
        description="Neckline or collar type: Crewneck, V-neck, Polo Collar, Button-down Collar, Hooded, Lapel, Turtleneck, Scoop",
    )
    fit: str = Field(
        default="Regular",
        description="Garment fit: Slim, Regular, Relaxed, Oversized, Tailored",
    )
    formality: str = Field(
        default="Casual",
        description="Primary formality level: Casual, Smart Casual, Business Formal, Streetwear, Athletic",
    )
    material_appearance: str = Field(
        default="Cotton",
        description="Perceived fabric texture: Cotton, Denim, Linen, Wool / Knit, Leather, Silk / Satin, Synthetic",
    )
    style_keywords: List[str] = Field(
        default_factory=lambda: ["modern", "versatile"],
        description="Descriptive styling keywords",
    )
    confidence: float = Field(
        default=0.85,
        description="Model confidence score between 0.0 and 1.0",
    )


# ---------------------------------------------------------------------------
# Gemini System Prompt & Request Construction
# ---------------------------------------------------------------------------
GEMINI_SYSTEM_PROMPT = """You are an expert fashion technologist and stylist.
Analyze the provided clothing photo and return a strict, valid JSON object describing its semantic fashion attributes.

Rules:
1. Return ONLY valid JSON matching this schema:
{
  "category": "Top" | "Bottom" | "Outerwear" | "One-Piece",
  "subcategory": "T-shirt" | "Polo Shirt" | "Button-Down Shirt" | "Blazer" | "Hoodie" | "Sweater" | "Cardigan" | "Jacket" | "Coat" | "Jeans" | "Chinos" | "Trousers" | "Shorts" | "Dress" | "Skirt",
  "pattern": "Solid" | "Striped" | "Checked / Plaid" | "Floral" | "Graphic / Printed" | "Polka Dot" | "Textured",
  "sleeve_length": "Short Sleeve" | "Long Sleeve" | "Sleeveless" | "3/4 Sleeve" | "Not Applicable",
  "neckline": "Crewneck" | "V-neck" | "Polo Collar" | "Button-down Collar" | "Hooded" | "Lapel" | "Turtleneck" | "Scoop",
  "fit": "Slim" | "Regular" | "Relaxed" | "Oversized" | "Tailored",
  "formality": "Casual" | "Smart Casual" | "Business Formal" | "Streetwear" | "Athletic",
  "material_appearance": "Cotton" | "Denim" | "Linen" | "Wool / Knit" | "Leather" | "Silk / Satin" | "Synthetic",
  "style_keywords": ["keyword1", "keyword2"],
  "confidence": 0.95
}

2. Do NOT output markdown code blocks or explanatory text outside the JSON.
3. Be precise in distinguishing a Blazer from a Suit Jacket or Casual Jacket, a Polo from a T-shirt, and Striped vs Solid."""


def _clean_json_response(raw_text: str) -> str:
    """Extracts raw JSON string by stripping markdown formatting if present."""
    text = raw_text.strip()
    if text.startswith("```"):
        # Remove ```json and trailing ```
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


async def analyze_garment_semantics(image_path: Path) -> Optional[GarmentAnalysis]:
    """
    Sends the clothing photo to Gemini Vision for structured semantic classification.
    
    Returns:
        GarmentAnalysis object if successful, or None on failure / disabled.
    """
    if not settings.GEMINI_ENABLED or not settings.GEMINI_API_KEY:
        logger.debug("Gemini semantic analysis is disabled or API key is not configured.")
        return None

    if not image_path.exists():
        logger.warning("Image path does not exist for Gemini analysis: %s", image_path)
        return None

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
                        {"text": GEMINI_SYSTEM_PROMPT},
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
            response = None
            # Try up to 2 attempts for transient 503/429 spikes
            for attempt in range(2):
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    break
                elif response.status_code in (503, 429) and attempt == 0:
                    await asyncio.sleep(1.0)
                    continue
                else:
                    break

            if not response or response.status_code != 200:
                logger.warning(
                    "Gemini API returned HTTP %s: %s",
                    response.status_code if response else "NO_RESPONSE",
                    response.text if response else "",
                )
                return None

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini returned empty candidates.")
                return None

            content_parts = candidates[0].get("content", {}).get("parts", [])
            if not content_parts:
                return None

            raw_text = content_parts[0].get("text", "")
            clean_text = _clean_json_response(raw_text)
            
            # Validate with Pydantic
            analysis = GarmentAnalysis.model_validate_json(clean_text)
            logger.info(
                "Gemini Semantic Analysis OK: subcategory=%s, pattern=%s, formality=%s",
                analysis.subcategory,
                analysis.pattern,
                analysis.formality,
            )
            return analysis

    except Exception as exc:
        logger.warning(
            "Gemini semantic analysis encountered an error (%s). Falling back gracefully to CV.",
            exc,
        )
        return None


# ---------------------------------------------------------------------------
# Gemini Personalized Fit & Silhouette Analysis
# ---------------------------------------------------------------------------
PERSONALIZED_FIT_SYSTEM_PROMPT = """You are a senior luxury fashion consultant and body-silhouette stylist.
Analyze how the detected garment visually harmonizes with this specific user.
Strictly focus on visual styling principles, colour balance, and aesthetic proportions.
Do NOT make judgments about personal attractiveness or sensitive demographic assumptions.

Input context provided:
1. User styling attributes (complexion undertone, apparent build, face shape, silhouette balance).
2. Garment attributes (category, subcategory, exact colour shade, HEX, pattern, neckline, fit).

You must evaluate and return a strict JSON object:
{
  "garment_summary": "Concise garment title and attributes (e.g. Charcoal Grey T-shirt)",
  "how_it_works_with_you": "A cohesive 2-3 sentence analysis directly answering: (1) Does the colour complement the user's visible complexion? (2) Does the garment proportion work with their build? (3) Does the neckline suit their face shape? (4) Which trouser rise/cut and footwear proportions complete the silhouette?",
  "complexion_harmony": "Why this specific colour shade flatters their complexion undertones",
  "silhouette_advice": "Specific guidance on fit approach (relaxed/regular/slim) and bottom cut to balance proportions",
  "looks_reasons": {
    "Casual Classic": "Specific personalized reason why this casual pairing balances their proportions and complexion",
    "Smart Casual Elegance": "Specific personalized reason why this smart-casual tailored look elevates their posture",
    "Elevated Casual / Layered": "Specific personalized reason why this layered combination adds dimensional balance",
    "Evening Minimalist": "Specific personalized reason why this evening look anchors their visual silhouette"
  }
}
Output valid JSON only without markdown formatting."""


async def analyze_personalized_fit(
    colour_shade: str,
    hex_value: str,
    clothing_type: str,
    garment_semantics: Optional[GarmentAnalysis],
    user_profile: Any,
) -> Optional[dict]:
    """
    Calls Gemini to generate a tailored fit analysis evaluating colour,
    proportions, neckline, silhouette, and occasion-specific rationales.
    """
    if not settings.GEMINI_ENABLED or not settings.GEMINI_API_KEY:
        return None

    if not user_profile or not getattr(user_profile, "is_valid_person", True):
        return None

    try:
        subcat = getattr(garment_semantics, "subcategory", clothing_type) if garment_semantics else clothing_type
        pattern = getattr(garment_semantics, "pattern", "Solid") if garment_semantics else "Solid"
        neckline = getattr(garment_semantics, "neckline", "Crewneck") if garment_semantics else "Crewneck"
        fit = getattr(garment_semantics, "fit", "Regular") if garment_semantics else "Regular"

        complexion = getattr(user_profile, "complexion_tone", "Neutral Medium")
        build = getattr(user_profile, "apparent_build", "Balanced / Proportionate")
        face = getattr(user_profile, "face_shape", "Oval")
        silhouette = getattr(user_profile, "styling_silhouette_preference", "Clean vertical lines")

        user_content = (
            f"USER ATTRIBUTES:\n"
            f"- Complexion Undertone: {complexion}\n"
            f"- Apparent Build: {build}\n"
            f"- Face Shape: {face}\n"
            f"- Preferred Silhouette: {silhouette}\n\n"
            f"GARMENT ATTRIBUTES:\n"
            f"- Item: {subcat}\n"
            f"- Exact Colour Shade: {colour_shade} (HEX: {hex_value})\n"
            f"- Pattern: {pattern}\n"
            f"- Neckline: {neckline}\n"
            f"- Fit: {fit}\n"
        )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
            f"?key={settings.GEMINI_API_KEY}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": PERSONALIZED_FIT_SYSTEM_PROMPT},
                        {"text": user_content},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
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
                        parsed = json.loads(clean_text)
                        logger.info("Gemini Personalized Fit Analysis generated successfully.")
                        return parsed

    except Exception as exc:
        logger.warning("Gemini personalized fit analysis failed (%s). Using rule synthesis.", exc)

    return None


# ---------------------------------------------------------------------------
# Distinct 4-Look Styling Plan System Prompt & Validation
# ---------------------------------------------------------------------------
DISTINCT_LOOKS_SYSTEM_PROMPT = """You are a premier fashion stylist and wardrobe director.
The user has uploaded a single anchor garment.
Your goal is to generate FOUR DISTINCT COMPLETE OUTFIT COMBINATIONS FOR THIS EXACT SAME GARMENT on this specific user.

CRITICAL RULES:
1. SAME ORIGINAL GARMENT:
   The user is wearing the exact same uploaded garment in all 4 looks.
   Do NOT change the uploaded piece. Do NOT substitute other tops/garments.

2. COMPLETE OUTFIT COMBINATIONS & FABRIC MATERIALS:
   - For every look, provide a complete head-to-toe combination: Bottom, Shoes, optional Layer (jacket/cardigan/overshirt), and Accessories.
   - For EACH piece, specify the EXACT FABRIC / MATERIAL TEXTURE (e.g., Brushed Cotton Twill, Raw Japanese Denim, Washed Linen, Tropical Wool, Full-Grain Calfskin Leather, Suede).
   - Provide a "fabric_harmony" analysis describing how the textures interact and elevate the wearer's proportions.
   - Provide a 3-to-4 color "palette" array with hex codes and styling roles (Anchor, Contrast, Accent, Neutral).

3. FOUR DISTINCT LOOK DIRECTIONS:
   - LOOK 1 ("Base Try-On"): The original garment with the best natural combination answering: "How does this garment look on me?".
     (e.g., straight-fit trousers, clean white leather sneakers, minimal watch).
   - LOOK 2 ("Contrast Try-On"): Keep the exact same original garment. Change the bottom colour to a contrasting harmonious tone with matching footwear answering: "How does this garment look with another pant colour?".
     (e.g., beige or light chinos, complementary footwear).
   - LOOK 3 ("Complete Outfit & Fabric Texture Guide"): Keep the exact same original garment. Create a clearly different styling direction with distinct textured pants, footwear, and layering piece answering: "How else can I style this garment?".
     (e.g., relaxed pleated trousers, retro runners, casual jacket or cardigan).
   - LOOK 4 ("Elevated Ensemble & Material Guide"): Keep the exact same original garment. Create an elevated complete combination with refined tailoring, dress footwear, and upscale accessories answering: "What is another complete way I can wear it?".
     (e.g., tailored wool trousers, loafers, dress watch).

4. STRICT DIVERSITY REQUIREMENT:
   - Bottom items, bottom colours, and materials MUST be distinct across all four looks.
   - Footwear must match the distinct styling direction.
   - Every look must have a unique combination signature.

Return ONLY a valid JSON object matching this schema:
{
  "looks": [
    {
      "look_id": 1,
      "title": "Base Try-On",
      "style": "Clean casual",
      "occasion": "Everyday Outing",
      "top": {
        "item": "Polo shirt",
        "color": "Royal Blue",
        "material": "Cotton Pique"
      },
      "bottom": {
        "item": "Straight-fit trousers",
        "color": "Black",
        "material": "Brushed Cotton Twill"
      },
      "shoes": {
        "item": "Sneakers",
        "color": "White",
        "material": "Full-Grain Leather"
      },
      "layer": {
        "item": "None",
        "color": "None",
        "material": "None"
      },
      "accessories": ["Minimal watch"],
      "fabric_harmony": "Matte cotton piqué paired with dense brushed twill and smooth leather creates balanced, everyday texture.",
      "palette": [
        {"name": "Royal Blue", "hex": "#4169E2", "role": "Anchor Top"},
        {"name": "Black", "hex": "#000000", "role": "Grounding Bottom"},
        {"name": "White", "hex": "#FFFFFF", "role": "Footwear Accent"}
      ],
      "explanation": "Why this base combination works naturally with the original garment."
    },
    {
      "look_id": 2,
      "title": "Light Contrast Try-On",
      "style": "Smart casual",
      "occasion": "Brunch / Social",
      "bottom": {
        "item": "Chinos",
        "color": "Beige",
        "material": "Washed Stretch Twill"
      },
      "shoes": {
        "item": "Sneakers",
        "color": "Off-White",
        "material": "Nappa Leather"
      },
      "accessories": ["Leather strap watch"],
      "fabric_harmony": "Lightweight twill lifts the silhouette, providing a soft tactile counterpoint to the blue upper.",
      "palette": [
        {"name": "Royal Blue", "hex": "#4169E2", "role": "Anchor Top"},
        {"name": "Beige", "hex": "#F5F5DC", "role": "Luminosity Contrast"},
        {"name": "Off-White", "hex": "#FAF0E6", "role": "Footwear Accent"}
      ],
      "explanation": "How the contrasting bottom colour and materials transform the look."
    },
    {
      "look_id": 3,
      "title": "Contemporary Casual",
      "style": "Contemporary casual",
      "occasion": "Creative / Weekend",
      "bottom": {
        "item": "Relaxed trousers",
        "color": "Olive",
        "material": "Cotton Ripstop / Linen Blend"
      },
      "shoes": {
        "item": "Sneakers",
        "color": "Black",
        "material": "Suede & Mesh"
      },
      "layer": {
        "item": "Overshirt",
        "color": "Navy",
        "material": "Raw Denim"
      },
      "accessories": ["Woven bracelet"],
      "fabric_harmony": "Pairing airy textured blend bottoms with suede runners adds modern dimensional depth.",
      "palette": [
        {"name": "Royal Blue", "hex": "#4169E2", "role": "Anchor Top"},
        {"name": "Olive", "hex": "#808000", "role": "Organic Complement"},
        {"name": "Black", "hex": "#000000", "role": "Base Foundation"}
      ],
      "explanation": "A distinct styling direction adding modern texture and character."
    },
    {
      "look_id": 4,
      "title": "Elevated Refinement",
      "style": "Elevated refinement",
      "occasion": "Dinner / Evening",
      "bottom": {
        "item": "Tailored trousers",
        "color": "Charcoal",
        "material": "Tropical Wool Flannel"
      },
      "shoes": {
        "item": "Loafers",
        "color": "Dark Brown",
        "material": "Burnished Calfskin Leather"
      },
      "layer": {
        "item": "Unstructured blazer",
        "color": "Midnight Navy",
        "material": "Hopsack Wool"
      },
      "accessories": ["Dress watch", "Leather belt"],
      "fabric_harmony": "Fine wool flannel and burnished calfskin provide luxurious drape and sophisticated evening luster.",
      "palette": [
        {"name": "Royal Blue", "hex": "#4169E2", "role": "Anchor Top"},
        {"name": "Charcoal", "hex": "#36454F", "role": "Tailored Structure"},
        {"name": "Dark Brown", "hex": "#654321", "role": "Footwear Anchor"}
      ],
      "explanation": "A sophisticated complete combination for formal or evening settings."
    }
  ],
  "overall_advice": "A cohesive 2-sentence styling summary."
}
Output valid JSON only without markdown formatting."""


def validate_looks_diversity(looks: List[Dict[str, Any]]) -> bool:
    """
    Validates that the four looks are genuinely distinct by checking their signatures.
    Each signature combines:
      bottom item, bottom color, shoe item, shoe color, style direction, accessories.
    Ensures:
      1. Exactly 4 looks exist.
      2. No two looks have identical signatures.
      3. At least 3 distinct bottom colors/items exist across the 4 looks.
    """
    if not isinstance(looks, list) or len(looks) != 4:
        return False

    signatures = set()
    bottom_colors = set()

    for lk in looks:
        b = lk.get("bottom", {})
        s = lk.get("shoes", {})
        acc = lk.get("accessories", [])
        style = lk.get("style", "")

        b_item = b.get("item", "").strip().lower() if isinstance(b, dict) else str(b).strip().lower()
        b_color = b.get("color", "").strip().lower() if isinstance(b, dict) else ""
        s_item = s.get("item", "").strip().lower() if isinstance(s, dict) else str(s).strip().lower()
        s_color = s.get("color", "").strip().lower() if isinstance(s, dict) else ""
        acc_str = (
            ",".join(sorted(str(a).strip().lower() for a in acc))
            if isinstance(acc, list)
            else str(acc).strip().lower()
        )

        sig = f"{b_item}|{b_color}|{s_item}|{s_color}|{style.lower()}|{acc_str}"
        signatures.add(sig)
        if b_color:
            bottom_colors.add(b_color)
        elif b_item:
            bottom_colors.add(b_item)

    is_valid = len(signatures) == 4 and len(bottom_colors) >= 3
    if not is_valid:
        logger.warning(
            "Looks validation failed: %d unique signatures, %d unique bottom colors",
            len(signatures),
            len(bottom_colors),
        )
    return is_valid


async def generate_four_distinct_looks(
    colour_shade: str,
    hex_value: str,
    clothing_type: str,
    garment_semantics: Optional[GarmentAnalysis],
    user_profile: Any,
) -> Optional[Dict[str, Any]]:
    """
    Calls Gemini to generate 4 distinct styling combinations for the same garment on the same user.
    Validates diversity before returning.
    """
    if not settings.GEMINI_ENABLED or not settings.GEMINI_API_KEY:
        return None

    try:
        subcat = getattr(garment_semantics, "subcategory", clothing_type) if garment_semantics else clothing_type
        pattern = getattr(garment_semantics, "pattern", "Solid") if garment_semantics else "Solid"
        neckline = getattr(garment_semantics, "neckline", "Crewneck") if garment_semantics else "Crewneck"
        fit = getattr(garment_semantics, "fit", "Regular") if garment_semantics else "Regular"
        formality = getattr(garment_semantics, "formality", "Casual") if garment_semantics else "Casual"

        complexion = getattr(user_profile, "complexion_tone", "Neutral / Balanced") if user_profile else "Neutral / Balanced"
        build = getattr(user_profile, "apparent_build", "Proportionate") if user_profile else "Proportionate"
        silhouette = getattr(user_profile, "styling_silhouette_preference", "Clean vertical lines") if user_profile else "Clean vertical lines"

        user_content = (
            f"USER CONTEXT:\n"
            f"- Complexion: {complexion}\n"
            f"- Build: {build}\n"
            f"- Silhouette: {silhouette}\n\n"
            f"PRIMARY UPLOADED GARMENT:\n"
            f"- Item: {subcat}\n"
            f"- Color Shade: {colour_shade} (HEX: {hex_value})\n"
            f"- Pattern: {pattern}\n"
            f"- Neckline: {neckline}\n"
            f"- Fit: {fit}\n"
            f"- Formality: {formality}\n"
        )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
            f"?key={settings.GEMINI_API_KEY}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": DISTINCT_LOOKS_SYSTEM_PROMPT},
                        {"text": user_content},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
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
                        parsed = json.loads(clean_text)
                        looks = parsed.get("looks", [])
                        if validate_looks_diversity(looks):
                            logger.info("Gemini generated 4 validated diverse looks successfully.")
                            return parsed
                        else:
                            logger.warning("Gemini looks failed diversity validation.")

    except Exception as exc:
        logger.warning("Gemini 4-look generation encountered error (%s). Falling back to rule matrix.", exc)

    return None


