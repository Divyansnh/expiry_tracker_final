import os
from PIL import Image, ImageDraw, ImageFont
import random
import numpy as np
from datetime import datetime, timedelta
import cv2

def apply_perspective_transform(image, angle=0, perspective=0.1):
    """Apply perspective transformation to simulate camera angle."""
    if perspective == 0:
        return image.rotate(angle, expand=True, fillcolor=(255, 255, 255))
    
    # Convert PIL image to OpenCV format
    img_array = np.array(image)
    
    # Get image dimensions
    height, width = img_array.shape[:2]
    
    # Define source points (original image corners)
    src_points = np.array([
        [0, 0],
        [width, 0],
        [0, height],
        [width, height]
    ], dtype=np.float32)
    
    # Calculate perspective shift
    shift = width * perspective
    
    # Define destination points (transformed corners)
    dst_points = np.array([
        [shift, 0],
        [width - shift, 0],
        [0, height],
        [width, height]
    ], dtype=np.float32)
    
    # Get perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    
    # Apply perspective transform
    transformed = cv2.warpPerspective(img_array, matrix, (width, height))
    
    # Convert back to PIL image
    result = Image.fromarray(transformed)
    
    # Apply rotation if needed
    if angle != 0:
        result = result.rotate(angle, expand=True, fillcolor=(255, 255, 255))
    
    return result

def create_real_world_test_images():
    """Create test images simulating real-world scenarios for date extraction."""
    # Create output directory
    output_dir = "test_images_real_world"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define test cases
    test_cases = [
        # 1. Product Labels with Different Angles
        {
            "name": "product_label_angle_0",
            "text": "Best Before: 31/12/2024",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 0,
            "perspective": 0,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_angle_15",
            "text": "Best Before: 31/12/2024",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 15,
            "perspective": 0,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_angle_30",
            "text": "Best Before: 31/12/2024",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 30,
            "perspective": 0,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_angle_45",
            "text": "Best Before: 31/12/2024",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 45,
            "perspective": 0,
            "multiline": False,
            "add_noise": False
        },
        
        # 2. Perspective Transformations
        {
            "name": "product_label_perspective_light",
            "text": "Use By: 2024/08/30",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 0,
            "perspective": 0.1,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_perspective_medium",
            "text": "Use By: 2024/08/30",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 0,
            "perspective": 0.2,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_perspective_heavy",
            "text": "Use By: 2024/08/30",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 0,
            "perspective": 0.3,
            "multiline": False,
            "add_noise": False
        },
        
        # 3. Combined Angle and Perspective
        {
            "name": "product_label_combined_1",
            "text": "Expiry: 2024-12-31",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 15,
            "perspective": 0.1,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_combined_2",
            "text": "Expiry: 2024-12-31",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 30,
            "perspective": 0.2,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_combined_3",
            "text": "Expiry: 2024-12-31",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 45,
            "perspective": 0.3,
            "multiline": False,
            "add_noise": False
        },
        
        # 4. Curved Surface Simulation
        {
            "name": "product_label_curved_1",
            "text": "Best Before: 2024/12/31",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 0,
            "perspective": 0.15,
            "multiline": False,
            "add_noise": False
        },
        {
            "name": "product_label_curved_2",
            "text": "Best Before: 2024/12/31",
            "font_size": 12,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 0,
            "perspective": 0.25,
            "multiline": False,
            "add_noise": False
        },
        
        # 5. Complex Scenarios
        {
            "name": "complex_label_angle_1",
            "text": "Manufactured: 01/01/2023\nBest Before: 31/12/2024",
            "font_size": 10,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 20,
            "perspective": 0.1,
            "multiline": True,
            "add_noise": False
        },
        {
            "name": "complex_label_angle_2",
            "text": "Production: 2023-01-01\nExpiry: 2024-12-31",
            "font_size": 10,
            "background_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "rotation": 35,
            "perspective": 0.2,
            "multiline": True,
            "add_noise": False
        }
    ]
    
    # Generate images for each test case
    for case in test_cases:
        # Create image
        img = Image.new('RGB', (400, 100), case["background_color"])
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial", case["font_size"])
        except:
            font = ImageFont.load_default()
        
        # Draw text
        if case["multiline"]:
            lines = case["text"].split('\n')
            y = 10
            for line in lines:
                draw.text((10, y), line, font=font, fill=case["text_color"])
                y += case["font_size"] + 5
        else:
            draw.text((10, 40), case["text"], font=font, fill=case["text_color"])
        
        # Add noise if specified
        if case["add_noise"]:
            img_array = np.array(img)
            noise = np.random.normal(0, 10, img_array.shape).astype(np.uint8)
            img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_array)
        
        # Apply perspective and rotation transformations
        img = apply_perspective_transform(
            img, 
            angle=case["rotation"],
            perspective=case["perspective"]
        )
        
        # Save image
        output_path = os.path.join(output_dir, f"{case['name']}.png")
        img.save(output_path)
        print(f"Created test image: {output_path}")

if __name__ == "__main__":
    create_real_world_test_images() 