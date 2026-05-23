from io import BytesIO

import fitz
import pandas as pd
import pytesseract
from PIL import Image
from docx import Document
from pypdf import PdfReader


def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""

    file_type = uploaded_file.type or ""
    file_name = uploaded_file.name.lower()

    if file_type == "text/plain" or file_name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")

    if file_type == "application/pdf" or file_name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        text_parts = []

        for page in reader.pages[:25]:
            text_parts.append(page.extract_text() or "")

        extracted_text = "\n".join(text_parts).strip()

        if extracted_text:
            return extracted_text

        uploaded_file.seek(0)
        pdf_document = fitz.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf"
        )
        ocr_parts = []

        for page in pdf_document[:8]:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image = Image.open(
                BytesIO(pixmap.tobytes("png"))
            )
            ocr_parts.append(
                pytesseract.image_to_string(image)
            )

        return "\n".join(ocr_parts).strip()

    if file_name.endswith(".docx"):
        document = Document(uploaded_file)
        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

    if file_name.endswith(".csv"):
        dataframe = pd.read_csv(uploaded_file)
        return dataframe.to_string(index=False)

    if file_name.endswith(".xlsx"):
        dataframe = pd.read_excel(uploaded_file)
        return dataframe.to_string(index=False)

    if file_type.startswith("image/") or file_name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        image = Image.open(BytesIO(uploaded_file.getvalue()))
        return pytesseract.image_to_string(image).strip()

    return ""


def extraction_note():
    return (
        "OCR works best with clear, well-lit scans. Handwritten student copies may need "
        "teacher correction in the extracted-text box before grading. Scanned PDFs are "
        "OCR-read page by page, but unclear handwriting still needs human review."
    )
