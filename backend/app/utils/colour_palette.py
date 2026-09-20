import numpy as np

FASHION_PALETTE = [
    # BLUE FAMILY
    {"base": "Blue", "shade": "Royal Blue", "hex": "#4169E1", "rgb": (65, 105, 225)},
    {"base": "Blue", "shade": "Classic Blue", "hex": "#0F52BA", "rgb": (15, 82, 186)},
    {"base": "Blue", "shade": "Sky Blue", "hex": "#87CEEB", "rgb": (135, 206, 235)},
    {"base": "Blue", "shade": "Light Blue", "hex": "#ADD8E6", "rgb": (173, 216, 230)},
    {"base": "Blue", "shade": "Baby Blue", "hex": "#89CFF0", "rgb": (137, 207, 240)},
    {"base": "Navy", "shade": "Navy Blue", "hex": "#000080", "rgb": (0, 0, 128)},
    {"base": "Navy", "shade": "Dark Navy", "hex": "#000055", "rgb": (0, 0, 85)},
    {"base": "Navy", "shade": "Midnight Blue", "hex": "#191970", "rgb": (25, 25, 112)},
    
    # RED / MAROON FAMILY
    {"base": "Red", "shade": "Crimson Red", "hex": "#DC143C", "rgb": (220, 20, 60)},
    {"base": "Red", "shade": "Bright Red", "hex": "#FF0000", "rgb": (255, 0, 0)},
    {"base": "Red", "shade": "Dark Red", "hex": "#8B0000", "rgb": (139, 0, 0)},
    {"base": "Maroon", "shade": "Maroon", "hex": "#800000", "rgb": (128, 0, 0)},
    {"base": "Maroon", "shade": "Burgundy", "hex": "#800020", "rgb": (128, 0, 32)},
    {"base": "Maroon", "shade": "Wine", "hex": "#722F37", "rgb": (114, 47, 55)},
    
    # GREEN / OLIVE FAMILY
    {"base": "Green", "shade": "Emerald Green", "hex": "#50C878", "rgb": (80, 200, 120)},
    {"base": "Green", "shade": "Forest Green", "hex": "#228B22", "rgb": (34, 139, 34)},
    {"base": "Green", "shade": "Dark Green", "hex": "#006400", "rgb": (0, 100, 0)},
    {"base": "Green", "shade": "Light Green", "hex": "#90EE90", "rgb": (144, 238, 144)},
    {"base": "Green", "shade": "Mint Green", "hex": "#98FF98", "rgb": (152, 255, 152)},
    {"base": "Green", "shade": "Sage Green", "hex": "#9DC183", "rgb": (157, 193, 131)},
    {"base": "Olive", "shade": "Olive Green", "hex": "#808000", "rgb": (128, 128, 0)},
    {"base": "Olive", "shade": "Dark Olive", "hex": "#556B2F", "rgb": (85, 107, 47)},
    
    # NEUTRALS (BLACK, WHITE, GREY)
    {"base": "Black", "shade": "Jet Black", "hex": "#111111", "rgb": (17, 17, 17)},
    {"base": "Black", "shade": "Soft Black", "hex": "#2B2B2B", "rgb": (43, 43, 43)},
    {"base": "White", "shade": "Pure White", "hex": "#FFFFFF", "rgb": (255, 255, 255)},
    {"base": "White", "shade": "Off-White", "hex": "#FAF9F6", "rgb": (250, 249, 246)},
    {"base": "Cream", "shade": "Cream", "hex": "#FFFDD0", "rgb": (255, 253, 208)},
    {"base": "Grey", "shade": "Light Grey", "hex": "#D3D3D3", "rgb": (211, 211, 211)},
    {"base": "Grey", "shade": "Heather Grey", "hex": "#9E9E9E", "rgb": (158, 158, 158)},
    {"base": "Grey", "shade": "Charcoal Grey", "hex": "#36454F", "rgb": (54, 69, 79)},
    
    # WARM EARTH TONES (BEIGE, BROWN, ORANGE, YELLOW)
    {"base": "Beige", "shade": "Warm Beige", "hex": "#F5F5DC", "rgb": (245, 245, 220)},
    {"base": "Beige", "shade": "Sand Beige", "hex": "#C2B280", "rgb": (194, 178, 128)},
    {"base": "Brown", "shade": "Camel Brown", "hex": "#C19A6B", "rgb": (193, 154, 107)},
    {"base": "Brown", "shade": "Chocolate Brown", "hex": "#7B3F00", "rgb": (123, 63, 0)},
    {"base": "Brown", "shade": "Dark Brown", "hex": "#4A2E18", "rgb": (74, 46, 24)},
    {"base": "Yellow", "shade": "Mustard Yellow", "hex": "#FFDB58", "rgb": (255, 219, 88)},
    {"base": "Yellow", "shade": "Bright Yellow", "hex": "#FFEA00", "rgb": (255, 234, 0)},
    {"base": "Yellow", "shade": "Pastel Yellow", "hex": "#FFFACD", "rgb": (255, 250, 205)},
    {"base": "Orange", "shade": "Tangerine Orange", "hex": "#FFA500", "rgb": (255, 165, 0)},
    {"base": "Orange", "shade": "Rust / Terracotta", "hex": "#E2725B", "rgb": (226, 114, 91)},
    
    # PINK & PURPLE FAMILY
    {"base": "Pink", "shade": "Pastel Pink", "hex": "#FFD1DC", "rgb": (255, 209, 220)},
    {"base": "Pink", "shade": "Blush Pink", "hex": "#DE5D83", "rgb": (222, 93, 131)},
    {"base": "Pink", "shade": "Hot Pink", "hex": "#FF69B4", "rgb": (255, 105, 180)},
    {"base": "Purple", "shade": "Lavender", "hex": "#E6E6FA", "rgb": (230, 230, 250)},
    {"base": "Purple", "shade": "Royal Purple", "hex": "#7851A9", "rgb": (120, 81, 169)},
    {"base": "Purple", "shade": "Deep Plum", "hex": "#4A0E4E", "rgb": (74, 14, 78)},
]

def rgb_to_lab(rgb):
    """Convert RGB [0..255] to CIELAB space for perceptual distance matching."""
    # Normalized sRGB
    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0

    # Gamma inverse companding
    def pivot_rgb(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    r_lin = pivot_rgb(r)
    g_lin = pivot_rgb(g)
    b_lin = pivot_rgb(b)

    # sRGB to CIE XYZ using D65 illuminant
    x = (r_lin * 0.4124564 + g_lin * 0.3575761 + b_lin * 0.1804375) / 0.95047
    y = (r_lin * 0.2126729 + g_lin * 0.7151522 + b_lin * 0.0721750) / 1.00000
    z = (r_lin * 0.0193339 + g_lin * 0.1191920 + b_lin * 0.9503041) / 1.08883

    def pivot_xyz(c):
        return c ** (1.0 / 3.0) if c > 0.008856 else (7.787 * c) + (16.0 / 116.0)

    fx = pivot_xyz(x)
    fy = pivot_xyz(y)
    fz = pivot_xyz(z)

    L = (116.0 * fy) - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    return np.array([L, a, b])

# Precompute LAB values for all fashion palette colors
for entry in FASHION_PALETTE:
    entry["lab"] = rgb_to_lab(entry["rgb"])
