from typing import List, Dict, Any, Optional

# Dynamic Color Harmony Matrix based on Color Theory
COLOUR_HARMONY_RULES = {
    "Blue": {
        "swatches": [
            {"name": "Crisp White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Neutral Contrast", "reason": "Creates a clean, sharp contrast that lets the blue hue stand out vibrantly."},
            {"name": "Warm Beige", "hex": "#D2B48C", "rgb": "210, 180, 140", "harmony_type": "Warm-Cool Balance", "reason": "Soft earthy neutral that balances the cool blue energy with timeless sophistication."},
            {"name": "Light Grey", "hex": "#D3D3D3", "rgb": "211, 211, 211", "harmony_type": "Soft Neutral", "reason": "Provides an effortless modern undertone without competing with the blue."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Monochromatic Depth", "reason": "Deeper tonal shade from the same color family for an intentional layered aesthetic."},
            {"name": "Terracotta / Rust", "hex": "#E2725B", "rgb": "226, 114, 91", "harmony_type": "Complementary Harmony", "reason": "Opposite on the color wheel; delivers a bold, sun-drenched stylish accent."}
        ],
        "casual_bottom": "Beige Chinos or Washed Blue Denim",
        "smart_bottom": "Charcoal Tailored Trousers or Crisp White Jeans",
        "shoes": "Clean White Minimalist Sneakers or Tan Loafers",
        "layer": "Navy Unstructured Blazer or Beige Overshirt",
        "accessory": "Silver Mesh Watch / Cognac Leather Belt",
        "advice": "Blue is one of the most versatile primary colors. Pairing it with light warm neutrals like beige and off-white yields an effortlessly polished appearance."
    },
    "Navy": {
        "swatches": [
            {"name": "Crisp White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "High Contrast Neutral", "reason": "Iconic nautical and business pairing that looks exceptionally sharp."},
            {"name": "Khaki / Tan", "hex": "#C2B280", "rgb": "194, 178, 128", "harmony_type": "Classic Complement", "reason": "Traditional menswear and womenswear harmony that exudes refined confidence."},
            {"name": "Sky Blue", "hex": "#87CEEB", "rgb": "135, 206, 235", "harmony_type": "Monochromatic Tonal", "reason": "Lighter tint from the blue spectrum softens the deep navy structure."},
            {"name": "Burgundy / Maroon", "hex": "#800020", "rgb": "128, 0, 32", "harmony_type": "Rich Accent", "reason": "Deep autumnal accent creating a stately, dignified color pairing."},
            {"name": "Olive Green", "hex": "#808000", "rgb": "128, 128, 0", "harmony_type": "Earthy Analogous", "reason": "Muted military green complements navy for an adventurous casual palette."}
        ],
        "casual_bottom": "Khaki Cargo Chinos or Off-White Denim",
        "smart_bottom": "Light Grey Flannel Trousers",
        "shoes": "Dark Brown Leather Oxford / White Tennis Shoes",
        "layer": "Camel Overcoat or Olive Field Jacket",
        "accessory": "Rose Gold Watch / Dark Brown Leather Strap",
        "advice": "Navy functions as a softer, richer alternative to black. Use lighter neutrals to bring light and dimension to your silhouette."
    },
    "Red": {
        "swatches": [
            {"name": "Pure White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Graphic Contrast", "reason": "Brightens the outfit and tempers the fiery intensity of red."},
            {"name": "Jet Black", "hex": "#111111", "rgb": "17, 17, 17", "harmony_type": "Dramatic Contrast", "reason": "Bold, confident high-fashion evening contrast."},
            {"name": "Charcoal Grey", "hex": "#36454F", "rgb": "54, 69, 79", "harmony_type": "Subdued Neutral", "reason": "Slightly softer than black; anchors red with understated elegance."},
            {"name": "Camel Brown", "hex": "#C19A6B", "rgb": "193, 154, 107", "harmony_type": "Warm Earthy Harmony", "reason": "Warm brown tones soften red and create an inviting autumnal mood."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Classic Triadic", "reason": "Cool dark navy grounds vibrant red without clash."}
        ],
        "casual_bottom": "Dark Indigo Slim Jeans or Beige Chinos",
        "smart_bottom": "Charcoal Grey Pleated Trousers",
        "shoes": "Black Chelsea Boots or Crisp White Low-Tops",
        "layer": "Black Leather Biker Jacket or Camel Cardigan",
        "accessory": "Gunmetal Minimalist Cuff / Black Matte Belt",
        "advice": "Red is a focal statement color. Let it take center stage while keeping surrounding garments in neutral and grounded tones."
    },
    "Maroon": {
        "swatches": [
            {"name": "Warm Cream", "hex": "#FFFDD0", "rgb": "255, 253, 208", "harmony_type": "Soft Contrast", "reason": "Gentle creamy undertone highlights the royal richness of maroon."},
            {"name": "Heather Grey", "hex": "#9E9E9E", "rgb": "158, 158, 158", "harmony_type": "Cool Neutral", "reason": "Balances warmth with modern urban minimalism."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Regal Pairing", "reason": "Deep jewel tones that reinforce an air of understated luxury."},
            {"name": "Olive Green", "hex": "#808000", "rgb": "128, 128, 0", "harmony_type": "Earthy Complement", "reason": "Natural, organic contrast straight from botanical color palettes."},
            {"name": "Dusty Pink", "hex": "#DCAE96", "rgb": "220, 174, 150", "harmony_type": "Monochromatic Tint", "reason": "Softens the deep burgundy tone with romantic lightness."}
        ],
        "casual_bottom": "Grey Wool-Blend Trousers or Black Denim",
        "smart_bottom": "Navy Tailored Chinos",
        "shoes": "Oxblood Loafers or White Court Sneakers",
        "layer": "Dark Olive Trench or Grey Peacoat",
        "accessory": "Brass or Warm Gold Jewelry / Espresso Watch",
        "advice": "Maroon brings warmth and depth. Pair with cream and grey for a sophisticated autumn or winter look."
    },
    "Green": {
        "swatches": [
            {"name": "Off-White", "hex": "#FAF9F6", "rgb": "250, 249, 246", "harmony_type": "Clean Neutral", "reason": "Freshens up green tones and highlights natural vibrancy."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Analogous Cool", "reason": "Cool neighboring hues on the color wheel that harmonize naturally."},
            {"name": "Warm Beige", "hex": "#D2B48C", "rgb": "210, 180, 140", "harmony_type": "Organic Earthy", "reason": "Evokes natural foliage and earth, creating an organic lifestyle look."},
            {"name": "Charcoal Grey", "hex": "#36454F", "rgb": "54, 69, 79", "harmony_type": "Modern Base", "reason": "Provides a contemporary architectural backdrop for lively greens."},
            {"name": "Mustard Yellow", "hex": "#FFDB58", "rgb": "255, 219, 88", "harmony_type": "Analogous Accent", "reason": "Warm golden accent that adds sunlit personality."}
        ],
        "casual_bottom": "Beige Linen Pants or Light Wash Denim",
        "smart_bottom": "Navy Pleated Trousers",
        "shoes": "White Leather Sneakers or Suede Chukka Boots",
        "layer": "Tan Harrington Jacket or Navy Cardigan",
        "accessory": "Woven Leather Bracelet / Bronze Watch",
        "advice": "Green connects deeply with natural aesthetics. Pair with earth tones like beige, tan, and soft white for relaxed elegance."
    },
    "Olive": {
        "swatches": [
            {"name": "Pure White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "High Contrast", "reason": "Cuts through the utilitarian feel of olive with crisp freshness."},
            {"name": "Black", "hex": "#111111", "rgb": "17, 17, 17", "harmony_type": "Urban Sleek", "reason": "Elevates olive into a modern streetwear or evening-ready ensemble."},
            {"name": "Terracotta / Rust", "hex": "#E2725B", "rgb": "226, 114, 91", "harmony_type": "Complementary Earth", "reason": "Warm burnt orange tones create a stunning botanical contrast."},
            {"name": "Cream / Ecru", "hex": "#FFFDD0", "rgb": "255, 253, 208", "harmony_type": "Soft Neutral", "reason": "Gentle creamy warmth pairs seamlessly with muted olive greens."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Classic Layer", "reason": "A staple pairing in contemporary casual menswear and womenswear."}
        ],
        "casual_bottom": "Ecru Jeans or Black Relaxed Trousers",
        "smart_bottom": "Navy Tailored Chinos",
        "shoes": "Sand Suede Chelsea Boots or White Sneakers",
        "layer": "Black Denim Jacket or Cream Knit Sweater",
        "accessory": "Canvas Field Watch / Matte Black Sunglasses",
        "advice": "Olive is a modern neutral. Treat it with the versatility of grey, but enjoy the extra character it brings."
    },
    "Black": {
        "swatches": [
            {"name": "Pure White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Monochrome Contrast", "reason": "The quintessential high-fashion contrast; clean, sharp, and timeless."},
            {"name": "Light Grey", "hex": "#D3D3D3", "rgb": "211, 211, 211", "harmony_type": "Tonal Gradient", "reason": "Softens the total black look into an approachable monochromatic gradient."},
            {"name": "Camel Brown", "hex": "#C19A6B", "rgb": "193, 154, 107", "harmony_type": "Warm Luxe", "reason": "Warm camel coats or accessories over black create luxury runway appeal."},
            {"name": "Crimson Red", "hex": "#DC143C", "rgb": "220, 20, 60", "harmony_type": "Statement Pop", "reason": "An electrifying focal accent against a black canvas."},
            {"name": "Olive Green", "hex": "#808000", "rgb": "128, 128, 0", "harmony_type": "Utilitarian Edge", "reason": "Grounds the outfit with contemporary street style."}
        ],
        "casual_bottom": "Medium Wash Denim or Grey Sweats/Chinos",
        "smart_bottom": "Black Slim Dress Trousers or Charcoal Slacks",
        "shoes": "Black Derby Shoes or Minimalist White Sneakers",
        "layer": "Camel Wool Overcoat or Grey Denim Jacket",
        "accessory": "Polished Silver Watch / Minimalist Black Ring",
        "advice": "Black offers absolute versatility. Break up solid black silhouettes with contrasting textures (e.g. leather, knit, denim) or light neutral layers."
    },
    "White": {
        "swatches": [
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Classic Contrast", "reason": "Timeless, clean contrast suitable for both casual seaside and boardroom styles."},
            {"name": "Olive Green", "hex": "#808000", "rgb": "128, 128, 0", "harmony_type": "Earthy Modern", "reason": "Lends depth and a relaxed outdoor aesthetic to pure white tops."},
            {"name": "Beige / Khaki", "hex": "#C2B280", "rgb": "194, 178, 128", "harmony_type": "Monochromatic Neutral", "reason": "Effortless tonal summer look radiating clean luxury."},
            {"name": "Charcoal Grey", "hex": "#36454F", "rgb": "54, 69, 79", "harmony_type": "Sharp Monochrome", "reason": "Sleek contemporary look that feels deliberate and sharp."},
            {"name": "Sky Blue", "hex": "#87CEEB", "rgb": "135, 206, 235", "harmony_type": "Airy Pastel", "reason": "Evokes clear skies and light breezes; ultra-clean daytime vibe."}
        ],
        "casual_bottom": "Light Blue Washed Denim or Tan Linen Shorts",
        "smart_bottom": "Navy Pleated Trousers or Olive Chinos",
        "shoes": "Brown Leather Loafers or Crisp White Low-Tops",
        "layer": "Navy Blazer or Olive Overshirt",
        "accessory": "Tortoise Shell Sunglasses / Woven Brown Belt",
        "advice": "White acts as the ultimate blank canvas. Focus on fit and introduce rich textures or accent colors through pants and outerwear."
    },
    "Grey": {
        "swatches": [
            {"name": "Crisp White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Clean Light", "reason": "Lifts grey with crisp brightness."},
            {"name": "Jet Black", "hex": "#111111", "rgb": "17, 17, 17", "harmony_type": "Anchor Contrast", "reason": "Provides weight and structure to light or mid-grey garments."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Corporate & Smart", "reason": "One of the safest, most flattering pairings in modern dressing."},
            {"name": "Pastel Pink", "hex": "#FFD1DC", "rgb": "255, 209, 220", "harmony_type": "Gentle Contrast", "reason": "Soft pink warms up cool grey tones delightfully."},
            {"name": "Burgundy", "hex": "#800020", "rgb": "128, 0, 32", "harmony_type": "Rich Warmth", "reason": "Infuses richness and sophisticated color into neutral grey."}
        ],
        "casual_bottom": "Black Slim Jeans or Dark Indigo Denim",
        "smart_bottom": "Navy Tailored Trousers",
        "shoes": "White Tennis Shoes or Chelsea Boots",
        "layer": "Black Overcoat or Navy Cardigan",
        "accessory": "Brushed Steel Watch / Charcoal Scarf",
        "advice": "Grey is the ultimate balancing neutral. Pair light grey with dark navy or black for high impact, or with pastels for an approachable aesthetic."
    },
    "Yellow": {
        "swatches": [
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Complementary Contrast", "reason": "Deep navy grounds the energetic, vibrant yellow beautifully."},
            {"name": "Charcoal Grey", "hex": "#36454F", "rgb": "54, 69, 79", "harmony_type": "Modern Balance", "reason": "Sleek grey tones temper yellow's brightness for professional flair."},
            {"name": "Crisp White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Sunlit Fresh", "reason": "Maximizes light and creates a bright summery optimism."},
            {"name": "Olive Green", "hex": "#808000", "rgb": "128, 128, 0", "harmony_type": "Natural Harmony", "reason": "Earth-inspired pairing reminiscent of golden sunlight filtering through trees."},
            {"name": "Denim Blue", "hex": "#4682B4", "rgb": "70, 130, 180", "harmony_type": "Casual Standard", "reason": "The quintessential weekend pairing that never fails."}
        ],
        "casual_bottom": "Medium Wash Blue Jeans or White Shorts",
        "smart_bottom": "Navy Pleated Chinos",
        "shoes": "White Canvas Sneakers or Tan Boat Shoes",
        "layer": "Dark Denim Jacket or Navy Blazer",
        "accessory": "Woven Leather Belt / Minimalist Watch",
        "advice": "Yellow radiates optimism. Balance its luminosity with deep navy or cool grey trousers to keep the overall look grounded."
    },
    "Pink": {
        "swatches": [
            {"name": "Heather Grey", "hex": "#9E9E9E", "rgb": "158, 158, 158", "harmony_type": "Soft Modern", "reason": "The cool neutrality of grey perfectly balances pink's romantic warmth."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Smart Contrast", "reason": "Provides masculine or structured weight against delicate pink."},
            {"name": "Crisp White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Airy Pastel", "reason": "Creates a fresh, breezy summer daytime appearance."},
            {"name": "Olive Green", "hex": "#808000", "rgb": "128, 128, 0", "harmony_type": "Botanical Complement", "reason": "Complementary palette inspired by flower petals and garden leaves."},
            {"name": "Burgundy", "hex": "#800020", "rgb": "128, 0, 32", "harmony_type": "Monochromatic Tonal", "reason": "Rich berry pairing across the red/pink spectrum."}
        ],
        "casual_bottom": "Light Grey Chinos or White Denim",
        "smart_bottom": "Navy Tailored Trousers",
        "shoes": "White Leather Low-Tops or Brown Penny Loafers",
        "layer": "Navy Cotton Blazer or Light Grey Bomber",
        "accessory": "Rose Gold / Silver Watch",
        "advice": "Pink is exceptionally flattering against diverse skin tones. Pair with tailored navy or cool grey to add structure."
    },
    "Brown": {
        "swatches": [
            {"name": "Cream / Ecru", "hex": "#FFFDD0", "rgb": "255, 253, 208", "harmony_type": "Warm Tonal", "reason": "Creates a cozy, expensive coffee-and-cream aesthetic."},
            {"name": "Sky Blue", "hex": "#87CEEB", "rgb": "135, 206, 235", "harmony_type": "Complementary Freshness", "reason": "Light blue introduces cool crisp air into warm brown undertones."},
            {"name": "Forest Green", "hex": "#228B22", "rgb": "34, 139, 34", "harmony_type": "Woodland Harmony", "reason": "Rich organic connection straight from natural scenery."},
            {"name": "White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Sharp Contrast", "reason": "Prevents brown from looking overly dark or muddy."},
            {"name": "Terracotta", "hex": "#E2725B", "rgb": "226, 114, 91", "harmony_type": "Analogous Warm", "reason": "Warm sunset tones that complement deep leather and wool."}
        ],
        "casual_bottom": "Off-White Denim or Washed Blue Jeans",
        "smart_bottom": "Beige Wool Trousers",
        "shoes": "Cognac Leather Boots or White Minimalist Sneakers",
        "layer": "Cream Cable-Knit Cardigan or Green Waxed Jacket",
        "accessory": "Antiqued Brass Watch / Suede Belt",
        "advice": "Brown brings tactile richness and warmth. Elevate it with crisp off-white or sky blue accents to keep the outfit fresh."
    },
    "Beige": {
        "swatches": [
            {"name": "Pure White", "hex": "#FFFFFF", "rgb": "255, 255, 255", "harmony_type": "Quiet Luxury", "reason": "The defining palette of quiet luxury; effortlessly clean and upscale."},
            {"name": "Navy Blue", "hex": "#000080", "rgb": "0, 0, 128", "harmony_type": "Classic Anchor", "reason": "Deep navy anchors light beige with authority."},
            {"name": "Olive Green", "hex": "#808000", "rgb": "128, 128, 0", "harmony_type": "Safari / Earthy", "reason": "Authentic organic combination suitable for year-round styling."},
            {"name": "Chocolate Brown", "hex": "#7B3F00", "rgb": "123, 63, 0", "harmony_type": "Monochromatic Depth", "reason": "Richer shade of brown adding dynamic shadow and depth."},
            {"name": "Charcoal Grey", "hex": "#36454F", "rgb": "54, 69, 79", "harmony_type": "Contemporary Contrast", "reason": "Modern cool grey juxtaposed with warm sandy beige."}
        ],
        "casual_bottom": "White Linen Trousers or Light Blue Denim",
        "smart_bottom": "Navy Tailored Slacks",
        "shoes": "Sand Suede Loafers or Clean White Sneakers",
        "layer": "Navy Wool Blazer or Olive Trench Coat",
        "accessory": "Tan Leather Belt / Gold Accent Watch",
        "advice": "Beige offers subtle sophistication. Pair with contrasting textures like linen, suede, and knitwear to achieve an elevated look."
    }
}

def generate_fashion_recommendations(
    clothing_type: str,
    detected_colour: str,
    colour_shade: str,
    hex_value: str,
    semantic_data: Optional[Any] = None,
    user_profile: Optional[Any] = None,
    personalized_fit_override: Optional[Dict[str, Any]] = None,
    gemini_looks_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Synthesizes 4 genuinely distinct styling combinations for the SAME uploaded garment on the SAME user.
    Enforces distinct bottom colors, footwear, styles, and accessories across all four looks:
      - Look 1: Base Look (original garment with best natural combination)
      - Look 2: Different Pant Colour (same garment, different bottom color & matching shoes)
      - Look 3: Different Style (same garment, clearly different styling direction)
      - Look 4: Elevated / Alternative Complete Look (same garment, refined complete combination)
    """
    rule = COLOUR_HARMONY_RULES.get(detected_colour)
    if not rule:
        rule = COLOUR_HARMONY_RULES["Blue"]
        
    swatches = rule["swatches"]

    # Extract semantic attributes if present
    subcategory = getattr(semantic_data, "subcategory", clothing_type) if semantic_data else clothing_type
    pattern = getattr(semantic_data, "pattern", "Solid") if semantic_data else "Solid"
    neckline = getattr(semantic_data, "neckline", "Crewneck") if semantic_data else "Crewneck"
    fit = getattr(semantic_data, "fit", "Regular") if semantic_data else "Regular"
    top_material = getattr(semantic_data, "material_appearance", "Cotton") if semantic_data else "Cotton"

    # Extract user styling attributes if present
    complexion = getattr(user_profile, "complexion_tone", "Neutral / Balanced") if user_profile else "Neutral / Balanced"
    build = getattr(user_profile, "apparent_build", "Proportionate") if user_profile else "Proportionate"
    silhouette_pref = getattr(user_profile, "styling_silhouette_preference", "Clean vertical lines") if user_profile else "Clean vertical lines"
    is_personalized = bool(user_profile and getattr(user_profile, "is_valid_person", True))

    primary_top = f"{colour_shade} {subcategory}"
    top_detail = {
        "item": subcategory,
        "color": colour_shade,
        "material": f"{top_material} Fabric",
    }

    outfits = []

    # Case A: Validated Gemini Looks Plan provided
    if gemini_looks_plan and isinstance(gemini_looks_plan.get("looks"), list) and len(gemini_looks_plan["looks"]) == 4:
        for idx, lk in enumerate(gemini_looks_plan["looks"]):
            b = lk.get("bottom", {})
            s = lk.get("shoes", {})
            ly = lk.get("layer")
            acc = lk.get("accessories", [])
            acc_list = acc if isinstance(acc, list) else [str(acc)]
            fab_harm = lk.get("fabric_harmony")
            pal = lk.get("palette")

            # Standardize bottom dict
            if isinstance(b, dict):
                bottom_dict = {
                    "item": b.get("item", "Trousers"),
                    "color": b.get("color", "Neutral"),
                    "material": b.get("material", "Brushed Twill"),
                }
            else:
                bottom_dict = {"item": str(b), "color": "Complementary", "material": "Structured Cotton"}

            # Standardize shoes dict
            if isinstance(s, dict):
                shoes_dict = {
                    "item": s.get("item", "Shoes"),
                    "color": s.get("color", "Neutral"),
                    "material": s.get("material", "Leather"),
                }
            else:
                shoes_dict = {"item": str(s), "color": "Matching", "material": "Leather"}

            # Standardize layer dict
            layer_dict = None
            if isinstance(ly, dict) and ly.get("item") and ly.get("item") != "None":
                layer_dict = ly
            elif isinstance(ly, str) and ly != "None" and ly.strip():
                layer_dict = {"item": ly, "color": "Neutral", "material": "Coordinated Blend"}

            outfits.append({
                "look_id": idx + 1,
                "title": lk.get("title", f"Look {idx + 1}"),
                "style": lk.get("style", "Clean casual"),
                "occasion": lk.get("occasion", "Everyday" if idx == 0 else ("Social" if idx == 1 else ("Creative" if idx == 2 else "Elevated"))),
                "top": primary_top,
                "top_detail": top_detail,
                "bottom": bottom_dict,
                "shoes": shoes_dict,
                "layer": layer_dict,
                "accessories": acc_list,
                "fabric_harmony": fab_harm or f"Balanced tactile pairing of {top_material.lower()} with {bottom_dict.get('material', 'twill').lower()}.",
                "palette": pal or [
                    {"name": colour_shade, "hex": hex_value, "role": "Anchor Garment"},
                    {"name": bottom_dict.get("color", "Neutral"), "hex": "#333333", "role": "Bottom Foundation"},
                    {"name": shoes_dict.get("color", "White"), "hex": "#FFFFFF", "role": "Footwear Accent"},
                ],
                "explanation": lk.get("explanation", f"Curated combination for your {colour_shade} {subcategory}."),
                "personalization_reason": (
                    f"Tailored to your {complexion.lower()} complexion and {build.lower()} build."
                ),
            })
    else:
        # Case B: Rule-based dynamic synthesis guaranteeing 4 distinct signatures
        # 1. Base Look: Classic grounding neutrals (Charcoal/Black or White)
        base_bottom_color = "Black" if detected_colour not in ("Black", "Navy") else "Crisp White"
        base_bottom_item = "Straight-fit trousers" if "pants" not in subcategory.lower() else "Tailored dark chinos"

        # 2. Light Contrast: Soft warm neutral from harmony swatches
        contrast_swatch = swatches[1] if len(swatches) > 1 else {"name": "Warm Beige", "hex": "#D2B48C"}
        contrast_color = contrast_swatch["name"].split("/")[0].strip()

        # 3. Different Style: Earthy or alternative hue from harmony swatches
        alt_swatch = swatches[2] if len(swatches) > 2 else {"name": "Olive Green", "hex": "#556B2F"}
        alt_color = alt_swatch["name"].split("/")[0].strip()

        # 4. Elevated: Deep stately neutral or jewel tone
        elevated_swatch = swatches[3] if len(swatches) > 3 else {"name": "Charcoal Grey", "hex": "#36454F"}
        elevated_color = elevated_swatch["name"].split("/")[0].strip()

        outfits = [
            {
                "look_id": 1,
                "title": "Base Try-On",
                "style": "Clean casual",
                "occasion": "Everyday Outing / Weekend",
                "top": primary_top,
                "top_detail": top_detail,
                "bottom": {
                    "item": base_bottom_item,
                    "color": base_bottom_color,
                    "material": "Brushed Cotton Twill (8.5 oz)",
                },
                "shoes": {
                    "item": "Minimalist low-top sneakers",
                    "color": "Crisp White",
                    "material": "Full-Grain Nappa Leather",
                },
                "layer": {
                    "item": "Lightweight Harrington Jacket",
                    "color": "Slate Grey",
                    "material": "Water-Repellent Cotton Blend",
                },
                "accessories": ["Minimal stainless steel watch", "Woven canvas belt"],
                "fabric_harmony": f"The breathable {top_material.lower()} texture of the {subcategory.lower()} pairs effortlessly with dense brushed twill, while smooth leather sneakers provide a clean modern finish.",
                "palette": [
                    {"name": colour_shade, "hex": hex_value, "role": "Anchor Garment"},
                    {"name": base_bottom_color, "hex": "#1A1A1A" if base_bottom_color == "Black" else "#FFFFFF", "role": "Grounding Bottom"},
                    {"name": "Crisp White", "hex": "#FFFFFF", "role": "Clean Accent"},
                ],
                "explanation": f"The natural everyday anchor showcasing your {colour_shade.lower()} {subcategory.lower()} with clean, grounded proportions.",
                "personalization_reason": (
                    f"The {colour_shade.lower()} provides an intentional focal anchor that flatters your {complexion.lower()} complexion. "
                    f"Pairing it with {base_bottom_color.lower()} {base_bottom_item.lower()} balances your {build.lower()} frame."
                ),
            },
            {
                "look_id": 2,
                "title": "Contrast Try-On",
                "style": "Smart casual",
                "occasion": "Brunch / Daytime Social",
                "top": primary_top,
                "top_detail": top_detail,
                "bottom": {
                    "item": "Tailored chinos",
                    "color": contrast_color,
                    "material": "Washed Stretch Twill / Chino Cotton",
                },
                "shoes": {
                    "item": "Classic low-top trainers",
                    "color": "Off-White",
                    "material": "Tumbled Calfskin & Suede Trim",
                },
                "layer": {
                    "item": "Unstructured Overshirt",
                    "color": "Sandstone Beige",
                    "material": "Medium-Weight Cotton Poplin",
                },
                "accessories": ["Horween leather strap watch", "Braided cotton bracelet"],
                "fabric_harmony": f"Lightweight washed twill trousers lift visual weight, creating a warm, airy contrast against your {colour_shade.lower()} upper.",
                "palette": [
                    {"name": colour_shade, "hex": hex_value, "role": "Anchor Garment"},
                    {"name": contrast_color, "hex": contrast_swatch.get("hex", "#D2B48C"), "role": "Warm Contrast"},
                    {"name": "Off-White", "hex": "#FAF0E6", "role": "Footwear Anchor"},
                ],
                "explanation": f"Introduces {contrast_color.lower()} bottoms to create a soft, inviting contrast that highlights the character of your {colour_shade.lower()} piece.",
                "personalization_reason": (
                    f"The lighter {contrast_color.lower()} lower half lifts your visual presence, balancing your {complexion.lower()} undertones with warm daylight optimism."
                ),
            },
            {
                "look_id": 3,
                "title": "Complete Outfit & Fabric Texture Guide",
                "style": "Contemporary casual",
                "occasion": "Creative Office / Weekend Outing",
                "top": primary_top,
                "top_detail": top_detail,
                "bottom": {
                    "item": "Relaxed pleated trousers",
                    "color": alt_color,
                    "material": "Cotton-Linen Slub Blend",
                },
                "shoes": {
                    "item": "Retro runner sneakers",
                    "color": "Black",
                    "material": "Textured Suede & Ballistic Mesh",
                },
                "layer": {
                    "item": "Worker Jacket / Casual Overshirt",
                    "color": "Charcoal / Indigo",
                    "material": "Japanese Raw Denim / Heavy Twill",
                },
                "accessories": ["Woven cord bracelet", "Matte black sunglasses", "Canvas tote"],
                "fabric_harmony": f"Slub-textured cotton-linen trousers add organic tactile depth, juxtaposed with the technical suede-mesh of retro runners for a modern creative silhouette.",
                "palette": [
                    {"name": colour_shade, "hex": hex_value, "role": "Anchor Garment"},
                    {"name": alt_color, "hex": alt_swatch.get("hex", "#556B2F"), "role": "Earthy Accent"},
                    {"name": "Charcoal / Black", "hex": "#2B2B2B", "role": "Urban Foundation"},
                ],
                "explanation": f"A distinctive contemporary styling direction pairing relaxed {alt_color.lower()} trousers with dark athletic footwear for an expressive silhouette.",
                "personalization_reason": (
                    f"The interplay with {alt_color.lower()} adds modern dimensional texture without overwhelming your {complexion.lower()} complexion."
                ),
            },
            {
                "look_id": 4,
                "title": "Elevated Ensemble & Material Guide",
                "style": "Elevated refinement",
                "occasion": "Dinner / Evening Gathering",
                "top": primary_top,
                "top_detail": top_detail,
                "bottom": {
                    "item": "Tailored dress trousers",
                    "color": elevated_color,
                    "material": "Super 120s Tropical Wool Flannel",
                },
                "shoes": {
                    "item": "Penny loafers",
                    "color": "Dark Espresso",
                    "material": "Burnished Italian Calfskin",
                },
                "layer": {
                    "item": "Unstructured Tailored Blazer",
                    "color": "Midnight Navy",
                    "material": "Hopsack Wool / Fine Serge",
                },
                "accessories": ["Chronograph dress watch", "Fine calfskin belt", "Silk pocket square"],
                "fabric_harmony": f"The fluid drape of tropical wool flannel and burnished calfskin elevates the {colour_shade.lower()} {subcategory.lower()} with sartorial restraint and evening luster.",
                "palette": [
                    {"name": colour_shade, "hex": hex_value, "role": "Anchor Garment"},
                    {"name": elevated_color, "hex": elevated_swatch.get("hex", "#36454F"), "role": "Sartorial Anchor"},
                    {"name": "Espresso Brown", "hex": "#4A2E18", "role": "Leather Accent"},
                ],
                "explanation": f"A sophisticated complete combination elevating your {colour_shade.lower()} {subcategory.lower()} for formal or refined evening occasions.",
                "personalization_reason": (
                    f"Deep {elevated_color.lower()} tailored tones below anchor your {colour_shade.lower()} piece, framing your face and posture with polished restraint."
                ),
            },
        ]

    # Synthesis of Overall Personalized Style Analysis
    garment_summary = f"{colour_shade} {subcategory} ({pattern}, {fit} Fit, {neckline})"
    how_it_works_with_you = (
        f"The {colour_shade.lower()} tone complements your {complexion.lower()} complexion by providing clear visual definition. "
        f"With your {build.lower()} frame, pairing this {fit.lower()} {subcategory.lower()} with {silhouette_pref.lower()} ensures your vertical silhouette remains balanced and stylish."
    )
    complexion_harmony = (
        f"Your {complexion.lower()} undertones naturally harmonize with {colour_shade.lower()} and its neutral companions (crisp whites, deep navies, and warm earth tones)."
    )
    silhouette_advice = (
        f"Maintain {silhouette_pref.lower()} to balance garment length and shoulder structure for optimum aesthetic proportions."
    )

    if personalized_fit_override:
        if "garment_summary" in personalized_fit_override and personalized_fit_override["garment_summary"]:
            garment_summary = personalized_fit_override["garment_summary"]
        if "how_it_works_with_you" in personalized_fit_override and personalized_fit_override["how_it_works_with_you"]:
            how_it_works_with_you = personalized_fit_override["how_it_works_with_you"]
        if "complexion_harmony" in personalized_fit_override and personalized_fit_override["complexion_harmony"]:
            complexion_harmony = personalized_fit_override["complexion_harmony"]
        if "silhouette_advice" in personalized_fit_override and personalized_fit_override["silhouette_advice"]:
            silhouette_advice = personalized_fit_override["silhouette_advice"]

    personalized_analysis = {
        "garment_summary": garment_summary,
        "how_it_works_with_you": how_it_works_with_you,
        "complexion_harmony": complexion_harmony,
        "silhouette_advice": silhouette_advice,
        "recommended_looks_count": 4,
        "try_on_status": "personalized" if is_personalized else "unpersonalized_preview",
        "validation_message": getattr(user_profile, "validation_message", None) if user_profile else None,
    }

    return {
        "recommended_colours": swatches,
        "outfit_suggestions": outfits,
        "overall_advice": rule["advice"],
        "personalized_analysis": personalized_analysis,
    }
