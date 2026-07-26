from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def generate_logo():
    """Generates a simple SVG/PNG style logo for the application."""
    assets_dir = Path("app/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    logo_path = assets_dir / "logo.png"
    
    if logo_path.exists():
        return
        
    # Create a simple modern logo
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Shield background
    draw.polygon([(100, 10), (190, 40), (190, 140), (100, 190), (10, 140), (10, 40)], fill=(30, 144, 255))
    
    # Inner shape (car silhouette abstraction)
    draw.rectangle([60, 80, 140, 110], fill=(255, 255, 255))
    draw.rectangle([80, 60, 120, 80], fill=(255, 255, 255))
    draw.ellipse([70, 100, 90, 120], fill=(50, 50, 50))
    draw.ellipse([110, 100, 130, 120], fill=(50, 50, 50))
    
    # Magnifying glass
    draw.ellipse([110, 110, 160, 160], outline=(255, 215, 0), width=10)
    draw.line([145, 145, 180, 180], fill=(255, 215, 0), width=12)
    
    img.save(logo_path)

if __name__ == "__main__":
    generate_logo()
