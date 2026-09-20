"""
AI Stylist Try-On Prompt Builder
================================
Assembles controlled, high-precision prompts for Gemini image generation
using dual reference images:
  Image 1: Person Reference (Uploaded user portrait/photo)
  Image 2: Garment Reference (Uploaded clothing photo)
"""

from typing import Optional, Dict, Any


def build_gemini_tryon_prompt(
    outfit: Dict[str, Any],
    detected_colour_shade: str,
    detected_colour_hex: str,
    detected_clothing_type: str,
    user_persona: Optional[str] = None,
    semantic_data: Optional[Any] = None,
    styling_instructions: Optional[str] = None,
) -> str:
    """
    Builds an exacting prompt for Gemini multi-image virtual try-on.
    Specifies image roles, strict identity locking, garment preservation,
    and coordinated pieces.
    """
    title = outfit.get("title", "Fashion Look")
    occasion = outfit.get("occasion", "Everyday Wear")
    top = outfit.get("top", "")
    bottom = outfit.get("bottom", "")
    shoes = outfit.get("shoes", "")
    accessories = outfit.get("accessories", "")
    explanation = outfit.get("explanation", "")
    personalization_reason = outfit.get("personalization_reason", "")

    # Extract semantic garment properties
    pattern = getattr(semantic_data, "pattern", "Solid") if semantic_data else "Solid"
    sleeve = getattr(semantic_data, "sleeve_length", "") if semantic_data else ""
    fit = getattr(semantic_data, "fit", "") if semantic_data else ""
    neckline = getattr(semantic_data, "neckline", "") if semantic_data else ""
    material = getattr(semantic_data, "material_appearance", "") if semantic_data else ""
    subcategory = (
        getattr(semantic_data, "subcategory", detected_clothing_type)
        if semantic_data and getattr(semantic_data, "subcategory", None)
        else detected_clothing_type
    )

    # Build garment descriptor
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
        garment_descriptors.append(f"in {material.lower()} fabric")

    full_garment_desc = " ".join(garment_descriptors)

    persona_desc = (
        user_persona
        if user_persona
        else "the individual shown in the first reference photograph"
    )

    prompt = (
        f"HIGH-PRIORITY DIRECTIVE: High-Fidelity AI Virtual Try-On.\n\n"
        f"REFERENCE ROLES:\n"
        f"1. PERSON REFERENCE: The first image provided is the exact person who MUST appear in the final photograph.\n"
        f"2. GARMENT REFERENCE: The second image provided is the actual clothing piece that this person MUST be wearing.\n\n"
        f"IDENTITY PRESERVATION:\n"
        f"- Maintain {persona_desc}'s recognizable facial appearance, facial structure, skin tone, hair color/texture, and natural body proportions.\n"
        f"- Strictly DO NOT replace this person with a generic or different fashion model.\n\n"
        f"GARMENT PRESERVATION (MANDATORY):\n"
        f"- The subject must wear the actual garment from the second image: {full_garment_desc}.\n"
        f"- Anchor exact colour: {detected_colour_shade} (HEX: {detected_colour_hex}). Do NOT change, lighten, darken, or shift this colour.\n"
        f"- Preserve the exact garment silhouette, neckline ({neckline or 'as shown'}), sleeve length ({sleeve or 'as shown'}), "
        f"pattern ({pattern}), and fabric texture.\n"
        f"- Do NOT redesign the garment into a different clothing type (e.g. do not turn a t-shirt into a polo, shirt, hoodie, or blazer).\n\n"
        f"COORDINATED STYLING FOR LOOK '{title.upper()}' ({occasion}):\n"
        f"- Anchor Piece: {top}\n"
        f"- Coordinated Bottoms: {bottom}\n"
        f"- Coordinated Footwear: {shoes}\n"
    )

    if accessories and accessories.lower() != "none" and accessories.strip():
        prompt += f"- Layering & Accessories: {accessories}\n"

    if styling_instructions:
        prompt += f"- Stylist Guidance: {styling_instructions}\n"
    elif personalization_reason:
        prompt += f"- Stylist Guidance: {personalization_reason}\n"

    prompt += (
        f"\nPHOTOGRAPHY & COMPOSITION:\n"
        f"- Authentic, full-body realistic fashion editorial photograph of the person naturally wearing the complete outfit.\n"
        f"- Natural standing human posture with natural fabric drape and realistic folds.\n"
        f"- Clean, modern, minimalist neutral editorial background with soft diffused natural studio lighting.\n"
        f"- Sharp focus, photorealistic 8K lookbook quality, realistic skin texture, realistic hands.\n"
        f"- Strictly no watermarks, no distorted hands, no cartoon or CGI effects, and no product-only flat lay."
    )

    return prompt
