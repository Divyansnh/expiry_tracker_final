from PIL import Image, ImageDraw, ImageFont
import os
import random
from datetime import datetime, timedelta

def create_comprehensive_test_images():
    # Create output directory if it doesn't exist
    output_dir = 'test_images'
    os.makedirs(output_dir, exist_ok=True)
    
    # List of test cases
    test_cases = [
        # Standard formats
        {
            'name': 'standard_expiry',
            'text': 'EXPIRY DATE: 31/12/2024',
            'font_size': 24,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        {
            'name': 'standard_expiry_with_colon',
            'text': 'EXPIRY DATE: 31/12/2024',
            'font_size': 24,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        
        # Month name formats
        {
            'name': 'month_name_full',
            'text': 'Best Before: December 25, 2024',
            'font_size': 20,
            'background': 'lightgray',
            'text_color': 'darkblue',
            'rotation': 0
        },
        {
            'name': 'month_name_abbreviated',
            'text': 'Use by: Dec 25, 2024',
            'font_size': 20,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        
        # Different date formats
        {
            'name': 'date_with_dots',
            'text': 'EXP: 15.06.2025',
            'font_size': 22,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        {
            'name': 'date_with_slashes',
            'text': 'EXP: 15/06/2025',
            'font_size': 22,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        {
            'name': 'date_with_dashes',
            'text': 'EXP: 15-06-2025',
            'font_size': 22,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        
        # Small print and low contrast
        {
            'name': 'small_print',
            'text': 'Use by: 2024/08/30',
            'font_size': 16,
            'background': 'white',
            'text_color': 'gray',
            'rotation': 0
        },
        {
            'name': 'low_contrast',
            'text': 'EXP: 31/12/2024',
            'font_size': 20,
            'background': 'lightgray',
            'text_color': 'gray',
            'rotation': 0
        },
        
        # Complex formats
        {
            'name': 'complex_format',
            'text': 'Manufactured: 01.01.2024\nExpires: 31.12.2025',
            'font_size': 18,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0,
            'multiline': True
        },
        {
            'name': 'complex_format_with_colons',
            'text': 'Manufactured: 01.01.2024\nExpires: 31.12.2025',
            'font_size': 18,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0,
            'multiline': True
        },
        
        # Damaged or worn labels
        {
            'name': 'damaged_label',
            'text': 'EXP: 15-06-2025',
            'font_size': 22,
            'background': 'white',
            'text_color': 'black',
            'rotation': 5,
            'noise': True
        },
        {
            'name': 'worn_label',
            'text': 'EXP: 15-06-2025',
            'font_size': 22,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0,
            'noise': True,
            'noise_level': 0.02
        },
        
        # Different languages and formats
        {
            'name': 'spanish_format',
            'text': 'Fecha de caducidad: 31/12/2024',
            'font_size': 20,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        {
            'name': 'french_format',
            'text': 'Date d\'expiration: 31/12/2024',
            'font_size': 20,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        
        # Edge cases
        {
            'name': 'year_only',
            'text': 'EXP: 2024',
            'font_size': 20,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        {
            'name': 'month_year_only',
            'text': 'EXP: 12/2024',
            'font_size': 20,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0
        },
        {
            'name': 'multiple_dates',
            'text': 'Manufactured: 01.01.2024\nBest Before: 31.12.2024\nUse by: 31.12.2024',
            'font_size': 18,
            'background': 'white',
            'text_color': 'black',
            'rotation': 0,
            'multiline': True
        }
    ]
    
    for case in test_cases:
        # Create image
        width, height = 400, 200
        image = Image.new('RGB', (width, height), case['background'])
        draw = ImageDraw.Draw(image)
        
        # Try to use a bold font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial Bold.ttf", case['font_size'])
        except:
            font = ImageFont.load_default()
        
        # Add text
        if case.get('multiline'):
            lines = case['text'].split('\n')
            y = 50
            for line in lines:
                text_bbox = draw.textbbox((0, 0), line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y), line, fill=case['text_color'], font=font)
                y += case['font_size'] + 10
        else:
            text_bbox = draw.textbbox((0, 0), case['text'], font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), case['text'], fill=case['text_color'], font=font)
        
        # Add rotation if specified
        if case.get('rotation'):
            image = image.rotate(case['rotation'], expand=True, fillcolor=case['background'])
        
        # Add noise if specified
        if case.get('noise'):
            pixels = image.load()
            if pixels is not None:
                noise_level = case.get('noise_level', 0.01)
                for i in range(width):
                    for j in range(height):
                        if random.random() < noise_level:
                            pixels[i, j] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        # Save the image
        output_path = os.path.join(output_dir, f'{case["name"]}.png')
        image.save(output_path)
        print(f"Created test image: {output_path}")

if __name__ == '__main__':
    create_comprehensive_test_images() 