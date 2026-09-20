import sys
import io
import os
import cv2
import numpy as np

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_synthetic_garment_image(color_bgr):
    """
    Creates a realistic synthetic garment image:
    A neutral background with a garment shape filled with target color.
    """
    img = np.full((500, 500, 3), (240, 240, 240), dtype=np.uint8)
    pts = np.array([
        [150, 80], [350, 80], [420, 150], [370, 200], [340, 170],
        [340, 420], [160, 420], [160, 170], [130, 200], [80, 150]
    ], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.fillPoly(img, [pts], color_bgr)
    
    _, encoded = cv2.imencode(".jpg", img)
    return io.BytesIO(encoded.tobytes())

def run_tests():
    print("=== STARTING BACKEND TESTS ===")
    
    # 1. Sign Up
    email = "stylist_tester@example.com"
    signup_data = {
        "full_name": "Test User",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    resp = client.post("/auth/signup", json=signup_data)
    if resp.status_code == 400 and "already exists" in resp.text:
        login_resp = client.post("/auth/signin", json={"email": email, "password": "Password123!"})
        assert login_resp.status_code == 200, f"Signin failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        print("[OK] Existing test user signed in successfully")
    else:
        assert resp.status_code == 201, f"Signup failed: {resp.text}"
        token = resp.json()["access_token"]
        print("[OK] New user registered and JWT received")
        
        dup_resp = client.post("/auth/signup", json=signup_data)
        assert dup_resp.status_code == 400, "Duplicate email check failed"
        print("[OK] Duplicate email prevented")
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Me
    me_resp = client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    user_data = me_resp.json()
    user_id = user_data["id"]
    print(f"[OK] Current user retrieved: {user_data['full_name']} (ID: {user_id})")
    
    # 3. Test Actual Colour Detection on BLUE T-SHIRT
    # BGR for Royal Blue: B=225, G=105, R=65
    blue_bgr = (225, 105, 65)
    blue_img_stream = create_synthetic_garment_image(blue_bgr)
    
    analyze_resp = client.post(
        "/analyze",
        headers=headers,
        files={"clothing_image": ("blue_tshirt.jpg", blue_img_stream, "image/jpeg")},
        data={"clothing_category_hint": "T-shirt"}
    )
    assert analyze_resp.status_code == 200, f"Analyze failed: {analyze_resp.text}"
    analysis = analyze_resp.json()
    
    print("\n--- Mandatory Blue T-shirt Analysis Result ---")
    print(f"Detected Clothing: {analysis['clothing_type']}")
    print(f"Detected Colour:   {analysis['detected_colour']}")
    print(f"Colour Shade:      {analysis['colour_shade']}")
    print(f"HEX Value:         {analysis['hex_value']}")
    print(f"RGB Value:         {analysis['rgb_value']}")
    print(f"Confidence:        {analysis['confidence'] * 100:.1f}%")
    print(f"Recommended Colors: {[s['name'] for s in analysis['recommended_colours']]}")
    print(f"Outfit Looks:      {[o['title'] for o in analysis['outfit_suggestions']]}")
    
    assert analysis["detected_colour"] == "Blue", f"Expected Blue, got {analysis['detected_colour']}"
    assert "Blue" in analysis["colour_shade"], f"Expected Blue shade, got {analysis['colour_shade']}"
    assert len(analysis["recommended_colours"]) >= 3, "Insufficient color recommendations"
    assert len(analysis["outfit_suggestions"]) >= 3, "Insufficient outfit suggestions"
    assert analysis["try_on_available"] is True, "Try on should be available"
    print("[OK] Mandatory Blue T-shirt actual colour detection test PASSED!")

    # 4. Test PERSONALIZED VIRTUAL TRY-ON (Clothing + User Portrait)
    print("\n--- Testing Personalized Virtual Try-On Pipeline ---")
    # Create synthetic user portrait: a face-like region with skin tone
    user_img = np.full((400, 400, 3), (245, 245, 245), dtype=np.uint8)
    # Head circle in warm skin tone BGR: B=150, G=180, R=220
    cv2.circle(user_img, (200, 180), 90, (150, 180, 220), -1)
    # Hair in dark brown BGR: B=30, G=40, R=50
    cv2.ellipse(user_img, (200, 130), (95, 60), 0, 180, 360, (30, 40, 50), -1)
    # Shoulders
    cv2.ellipse(user_img, (200, 350), (140, 90), 0, 180, 360, (80, 80, 80), -1)
    _, user_encoded = cv2.imencode(".jpg", user_img)
    user_img_stream = io.BytesIO(user_encoded.tobytes())

    charcoal_bgr = (79, 80, 80)
    charcoal_img_stream = create_synthetic_garment_image(charcoal_bgr)

    tryon_resp = client.post(
        "/analyze",
        headers=headers,
        files={
            "clothing_image": ("charcoal_tshirt.jpg", charcoal_img_stream, "image/jpeg"),
            "user_image": ("my_portrait.jpg", user_img_stream, "image/jpeg"),
        },
        data={"clothing_category_hint": "T-shirt"}
    )
    assert tryon_resp.status_code == 200, f"Try-on analyze failed: {tryon_resp.text}"
    tryon_data = tryon_resp.json()

    print(f"Personalized Garment: {tryon_data['colour_shade']} {tryon_data['clothing_type']}")
    print(f"Personalized Analysis: {tryon_data.get('personalized_analysis') is not None}")
    if tryon_data.get('personalized_analysis'):
        pa = tryon_data['personalized_analysis']
        print(f"  Summary: {pa.get('garment_summary')}")
        print(f"  How it works: {pa.get('how_it_works_with_you')[:80]}...")
        print(f"  Status: {pa.get('try_on_status')}")

    assert tryon_data["user_image_url"] is not None, "User image URL missing from response"
    assert len(tryon_data["outfit_suggestions"]) == 4, f"Expected 4 personalized looks, got {len(tryon_data['outfit_suggestions'])}"
    for idx, look in enumerate(tryon_data["outfit_suggestions"]):
        print(f"  Look {idx+1}: {look['title']} -> Image: {look.get('image_url')}")
        assert look.get("image_url") is not None and len(look["image_url"]) > 0, f"Look {look['title']} missing image_url"
        assert look.get("personalization_reason") is not None and len(look["personalization_reason"]) > 0, f"Look {look['title']} missing personalization_reason"
    print("[OK] Personalized Virtual Try-On 4-Look Generation PASSED!")
    
    # 5. Test Save Result with Personalized Analysis
    save_payload = {
        "clothing_image": tryon_data["clothing_image_url"],
        "user_image": tryon_data.get("user_image_url"),
        "clothing_type": tryon_data["clothing_type"],
        "detected_colour": tryon_data["detected_colour"],
        "colour_shade": tryon_data["colour_shade"],
        "hex_value": tryon_data["hex_value"],
        "rgb_value": tryon_data["rgb_value"],
        "confidence": tryon_data["confidence"],
        "recommendations": tryon_data["recommended_colours"],
        "outfit_suggestions": tryon_data["outfit_suggestions"],
        "explanations": tryon_data["overall_advice"],
        "personalized_analysis": tryon_data.get("personalized_analysis"),
    }
    save_resp = client.post("/saved-results", headers=headers, json=save_payload)
    assert save_resp.status_code == 201, f"Save failed: {save_resp.text}"
    saved_item = save_resp.json()
    saved_id = saved_item["id"]
    print(f"[OK] Personalized look saved with ID: {saved_id}")
    assert saved_item.get("personalized_analysis") is not None, "Saved item missing preserved personalized_analysis"
    assert len(saved_item["outfit_suggestions"]) == 4, "Saved item missing 4 try-on looks"
    print("[OK] Saved wardrobe persistence with try-on images and analysis PASSED!")
    
    # 6. Test List Saved Results
    list_resp = client.get("/saved-results", headers=headers)
    assert list_resp.status_code == 200
    saved_list = list_resp.json()
    assert any(item["id"] == saved_id for item in saved_list), "Saved item missing from list"
    print(f"[OK] Listed {len(saved_list)} saved results for user")
    
    # 7. Test Multi-tenant Security: User B cannot access User A's result
    user_b_data = {
        "full_name": "User B",
        "email": "user_b@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    b_signup = client.post("/auth/signup", json=user_b_data)
    if b_signup.status_code == 201:
        b_token = b_signup.json()["access_token"]
    else:
        b_login = client.post("/auth/signin", json={"email": "user_b@example.com", "password": "Password123!"})
        b_token = b_login.json()["access_token"]
        
    b_headers = {"Authorization": f"Bearer {b_token}"}
    b_access_resp = client.get(f"/saved-results/{saved_id}", headers=b_headers)
    assert b_access_resp.status_code == 404, "Security violation: User B was able to access User A's result!"
    print("[OK] User data isolation confirmed: User B cannot access User A's saved results")
    
    # 8. Test Delete Saved Result
    del_resp = client.delete(f"/saved-results/{saved_id}", headers=headers)
    assert del_resp.status_code == 200, f"Delete failed: {del_resp.text}"
    print(f"[OK] Saved result {saved_id} deleted successfully")
    
    verify_del = client.get(f"/saved-results/{saved_id}", headers=headers)
    assert verify_del.status_code == 404
    print("[OK] Deletion verified (404 Not Found)")
    
    print("\nALL BACKEND API & VIRTUAL TRY-ON TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
