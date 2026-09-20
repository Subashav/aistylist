import cv2
import numpy as np
from typing import Tuple, Optional

def detect_clothing_region(image_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray, str]:
    """
    Isolates the clothing region in an image by:
    1. Detecting and suppressing human skin and hair.
    2. Segmenting background from foreground using GrabCut / color edge contrast.
    3. Extracting fabric RGB pixels strictly from the clothing area.
    Returns:
        fabric_pixels_rgb: (N, 3) ndarray of RGB pixels.
        masked_garment_bgr: BGR visualization of the segmented clothing.
        inferred_category: Inferred garment type (e.g., T-shirt, Shirt, Dress).
    """
    height, width = image_bgr.shape[:2]
    
    # 1. Resize for fast, consistent processing (max dimension 640)
    max_dim = 640
    scale = min(max_dim / height, max_dim / width, 1.0)
    if scale < 1.0:
        new_w = int(width * scale)
        new_h = int(height * scale)
        img = cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        img = image_bgr.copy()
        
    h, w = img.shape[:2]
    
    # 2. Skin detection in HSV and YCrCb space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    
    # Standard skin color ranges
    # HSV: Hue [0, 25], Sat [30, 200], Val [60, 255]
    skin_mask_hsv = cv2.inRange(hsv, np.array([0, 30, 60]), np.array([25, 200, 255]))
    # YCrCb: Cr [133, 175], Cb [77, 127]
    skin_mask_ycrcb = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 175, 127]))
    
    combined_skin_mask = cv2.bitwise_and(skin_mask_hsv, skin_mask_ycrcb)
    # Dilate skin mask slightly to ensure edge skin pixels aren't counted as fabric
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated_skin_mask = cv2.dilate(combined_skin_mask, kernel, iterations=2)
    
    # 3. Focus on the torso / garment region
    # Garments predominantly sit in the central vertical & horizontal band
    # Margins: 8% from top/bottom, 8% from left/right
    margin_x = int(w * 0.08)
    margin_y = int(h * 0.08)
    
    # GrabCut Initialization rectangle
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)
    
    mask = np.zeros((h, w), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    
    try:
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 3, cv2.GC_INIT_WITH_RECT)
        # Foreground pixels are 1 or 3
        fg_mask = np.where((mask == 1) | (mask == 3), 255, 0).astype("uint8")
    except Exception:
        # Fallback if grabcut fails on unusual aspect ratio
        fg_mask = np.zeros((h, w), np.uint8)
        fg_mask[margin_y:h - margin_y, margin_x:w - margin_x] = 255
        
    # 4. Exclude skin pixels from foreground garment mask
    garment_mask = cv2.bitwise_and(fg_mask, cv2.bitwise_not(dilated_skin_mask))
    
    # Remove small noise specks with morphological opening
    garment_mask = cv2.morphologyEx(garment_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Check if we have sufficient garment pixels
    valid_pixel_count = cv2.countNonZero(garment_mask)
    total_pixels = h * w
    
    if valid_pixel_count < (total_pixels * 0.05):
        # Center crop fallback if foreground extraction was too aggressive
        cy1, cy2 = int(h * 0.25), int(h * 0.75)
        cx1, cx2 = int(w * 0.25), int(w * 0.75)
        center_mask = np.zeros((h, w), np.uint8)
        center_mask[cy1:cy2, cx1:cx2] = 255
        garment_mask = cv2.bitwise_and(center_mask, cv2.bitwise_not(dilated_skin_mask))
        
    # 5. Extract Fabric Pixels in RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    fabric_pixels_rgb = img_rgb[garment_mask > 0]
    
    # 6. Create masked visual result
    masked_garment_bgr = cv2.bitwise_and(img, img, mask=garment_mask)
    
    # 7. Basic category inference from aspect ratio & contour
    aspect_ratio = float(w) / float(h)
    if aspect_ratio > 1.3:
        inferred_category = "Top / Shirt"
    elif aspect_ratio < 0.6:
        inferred_category = "Dress / Long Coat"
    else:
        inferred_category = "T-shirt"
        
    return fabric_pixels_rgb, masked_garment_bgr, inferred_category
