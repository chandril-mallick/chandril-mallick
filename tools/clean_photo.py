import sys
import os
from PIL import Image
import numpy as np
import cv2

def clean_photo(input_path, output_path="assets/photo-ready.png"):
    print(f"Loading image from {input_path}...")
    img = Image.open(input_path).convert("RGBA")
    
    # 1. Background removal using rembg
    try:
        from rembg import remove
        print("Removing background with rembg...")
        nobg_img = remove(img)
    except Exception as e:
        print(f"rembg notice ({e}), proceeding with standard foreground extraction...")
        nobg_img = img

    nobg_np = np.array(nobg_img)
    
    # Extract channels (RGBA format from PIL)
    r, g, b, a = cv2.split(nobg_np)
    rgb = cv2.merge([r, g, b])
    
    # 2. Even out lighting with CLAHE on LAB luminance channel
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, ca, cb = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    limg = cv2.merge((cl, ca, cb))
    enhanced_rgb = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    # 3. Composite onto white canvas so background falls at the light end of character ramp
    h, w = enhanced_rgb.shape[:2]
    white_bg = np.full((h, w, 3), 255, dtype=np.uint8)
    
    alpha_factor = (a.astype(float) / 255.0)[:, :, np.newaxis]
    composite = (enhanced_rgb * alpha_factor + white_bg * (1.0 - alpha_factor)).astype(np.uint8)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    res_img = Image.fromarray(composite)
    res_img.save(output_path)
    print(f"Saved cleaned photo to {output_path}")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "/Users/chandrilmallick/.gemini/antigravity-ide/brain/0ae88e62-d97b-43e9-881b-fbfe99011352/media__1784912909056.jpg"
    clean_photo(src)
