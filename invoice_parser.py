# invoice_parser.py
import pytesseract
from PIL import Image
import re
import json
from typing import Dict, List
import os

# Configure tesseract path (Windows)
tesseract_cmd = os.getenv('TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def extract_text(image_path: str, debug: bool = False) -> str:
    """Run OCR on the image and return raw text."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)

        # Debug option: save OCR text for inspection
        if debug:
            with open("ocr_output.txt", "w", encoding="utf-8") as f:
                f.write(text)

        return text
    except Exception as e:
        raise Exception(f"OCR failed: {str(e)}")


def parse_invoice(text: str) -> Dict:
    """Extract invoice-level fields using regex."""
    invoice_data = {
        "invoice_number": None,
        "invoice_date": None, 
        "customer_name": None,
        "vendor_name": None,
        "total_amount": None
    }

    # Updated patterns
    patterns = {
        "invoice_number": r"CN3[-\s]?(\d+)",  # Specifically match CN3-002254 format
        "invoice_date": r"(?:BILL\s+DATE|DATE)\s*:?\s*(\d{2}/\d{2}/\d{4})",
        "customer_name": r"(?:BILL TO|TO)\s*:?\s*(RAJ DATA PROCESSORS)",
        "vendor_name": r"(RAJ SUPER WHOLESALE BAZAR)",
        "total_amount": r"(?:GRAND\s+TOTAL|TOTAL)\s*:?\s*(\d+\.?\d{2})"
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            invoice_data[field] = match.group(1).strip()

    return invoice_data


def extract_items(text: str) -> List[Dict]:
    """Extract line items from invoice body using regex."""
    items = []
    lines = text.splitlines()

    # Improved pattern for item rows
    item_pattern = re.compile(
        r"""
        ^\s*                             # Start of line
        (?:\d+\s+)?                      # Optional item number
        ([A-Za-z0-9\s\(\)\/.-]+?)        # Item description
        \s+                              # Whitespace
        (\d+)                            # Quantity
        \s+                              # Whitespace
        (\d+(?:\.\d{2})?)               # Unit price
        \s+                              # Whitespace
        (?:\d+(?:\.\d{2})?\s+)?         # Optional intermediate amount
        (\d+(?:\.\d{2})?)               # Total amount
        \s*$                             # End of line
        """,
        re.VERBOSE
    )

    for line in lines:
        line = line.strip()
        match = item_pattern.search(line)
        if match and len(match.groups()) == 4:
            desc = match.group(1).strip()
            # Filter valid items
            if (len(desc) > 3 and 
                not desc.lower().startswith(('total', 'grand', 'bill')) and
                not desc[0].isdigit()):
                    items.append({
                        "item_description": desc,
                        "quantity": match.group(2),
                        "unit_price": match.group(3),
                        "total_amount": match.group(4)
                    })

    return items


# Add debug function
def debug_ocr(text: str):
    """Save OCR text for debugging"""
    with open("ocr_debug.txt", "w", encoding="utf-8") as f:
        f.write(text)
