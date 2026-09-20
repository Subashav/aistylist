"""
Outfit Visual Provider
======================
Generates colour-accurate outfit card images from structured outfit recommendation data.

Architecture:
  OutfitVisualProvider  — abstract base class (swap in AI generation by subclassing)
  PillowOutfitComposer  — default provider using Pillow (no external API required)

Each generated card:
  - 480 × 660 px PNG
  - Dark editorial header with outfit title + occasion
  - 4 colour-accurate garment strips: Top, Bottoms, Footwear, Accent/Layer
  - HEX badge on each strip for transparency
  - Saved to uploads/outfit_recommendations/ with a UUID filename
"""

import uuid
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Try importing Pillow — gracefully degrade if unavailable
# ---------------------------------------------------------------------------
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not found — outfit visual generation disabled.")

# ---------------------------------------------------------------------------
# Colour keyword → HEX mapping
# Covers every colour word used by the recommendation engine.
# Longest phrases are matched first to avoid "navy" matching before "navy blue".
# ---------------------------------------------------------------------------
COLOUR_KEYWORD_MAP: Dict[str, str] = {
    # Whites & creams
    "crisp white": "#FFFFFF",
    "pure white": "#FFFFFF",
    "white linen": "#FAF0E6",
    "off-white": "#FAF9F6",
    "off white": "#FAF9F6",
    "cream": "#FFFDD0",
    "warm cream": "#FFFDD0",
    "ecru": "#FFFDD0",
    "ivory": "#FFFFF0",
    "linen": "#FAF0E6",
    "chalk": "#F8F8FF",
    "white": "#FFFFFF",

    # Blacks
    "jet black": "#111111",
    "soft black": "#2B2B2B",
    "matte black": "#111111",
    "black": "#111111",

    # Greys
    "charcoal grey": "#36454F",
    "charcoal gray": "#36454F",
    "charcoal": "#36454F",
    "heather grey": "#9E9E9E",
    "heather gray": "#9E9E9E",
    "light grey": "#D3D3D3",
    "light gray": "#D3D3D3",
    "brushed steel": "#9E9E9E",
    "flannel": "#9E9E9E",
    "grey": "#9E9E9E",
    "gray": "#9E9E9E",

    # Blues
    "midnight blue": "#191970",
    "dark navy": "#000055",
    "royal blue": "#4169E1",
    "classic blue": "#0F52BA",
    "denim blue": "#4682B4",
    "sky blue": "#87CEEB",
    "light blue": "#ADD8E6",
    "baby blue": "#89CFF0",
    "washed blue": "#7CA3C6",
    "medium wash": "#7CA3C6",
    "light wash": "#A8C4D4",
    "dark indigo": "#3B2B6B",
    "indigo": "#4B0082",
    "navy blue": "#000080",
    "navy": "#000080",
    "denim": "#4682B4",
    "blue": "#4169E1",

    # Reds & Maroons
    "crimson red": "#DC143C",
    "dark red": "#8B0000",
    "bright red": "#FF0000",
    "oxblood": "#800020",
    "burgundy": "#800020",
    "maroon": "#800000",
    "wine": "#722F37",
    "red": "#DC143C",

    # Greens & Olives
    "emerald green": "#50C878",
    "forest green": "#228B22",
    "sage green": "#9DC183",
    "dark green": "#006400",
    "light green": "#90EE90",
    "dark olive": "#556B2F",
    "olive green": "#808000",
    "mint green": "#98FF98",
    "olive": "#808000",
    "green": "#50C878",

    # Browns & Earths
    "camel brown": "#C19A6B",
    "chocolate brown": "#7B3F00",
    "dark brown": "#4A2E18",
    "warm beige": "#D2B48C",
    "sand beige": "#C2B280",
    "cognac": "#9B5523",
    "camel": "#C19A6B",
    "beige": "#D2B48C",
    "suede": "#C19A6B",
    "khaki": "#C2B280",
    "sand": "#C2B280",
    "tan": "#C19A6B",
    "taupe": "#918273",
    "brown": "#7B3F00",

    # Yellows & Oranges
    "mustard yellow": "#FFDB58",
    "pastel yellow": "#FFFACD",
    "bright yellow": "#FFEA00",
    "mustard": "#FFDB58",
    "yellow": "#FFDB58",
    "tangerine": "#FFA500",
    "terracotta": "#E2725B",
    "rust": "#E2725B",
    "orange": "#FFA500",

    # Pinks & Purples
    "pastel pink": "#FFD1DC",
    "blush pink": "#DE5D83",
    "dusty pink": "#DCAE96",
    "hot pink": "#FF69B4",
    "royal purple": "#7851A9",
    "deep plum": "#4A0E4E",
    "lavender": "#E6E6FA",
    "blush": "#DE5D83",
    "pink": "#FFD1DC",
    "plum": "#4A0E4E",
    "purple": "#7851A9",

    # Metals / Accessories
    "rose gold": "#B76E79",
    "gunmetal": "#2C3539",
    "antiqued brass": "#B5A642",
    "silver": "#C0C0C0",
    "brass": "#B5A642",
    "bronze": "#CD7F32",
    "copper": "#B87333",
    "gold": "#D4AF37",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_hex_from_text(text: str) -> str:
    """
    Extracts the most likely garment colour from a description string.
    Matches the longest keyword phrase first to maximise accuracy.
    Returns a HEX colour string.
    """
    if not text:
        return "#A0A8B0"
    text_lower = text.lower()
    sorted_keys = sorted(COLOUR_KEYWORD_MAP.keys(), key=len, reverse=True)
    for kw in sorted_keys:
        if kw in text_lower:
            return COLOUR_KEYWORD_MAP[kw]
    return "#A0A8B0"  # Neutral cool-grey fallback


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return (160, 168, 176)


def _is_dark(rgb: tuple) -> bool:
    r, g, b = rgb
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance < 145


def _truncate(text: str, max_len: int = 44) -> str:
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


def _load_font(size: int):
    """Attempt to load a system font; fall back to PIL built-in default."""
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DejaVuSans.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _load_bold_font(size: int):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "DejaVuSans-Bold.ttf",
        "arialbd.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return _load_font(size)


# ---------------------------------------------------------------------------
# Provider Interface
# ---------------------------------------------------------------------------

class OutfitVisualProvider(ABC):
    """
    Abstract base class for outfit visual generation.
    Implement this to swap in any backend (AI API, Stable Diffusion, Pillow, etc.).
    """

    @abstractmethod
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
        """
        Generate a visual for a single outfit recommendation.

        Args:
            outfit: The OutfitSuggestion dict (title, occasion, top, bottom, shoes, accessories, explanation).
            detected_colour_hex: HEX of the detected garment (e.g. '#4169E1').
            detected_colour_shade: Human shade name (e.g. 'Royal Blue').
            detected_clothing_type: Garment type (e.g. 'T-shirt').
            output_dir: Directory to save generated images.
            reference_image_path: Optional path to the user's uploaded clothing photo.
            semantic_data: Optional GarmentAnalysis semantic metadata.

        Returns:
            Relative URL string like '/uploads/outfit_recommendations/outfit_abc.png',
            or None if generation failed.
        """


# ---------------------------------------------------------------------------
# Default Fallback Provider — Pillow Outfit Card Composer
# ---------------------------------------------------------------------------

class PillowOutfitComposer(OutfitVisualProvider):
    """
    Generates a clean, colour-accurate outfit card PNG using Pillow.
    Acts as a reliable local offline fallback whenever AI image generation is disabled
    or temporarily unavailable.
    """

    # Fixed canvas size
    WIDTH = 480
    HEIGHT = 660
    HEADER_H = 90
    PADDING = 10

    # Garment strip heights (must sum to HEIGHT - HEADER_H - small gap)
    STRIP_HEIGHTS = [155, 145, 130, 120]
    STRIP_LABELS = ["TOP / BASE", "BOTTOMS", "FOOTWEAR", "ACCENT / LAYER"]

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
        if not PIL_AVAILABLE:
            return None
        try:
            return self._compose(
                outfit=outfit,
                detected_colour_hex=detected_colour_hex,
                detected_colour_shade=detected_colour_shade,
                detected_clothing_type=detected_clothing_type,
                output_dir=output_dir,
            )
        except Exception as exc:
            logger.error("PillowOutfitComposer failed: %s", exc, exc_info=True)
            return None

    def _compose(
        self,
        outfit: Dict[str, Any],
        detected_colour_hex: str,
        detected_colour_shade: str,
        detected_clothing_type: str,
        output_dir: Path,
    ) -> str:
        W, H = self.WIDTH, self.HEIGHT
        BG = (248, 249, 250)
        HEADER_BG = (22, 22, 30)

        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)

        # ── Header ──────────────────────────────────────────────────────────
        draw.rectangle([0, 0, W, self.HEADER_H], fill=HEADER_BG)

        title_font = _load_bold_font(17)
        occ_font = _load_font(12)

        title_text = outfit.get("title", "Outfit Recommendation").upper()
        draw.text((20, 16), title_text, fill=(255, 255, 255), font=title_font)

        occ_text = outfit.get("occasion", "")
        draw.text((20, 50), occ_text, fill=(170, 172, 185), font=occ_font)

        # Accent bar at bottom of header
        acc_rgb = _hex_to_rgb(detected_colour_hex)
        draw.rectangle([0, self.HEADER_H - 3, W, self.HEADER_H], fill=acc_rgb)

        # ── Garment Strips ───────────────────────────────────────────────────
        strip_items = [
            f"{detected_colour_shade} {detected_clothing_type}",
            outfit.get("bottom", ""),
            outfit.get("shoes", ""),
            outfit.get("accessories", ""),
        ]

        strip_hexes = [
            detected_colour_hex,
            _extract_hex_from_text(outfit.get("bottom", "")),
            _extract_hex_from_text(outfit.get("shoes", "")),
            _extract_hex_from_text(outfit.get("accessories", "")),
        ]

        label_font = _load_bold_font(10)
        item_font = _load_font(13)
        hex_font = _load_font(10)

        PAD = self.PADDING
        y = self.HEADER_H + PAD

        for i, (label, item, hex_val, strip_h) in enumerate(
            zip(self.STRIP_LABELS, strip_items, strip_hexes, self.STRIP_HEIGHTS)
        ):
            rgb = _hex_to_rgb(hex_val)
            is_dark = _is_dark(rgb)
            text_col = (255, 255, 255) if is_dark else (28, 28, 36)
            muted_col = (210, 215, 220) if is_dark else (90, 96, 110)

            strip_bottom = y + strip_h - PAD

            # Main colour fill
            draw.rectangle([PAD, y, W - PAD, strip_bottom], fill=rgb)

            # Subtle inner border for light colours
            border_col = (200, 202, 208) if not is_dark else (255, 255, 255, 30)
            draw.rectangle([PAD, y, W - PAD, strip_bottom], outline=(200, 202, 208), width=1)

            # Colour swatch square on left
            swatch_size = 32
            swatch_x1, swatch_y1 = PAD + 14, y + 16
            swatch_x2, swatch_y2 = swatch_x1 + swatch_size, swatch_y1 + swatch_size

            # Slightly lighter/darker swatch for visual accent
            sr, sg, sb = rgb
            sv_factor = 0.85 if is_dark else 1.15
            swatch_fill = (
                min(255, int(sr * sv_factor)),
                min(255, int(sg * sv_factor)),
                min(255, int(sb * sv_factor)),
            )
            draw.rectangle([swatch_x1, swatch_y1, swatch_x2, swatch_y2], fill=swatch_fill)
            draw.rectangle([swatch_x1, swatch_y1, swatch_x2, swatch_y2],
                           outline=(200, 202, 208), width=1)

            # Text to the right of the swatch
            tx = swatch_x2 + 14
            draw.text((tx, y + 14), label, fill=muted_col, font=label_font)
            draw.text((tx, y + 30), _truncate(item, 36), fill=text_col, font=item_font)

            # HEX badge bottom-right
            hex_text = hex_val.upper()
            draw.text((W - PAD - 70, strip_bottom - 18), hex_text,
                      fill=muted_col, font=hex_font)

            # Divider line at bottom of strip (skip last)
            if i < len(self.STRIP_HEIGHTS) - 1:
                div_y = strip_bottom + PAD // 2
                draw.line([(PAD, div_y), (W - PAD, div_y)], fill=(220, 221, 225), width=1)

            y = strip_bottom + PAD + 2

        # ── Save ─────────────────────────────────────────────────────────────
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"outfit_{uuid.uuid4().hex}.png"
        filepath = output_dir / filename
        img.save(str(filepath), "PNG", optimize=True)

        return f"/uploads/outfit_recommendations/{filename}"


# ---------------------------------------------------------------------------
# Factory — returns the active provider based on configuration
# ---------------------------------------------------------------------------

def get_visual_provider() -> OutfitVisualProvider:
    """
    Returns the configured visual provider.
    - 'ai'     : AIImageProvider (photorealistic fashion photography)
    - 'pillow' : PillowOutfitComposer (local infographic fallback)
    """
    from app.config import settings
    
    provider_mode = settings.OUTFIT_VISUAL_PROVIDER.lower().strip()
    if provider_mode == "ai":
        from app.services.ai_image_provider import AIImageProvider
        return AIImageProvider()
    
    return PillowOutfitComposer()

