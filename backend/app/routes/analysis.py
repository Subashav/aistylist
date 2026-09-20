import os
import time
import uuid
import asyncio
import logging
import cv2
import numpy as np
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings, BASE_DIR
from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_user
from app.schemas.analysis import (
    AnalysisResponse,
    ColourSwatch,
    OutfitSuggestion,
    PersonalizedStyleAnalysis,
    VirtualTryOnResponse,
)
from app.services.clothing_detection import detect_clothing_region
from app.services.colour_detection import extract_actual_clothing_colour
from app.services.recommendation_engine import generate_fashion_recommendations
from app.services.visual_provider import get_visual_provider
from app.services.gemini_service import (
    analyze_garment_semantics,
    analyze_personalized_fit,
    generate_four_distinct_looks,
)
import httpx
from app.services.storage_provider import get_storage_provider, ProductionImageStorage
from app.services.user_analysis_service import analyze_user_portrait, UserStylingProfile
from app.services.virtual_tryon_provider import (
    get_virtual_tryon_provider,
    DisabledVirtualTryOnProvider,
    ProductionVTONProvider,
)
from app.services.duplicate_detector import check_for_duplicates


logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Analysis"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

def validate_image_file(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type ({file.filename}). Please upload a JPEG, PNG, or WebP image."
        )
    return ext if ext in ALLOWED_EXTENSIONS else ".jpg"

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_clothing(
    clothing_image: UploadFile = File(...),
    user_image: Optional[UploadFile] = File(None),
    clothing_category_hint: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    storage = get_storage_provider()

    # 1. Validate & Save Clothing Image
    c_ext = validate_image_file(clothing_image)
    c_filename = f"clothing_{uuid.uuid4().hex}{c_ext}"
    c_path = settings.UPLOAD_DIR / c_filename
    
    c_content = await clothing_image.read()
    if len(c_content) == 0:
        raise HTTPException(status_code=400, detail="Clothing image file is empty.")
        
    try:
        with open(c_path, "wb") as f:
            f.write(c_content)
    except Exception as io_err:
        logger.debug("Local disk write note: %s", io_err)

    c_url = await storage.save_image(
        c_content,
        c_filename,
        content_type=clothing_image.content_type or "image/jpeg",
    )
        
    # 2. Process User Portrait Photo if provided
    u_url = None
    u_path = None
    if user_image and user_image.filename:
        u_ext = validate_image_file(user_image)
        u_filename = f"user_{uuid.uuid4().hex}{u_ext}"
        u_path = settings.UPLOAD_DIR / u_filename
        u_content = await user_image.read()
        if len(u_content) > 0:
            try:
                with open(u_path, "wb") as f:
                    f.write(u_content)
            except Exception as io_err:
                logger.debug("Local disk write note: %s", io_err)
            u_url = await storage.save_image(
                u_content,
                u_filename,
                content_type=user_image.content_type or "image/jpeg",
            )

    # 3. Decode clothing image for OpenCV
    t_start = time.perf_counter()
    nparr = np.frombuffer(c_content, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Failed to decode clothing image. Please upload a clear photo.")
        
    # 4. Computer Vision Step: Clothing Segmentation & Skin Suppression
    t_cv_start = time.perf_counter()
    fabric_pixels, masked_vis, detected_cat = detect_clothing_region(img_bgr)
    
    # 5. Computer Vision Step: LAB K-Means Clustering & CIEDE2000 Shade Detection
    color_info = extract_actual_clothing_colour(fabric_pixels)
    t_cv_end = time.perf_counter()
    logger.info("CV Pipeline Time: %.3fs (Color: %s %s, Confidence: %.2f)",
                t_cv_end - t_cv_start, color_info["colour_shade"], color_info["hex_value"], color_info["confidence"])
    
    # 6. Optional Gemini Semantic Understanding Step for Garment & User Portrait
    t_gem_start = time.perf_counter()
    semantic_data = None
    user_profile = None

    async def _fetch_garment_semantics():
        if settings.GEMINI_ENABLED and settings.GEMINI_API_KEY:
            return await analyze_garment_semantics(c_path)
        return None

    async def _fetch_user_analysis():
        if u_path and u_path.exists():
            return await analyze_user_portrait(u_path)
        return None

    semantic_data, user_profile = await asyncio.gather(
        _fetch_garment_semantics(),
        _fetch_user_analysis(),
    )
    t_gem_end = time.perf_counter()
    logger.info("Semantic / Profile Analysis Time: %.3fs", t_gem_end - t_gem_start)

    # Resolve garment category: Manual user hint > Gemini Subcategory > CV Inferred
    if clothing_category_hint and clothing_category_hint.strip():
        category = clothing_category_hint.strip()
    elif semantic_data and semantic_data.subcategory:
        category = semantic_data.subcategory
    else:
        category = detected_cat

    # 7. Personalized Color Harmony Engine & Enriched Outfit Suggestions
    t_rec_start = time.perf_counter()
    pers_fit_data = None
    gemini_looks_plan = None
    if user_profile and getattr(user_profile, "is_valid_person", False):
        pers_fit_data, gemini_looks_plan = await asyncio.gather(
            analyze_personalized_fit(
                colour_shade=color_info["colour_shade"],
                hex_value=color_info["hex_value"],
                clothing_type=category,
                garment_semantics=semantic_data,
                user_profile=user_profile,
            ),
            generate_four_distinct_looks(
                colour_shade=color_info["colour_shade"],
                hex_value=color_info["hex_value"],
                clothing_type=category,
                garment_semantics=semantic_data,
                user_profile=user_profile,
            ),
        )

    recommendations = generate_fashion_recommendations(
        clothing_type=category,
        detected_colour=color_info["base_colour"],
        colour_shade=color_info["colour_shade"],
        hex_value=color_info["hex_value"],
        semantic_data=semantic_data,
        user_profile=user_profile,
        personalized_fit_override=pers_fit_data,
        gemini_looks_plan=gemini_looks_plan,
    )
    t_rec_end = time.perf_counter()
    logger.info("Recommendation Engine Time: %.3fs", t_rec_end - t_rec_start)

    # 8. Local FASHN VTON Virtual Try-On Generation (Sequential GPU Inference for exactly 2 looks)
    t_img_start = time.perf_counter()
    vton_provider = get_virtual_tryon_provider()
    max_looks_to_generate = getattr(settings, "TRYON_MAX_LOOKS", 2)

    outfit_suggestions_with_visuals = []
    has_actual_tryon = False

    # Execute exactly up to 2 looks for real FASHN VTON; remaining looks are Complete Outfit & Material Guides
    for idx, outfit_data in enumerate(recommendations["outfit_suggestions"]):
        try:
            if idx < max_looks_to_generate:
                look_seed = 42 + idx * 101
                person_img = u_path if (u_path and u_path.exists()) else None
                garment_img = c_path if (c_path and c_path.exists()) else c_content
                res = await vton_provider.generate_try_on(
                    person_image=person_img,
                    garment_image=garment_img,
                    category=category,
                    styling_context=outfit_data,
                    detected_colour_shade=color_info["colour_shade"],
                    detected_colour_hex=color_info["hex_value"],
                    semantic_data=semantic_data,
                    seed=look_seed,
                )
                img_url = res.get("image_url")
                res_type = res.get("result_type", "actual_try_on")
                if res_type == "actual_try_on" and img_url:
                    has_actual_tryon = True
                    # If remote URL (e.g. FASHN Cloud API), persist in storage provider
                    if img_url.startswith("http://") or img_url.startswith("https://"):
                        try:
                            async with httpx.AsyncClient(timeout=15.0) as client:
                                dl_resp = await client.get(img_url)
                                if dl_resp.status_code == 200:
                                    vton_fn = f"tryon_{uuid.uuid4().hex}.png"
                                    img_url = await storage.save_image(
                                        dl_resp.content,
                                        vton_fn,
                                        content_type="image/png",
                                        subfolder="virtual_tryon",
                                    )
                        except Exception as dl_err:
                            logger.warning("Could not persist remote try-on image; using direct URL: %s", dl_err)
                    elif img_url.startswith("/uploads/"):
                        # If local file generated by local FASHN, register with storage provider for persistence
                        try:
                            local_f = settings.DATA_DIR / img_url.lstrip("/")
                            if local_f.exists():
                                stored_url = await storage.save_image(
                                    local_f.read_bytes(),
                                    local_f.name,
                                    content_type="image/png",
                                    subfolder="virtual_tryon",
                                )
                                if isinstance(storage, ProductionImageStorage):
                                    img_url = stored_url
                        except Exception as st_err:
                            logger.debug("Storage persistence note: %s", st_err)

                outfit_suggestions_with_visuals.append(
                    OutfitSuggestion(
                        **outfit_data,
                        image_url=img_url,
                        try_on_image_url=img_url,
                        result_type=res_type,
                        try_on_type=res_type,
                        provider=res.get("provider", "fashn_vton_local"),
                    )
                )
            else:
                # Looks 3 & 4 (or when user portrait not supplied):
                # Complete Outfit & Material Guide with fabric coordination & palette
                outfit_suggestions_with_visuals.append(
                    OutfitSuggestion(
                        **outfit_data,
                        image_url=None,
                        try_on_image_url=None,
                        result_type="outfit_guide",
                        try_on_type="outfit_guide",
                        provider="outfit_material_guide",
                    )
                )
        except Exception as look_err:
            logger.warning("Error generating visual for look %d ('%s'): %s", idx + 1, outfit_data.get("title"), look_err)
            outfit_suggestions_with_visuals.append(
                OutfitSuggestion(
                    **outfit_data,
                    image_url=None,
                    try_on_image_url=None,
                    result_type="unavailable",
                    try_on_type="unavailable",
                    provider="none",
                )
            )

    # 8b. Duplicate Detection
    gen_paths = []
    for s in outfit_suggestions_with_visuals:
        if s.image_url and not s.image_url.startswith("data:"):
            gen_paths.append(BASE_DIR / s.image_url.lstrip("/"))
        else:
            gen_paths.append(None)
    duplicates = check_for_duplicates(gen_paths)
    if duplicates:
        logger.warning(
            "Duplicate check detected %d pair(s) of identical/near-identical try-on images: %s",
            len(duplicates),
            duplicates,
        )

    t_img_end = time.perf_counter()
    t_total = time.perf_counter() - t_start
    logger.info("Virtual Try-On Generation Time: %.3fs, Total Request Time: %.3fs",
                t_img_end - t_img_start, t_total)

    # 9. Construct Personalized Response
    pers_analysis = None
    if "personalized_analysis" in recommendations:
        pers_analysis = PersonalizedStyleAnalysis(**recommendations["personalized_analysis"])
        if has_actual_tryon:
            pers_analysis.try_on_status = "actual_try_on"
        else:
            pers_analysis.try_on_status = "outfit_preview"

    # Dynamic capability indicator: false if provider is disabled or unconfigured in production
    try_on_available = True
    if isinstance(vton_provider, DisabledVirtualTryOnProvider):
        try_on_available = False
    elif isinstance(vton_provider, ProductionVTONProvider) and not vton_provider.is_ready:
        try_on_available = False

    return AnalysisResponse(
        clothing_type=category,
        detected_colour=color_info["base_colour"],
        colour_shade=color_info["colour_shade"],
        hex_value=color_info["hex_value"],
        rgb_value=color_info["rgb_value"],
        confidence=color_info["confidence"],
        is_low_confidence=color_info["is_low_confidence"],
        clothing_image_url=c_url,
        user_image_url=u_url,
        recommended_colours=[ColourSwatch(**s) for s in recommendations["recommended_colours"]],
        outfit_suggestions=outfit_suggestions_with_visuals,
        overall_advice=recommendations["overall_advice"],
        personalized_analysis=pers_analysis,
        user_attributes=user_profile.model_dump() if user_profile else None,
        try_on_available=try_on_available,
    )


@router.post("/virtual-tryon", response_model=VirtualTryOnResponse)
async def direct_virtual_tryon(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    category: str = Form("T-shirt"),
    outfit_description: Optional[str] = Form(None),
    styling_instructions: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    """
    Direct Virtual Try-On endpoint:
    Takes person_image and garment_image with styling instructions,
    and returns an actual try-on image generated via local FASHN VTON.
    """
    storage = get_storage_provider()

    p_ext = validate_image_file(person_image)
    p_filename = f"person_{uuid.uuid4().hex}{p_ext}"
    p_path = settings.UPLOAD_DIR / p_filename
    p_content = await person_image.read()
    if len(p_content) == 0:
        raise HTTPException(status_code=400, detail="Person image is empty.")
    try:
        with open(p_path, "wb") as f:
            f.write(p_content)
    except Exception as io_err:
        logger.debug("Local disk write note: %s", io_err)
    await storage.save_image(p_content, p_filename, content_type=person_image.content_type or "image/jpeg")

    g_ext = validate_image_file(garment_image)
    g_filename = f"garment_{uuid.uuid4().hex}{g_ext}"
    g_path = settings.UPLOAD_DIR / g_filename
    g_content = await garment_image.read()
    if len(g_content) == 0:
        raise HTTPException(status_code=400, detail="Garment image is empty.")
    try:
        with open(g_path, "wb") as f:
            f.write(g_content)
    except Exception as io_err:
        logger.debug("Local disk write note: %s", io_err)
    await storage.save_image(g_content, g_filename, content_type=garment_image.content_type or "image/jpeg")

    # Extract garment colour for styling record
    nparr = np.frombuffer(g_content, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    detected_shade = "Classic"
    detected_hex = "#000000"
    if img_bgr is not None:
        try:
            fabric_pixels, _, _ = detect_clothing_region(img_bgr)
            color_info = extract_actual_clothing_colour(fabric_pixels)
            detected_shade = color_info.get("colour_shade", "Classic")
            detected_hex = color_info.get("hex_value", "#000000")
        except Exception as e:
            logger.warning("Color extraction exception during direct tryon: %s", e)

    look_data = {
        "title": "Clean Casual",
        "style_direction": styling_instructions or "Relaxed contemporary styling",
        "bottom": "Tailored trousers or clean denim",
        "shoes": "Classic low-top sneakers",
        "accessories": ["Minimalist watch"],
    }

    p_input = p_path if (p_path and p_path.exists()) else p_content
    g_input = g_path if (g_path and g_path.exists()) else g_content

    vton_provider = get_virtual_tryon_provider()
    res = await vton_provider.generate_try_on(
        person_image=p_input,
        garment_image=g_input,
        category=category,
        styling_context=look_data,
        detected_colour_shade=detected_shade,
        detected_colour_hex=detected_hex,
    )

    img_url = res.get("image_url")
    if img_url:
        if img_url.startswith("http://") or img_url.startswith("https://"):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    dl_resp = await client.get(img_url)
                    if dl_resp.status_code == 200:
                        vton_fn = f"tryon_{uuid.uuid4().hex}.png"
                        img_url = await storage.save_image(
                            dl_resp.content,
                            vton_fn,
                            content_type="image/png",
                            subfolder="virtual_tryon",
                        )
            except Exception as dl_err:
                logger.warning("Could not persist remote try-on image; using direct URL: %s", dl_err)
        elif img_url.startswith("/uploads/"):
            try:
                local_f = settings.DATA_DIR / img_url.lstrip("/")
                if local_f.exists():
                    stored_url = await storage.save_image(
                        local_f.read_bytes(),
                        local_f.name,
                        content_type="image/png",
                        subfolder="virtual_tryon",
                    )
                    if isinstance(storage, ProductionImageStorage):
                        img_url = stored_url
            except Exception as st_err:
                logger.debug("Storage persistence note: %s", st_err)

    return VirtualTryOnResponse(
        success=res.get("success", False),
        result_type=res.get("result_type", "actual_try_on"),
        image_url=img_url,
        provider=res.get("provider", "fashn_vton_local"),
        category=category,
        look=look_data,
        error_code=res.get("error_code"),
        message=res.get("message"),
    )


@router.get("/diagnostics/system")
def get_system_diagnostics():
    """
    Returns system diagnostic telemetry including GPU, VRAM, Gemini, and VTON status.
    Never exposes API keys.
    """
    import torch

    gpu_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    vram_total = None
    vram_free = None

    if gpu_available:
        try:
            total_b = torch.cuda.get_device_properties(0).total_memory
            reserved_b = torch.cuda.memory_reserved(0)
            allocated_b = torch.cuda.memory_allocated(0)
            vram_total = int(total_b / (1024 * 1024))
            vram_free = int((total_b - reserved_b) / (1024 * 1024))
        except Exception:
            pass

    gemini_configured = bool(settings.GEMINI_ENABLED and settings.GEMINI_API_KEY)
    vton_weights_exist = (
        settings.VTON_WEIGHTS_DIR.exists()
        and (settings.VTON_WEIGHTS_DIR / "model.safetensors").exists()
    )

    vton_provider = get_virtual_tryon_provider()
    vton_ready = getattr(vton_provider.local_provider, "is_ready", False) or vton_weights_exist

    return {
        "gpu_available": gpu_available,
        "gpu_name": gpu_name,
        "vram_total_mb": vram_total,
        "vram_available_mb": vram_free,
        "gemini_configured": gemini_configured,
        "vton_configured": settings.VTON_ENABLED,
        "vton_model": settings.VTON_MODEL_NAME,
        "vton_ready": vton_ready,
    }



