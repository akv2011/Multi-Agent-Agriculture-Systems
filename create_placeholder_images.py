#!/usr/bin/env python3
"""
Create placeholder product images for marketplace demo
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_placeholder_image(text, filename, size=(400, 300), bg_color=(34, 197, 94), text_color=(255, 255, 255)):
    """Create a placeholder image with text"""
    # Create image
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save image
    upload_dir = Path("uploads/product_images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    img.save(upload_dir / filename)
    print(f"Created: {filename}")

def create_sample_images():
    """Create sample product images"""
    products = [
        ("Basmati Rice", "basmati-rice.jpg", (245, 158, 11)),
        ("Wheat Flour", "wheat-flour.jpg", (139, 69, 19)),
        ("Fresh Tomatoes", "tomatoes.jpg", (220, 38, 38)),
        ("Cotton Bulk", "cotton-bulk.jpg", (255, 255, 255)),
        ("Rice Field", "rice-field.jpg", (34, 197, 94)),
        ("Wheat Field", "wheat-field.jpg", (251, 191, 36)),
        ("Tomato Farm", "tomato-farm.jpg", (34, 197, 94)),
        ("Cotton Field", "cotton-field.jpg", (34, 197, 94)),
        ("Organic Vegetables", "organic-vegetables.jpg", (22, 163, 74)),
        ("Fresh Fruits", "fresh-fruits.jpg", (249, 115, 22)),
        ("Spices", "spices.jpg", (251, 146, 60)),
        ("Pulses", "pulses.jpg", (168, 85, 247)),
        ("Placeholder", "placeholder.jpg", (156, 163, 175))
    ]
    
    for text, filename, color in products:
        create_placeholder_image(text, filename, bg_color=color)

if __name__ == "__main__":
    create_sample_images()
    print("All placeholder images created successfully!")
