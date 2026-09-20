# AI Stylist – Personalised Fashion Harmony

An intelligent, full-stack cross-platform fashion assistant developed using **Flutter (Web, Android & iOS)** and a **Python FastAPI** backend with Computer Vision.

---

## 🌟 Core Features

1. **Authentication First**:
   - Responsive Sign Up, Sign In, Forgot Password, and Logout.
   - Salted Bcrypt password hashing and JWT token authentication.
   - Multi-tenant data isolation (users can only access their own wardrobe).

2. **Actual Clothing Colour Detection**:
   - Not based on filenames, random guesses, or manual entry.
   - Computer vision pipeline: isolates the garment, suppresses human skin/hair and backgrounds, performs CIELAB K-Means clustering, and matches perceptual shades ($\Delta E$).
   - Returns detected garment type, base colour, colour shade, precise HEX/RGB values, and confidence scores.

3. **Dynamic Colour Harmony & Outfits**:
   - Applies colour theory: Complementary, Monochromatic, Neutral Contrast, and Triadic harmonies.
   - Generates complete outfits: Tops, Bottoms, Footwear, Layers, Accessories, and styling rationale.

4. **Wardrobe Management**:
   - Save analysis results.
   - View previously saved looks.
   - Delete saved recommendations.

5. **Single Flutter Codebase**:
   - Adaptive responsive UI tailored for Mobile and Web/Desktop.

---

## 🚀 Beginner-Friendly Quick Start Guide

### Step 1: Open Your Terminals
Open **two** terminal windows (PowerShell or Command Prompt).

---

### Terminal 1: Backend Server (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   - On Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On Windows Command Prompt (CMD):
     ```cmd
     .\venv\Scripts\activate.bat
     ```

3. Run the automated backend verification test (proves Blue T-Shirt color detection, Virtual Try-On, and Auth):
   ```bash
   python test_backend.py
   ```

4. Start the backend server:
   ```bash
   python run.py
   ```
   The backend will start on **http://127.0.0.1:8000**.
   You can view the interactive API documentation at **http://127.0.0.1:8000/docs**.

---

### Terminal 2: Frontend Client (Flutter / Web)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. **Run on Web (Google Chrome)**:
   ```bash
   flutter run -d chrome
   ```

3. **Run on Android Emulator or Connected Device**:
   ```bash
   flutter run
   ```

4. **Build Production Web Application**:
   ```bash
   flutter build web
   ```

---

## 📸 Demonstration Walkthrough (For Final-Year Viva)

1. **Launch App**: The app opens directly to the luxury **Sign In / Sign Up** screen.
2. **Register New User**: Create an account with name, email, and password. You are automatically logged in.
3. **Upload Clothing Photo**:
   - Click "Upload Clothing Photo" or "Take Clothing Photo".
   - Select an image of a **Blue T-Shirt**.
4. **Run Analysis**:
   - Click "Analyze Actual Colour & Match Outfits".
   - Watch the animated 4-step pipeline in action.
5. **Inspect Verified Results**:
   - Detected Clothing: **T-shirt**
   - Detected Colour: **Blue**
   - Colour Shade: **Royal Blue** (or relevant blue shade)
   - HEX / RGB / Confidence: Displays `#4169E2` with ~92% confidence.
   - Matching Colours: Crisp White, Warm Beige, Light Grey, Navy Blue, Terracotta.
   - Outfit Combinations: Casual Classic, Smart Casual Elegance, Layered Dimension.
6. **Save to Wardrobe**: Click "Save Look to Wardrobe".
7. **Saved Looks**: Switch to "Saved Looks" tab to verify the saved item card with the authentic color swatch.
8. **Delete**: Click the trash icon to confirm deletion.
