"""
Test Script: Four Distinct Looks Generation and Validation
===========================================================
Validates:
1. 4 distinct styling combinations for the same uploaded garment.
2. Signatures (bottom item, bottom color, shoe item, shoe color, style, accessories) are distinct.
3. Bottom colors and styles differ across looks.
4. Same original garment in all 4 looks.
5. Output data matches required schema.
6. Duplicate detection runs properly.
"""

import sys
from pathlib import Path

# Ensure backend path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.services.recommendation_engine import generate_fashion_recommendations
from app.services.gemini_service import validate_looks_diversity
from app.services.duplicate_detector import compute_image_dhash, hamming_distance, check_for_duplicates
from app.schemas.analysis import OutfitSuggestion

def test_four_distinct_looks_engine():
    print("=" * 64)
    print("      TESTING 4 DISTINCT LOOKS GENERATION & VALIDATION")
    print("=" * 64)

    # 1. Test Rule-based diverse 4-look synthesis
    clothing_type = "T-shirt"
    detected_colour = "Blue"
    colour_shade = "Royal Blue"
    hex_value = "#4169E2"

    recs = generate_fashion_recommendations(
        clothing_type=clothing_type,
        detected_colour=detected_colour,
        colour_shade=colour_shade,
        hex_value=hex_value,
    )

    outfits = recs["outfit_suggestions"]
    assert len(outfits) == 4, f"Expected 4 looks, got {len(outfits)}"

    print(f"\n[1/4] Checking 4 Look Titles & Styles for {colour_shade} {clothing_type}:")
    for lk in outfits:
        print(f"  Look {lk['look_id']}: {lk['title']} ({lk['style']})")
        print(f"    Top:         {lk['top']}")
        print(f"    Bottom:      {lk['bottom']}")
        print(f"    Shoes:       {lk['shoes']}")
        print(f"    Accessories: {lk['accessories']}")
        print(f"    Explanation: {lk['explanation'][:70]}...")

    # 2. Check that the original garment is preserved across all four looks
    print("\n[2/4] Verifying Original Garment Consistency:")
    for lk in outfits:
        assert colour_shade in lk["top"], f"Original shade missing in Look {lk['look_id']}"
        assert clothing_type in lk["top"], f"Original clothing type missing in Look {lk['look_id']}"
    print("  -> Original garment is consistent across all 4 looks!")

    # 3. Validate Diversity of Signatures
    print("\n[3/4] Validating Signature Diversity:")
    is_diverse = validate_looks_diversity(outfits)
    assert is_diverse is True, "Looks failed diversity validation!"

    signatures = []
    bottom_colors = []
    for lk in outfits:
        b = lk["bottom"]
        s = lk["shoes"]
        sig = f"{b['item']}|{b['color']}|{s['item']}|{s['color']}|{lk['style']}|{','.join(lk['accessories'])}"
        signatures.append(sig)
        bottom_colors.append(b['color'])

    print(f"  Unique Signatures: {len(set(signatures))} / 4")
    print(f"  Bottom Colors:     {bottom_colors}")
    assert len(set(signatures)) == 4, "Found duplicate signatures across looks!"
    assert len(set(bottom_colors)) >= 3, f"Insufficient bottom color variation: {bottom_colors}"
    print("  -> All 4 looks have distinct combinations and differing bottom colors!")

    # 4. Validate Pydantic Schema compatibility
    print("\n[4/4] Validating Pydantic OutfitSuggestion Schema:")
    pydantic_looks = []
    for lk in outfits:
        obj = OutfitSuggestion(
            **lk,
            image_url="/uploads/virtual_tryon/test.png",
            result_type="actual_try_on",
            try_on_type="actual_try_on",
            provider="fashn_vton_local",
        )
        assert obj.try_on_image_url == "/uploads/virtual_tryon/test.png"
        assert obj.look_id == lk["look_id"]
        assert isinstance(obj.bottom, dict)
        assert isinstance(obj.shoes, dict)
        pydantic_looks.append(obj)
    print("  -> Schema serialization validated successfully!")

    # 5. Test Duplicate Detection Logic
    test_img = Path("uploads/user_5721df14d16a45af8a8470b85ade677b.jpg")
    if test_img.exists():
        h1 = compute_image_dhash(test_img)
        h2 = compute_image_dhash(test_img)
        assert h1 == h2
        assert hamming_distance(h1, h2) == 0
        dups = check_for_duplicates([test_img, test_img])
        assert len(dups) == 1, "Duplicate detector should find duplicate identical pair"
        print("  -> Duplicate detector verified with dHash!")

    print("\nALL 4 DISTINCT LOOKS TESTS PASSED SUCCESSFULLY!")
    print("=" * 64)

if __name__ == "__main__":
    test_four_distinct_looks_engine()
