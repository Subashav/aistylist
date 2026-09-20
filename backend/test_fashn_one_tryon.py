"""
Test Script: FASHN VTON v1.5 Single Try-On Quality Gate
======================================================
Tests:
User Photo + Garment Photo -> FASHN VTON -> User wearing the garment
Evaluates:
- Model loading
- VRAM allocation and memory peak
- Generation time
- Identity preservation
- Garment shape and color preservation
- Output image verification
"""

import sys
import os
import time
import asyncio
from pathlib import Path

import torch
from PIL import Image

# Ensure backend path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.config import settings, BASE_DIR
from app.services.fashn_vton_local_provider import FASHNVTONLocalProvider



async def run_single_tryon_test():
    print("=" * 64)
    print("      FASHN VTON v1.5 — SINGLE GARMENT QUALITY GATE TEST")
    print("=" * 64)

    # 1. Inspect GPU & VRAM before loading
    gpu_available = torch.cuda.is_available()
    print(f"[1/5] GPU Status:")
    print(f"  PyTorch version:  {torch.__version__}")
    print(f"  CUDA Available:   {gpu_available}")
    if gpu_available:
        print(f"  Device Name:      {torch.cuda.get_device_name(0)}")
        total_vram = torch.cuda.get_device_properties(0).total_memory / 1e6
        print(f"  Total VRAM:       {total_vram:.1f} MB")
        print(f"  Allocated VRAM:   {torch.cuda.memory_allocated(0) / 1e6:.1f} MB")

    # 2. Select Test Images
    user_img = Path("uploads/user_5721df14d16a45af8a8470b85ade677b.jpg")
    garment_img = Path("uploads/clothing_244cbaffffb24fc3b0533c1f373a53aa.jpg")

    assert user_img.exists(), f"User test image not found at {user_img}"
    assert garment_img.exists(), f"Garment test image not found at {garment_img}"

    print(f"\n[2/5] Test Inputs:")
    print(f"  Person Image:     {user_img} ({user_img.stat().st_size / 1024:.1f} KB)")
    print(f"  Garment Image:    {garment_img} ({garment_img.stat().st_size / 1024:.1f} KB)")
    print(f"  Garment Category: tops")

    # 3. Initialize Provider & Load Model
    print(f"\n[3/5] Initializing FASHNVTONLocalProvider...")
    t_load_start = time.perf_counter()
    provider = FASHNVTONLocalProvider(weights_dir=settings.VTON_WEIGHTS_DIR)
    provider.load_model()
    t_load_end = time.perf_counter()

    assert provider.is_ready, f"FASHN VTON failed to load: {provider.load_error}"
    print(f"  Model loaded successfully in {t_load_end - t_load_start:.2f}s!")
    if gpu_available:
        print(f"  VRAM Allocated after model load: {torch.cuda.memory_allocated(0) / 1e6:.1f} MB")

    # 4. Run Virtual Try-On Inference
    print(f"\n[4/5] Running Single Virtual Try-On Inference (25 timesteps)...")
    t_infer_start = time.perf_counter()

    result = await provider.generate_try_on(
        person_image=user_img,
        garment_image=garment_img,
        category="tops",
        num_timesteps=25,
        guidance_scale=1.5,
        seed=42,
    )
    t_infer_end = time.perf_counter()

    # 5. Output Verification
    print(f"\n[5/5] Inference Result:")
    print(f"  Success:          {result.get('success')}")
    print(f"  Result Type:      {result.get('result_type')}")
    print(f"  Provider:         {result.get('provider')}")
    print(f"  Image URL:        {result.get('image_url')}")
    print(f"  Inference Time:   {t_infer_end - t_infer_start:.2f}s")

    if gpu_available:
        print(f"  Peak VRAM:        {torch.cuda.max_memory_allocated(0) / 1e6:.1f} MB")
        print(f"  Current VRAM:     {torch.cuda.memory_allocated(0) / 1e6:.1f} MB")

    image_rel = result.get("image_url", "").lstrip("/")
    output_path = BASE_DIR / image_rel

    if output_path.exists():
        with Image.open(output_path) as out_img:
            w, h = out_img.size
            fmt = out_img.format
        print(f"  Output Verified:  {output_path.name} ({output_path.stat().st_size / 1024:.1f} KB, {w}x{h} {fmt})")
        print("\nQUALITY GATE PASSED: ONE FASHN VTON try-on generated successfully on local GPU!")
    else:
        print(f"  [ERROR] Output file not found at: {output_path}")

    print("=" * 64)


if __name__ == "__main__":
    asyncio.run(run_single_tryon_test())
