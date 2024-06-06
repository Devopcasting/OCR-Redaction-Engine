import cv2
import pytesseract
from document_identification.documents.identify_cdsl_doc import IdentifyCDSLDocument
from document_identification.documents.identify_e_pancard import IdentifyEPancardDocument
from document_identification.documents.identify_pancard import IdentifyPancardDocument

class DocumentIdentification:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
    

    def _identified_documents_result(self) -> dict:
        data_text_list = self._get_text_from_image()
        # Identify the document type
        result = {
            "CDSL": IdentifyCDSLDocument(data_text_list, self.logger).check_cdsl_document_match(),
            "E-PANCARD": IdentifyEPancardDocument(data_text_list, self.logger).check_e_pancard_document_match(),
            "PANCARD": IdentifyPancardDocument(data_text_list, self.logger).check_pancard_document_match()
        }
        return result
    
    def _get_text_from_image(self) -> list:
        # Load the image
        img = cv2.imread(self.ocrr_workspace_doc_path)
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Tesseract configuration
        tesseract_config = r'--oem 3 --psm 11'
        # Apply OCR to the grayscale image
        data_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=tesseract_config)
        return data_text['text']

    def identify_document_type(self, document_type: str) -> bool:
        identified_document_result_dict = self._identified_documents_result()
        if document_type in identified_document_result_dict:
            return identified_document_result_dict[document_type]
        else:
            return False
