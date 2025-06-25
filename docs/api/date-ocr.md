# Date OCR API

This document covers the Date OCR API endpoints for extracting expiry dates from images using Azure Computer Vision.

## Overview

The Date OCR API provides endpoints for extracting expiry dates from product images using Azure Computer Vision services. This feature helps automate the process of entering expiry dates for inventory items.

## Endpoints

### Extract Date from Image

**POST** `/api/v1/date_ocr/extract`

Extract expiry date from an uploaded image.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Authentication**: Not required (public endpoint)

**Form Data:**
- `image`: Image file (JPEG, PNG, GIF, BMP)

**Response:**
```json
{
  "status": "success",
  "date": "2024-12-31",
  "confidence": 0.95,
  "extracted_text": "Expiry Date: 31/12/2024"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "No date found in image",
  "extracted_text": "Some text was found but no valid date"
}
```

## Supported Image Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **GIF** (.gif)
- **BMP** (.bmp)

## Date Format Support

The OCR service can recognize various date formats:

- **DD/MM/YYYY**: 31/12/2024
- **MM/DD/YYYY**: 12/31/2024
- **YYYY-MM-DD**: 2024-12-31
- **DD-MM-YYYY**: 31-12-2024
- **MM-DD-YYYY**: 12-31-2024
- **Text formats**: "Expiry: 31 Dec 2024", "Best Before: 2024-12-31"

## Usage Examples

### JavaScript (Frontend)

```javascript
// Extract date from image file
async function extractDateFromImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    try {
        const response = await fetch('/api/v1/date_ocr/extract', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            console.log('Extracted date:', result.date);
            return result.date;
        } else {
            console.error('OCR error:', result.error);
            return null;
        }
    } catch (error) {
        console.error('Request failed:', error);
        return null;
    }
}

// Usage in form
document.getElementById('imageInput').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (file) {
        const extractedDate = await extractDateFromImage(file);
        if (extractedDate) {
            document.getElementById('expiryDate').value = extractedDate;
        }
    }
});
```

### Python

```python
import requests

def extract_date_from_image(image_path):
    """Extract date from image using OCR API."""
    url = 'http://localhost:5000/api/v1/date_ocr/extract'
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            return result['date']
        else:
            print(f"OCR error: {result['error']}")
            return None
    else:
        print(f"Request failed: {response.status_code}")
        return None

# Usage
date = extract_date_from_image('product_image.jpg')
if date:
    print(f"Extracted date: {date}")
```

### cURL

```bash
# Extract date from image file
curl -X POST http://localhost:5000/api/v1/date_ocr/extract \
  -F "image=@product_image.jpg"
```

## Error Handling

### Common Error Responses

**No Date Found:**
```json
{
  "status": "error",
  "error": "No date found in image",
  "extracted_text": "Product information without date"
}
```

**Invalid Image Format:**
```json
{
  "status": "error",
  "error": "Unsupported image format. Please use JPEG, PNG, GIF, or BMP."
}
```

**File Too Large:**
```json
{
  "status": "error",
  "error": "Image file too large. Maximum size is 4MB."
}
```

**Azure Service Error:**
```json
{
  "status": "error",
  "error": "OCR service temporarily unavailable"
}
```

## Best Practices

### Image Quality

1. **High Resolution**: Use images with at least 300 DPI
2. **Good Lighting**: Ensure adequate lighting for clear text
3. **Sharp Focus**: Avoid blurry or out-of-focus images
4. **Contrast**: High contrast between text and background
5. **Orientation**: Ensure text is properly oriented

### Date Recognition

1. **Clear Text**: Ensure date text is clearly visible
2. **Standard Formats**: Use common date formats for better recognition
3. **Multiple Attempts**: Try different angles if first attempt fails
4. **Manual Verification**: Always verify extracted dates before saving

### Performance

1. **File Size**: Keep images under 4MB for faster processing
2. **Caching**: Cache results for repeated images
3. **Batch Processing**: Process multiple images sequentially
4. **Error Handling**: Implement proper error handling for failed extractions

## Integration with Inventory

### Frontend Integration

The Date OCR feature is integrated into the inventory management system:

1. **Add Item Form**: Upload image to auto-fill expiry date
2. **Edit Item Form**: Update expiry date using new image
3. **Bulk Import**: Process multiple images for batch import

### Workflow

1. **Upload Image**: User selects product image
2. **OCR Processing**: System extracts text from image
3. **Date Parsing**: System identifies and parses date
4. **Validation**: System validates extracted date
5. **Auto-fill**: Date is automatically filled in form
6. **Manual Review**: User can edit if needed

## Limitations

### Technical Limitations

- **File Size**: Maximum 4MB per image
- **Format Support**: Limited to common image formats
- **Processing Time**: 2-5 seconds per image
- **Accuracy**: Depends on image quality and text clarity

### Recognition Limitations

- **Handwriting**: Limited support for handwritten dates
- **Complex Layouts**: May struggle with complex document layouts
- **Multiple Dates**: May not always select the correct date
- **Language**: Primarily designed for English date formats

## Troubleshooting

### Common Issues

**No Date Found:**
- Check image quality and resolution
- Ensure date text is clearly visible
- Try different image angles
- Verify date format is supported

**Incorrect Date:**
- Review extracted text in response
- Check for multiple dates in image
- Verify date format interpretation
- Use manual entry if needed

**Service Errors:**
- Check Azure Computer Vision credentials
- Verify internet connectivity
- Check service status
- Retry after a few minutes

---

**Previous**: [Settings API](./settings.md) | **Next**: [Activities API](./activities.md) 