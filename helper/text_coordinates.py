import cv2
import pytesseract

class ImageTextCoordinates:
    def __init__(self, document_path: str, lang=None):
        self.document_path = document_path
        self.lang = lang
    
    def generate_text_coordinates(self) -> list:
        data = None
        if self.lang is None:
            # Tesseract configuration
            tesseract_config = r'--oem 3 --psm 11'
            data = pytesseract.image_to_data(self.document_path, output_type=pytesseract.Output.DICT, lang="eng", config=tesseract_config)
        elif self.lang == "default":
            data = pytesseract.image_to_data(self.document_path, output_type=pytesseract.Output.DICT, lang="eng")
        elif self.lang == "regionalplus":
            # Tesseract configuration
            tesseract_config = r'--oem 3 --psm 11 -l hin+eng'
            data = pytesseract.image_to_data(self.document_path, output_type=pytesseract.Output.DICT, lang="hin+eng", config=tesseract_config)
        
        coordinates = []
        for i in range(len(data['text'])):
            text = data['text'][i]
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            # Filter out empty strings and  special characters
            if text.strip() != '':
                coordinates.append((x, y, x + w, y + h, text))
        return coordinates