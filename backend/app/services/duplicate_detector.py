"""
Duplicate Detection Service
===========================
Calculates perceptual difference hashes (dHash) to detect identical or
visually duplicate virtual try-on images before returning them to the user.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


def compute_image_dhash(image_path: Path, hash_size: int = 8) -> Optional[str]:
    """
    Computes a 64-bit difference hash (dHash) for an image.
    Robust to slight compression artifacts while identifying visual duplicates.
    """
    if not image_path.exists():
        return None
    try:
        with Image.open(image_path) as img:
            # Convert to grayscale and resize to (hash_size + 1, hash_size)
            resized = img.convert("L").resize(
                (hash_size + 1, hash_size),
                Image.Resampling.LANCZOS,
            )
            pixels = np.array(resized, dtype=np.float32)
            # Compare adjacent pixels
            diff = pixels[:, 1:] > pixels[:, :-1]
            return "".join("1" if b else "0" for b in diff.flatten())
    except Exception as e:
        logger.warning("Failed to compute dHash for %s: %s", image_path, e)
        return None


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculates Hamming distance between two binary hash strings."""
    if len(hash1) != len(hash2):
        return max(len(hash1), len(hash2))
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))


def check_for_duplicates(
    image_paths: List[Optional[Path]],
    similarity_threshold: int = 2,
) -> List[Tuple[int, int, int]]:
    """
    Compares all pairs of generated try-on images.
    Returns list of duplicate tuples: (index_a, index_b, hamming_distance).
    A distance of 0 indicates an identical duplicate; <= 2 indicates near-identical.
    """
    duplicates = []
    hashes: Dict[int, str] = {}

    for idx, p in enumerate(image_paths):
        if p and p.exists():
            h = compute_image_dhash(p)
            if h:
                hashes[idx] = h

    indices = list(hashes.keys())
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            idx_a = indices[i]
            idx_b = indices[j]
            dist = hamming_distance(hashes[idx_a], hashes[idx_b])
            if dist <= similarity_threshold:
                logger.warning(
                    "Duplicate image detected: Look %d and Look %d have hamming distance %d (threshold %d)",
                    idx_a + 1,
                    idx_b + 1,
                    dist,
                    similarity_threshold,
                )
                duplicates.append((idx_a, idx_b, dist))

    return duplicates
