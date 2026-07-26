import os
import cv2
import numpy as np
import random
from pathlib import Path
from tqdm import tqdm

np.random.seed(42)
random.seed(42)

DATA_DIR = Path("data/synthetic")
CLASSES = ["no_damage", "scratch", "dent", "broken_glass", "broken_lamp", "crushed_panel"]
SEVERITIES = ["minor", "moderate", "severe"]
LOCATIONS = ["front", "rear", "side", "roof", "multiple"]

# Image properties
IMG_SIZE = 224

def generate_base_car_image(size=IMG_SIZE):
    """Generates a simple mock car silhouette or colored box as a base image."""
    img = np.ones((size, size, 3), dtype=np.uint8) * 200
    color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    # Draw a simple car shape
    cv2.rectangle(img, (int(size*0.1), int(size*0.4)), (int(size*0.9), int(size*0.8)), color, -1)
    cv2.rectangle(img, (int(size*0.3), int(size*0.2)), (int(size*0.7), int(size*0.4)), color, -1)
    
    # Wheels
    cv2.circle(img, (int(size*0.25), int(size*0.8)), int(size*0.1), (30,30,30), -1)
    cv2.circle(img, (int(size*0.75), int(size*0.8)), int(size*0.1), (30,30,30), -1)
    
    # Headlamps
    cv2.rectangle(img, (int(size*0.85), int(size*0.5)), (int(size*0.9), int(size*0.6)), (220,220,100), -1)
    
    # Windows
    cv2.rectangle(img, (int(size*0.35), int(size*0.25)), (int(size*0.65), int(size*0.4)), (150, 180, 200), -1)
    return img

def apply_scratch(img, severity):
    num_scratches = {"minor": 2, "moderate": 5, "severe": 12}[severity]
    for _ in range(num_scratches):
        x1 = random.randint(0, IMG_SIZE)
        y1 = random.randint(0, IMG_SIZE)
        x2 = x1 + random.randint(-50, 50)
        y2 = y1 + random.randint(-50, 50)
        color = (255, 255, 255) if random.random() > 0.5 else (50, 50, 50)
        thickness = random.randint(1, 3)
        cv2.line(img, (x1, y1), (x2, y2), color, thickness)
    return img

def apply_dent(img, severity):
    num_dents = {"minor": 1, "moderate": 2, "severe": 4}[severity]
    for _ in range(num_dents):
        center = (random.randint(int(IMG_SIZE*0.2), int(IMG_SIZE*0.8)), 
                  random.randint(int(IMG_SIZE*0.4), int(IMG_SIZE*0.8)))
        radius = random.randint(20, 60)
        # Create a dent effect using darkening and warping
        mask = np.zeros_like(img, dtype=np.uint8)
        cv2.circle(mask, center, radius, (255,255,255), -1)
        
        dent_effect = cv2.GaussianBlur(img, (21,21), 0)
        dent_effect = cv2.addWeighted(dent_effect, 0.7, np.zeros_like(img), 0.3, 0)
        
        img = np.where(mask > 0, dent_effect, img)
    return img

def apply_broken_glass(img, severity):
    center = (random.randint(int(IMG_SIZE*0.35), int(IMG_SIZE*0.65)), 
              random.randint(int(IMG_SIZE*0.25), int(IMG_SIZE*0.4)))
    lines = {"minor": 5, "moderate": 15, "severe": 40}[severity]
    
    for _ in range(lines):
        x2 = center[0] + random.randint(-40, 40)
        y2 = center[1] + random.randint(-30, 30)
        cv2.line(img, center, (x2, y2), (200, 200, 220), 1)
    return img

def apply_broken_lamp(img, severity):
    lamp_center = (int(IMG_SIZE*0.87), int(IMG_SIZE*0.55))
    radius = {"minor": 10, "moderate": 15, "severe": 25}[severity]
    
    # Shatter effect
    cv2.circle(img, lamp_center, radius, (50, 50, 50), -1)
    for _ in range(10):
        x2 = lamp_center[0] + random.randint(-radius, radius)
        y2 = lamp_center[1] + random.randint(-radius, radius)
        cv2.line(img, lamp_center, (x2, y2), (200, 200, 200), 1)
    return img

def apply_crushed_panel(img, severity):
    # Heavy warping and black shadow areas
    intensity = {"minor": 0.1, "moderate": 0.3, "severe": 0.6}[severity]
    rows, cols = img.shape[:2]
    
    # Define distortion points
    src = np.float32([[0,0], [cols-1,0], [0,rows-1], [cols-1,rows-1]])
    
    shift = int(rows * intensity)
    dst = np.float32([[0,0], [cols-1,0], [shift,rows-shift], [cols-shift,rows-1]])
    
    M = cv2.getPerspectiveTransform(src, dst)
    img_warped = cv2.warpPerspective(img, M, (cols, rows), borderValue=(200,200,200))
    
    # Add dark areas for crushing
    cv2.circle(img_warped, (int(cols/2), int(rows*0.6)), int(50*intensity*10), (30,30,30), -1)
    return img_warped

def generate_dataset(num_images=800):
    for c in CLASSES:
        os.makedirs(DATA_DIR / c, exist_ok=True)
        
    print(f"Generating {num_images} synthetic images...")
    
    # Prepare metadata tracking
    metadata = []
    
    for i in tqdm(range(num_images)):
        damage_type = random.choice(CLASSES)
        severity = random.choice(SEVERITIES)
        location = random.choice(LOCATIONS)
        
        img = generate_base_car_image()
        
        if damage_type == "scratch":
            img = apply_scratch(img, severity)
        elif damage_type == "dent":
            img = apply_dent(img, severity)
        elif damage_type == "broken_glass":
            img = apply_broken_glass(img, severity)
        elif damage_type == "broken_lamp":
            img = apply_broken_lamp(img, severity)
        elif damage_type == "crushed_panel":
            img = apply_crushed_panel(img, severity)
            
        if damage_type == "no_damage":
            severity = "minor"
            location = "none"
            
        # Add some noise
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)
        
        filename = f"{damage_type}_{severity}_{location}_{i:04d}.jpg"
        filepath = DATA_DIR / damage_type / filename
        
        cv2.imwrite(str(filepath), img)
        metadata.append(f"{filename},{damage_type},{severity},{location}")
        
    # Write metadata
    with open(DATA_DIR / "metadata.csv", "w") as f:
        f.write("filename,damage_type,severity,location\n")
        f.write("\n".join(metadata))

if __name__ == "__main__":
    generate_dataset()
