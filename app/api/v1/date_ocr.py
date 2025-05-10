from flask import Blueprint, request, jsonify
from app.core.extensions import csrf
from app.services.date_ocr_service import DateOCRService
import os

date_ocr_bp = Blueprint('date_ocr', __name__)
ocr_service = DateOCRService()

@date_ocr_bp.route('/test', methods=['GET'])
@csrf.exempt
def test_connection():
    """Test endpoint to verify Azure connection."""
    try:
        # Test if credentials are loaded
        if not os.getenv('AZURE_VISION_KEY') or not os.getenv('AZURE_VISION_ENDPOINT'):
            return jsonify({
                'status': 'error',
                'message': 'Azure credentials not found in environment variables'
            }), 500

        # Test Azure connection by making a simple OCR call
        test_image = b'fake_image_data'  # This will fail but will test the connection
        try:
            if ocr_service.vision_client is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Azure Computer Vision client not initialized'
                }), 500
                
            ocr_service.vision_client.recognize_printed_text_in_stream(image=test_image)
            return jsonify({
                'status': 'success',
                'message': 'Azure connection successful'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Azure connection test failed: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error testing Azure connection: {str(e)}'
        }), 500

@date_ocr_bp.route('/extract', methods=['POST'])
@csrf.exempt
def extract_date():
    """Extract date from uploaded image."""
    try:
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image file provided'
            }), 400

        image_file = request.files['image']
        if not image_file.filename:
            return jsonify({
                'status': 'error',
                'message': 'No image file selected'
            }), 400

        # Read image data
        image_data = image_file.read()
        if not image_data:
            return jsonify({
                'status': 'error',
                'message': 'Empty image file'
            }), 400

        # Check if Azure service is available
        if ocr_service.vision_client is None:
            return jsonify({
                'status': 'error',
                'message': 'OCR service not available. Please check Azure credentials.'
            }), 503

        # Extract date using Azure OCR
        date = ocr_service.extract_date(image_data)
        
        if date:
            return jsonify({
                'status': 'success',
                'date': date
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No date found in image'
            }), 404

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing image: {str(e)}'
        }), 500 