import pytesseract
import re
from PIL import Image
from qreader import QReader
from helper.text_coordinates import ImageTextCoordinates
from difflib import SequenceMatcher

class PancardDocumentInfo:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object, redaction_level: int) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.redaction_level = redaction_level
        self.coordinates = ImageTextCoordinates(self.ocrr_workspace_doc_path).generate_text_coordinates()
        # Tesseract configuration
        tesseract_config = r'--oem 3 --psm 11'
        self.text_data = pytesseract.image_to_string(self.ocrr_workspace_doc_path, lang="eng", config=tesseract_config)
        print(self.coordinates)
        
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
                self.logger.error("| Pancard Number not found in Pancard document")
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
            dob = ""
            dob_coordinates = []
            coordinates = []
            width = 0

            # DOB Pattern: DD/MM/YYY, DD-MM-YYY
            dob_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}'

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DOB pattern
                if re.match(dob_pattern, text, flags=re.IGNORECASE):
                    width = x2 - x1
                    dob += " "+ text
                    dob_coordinates.append([x1, y1, x2, y2])
            # Check if DOB is not found
            if not dob:
                self.logger.error("| DOB not found in Pancard document")
                return result
            # Update the result
            for i in dob_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.80 * width), i[3]])
            result = {
                "Pancars DOB": dob,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard DOB: {e}")
            return result

    # Method to extract Pancard Client Father Name and its Coordinates
    def _extract_pancard_client_father_name(self) -> dict:
        result = {"Pancard Client Father Name": "", "Coordinates": []}
        try:
            father_name = ""
            coordinates = None
            # Define the target text to search for
            target_text = ["Eather"]
            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]
            print(text_data_list)
            print(self._find_closest_matches(text_data_list, target_text))
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Client Father Name: {e}")
            return result
        
    # Function to find the closest match index for each target text
    def _find_closest_matches(self, text_list, target_texts):
        closest_matches = []
        for target_text in target_texts:
            closest_index = None
            highest_similarity = 0
        
        for i, text in enumerate(text_list):
            similarity = SequenceMatcher(None, text, target_text).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                closest_index = i
        
        closest_match = text_list[closest_index] if closest_index is not None else None
        closest_matches.append((target_text, closest_index, closest_match))
    
        return closest_matches
    
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

                # Collect Pancard Client Father Name
                pancard_client_father_name = self._extract_pancard_client_father_name()
                document_info_list.append(pancard_client_father_name)

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