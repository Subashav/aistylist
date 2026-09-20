"""
Download FASHN VTON model weights
=================================
Downloads:
1. model.safetensors from fashn-ai/fashn-vton-1.5
2. dwpose ONNX models from fashn-ai/DWPose
3. FashnHumanParser weights
"""

import os
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download


def download_all(weights_dir: Path):
    weights_dir.mkdir(parents=True, exist_ok=True)
    dwpose_dir = weights_dir / "dwpose"
    dwpose_dir.mkdir(parents=True, exist_ok=True)

    print(f"Target weights directory: {weights_dir}")

    # 1. Download TryOnModel weights (model.safetensors)
    tryon_file = weights_dir / "model.safetensors"
    if not tryon_file.exists() or tryon_file.stat().st_size < 100_000_000:
        print("\n[1/3] Downloading TryOnModel weights (model.safetensors) from fashn-ai/fashn-vton-1.5...")
        hf_hub_download(
            repo_id="fashn-ai/fashn-vton-1.5",
            filename="model.safetensors",
            local_dir=str(weights_dir),
        )
        print(f"  Downloaded: {tryon_file} ({tryon_file.stat().st_size / 1e6:.1f} MB)")
    else:
        print(f"\n[1/3] TryOnModel weights already present: {tryon_file.stat().st_size / 1e6:.1f} MB")

    # 2. Download DWPose models
    print("\n[2/3] Downloading DWPose models from fashn-ai/DWPose...")
    dw_files = ["yolox_l.onnx", "dw-ll_ucoco_384.onnx"]
    for f in dw_files:
        fpath = dwpose_dir / f
        if not fpath.exists() or fpath.stat().st_size < 1_000_000:
            print(f"  Downloading dwpose/{f}...")
            hf_hub_download(
                repo_id="fashn-ai/DWPose",
                filename=f,
                local_dir=str(dwpose_dir),
            )
            print(f"  Downloaded: {fpath} ({fpath.stat().st_size / 1e6:.1f} MB)")
        else:
            print(f"  DWPose model already present: {fpath.name} ({fpath.stat().st_size / 1e6:.1f} MB)")

    # 3. Cache human parser weights
    print("\n[3/3] Checking / caching FashnHumanParser weights...")
    try:
        from fashn_human_parser import FashnHumanParser
        _ = FashnHumanParser(device="cpu")
        print("  FashnHumanParser initialized successfully.")
    except Exception as e:
        print(f"  Note on human parser: {e}")

    print("\nModel weights verification complete!")


if __name__ == "__main__":
    from app.config import settings
    download_all(settings.VTON_WEIGHTS_DIR)
