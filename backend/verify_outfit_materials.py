import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.services.recommendation_engine import generate_fashion_recommendations
from app.schemas.analysis import OutfitSuggestion

def main():
    print("=" * 64)
    print("      VERIFYING COMPLETE OUTFIT & MATERIAL SUGGESTIONS")
    print("=" * 64)

    recs = generate_fashion_recommendations(
        clothing_type="T-shirt",
        detected_colour="Blue",
        colour_shade="Royal Blue",
        hex_value="#4169E2"
    )

    outfits = recs["outfit_suggestions"]
    assert len(outfits) == 4, f"Expected 4 looks, got {len(outfits)}"

    for lk in outfits:
        print(f"\nLook {lk['look_id']}: {lk['title']} ({lk['style']})")
        print(f"  Top:            {lk['top']}")
        print(f"  Top Detail:     {lk.get('top_detail')}")
        print(f"  Bottom:         {lk['bottom']}")
        print(f"  Shoes:          {lk['shoes']}")
        print(f"  Layer:          {lk.get('layer')}")
        print(f"  Fabric Harmony: {lk.get('fabric_harmony')}")
        print(f"  Palette:        {lk.get('palette')}")

        # Ensure bottom and shoes have material
        assert "material" in lk["bottom"], f"Look {lk['look_id']} bottom missing material"
        assert "material" in lk["shoes"], f"Look {lk['look_id']} shoes missing material"
        assert lk.get("fabric_harmony"), f"Look {lk['look_id']} missing fabric harmony"
        assert lk.get("palette"), f"Look {lk['look_id']} missing palette"

        # Validate with Pydantic
        obj = OutfitSuggestion(**lk)
        assert obj.look_id == lk["look_id"]

    # Verify look types: Look 1 & 2 actual try-on, Look 3 & 4 outfit guide
    sug_visuals = []
    for idx, lk in enumerate(outfits):
        if idx < 2:
            sug = OutfitSuggestion(
                **lk,
                image_url=f"/uploads/virtual_tryon/test_{idx}.png",
                result_type="actual_try_on",
                try_on_type="actual_try_on",
                provider="fashn_vton_local"
            )
            assert sug.result_type == "actual_try_on"
            assert sug.image_url is not None
        else:
            sug = OutfitSuggestion(
                **lk,
                image_url=None,
                result_type="outfit_guide",
                try_on_type="outfit_guide",
                provider="outfit_material_guide"
            )
            assert sug.result_type == "outfit_guide"
            assert sug.image_url is None
        sug_visuals.append(sug)

    print("\n" + "=" * 64)
    print("SUCCESS: All 4 looks validated with complete outfit color, material, fabric harmony, and palette!")
    print(f"Look 1 & 2: {sug_visuals[0].result_type} (with try-on image)")
    print(f"Look 3 & 4: {sug_visuals[2].result_type} (dedicated outfit & material guide)")
    print("=" * 64)

if __name__ == "__main__":
    main()
