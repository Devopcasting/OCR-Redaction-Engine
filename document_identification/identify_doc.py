import cv2
import pytesseract
from document_identification.documents.identify_cdsl_doc import IdentifyCDSLDocument
from document_identification.documents.identify_e_pancard import IdentifyEPancardDocument
from document_identification.documents.identify_pancard import IdentifyPancardDocument
from document_identification.documents.identify_e_aadhaar import IdentifyEAadhaarDocument
from document_identification.documents.identify_aadhaar import IdentifyAadhaarDocument
from document_identification.documents.identify_passport import IdentifyPassportDocument
from document_identification.documents.identify_driving_license import IdentifyDrivingLicenseDocument

class DocumentIdentification:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.allowed_document_types = ['CDSL', 'E-PANCARD', 'PANCARD', 'E-AADHAAR', 'AADHAAR', 'PASSPORT', 'DL']
    
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
        if document_type in self.allowed_document_types:
            # Use match case to identify the document type
            match document_type:
                case 'CDSL':
                    return IdentifyCDSLDocument(self._get_text_from_image(), self.logger).check_cdsl_document_match()
                case 'E-PANCARD':
                    return IdentifyEPancardDocument(self._get_text_from_image(), self.logger).check_e_pancard_document_match()
                case 'PANCARD':
                    return IdentifyPancardDocument(self._get_text_from_image(), self.logger).check_pancard_document_match()
                case 'E-AADHAAR':
                    return IdentifyEAadhaarDocument(self._get_text_from_image(), self.logger).check_e_aadhaar_document_match()
                case 'AADHAAR':
                    return IdentifyAadhaarDocument(self._get_text_from_image(), self.logger).check_aadhaar_document_match()
                case 'PASSPORT':
                    return IdentifyPassportDocument(self._get_text_from_image(), self.logger).check_passport_document_match()
                case 'DL':
                    return IdentifyDrivingLicenseDocument(self._get_text_from_image(), self.logger).check_driving_license_document_match()
        else:
            return False