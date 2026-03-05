import os
import pytesseract
from PIL import Image
import cv2
import pdfplumber
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------- IMAGE OCR (JPG / PNG) ----------
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return ""

    # Upscale image
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Reduce noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold (best for reports)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    config = r"--oem 3 --psm 6"

    text = pytesseract.image_to_string(thresh, config=config)
    
    print("=" * 50)
    print("EXTRACTED TEXT FROM IMAGE:")
    print("=" * 50)
    print(text)
    print("=" * 50)
    
    return text



# ---------- TEXT-BASED PDF OCR ----------
def extract_text_from_pdf_text(pdf_path):
    full_text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
    except Exception as e:
        return ""

    print("=" * 50)
    print("EXTRACTED TEXT FROM PDF:")
    print("=" * 50)
    print(full_text)
    print("=" * 50)
    
    return full_text


# ---------- SCANNED PDF OCR ----------
def extract_text_from_pdf_scanned(pdf_path):
    full_text = ""

    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        return "Error: PDF image conversion failed. Poppler may not be installed."

    for img in images:
        text = pytesseract.image_to_string(img)
        full_text += text + "\n"

    print("=" * 50)
    print("EXTRACTED TEXT FROM SCANNED PDF:")
    print("=" * 50)
    print(full_text)
    print("=" * 50)
    
    return full_text


# ---------- SMART OCR SELECTOR ----------
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path)

    elif ext == ".pdf":
        text = extract_text_from_pdf_text(file_path)

        # If text is too small, assume scanned PDF
        if len(text.strip()) < 50:
            return extract_text_from_pdf_scanned(file_path)

        return text

    else:
        return "Unsupported file format"