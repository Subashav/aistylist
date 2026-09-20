"""
Test Script: Gemini Virtual Try-On Controlled Test
==================================================
Tests 1 user photo + 1 garment photo + 1 personalized outfit
Evaluates:
- Prompt construction
- Gemini image generation request
- Reference image encoding
- Fallback compositor activation
- Output resolution, format, and storage
"""

import asyncio
import time
from pathlib import Path

from app.config import settings, BASE_DIR
from app.services.virtual_tryon_provider import get_virtual_tryon_provider
from app.services.tryon_prompt_builder import build_gemini_tryon_prompt



async def run_test():
    print("=" * 60)
    print("     TESTING GEMINI-POWERED VIRTUAL TRY-ON (PHASE 1)")
    print("=" * 60)

    user_img = Path("uploads/user_5721df14d16a45af8a8470b85ade677b.jpg")
    garment_img = Path("uploads/clothing_244cbaffffb24fc3b0533c1f373a53aa.jpg")

    if not user_img.exists():
        print(f"[WARN] User image {user_img} does not exist.")
        return
    if not garment_img.exists():
        print(f"[WARN] Garment image {garment_img} does not exist.")
        return

    outfit = {
        "title": "Casual Classic",
        "occasion": "Weekend Leisure",
        "top": "Relaxed Fit Navy Blue Crewneck T-Shirt",
        "bottom": "Slim-fit Off-White Chinos",
        "shoes": "Minimalist White Leather Low-Top Sneakers",
        "accessories": "Brushed Silver Wristwatch",
        "explanation": "Harmonious complementary contrast balancing relaxed fabric with structured pants.",
        "personalization_reason": "Complements your natural silhouette and balanced complexion tone.",
    }

    # 1. Test Prompt Builder
    print("\n[1/3] Building Structured Try-On Prompt...")
    prompt = build_gemini_tryon_prompt(
        outfit=outfit,
        detected_colour_shade="Navy Blue",
        detected_colour_hex="#1B263B",
        detected_clothing_type="T-shirt",
        user_persona="A contemporary individual with balanced natural features",
        styling_instructions=outfit["personalization_reason"],
    )
    print("--- PROMPT PREVIEW ---")
    print(prompt[:320] + "\n... [truncated] ...")
    print("----------------------")

    # 2. Test Try-On Provider
    print(f"\n[2/3] Calling Gemini Virtual Try-On Provider (Model: {settings.GEMINI_IMAGE_MODEL})...")
    provider = get_virtual_tryon_provider()
    t_start = time.perf_counter()

    result = await provider.generate_tryon(
        person_image=user_img,
        garment_image=garment_img,
        outfit=outfit,
        category="T-shirt",
        detected_colour_shade="Navy Blue",
        detected_colour_hex="#1B263B",
        styling_instructions=outfit["personalization_reason"],
    )
    t_duration = time.perf_counter() - t_start

    print(f"\n[3/3] Execution Completed in {t_duration:.2f}s!")
    print(f"  Success:       {result.get('success')}")
    print(f"  Provider:      {result.get('provider')}")
    print(f"  Model:         {result.get('model')}")
    print(f"  Try-On Type:   {result.get('try_on_type')}")
    print(f"  Image URL:     {result.get('image_url')}")
    if result.get("error"):
        print(f"  Note/Error:    {result.get('error')}")

    out_file = Path(result.get("image_url", "").lstrip("/"))
    if out_file.exists():
        print(f"  Output File Verified: {out_file} (Size: {out_file.stat().st_size / 1024:.1f} KB)")
    else:
        # Check in uploads
        full_p = BASE_DIR / result.get("image_url", "").lstrip("/")
        print(f"  Checking path: {full_p} -> Exists: {full_p.exists()} (Size: {full_p.stat().st_size / 1024:.1f} KB)")


    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_test())
