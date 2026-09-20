import sys
import os
import time
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

# Ensure backend path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.main import app
from app.config import BASE_DIR, settings

client = TestClient(app)

def test_api_endpoints():
    print("=" * 64)
    print("       TESTING SYSTEM DIAGNOSTICS & VTON API ENDPOINTS")
    print("=" * 64)

    # 1. Sign in or register to get JWT token
    email = "api_tester@example.com"
    signup_data = {
        "full_name": "API Tester",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    resp = client.post("/auth/signup", json=signup_data)
    if resp.status_code == 400:
        login_resp = client.post("/auth/signin", json={"email": email, "password": "Password123!"})
        assert login_resp.status_code == 200, f"Signin failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
    else:
        assert resp.status_code == 201, f"Signup failed: {resp.text}"
        token = resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    print("[1/3] Auth token obtained successfully.")

    # 2. Test GET /diagnostics/system
    print("\n[2/3] Testing GET /diagnostics/system ...")
    diag_resp = client.get("/diagnostics/system")
    assert diag_resp.status_code == 200, f"Diagnostics failed: {diag_resp.text}"
    diag_data = diag_resp.json()
    print("  Diagnostic Response:")
    for k, v in diag_data.items():
        print(f"    {k}: {v}")

    assert diag_data["gpu_available"] is True, "Expected GPU to be available"
    assert "RTX 3050" in diag_data["gpu_name"] or diag_data["gpu_name"] is not None
    assert diag_data["vton_configured"] is True
    assert diag_data["vton_ready"] is True
    print("  -> System diagnostics endpoint PASSED!")

    # 3. Test POST /virtual-tryon (Direct Virtual Try-On)
    print("\n[3/3] Testing POST /virtual-tryon ...")
    user_img_path = Path("uploads/user_5721df14d16a45af8a8470b85ade677b.jpg")
    garment_img_path = Path("uploads/clothing_244cbaffffb24fc3b0533c1f373a53aa.jpg")

    assert user_img_path.exists(), f"User test image missing: {user_img_path}"
    assert garment_img_path.exists(), f"Garment test image missing: {garment_img_path}"

    with open(user_img_path, "rb") as u_f, open(garment_img_path, "rb") as g_f:
        t0 = time.perf_counter()
        vton_resp = client.post(
            "/virtual-tryon",
            headers=headers,
            files={
                "person_image": ("person.jpg", u_f, "image/jpeg"),
                "garment_image": ("garment.jpg", g_f, "image/jpeg"),
            },
            data={
                "category": "T-shirt",
                "styling_instructions": "Smart casual with dark denim and white sneakers",
            },
        )
        t_vton = time.perf_counter() - t0

    assert vton_resp.status_code == 200, f"Direct VTON failed: {vton_resp.text}"
    vton_data = vton_resp.json()
    print(f"  Virtual Try-On Response (took {t_vton:.2f}s):")
    print(f"    Success:     {vton_data.get('success')}")
    print(f"    Result Type: {vton_data.get('result_type')}")
    print(f"    Provider:    {vton_data.get('provider')}")
    print(f"    Image URL:   {vton_data.get('image_url')}")
    print(f"    Category:    {vton_data.get('category')}")

    assert vton_data["success"] is True, "Expected success to be True"
    assert vton_data["result_type"] == "actual_try_on", f"Expected actual_try_on, got {vton_data['result_type']}"
    assert vton_data["provider"] == "fashn_vton_local"
    assert vton_data["image_url"] is not None

    # Verify physical file existence
    rel_path = vton_data["image_url"].lstrip("/")
    full_path = BASE_DIR / rel_path
    assert full_path.exists(), f"Generated image file does not exist at {full_path}"
    with Image.open(full_path) as im:
        print(f"    Verified Output: {full_path.name} ({im.size[0]}x{im.size[1]} {im.format})")

    print("\nALL ENDPOINT CHECKS PASSED SUCCESSFULLY!")
    print("=" * 64)

if __name__ == "__main__":
    test_api_endpoints()
