import pytesseract
import re
from PIL import Image
from qreader import QReader
from documents.pancard.pattern1 import PancardPattern1
from documents.pancard.pattern2 import PancardPattern2
from helper.text_coordinates import ImageTextCoordinates


class PancardDocumentInfo:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object, redaction_level: int) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.redaction_level = redaction_level
        self.coordinates = ImageTextCoordinates(self.ocrr_workspace_doc_path).generate_text_coordinates()
        # Tesseract configuration
        tesseract_config = r'--oem 3 --psm 11'
        self.text_data = pytesseract.image_to_string(self.ocrr_workspace_doc_path, lang="eng", config=tesseract_config)
        #print(self.coordinates)
        # Pancard Pattern
        self.pancard_pattern_1 = [
            r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
            r"\b\w*(hratlifies|facer|pacers|hratlieies)\b"
            ]   
        
    # Method to extract Pancard Number and its Coordinates
    def _extract_pancard_number(self) -> dict:
        result = {"Pancard Number": "", "Coordinates": []}
        try:
            # Extract Pancard Number and its Coordinates
            pancard_number = ""
            pancard_number_coordinates = []
            coordinates = []
            width = 0

            # Lambada function to check if any character in text is digit and alpha numeric
            is_digit_alpha_numeric = lambda x: any(char.isdigit() for char in x) and any(char.isalpha() for char in x)

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                if len(text) in(7, 9, 10) and text.isupper() and is_digit_alpha_numeric(text):
                    # Get the width of the text
                    width = x2 - x1
                    pancard_number = text
                    pancard_number_coordinates.append([x1, y1, x2, y2])
            # Check if Pancard Number is not found
            if not pancard_number:
                self.logger.warning("| Pancard Number not found in Pancard document")
                return result
            # Update the result
            for i in pancard_number_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.65 * width), i[3]])
            result = {
                "Pancard Number": pancard_number,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Number: {e}")
            return result
    
    # Method to extract Pancard DOB and its Coordinates
    def _extract_pancard_dob(self) -> dict:
        result = {"Pancard DOB": "", "Coordinates": []}
        try:
            # Extract Pancard DOB and its Coordinates
            dob = ""
            dob_coordinates = []
            coordinates = []
            width = 0

            # DOB Pattern: DD/MM/YYY, DD-MM-YYY
            #date_pattern = r'(?:(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d))|(?:(?:19\d\d|20\d\d)[-/.](?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12][0-9]|3[01]))|(?:(?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d))|(?:(?:19\d\d|20\d\d)[-/]\d{3})'

            dob_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}'

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DOB pattern
                if re.search(dob_pattern, text, flags=re.IGNORECASE):
                    dob += " "+ text
                    dob_coordinates.append([x1, y1, x2, y2])
            # Check if DOB is not found
            if not dob:
                self.logger.warning("| DOB not found in Pancard document")
                return result
            # Update the result
            for i in dob_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.80 * width), i[3]])
            result = {
                "Pancard DOB": dob,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard DOB: {e}")
            return result

    # Method to extract Pancard Names
    def _extract_pancard_names(self) -> dict:
        result = {"Pancard Names": "", "Coordinates": []}
        try:
            # Get the text from data list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]
            
            # Pancard Pattern 1 regex keywords
            pancard_pattern_1_found = False
            pancard_pattern_1 = [ r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
                                 r"\b\w*(hratlifies|facer|pacers|hratlieies|gather)\b"]
            # Identify the Pancard Pattern
            for text in text_data_list:
                for pattern in pancard_pattern_1:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        pancard_pattern_1_found = True
                        break
                if pancard_pattern_1_found:
                    break
            
            # Check if Pancard Pattern 1 is found
            if pancard_pattern_1_found:
                PATTERN = 1
                self.logger.info("| Pancard Pattern 1 found in Pancard document")
                pancard_name_result = PancardPattern1(self.coordinates, text_data_list, self.logger).get_names()
            else:
                PATTERN = 2
                self.logger.info("| Pancard Pattern 2 found in Pancard document")
                pancard_name_result = PancardPattern2(self.coordinates, text_data_list, self.logger).get_names()
            
            # Check if coordinates are not found
            if not pancard_name_result["coordinates"]:
                self.logger.warning(f"| Pancard Pattern {PATTERN}: Coordinates not found")
            
            # Get the 50% of each coordinates
            coordinates = []
            width = 0

            for i in pancard_name_result["coordinates"]:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])
            
            # Update the result
            result = {
                "Pancard Names": pancard_name_result["names"],
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Names: {e}")
            return result
        
    # Method to detect QR Codes in the document
    def _extract_qrcodes(self):
        result = {"Pancard QRCodes": "", "Coordinates": []}
        try:
            # Extract QR Codes coordinates from Pancard Document

            # Initialize QRCode Reader
            qrreader = QReader()
    
            # Initialize list to store QRCode coordinates
            qrcodes_coordinates = []

            # Load the image
            image = Image.open(self.ocrr_workspace_doc_path)

            # Detect and Decode QR Codes
            qrcodes = qrreader.detect(image)

            # Check if qrcodes not found
            if not qrcodes:
                self.logger.error("| QR Codes not found in Pancard document")
                return result
            
            # Get the 50% of QR Codes
            for qr in qrcodes:
                x1, y1, x2, y2 = qr['bbox_xyxy']
                qrcodes_coordinates.append([int(round(x1)), int(round(y1)), int(round(x2)), (int(round(y1)) + int(round(y2))) // 2])

            # Update result
            result = {
                "Pancard QRCodes": f"Found {len(qrcodes_coordinates)} QR Code",
                "Coordinates": qrcodes_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard QRCodes: {e}")
            return result
    
    # Method to collect document information
    def collect_document_info(self) -> list:
        document_info_list = []
        try:
            if self.redaction_level == 1:
                # Collect Pancard Number
                pancard_number = self._extract_pancard_number()
                document_info_list.append(pancard_number)

                # Collect Pancard DOB
                pancard_dob = self._extract_pancard_dob()
                document_info_list.append(pancard_dob)

                # Collect Pancard Names
                pancard_names = self._extract_pancard_names()
                document_info_list.append(pancard_names)
                
                # Collect Pancard QRCodes
                pancard_qrcodes = self._extract_qrcodes()
                document_info_list.append(pancard_qrcodes)
                
                print(document_info_list)
                # Check if all the dictionaries in the document_info_list are empty
                is_dictionary_empty = all(all(not v for v in d.values()) for d in document_info_list)
                if is_dictionary_empty:
                    self.logger.error("| No information found in Pancard document")
                    return {"message": "No information found in Pancard document", "status": "REJECTED"}
                else:
                    self.logger.info("| Successfully Redacted Pancard Document Information")
                    # Return the document information list
                    return {"message": "Successfully Redacted Pancard document", "status": "REDACTED", "data": document_info_list}
            else:
                # Collect Pancard Number
                pancard_number = self._extract_pancard_number()
                if len(pancard_number['Coordinates']) == 0:
                    self.logger.error("| No information for pancrd number found in Pancard document")
                    return {"message": "No information for pancard number found in Pancard document", "status": "REJECTED"}
                document_info_list.append(pancard_number)

                # Collect Pancard DOB
                pancard_dob = self._extract_pancard_dob()
                if len(pancard_dob['Coordinates']) == 0:
                    self.logger.error("| No information for pancrd dob found in Pancard document")
                    return {"message": "No information for pancard dob found in Pancard document", "status": "REJECTED"}
                
                # Collect Pancard Client Name
                pancard_client_name = self._extract_pancard_client_name()
                if len(pancard_client_name['Coordinates']) == 0:
                    self.logger.error("| No information for pancard client name found in Pancard document")
                    return {"message": "No information for pancard client name found in Pancard document", "status": "REJECTED"}
                
                # Collect Pancard Client Father Name
                pancard_client_father_name = self._extract_pancard_client_father_name()
                if len(pancard_client_father_name['Coordinates']) == 0:
                    self.logger.error("| No information for pancard client father name found in Pancard document")
                    return {"message": "No information for pancard client father name found in Pancard document", "status": "REJECTED"}

                # Return the document information list
                return {"message": "Successfully Redacted Pancard document", "status": "REDACTED", "data": document_info_list}
        except Exception as e:
            self.logger.error(f"| Error while collecting Pancard document information: {e}")
            return {"message": "Error in collecting Pancard Document Information", "status": "REJECTED"}