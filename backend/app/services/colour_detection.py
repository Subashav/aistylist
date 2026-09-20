import numpy as np
from sklearn.cluster import KMeans
from typing import Dict, Any
from app.utils.colour_palette import FASHION_PALETTE, rgb_to_lab

def extract_actual_clothing_colour(fabric_pixels_rgb: np.ndarray) -> Dict[str, Any]:
    """
    Applies K-Means clustering in CIELAB color space to extract dominant fabric colour,
    classifies base colour and shade, computes HEX/RGB, and determines confidence.
    """
    if len(fabric_pixels_rgb) == 0:
        # Fallback if no valid pixels
        return {
            "base_colour": "Unknown",
            "colour_shade": "Undetected",
            "hex_value": "#808080",
            "rgb_value": "128, 128, 128",
            "confidence": 0.30,
            "is_low_confidence": True
        }

    # 1. Convert candidate fabric pixels to LAB space
    # Subsample if large array for speed
    max_samples = 15000
    if len(fabric_pixels_rgb) > max_samples:
        indices = np.random.choice(len(fabric_pixels_rgb), max_samples, replace=False)
        sample_pixels = fabric_pixels_rgb[indices]
    else:
        sample_pixels = fabric_pixels_rgb

    # 2. Filter out extreme glare and deep black shadows before clustering
    # Calculate approximate lightness
    r, g, b = sample_pixels[:, 0], sample_pixels[:, 1], sample_pixels[:, 2]
    # Rough perceived brightness
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    
    # Exclude severe shadows (< 15) and pure white glares (> 250 with low saturation)
    # But ensure we don't discard genuine black garments
    non_extreme = sample_pixels[(brightness > 12) & (brightness < 252)]
    if len(non_extreme) > (len(sample_pixels) * 0.2):
        cluster_input = non_extreme
    else:
        cluster_input = sample_pixels

    # 3. K-Means clustering (k=3 to find dominant fabric vs folds/buttons/trims)
    k = min(4, len(cluster_input))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=5)
    kmeans.fit(cluster_input)
    
    # 4. Find cluster with the largest representation
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    dominant_idx = labels[np.argmax(counts)]
    dominant_rgb = np.clip(np.round(kmeans.cluster_centers_[dominant_idx]), 0, 255).astype(int)
    
    dom_r, dom_g, dom_b = int(dominant_rgb[0]), int(dominant_rgb[1]), int(dominant_rgb[2])
    hex_value = f"#{dom_r:02X}{dom_g:02X}{dom_b:02X}"
    rgb_str = f"{dom_r}, {dom_g}, {dom_b}"
    
    # Dominance ratio (fraction of pixels belonging to primary cluster)
    dominance_ratio = float(np.max(counts)) / float(len(cluster_input))
    
    # 5. Convert dominant RGB to CIELAB for perceptual distance matching
    dominant_lab = rgb_to_lab((dom_r, dom_g, dom_b))
    
    # 6. Find closest matching shade in FASHION_PALETTE using CIELAB Delta-E
    best_match = None
    min_delta_e = float("inf")
    
    for item in FASHION_PALETTE:
        target_lab = item["lab"]
        # CIELAB Euclidean distance (perceptually uniform)
        delta_e = float(np.linalg.norm(dominant_lab - target_lab))
        if delta_e < min_delta_e:
            min_delta_e = delta_e
            best_match = item
            
    base_colour = best_match["base"] if best_match else "Blue"
    colour_shade = best_match["shade"] if best_match else "Royal Blue"
    
    # 7. Confidence Score Calculation
    # Combines dominance ratio (uniformity of clothing) and delta-E certainty
    # Delta-E under 15 is extremely close match, over 40 has higher uncertainty
    delta_certainty = max(0.2, min(1.0, 1.0 - (min_delta_e / 45.0)))
    confidence = round(0.55 * dominance_ratio + 0.45 * delta_certainty, 2)
    confidence = min(0.98, max(0.40, confidence))
    is_low = confidence < 0.60
    
    return {
        "base_colour": base_colour,
        "colour_shade": colour_shade,
        "hex_value": hex_value,
        "rgb_value": rgb_str,
        "confidence": confidence,
        "is_low_confidence": is_low,
        "delta_e": round(min_delta_e, 2)
    }
