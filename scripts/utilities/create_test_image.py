from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    # Create a white background image
    width, height = 400, 200
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Use a bold font
    try:
        font = ImageFont.truetype("Arial Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add text
    text = "EXPIRY DATE: 31/12/2025"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='black', font=font)
    
    # Save the image
    image.save('test_image.png')
    print("Test image created: test_image.png")

if __name__ == "__main__":
    create_test_image() 