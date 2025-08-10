#!/usr/bin/env python3
"""
Create sample equipment images for testing the Site Survey AI system
"""

from PIL import Image, ImageDraw, ImageFont
import random
import numpy as np
import os

def create_equipment_image(width=800, height=600, equipment_type="general"):
    """Create a synthetic equipment image for testing"""
    
    # Create base image with industrial background
    img = Image.new('RGB', (width, height), color=(40, 40, 60))
    draw = ImageDraw.Draw(img)
    
    # Add some industrial-looking elements
    colors = {
        'metal': (120, 120, 130),
        'pipe': (80, 80, 90),
        'warning': (255, 200, 0),
        'danger': (255, 100, 100),
        'ok': (100, 255, 100)
    }
    
    if equipment_type == "fuel_lines":
        # Draw fuel lines
        for i in range(3):
            y = 150 + i * 100
            draw.rectangle([50, y-15, width-50, y+15], fill=colors['pipe'])
            draw.rectangle([60, y-10, width-60, y+10], fill=colors['metal'])
            
            # Add connection points
            for x in range(200, width-100, 150):
                draw.ellipse([x-20, y-20, x+20, y+20], fill=colors['warning'])
                draw.ellipse([x-15, y-15, x+15, y+15], fill=colors['metal'])
        
        # Add labels
        draw.text((100, 50), "FUEL LINE SYSTEM", fill=(255, 255, 255))
        draw.text((100, 80), "Pressure: 2500 PSI", fill=(255, 255, 255))
    
    elif equipment_type == "support_structure":
        # Draw support beams
        for i in range(4):
            x = 100 + i * 150
            draw.rectangle([x-10, 100, x+10, height-100], fill=colors['metal'])
            draw.rectangle([50, height-150, width-50, height-130], fill=colors['metal'])
            
            # Add bolts
            for y in range(150, height-100, 100):
                draw.ellipse([x-15, y-8, x+15, y+8], fill=colors['warning'])
                draw.ellipse([x-10, y-5, x+10, y+5], fill=(50, 50, 50))
        
        draw.text((100, 50), "SUPPORT STRUCTURE", fill=(255, 255, 255))
        draw.text((100, 80), "Load Rating: 50,000 lbs", fill=(255, 255, 255))
    
    elif equipment_type == "control_panel":
        # Draw control panel
        draw.rectangle([100, 100, width-100, height-100], fill=colors['metal'])
        draw.rectangle([120, 120, width-120, height-120], fill=(20, 20, 30))
        
        # Add buttons and indicators
        button_colors = [colors['ok'], colors['warning'], colors['danger']]
        for i in range(3):
            for j in range(4):
                x = 200 + j * 80
                y = 200 + i * 60
                color = random.choice(button_colors)
                draw.ellipse([x-15, y-15, x+15, y+15], fill=color)
                draw.ellipse([x-10, y-10, x+10, y+10], fill=(200, 200, 200))
        
        draw.text((150, 50), "CONTROL SYSTEM", fill=(255, 255, 255))
        draw.text((150, 80), "Status: OPERATIONAL", fill=(100, 255, 100))
    
    # Add some realistic noise and texture
    pixels = np.array(img)
    noise = np.random.normal(0, 5, pixels.shape)
    pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    
    return img

def main():
    """Generate sample equipment images"""
    
    output_dir = "sample_site_survey"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create different types of equipment images
    equipment_types = [
        ("fuel_lines", "Fuel Line System"),
        ("support_structure", "Support Structure"), 
        ("control_panel", "Control Panel"),
        ("general", "General Equipment")
    ]
    
    print("🏭 Generating sample equipment images...")
    
    for i, (eq_type, description) in enumerate(equipment_types, 1):
        img = create_equipment_image(equipment_type=eq_type)
        filename = f"{output_dir}/equipment_{i}_{eq_type}.jpg"
        img.save(filename, "JPEG", quality=85)
        print(f"✅ Created {filename} - {description}")
    
    print(f"\n📁 Sample images saved to: {output_dir}/")
    print("🚀 You can now test these with the Site Survey AI web interface!")

if __name__ == "__main__":
    main()