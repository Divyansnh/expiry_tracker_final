from typing import Optional, List, Dict, Any
import cv2
import numpy as np
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, OcrResult
from msrest.authentication import CognitiveServicesCredentials
import re
from datetime import datetime, timedelta
import os
from flask import current_app
from io import BytesIO

class DateOCRService:
    """Service for extracting dates from images using Azure Computer Vision."""
    
    def __init__(self):
        """Initialize the Azure Computer Vision service."""
        # Get Azure credentials from environment variables
        self.subscription_key = os.getenv('AZURE_VISION_KEY')
        self.endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        
        # Initialize vision client only if credentials are available
        self.vision_client = None
        if self.subscription_key and self.endpoint:
            try:
                # Ensure endpoint ends with a slash
                if not self.endpoint.endswith('/'):
                    self.endpoint = self.endpoint + '/'
                
                self.vision_client = ComputerVisionClient(
                    endpoint=self.endpoint,
                    credentials=CognitiveServicesCredentials(self.subscription_key)
                )
                print(f"Azure Computer Vision service initialized successfully with endpoint: {self.endpoint}")
            except Exception as e:
                print(f"Error initializing Azure Computer Vision: {str(e)}")
        else:
            print("Azure credentials not found. OCR service will not be available.")
            if not self.subscription_key:
                print("Missing AZURE_VISION_KEY")
            if not self.endpoint:
                print("Missing AZURE_VISION_ENDPOINT")

    def preprocess_image(self, image_data: bytes) -> bytes:
        """Preprocess the image to improve OCR accuracy."""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Apply bilateral filter to preserve edges while removing noise
            filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # Apply Otsu's thresholding
            _, otsu = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply adaptive thresholding as a backup
            adaptive = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Combine both thresholding results
            combined = cv2.bitwise_or(otsu, adaptive)
            
            # Apply gentle morphological operations
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
            
            # Save debug image
            debug_dir = os.path.join(current_app.root_path, 'debug_images')
            os.makedirs(debug_dir, exist_ok=True)
            debug_path = os.path.join(debug_dir, 'preprocessed.png')
            cv2.imwrite(debug_path, cleaned)
            print(f"Saved preprocessed image to {debug_path}")
            
            # Convert back to bytes
            _, img_encoded = cv2.imencode('.png', cleaned)
            return img_encoded.tobytes()
            
        except Exception as e:
            print(f"Error in image preprocessing: {str(e)}")
            return image_data  # Return original image if preprocessing fails

    def correct_ocr_errors(self, text: str) -> str:
        """Correct common OCR misreads."""
        corrections = {
            'マ': 'M', '了': 'L', 'ー': '-', 'つ': 'T', 'Ⅵ': '6', '「': '(',
            'see': 'exp', 'beee': 'date', 'expiry': 'exp', 'date': 'date',
            # Handle common OCR mistakes for month names
            '12ember': 'december',
            '12ember': 'december',
            '12ember': 'december',
            '12ember': 'december',
            '12ember': 'december',
            '12ember': 'december',
            # Handle month name variations
            'jan': 'january',
            'feb': 'february',
            'mar': 'march',
            'apr': 'april',
            'may': 'may',
            'jun': 'june',
            'jul': 'july',
            'aug': 'august',
            'sep': 'september',
            'oct': 'october',
            'nov': 'november',
            'dec': 'december',
            # Handle full month names
            'january': 'january',
            'february': 'february',
            'march': 'march',
            'april': 'april',
            'june': 'june',
            'july': 'july',
            'august': 'august',
            'september': 'september',
            'october': 'october',
            'november': 'november',
            'december': 'december',
            # Handle common OCR mistakes for expiry terms
            'use by': 'use by',
            'use-by': 'use by',
            'useby': 'use by',
            'use:by': 'use by',
            'best before': 'best before',
            'best-before': 'best before',
            'bestbefore': 'best before',
            'best:before': 'best before',
            'exp': 'expiry',
            'exp.': 'expiry',
            'exp:': 'expiry',
            'expiry': 'expiry',
            'expiry date': 'expiry date',
            'expiry-date': 'expiry date',
            'expirydate': 'expiry date',
            'expiry:date': 'expiry date',
            'bb': 'best before',
            'bb:': 'best before',
            'bb.': 'best before',
            'ub': 'use by',
            'ub:': 'use by',
            'ub.': 'use by',
            # Handle year-only formats
            'year': 'year',
            'years': 'year',
            'yr': 'year',
            'yrs': 'year',
            # Handle French terms
            'date d\'expiration': 'date d\'expiration',
            'date d\'exp': 'date d\'expiration',
            'date d\'exp.': 'date d\'expiration',
            'date d\'exp:': 'date d\'expiration',
            'date d\'expiry': 'date d\'expiration',
            'date d\'expiry date': 'date d\'expiration',
            'date d\'expiry-date': 'date d\'expiration',
            'date d\'expirydate': 'date d\'expiration',
            'date d\'expiry:date': 'date d\'expiration',
            'date d\'expiration:': 'date d\'expiration',
            'date d\'expiration.': 'date d\'expiration',
            'date d\'expiration-': 'date d\'expiration',
            'date d\'expiration date': 'date d\'expiration',
            'date d\'expiration-date': 'date d\'expiration',
            'date d\'expirationdate': 'date d\'expiration',
            'date d\'expiration:date': 'date d\'expiration',
            'date d\'expiration date:': 'date d\'expiration',
            'date d\'expiration date.': 'date d\'expiration',
            'date d\'expiration date-': 'date d\'expiration',
            'date d\'expiration date date': 'date d\'expiration',
            'date d\'expiration date-date': 'date d\'expiration',
            'date d\'expiration datedate': 'date d\'expiration',
            'date d\'expiration date:date': 'date d\'expiration',
            # Handle French OCR mistakes
            'date d\'expiration': 'date d\'expiration',
            'date d\'exp': 'date d\'expiration',
            'date d\'exp.': 'date d\'expiration',
            'date d\'exp:': 'date d\'expiration',
            'date d\'expiry': 'date d\'expiration',
            'date d\'expiry date': 'date d\'expiration',
            'date d\'expiry-date': 'date d\'expiration',
            'date d\'expirydate': 'date d\'expiration',
            'date d\'expiry:date': 'date d\'expiration',
            'date d\'expiration:': 'date d\'expiration',
            'date d\'expiration.': 'date d\'expiration',
            'date d\'expiration-': 'date d\'expiration',
            'date d\'expiration date': 'date d\'expiration',
            'date d\'expiration-date': 'date d\'expiration',
            'date d\'expirationdate': 'date d\'expiration',
            'date d\'expiration:date': 'date d\'expiration',
            'date d\'expiration date:': 'date d\'expiration',
            'date d\'expiration date.': 'date d\'expiration',
            'date d\'expiration date-': 'date d\'expiration',
            'date d\'expiration date date': 'date d\'expiration',
            'date d\'expiration date-date': 'date d\'expiration',
            'date d\'expiration datedate': 'date d\'expiration',
            'date d\'expiration date:date': 'date d\'expiration',
            # Handle French apostrophe variations
            'date d\'expiration': 'date d\'expiration',
            'date d\'exp': 'date d\'expiration',
            'date d\'exp.': 'date d\'expiration',
            'date d\'exp:': 'date d\'expiration',
            'date d\'expiry': 'date d\'expiration',
            'date d\'expiry date': 'date d\'expiration',
            'date d\'expiry-date': 'date d\'expiration',
            'date d\'expirydate': 'date d\'expiration',
            'date d\'expiry:date': 'date d\'expiration',
            'date d\'expiration:': 'date d\'expiration',
            'date d\'expiration.': 'date d\'expiration',
            'date d\'expiration-': 'date d\'expiration',
            'date d\'expiration date': 'date d\'expiration',
            'date d\'expiration-date': 'date d\'expiration',
            'date d\'expirationdate': 'date d\'expiration',
            'date d\'expiration:date': 'date d\'expiration',
            'date d\'expiration date:': 'date d\'expiration',
            'date d\'expiration date.': 'date d\'expiration',
            'date d\'expiration date-': 'date d\'expiration',
            'date d\'expiration date date': 'date d\'expiration',
            'date d\'expiration date-date': 'date d\'expiration',
            'date d\'expiration datedate': 'date d\'expiration',
            'date d\'expiration date:date': 'date d\'expiration'
        }
        
        # First, convert to lowercase for consistent matching
        corrected = text.lower()
        
        # Sort corrections by length (longest first) to prevent partial matches
        sorted_corrections = sorted(corrections.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Apply corrections
        for wrong, right in sorted_corrections:
            # Use word boundaries to prevent partial matches
            pattern = r'\b' + re.escape(wrong) + r'\b'
            corrected = re.sub(pattern, right, corrected)
        
        return corrected

    def parse_concatenated_date(self, date_str: str) -> Optional[datetime]:
        """Parse a concatenated date string (e.g., '3111212024' -> '31/12/2024')."""
        try:
            # Handle 8-digit format (DDMMYYYY)
            if len(date_str) == 8:
                day = int(date_str[:2])
                month = int(date_str[2:4])
                year = int(date_str[4:])
                if 1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 2100:
                    return datetime(year, month, day)
            
            # Handle 10-digit format (DDMMYYYY)
            elif len(date_str) == 10:
                day = int(date_str[:2])
                month = int(date_str[2:4])
                year = int(date_str[4:])
                if 1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 2100:
                    return datetime(year, month, day)
            
            return None
        except (ValueError, IndexError):
            return None

    def extract_date(self, image_data: bytes) -> Optional[str]:
        """
        Extract date from image data using Azure Computer Vision OCR.
        Returns the date in YYYY-MM-DD format if found, None otherwise.
        """
        try:
            # Check if Azure service is available
            if not self.vision_client:
                print("Azure Computer Vision service not available")
                return None

            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            
            # Create a file-like object from the bytes
            image_stream = BytesIO(processed_image)
            
            # Call Azure OCR
            ocr_result = self.vision_client.recognize_printed_text_in_stream(
                image=image_stream
            )
            
            # Check if OCR result is valid
            if not isinstance(ocr_result, OcrResult):
                print("Invalid OCR result type")
                return None
                
            if not hasattr(ocr_result, 'regions') or not ocr_result.regions:
                print("No text regions found in OCR result")
                return None
            
            # Extract all text from OCR results
            text_blocks: List[str] = []
            for region in ocr_result.regions:
                if not hasattr(region, 'lines'):
                    continue
                for line in region.lines:
                    if not hasattr(line, 'words'):
                        continue
                    text = ' '.join([word.text for word in line.words])
                    text_blocks.append(text)
                    print(f"Detected text: {text}")
            
            # Join all text blocks and clean up
            full_text = ' '.join(text_blocks)
            full_text = self.correct_ocr_errors(full_text)
            print(f"Full text after correction: {full_text}")
            
            # First, try to find dates after expiry-related keywords
            expiry_keywords = [
                # English keywords
                'expiry date', 'expiry', 'exp', 'best before', 'use by',
                'bb', 'ub', 'best-before', 'use-by', 'expiry-date',
                'best:before', 'use:by', 'expiry:date',
                # French keywords
                'date d\'expiration', 'date d\'exp', 'date d\'exp.',
                'date d\'exp:', 'date d\'expiry', 'date d\'expiry date',
                'date d\'expiry-date', 'date d\'expirydate', 'date d\'expiry:date',
                'date d\'expiration:', 'date d\'expiration.', 'date d\'expiration-',
                'date d\'expiration date', 'date d\'expiration-date', 'date d\'expirationdate',
                'date d\'expiration:date', 'date d\'expiration date:', 'date d\'expiration date.',
                'date d\'expiration date-', 'date d\'expiration date date', 'date d\'expiration date-date',
                'date d\'expiration datedate', 'date d\'expiration date:date',
                # Spanish keywords
                'fecha de caducidad', 'fecha de exp', 'fecha de exp.',
                'fecha de exp:', 'fecha de expiry', 'fecha de expiry date',
                'fecha de expiry-date', 'fecha de expirydate', 'fecha de expiry:date',
                'fecha de caducidad:', 'fecha de caducidad.', 'fecha de caducidad-',
                'fecha de caducidad date', 'fecha de caducidad-date', 'fecha de caducidaddate',
                'fecha de caducidad:date', 'fecha de caducidad date:', 'fecha de caducidad date.',
                'fecha de caducidad date-', 'fecha de caducidad date date', 'fecha de caducidad date-date',
                'fecha de caducidad datedate', 'fecha de caducidad date:date'
            ]
            
            # Sort keywords by length (longest first) to prevent partial matches
            sorted_keywords = sorted(expiry_keywords, key=len, reverse=True)
            
            for keyword in sorted_keywords:
                # Find the position of the keyword
                keyword_pos = full_text.lower().find(keyword.lower())
                if keyword_pos != -1:
                    # Get the text after the keyword
                    text_after_keyword = full_text[keyword_pos + len(keyword):]
                    # Remove any leading colons, spaces, or other punctuation
                    text_after_keyword = text_after_keyword.lstrip(' :.,;')
                    print(f"Text after {keyword}: {text_after_keyword}")
                    
                    # First, try to parse concatenated dates
                    concatenated_pattern = r'\d{8,10}'  # Match 8-10 digit numbers
                    matches = re.findall(concatenated_pattern, text_after_keyword)
                    if matches:
                        for match in matches:
                            date_obj = self.parse_concatenated_date(match)
                            if date_obj:
                                formatted_date = date_obj.strftime('%Y-%m-%d')
                                print(f"Successfully parsed concatenated date: {formatted_date}")
                                return formatted_date
                    
                    # If no concatenated date found, try other date formats
                    date_patterns = [
                        # Full year formats first (to prevent year truncation)
                        r'\d{4}[./-]\d{1,2}[./-]\d{1,2}',  # YYYY/MM/DD
                        r'\d{1,2}[./-]\d{1,2}[./-]\d{4}',  # DD/MM/YYYY
                        # Then 2-digit year formats
                        r'\d{1,2}[./-]\d{1,2}[./-]\d{2}',  # DD/MM/YY
                        r'\d{2}[./-]\d{1,2}[./-]\d{2}',    # YY/MM/DD
                        # Month name formats
                        r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4}',
                        # Month/Year only formats
                        r'\d{1,2}[./-]\d{4}',  # MM/YYYY
                        r'\d{4}[./-]\d{1,2}',  # YYYY/MM
                        r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',  # Month YYYY
                        # Year-only format
                        r'\b\d{4}\b'  # YYYY
                    ]
                    
                    # Try to find a date in the text after the keyword
                    for pattern in date_patterns:
                        matches = re.findall(pattern, text_after_keyword)
                        if matches:
                            date_str = matches[0] if isinstance(matches[0], str) else matches[0][0]
                            print(f"Found potential date after {keyword}: {date_str}")
                            try:
                                # Try different date formats
                                formats = [
                                    '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',  # YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
                                    '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y',  # DD-MM-YYYY or DD/MM/YYYY or DD.MM.YYYY
                                    '%d-%m-%y', '%d/%m/%y', '%d.%m.%y',  # DD-MM-YY or DD/MM/YY or DD.MM.YY
                                    '%y-%m-%d', '%y/%m/%d', '%y.%m.%d',  # YY-MM-DD or YY/MM/DD or YY.MM.DD
                                    '%B %d, %Y', '%b %d, %Y',  # Month name formats
                                    '%m/%Y', '%Y/%m',  # Month/Year formats
                                    '%B %Y',  # Month YYYY format
                                    '%Y'  # Year-only format
                                ]
                                
                                for fmt in formats:
                                    try:
                                        date_obj = datetime.strptime(date_str, fmt)
                                        # Validate year is reasonable
                                        if 2000 <= date_obj.year <= 2100:
                                            # For 2-digit years, assume 20xx if year is less than 50
                                            if date_obj.year < 50:
                                                date_obj = date_obj.replace(year=date_obj.year + 2000)
                                            
                                            # If it's a month/year only format, set day to last day of month
                                            if fmt in ['%m/%Y', '%Y/%m', '%B %Y']:
                                                # Get the last day of the month
                                                if date_obj.month == 12:
                                                    next_month = date_obj.replace(year=date_obj.year + 1, month=1)
                                                else:
                                                    next_month = date_obj.replace(month=date_obj.month + 1)
                                                last_day = (next_month - timedelta(days=1)).day
                                                date_obj = date_obj.replace(day=last_day)
                                            
                                            # If it's a year-only format, set to December 31st
                                            if fmt == '%Y':
                                                date_obj = date_obj.replace(month=12, day=31)
                                            
                                            formatted_date = date_obj.strftime('%Y-%m-%d')
                                            print(f"Successfully parsed date: {formatted_date}")
                                            return formatted_date
                                    except ValueError:
                                        continue
                                        
                            except Exception as e:
                                print(f"Error parsing date {date_str}: {str(e)}")
                                continue
            
            # If no expiry date found, try to find any date in the text
            print("No expiry date found, looking for any date in text")
            
            # First, try to parse concatenated dates
            concatenated_pattern = r'\d{8,10}'  # Match 8-10 digit numbers
            matches = re.findall(concatenated_pattern, full_text)
            if matches:
                for match in matches:
                    date_obj = self.parse_concatenated_date(match)
                    if date_obj:
                        formatted_date = date_obj.strftime('%Y-%m-%d')
                        print(f"Successfully parsed concatenated date: {formatted_date}")
                        return formatted_date
            
            # If no concatenated date found, try other date formats
            date_patterns = [
                # Full year formats first (to prevent year truncation)
                r'\d{4}[./-]\d{1,2}[./-]\d{1,2}',  # YYYY/MM/DD
                r'\d{1,2}[./-]\d{1,2}[./-]\d{4}',  # DD/MM/YYYY
                # Then 2-digit year formats
                r'\d{1,2}[./-]\d{1,2}[./-]\d{2}',  # DD/MM/YY
                r'\d{2}[./-]\d{1,2}[./-]\d{2}',    # YY/MM/DD
                # Month name formats
                r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4}',
                # Month/Year only formats
                r'\d{1,2}[./-]\d{4}',  # MM/YYYY
                r'\d{4}[./-]\d{1,2}',  # YYYY/MM
                r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',  # Month YYYY
                # Year-only format
                r'\b\d{4}\b'  # YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, full_text)
                if matches:
                    date_str = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    print(f"Found potential date: {date_str}")
                    try:
                        # Try different date formats
                        formats = [
                            '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',  # YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
                            '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y',  # DD-MM-YYYY or DD/MM/YYYY or DD.MM.YYYY
                            '%d-%m-%y', '%d/%m/%y', '%d.%m.%y',  # DD-MM-YY or DD/MM/YY or DD.MM.YY
                            '%y-%m-%d', '%y/%m/%d', '%y.%m.%d',  # YY-MM-DD or YY/MM/DD or YY.MM.DD
                            '%B %d, %Y', '%b %d, %Y',  # Month name formats
                            '%m/%Y', '%Y/%m',  # Month/Year formats
                            '%B %Y',  # Month YYYY format
                            '%Y'  # Year-only format
                        ]
                        
                        for fmt in formats:
                            try:
                                date_obj = datetime.strptime(date_str, fmt)
                                # Validate year is reasonable
                                if 2000 <= date_obj.year <= 2100:
                                    # For 2-digit years, assume 20xx if year is less than 50
                                    if date_obj.year < 50:
                                        date_obj = date_obj.replace(year=date_obj.year + 2000)
                                    
                                    # If it's a month/year only format, set day to last day of month
                                    if fmt in ['%m/%Y', '%Y/%m', '%B %Y']:
                                        # Get the last day of the month
                                        if date_obj.month == 12:
                                            next_month = date_obj.replace(year=date_obj.year + 1, month=1)
                                        else:
                                            next_month = date_obj.replace(month=date_obj.month + 1)
                                        last_day = (next_month - timedelta(days=1)).day
                                        date_obj = date_obj.replace(day=last_day)
                                    
                                    # If it's a year-only format, set to December 31st
                                    if fmt == '%Y':
                                        date_obj = date_obj.replace(month=12, day=31)
                                    
                                    formatted_date = date_obj.strftime('%Y-%m-%d')
                                    print(f"Successfully parsed date: {formatted_date}")
                                    return formatted_date
                            except ValueError:
                                continue
                                
                    except Exception as e:
                        print(f"Error parsing date {date_str}: {str(e)}")
                        continue
            
            print("No valid date found in text")
            return None
            
        except Exception as e:
            print(f"Error in OCR processing: {str(e)}")
            return None 