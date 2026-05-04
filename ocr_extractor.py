import pytesseract
from PIL import Image
import re
from datetime import datetime

import sys
import os

# NOTE FOR WINDOWS USERS:
# You MUST install the Tesseract executable for pytesseract to work.
# Download it here: https://github.com/UB-Mannheim/tesseract/wiki
# We explicitly point to the default path on Windows:
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def _extract_text_from_img(img):
    """Helper to extract text from an Image object, trying multiple rotations if MRZ is not found."""
    # Try original orientation
    text = pytesseract.image_to_string(img)
    if "P<" in text or "P<IND" in text:
        return text
        
    # If no MRZ found, try rotating
    for angle in [90, 180, 270]:
        rotated_img = img.rotate(angle, expand=True)
        text = pytesseract.image_to_string(rotated_img)
        if "P<" in text or "P<IND" in text:
            return text
            
    # If still not found, just return the original extraction
    return pytesseract.image_to_string(img)

def extract_text_from_image(image_path):
    """
    Reads an image file or PDF and extracts all text using Tesseract OCR.
    """
    try:
        print(f"Scanning document: {image_path}...")
        if image_path.lower().endswith('.pdf'):
            import fitz
            doc = fitz.open(image_path)
            full_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=300)
                pix.save(f"temp_pdf_page_{page_num}.png")
                img = Image.open(f"temp_pdf_page_{page_num}.png")
                full_text += _extract_text_from_img(img) + "\n"
            return full_text
        else:
            img = Image.open(image_path)
            return _extract_text_from_img(img)
    except Exception as e:
        print(f"[ERROR] Failed to extract text: {e}")
        print("Did you install Tesseract-OCR? Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        return ""

def parse_passport_details(raw_text):
    """
    Attempts to extract Name, DOB, and Passport Number from raw OCR text.
    This uses basic regex patterns common in US Passports/Visas.
    """
    details = {
        "first_name": "UNKNOWN",
        "last_name": "UNKNOWN",
        "dob": "UNKNOWN",
        "passport_number": "UNKNOWN",
        "country": "India (IND)" # Default to India as a fallback
    }
    
    # Try to parse MRZ first, as it's the most reliable
    # Remove all spaces from the text because MRZ lines don't have spaces but Tesseract might inject them
    mrz_text = raw_text.replace(' ', '')
    
    # Line 1: P<INDLASTNAME<<FIRSTNAME<<<<
    mrz1_match = re.search(r'P<[A-Z]{3}([A-Z0-9<]+)', mrz_text)
    # Line 2: PASSNUM<XINDYYMMDD...
    mrz2_match = re.search(r'([A-Z0-9<]{9})[0-9][A-Z<]{3}(\d{6})', mrz_text)
    
    if mrz1_match and mrz2_match:
        # Parse names from MRZ line 1
        names = mrz1_match.group(1).split('<<')
        if len(names) >= 2:
            details["last_name"] = names[0].replace('<', ' ').strip()
            details["first_name"] = names[1].replace('<', ' ').strip()
        elif len(names) == 1:
            details["last_name"] = names[0].replace('<', ' ').strip()
            
        # Parse passport num and DOB from MRZ line 2
        details["passport_number"] = mrz2_match.group(1).replace('<', '')
        
        yymmdd = mrz2_match.group(2)
        # Convert YYMMDD to YYYY-MM-DD
        year = int(yymmdd[:2])
        # simple heuristic: if year > 50, it's 19XX, else 20XX
        full_year = 1900 + year if year > 50 else 2000 + year
        details["dob"] = f"{full_year}-{yymmdd[2:4]}-{yymmdd[4:6]}"
        
        return details

    # Fallback to visual zone parsing if MRZ fails
    passport_match = re.search(r'(?i)(?:passport\s*no\.?|document\s*no\.?)[\s:]*([A-Z0-9]{8,9})', raw_text)
    if not passport_match:
        passport_match = re.search(r'\b[A-Z0-9]{8}\b', raw_text)
    
    if passport_match:
        details["passport_number"] = passport_match.group(1) if len(passport_match.groups()) > 0 else passport_match.group(0)

    dob_match = re.search(r'(?i)(?:Date of birth|DOB)[\s:]*([\d]{2}\s+[A-Za-z]{3}\s+[\d]{4})', raw_text)
    if dob_match:
        raw_dob = dob_match.group(1)
        try:
            dob_obj = datetime.strptime(raw_dob, "%d %b %Y")
            details["dob"] = dob_obj.strftime("%Y-%m-%d")
        except ValueError:
            details["dob"] = raw_dob

    surname_match = re.search(r'(?i)(?:Surname|Name)[^\nA-Z]*([A-Z]+)', raw_text)
    if surname_match:
        details["last_name"] = surname_match.group(1).upper()
        
    given_match = re.search(r'(?i)(?:Given Names|First Name)[^\nA-Z]*([A-Z\s]+)', raw_text)
    if given_match:
        details["first_name"] = given_match.group(1).strip().upper()

    return details

if __name__ == "__main__":
    # Test script - requires a sample image in the same directory
    sample_image = "sample_passport.jpg" 
    
    print("--- OCR Extractor Test ---")
    extracted_text = extract_text_from_image(sample_image)
    
    if extracted_text:
        print("\n[RAW TEXT EXTRACTED]")
        print("-" * 20)
        print(extracted_text)
        print("-" * 20)
        
        parsed_data = parse_passport_details(extracted_text)
        print("\n[PARSED DATA]")
        for k, v in parsed_data.items():
            print(f"{k.upper()}: {v}")
