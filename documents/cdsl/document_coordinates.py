import pytesseract
from helper.text_coordinates import ImageTextCoordinates

class CDSLDocumentInfo:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object, redaction_level: int):
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.redaction_level = redaction_level
        self.coordinates = ImageTextCoordinates(self.ocrr_workspace_doc_path, lang="default").generate_text_coordinates()
        
    def _extract_pancard_number(self) -> dict:
        result = {
            "CDSL Pancard Number": "",
            "Coordinates": []
        }
        try:
            # Extract Pancard Number and its Coordinates
            pancard_number = ""
            pancard_number_coordinates = []

            # Lambada function to check if any character in text is digit and alpha numeric
            is_digit_alpha_numeric = lambda x: any(char.isdigit() for char in x) and any(char.isalpha() for char in x)

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                if len(text) == 10 and text.isupper() and is_digit_alpha_numeric(text):
                    # Get the width of the text
                    width = x2 - x1
                    pancard_number = text
                    pancard_number_coordinates = [x1, y1, x2, y2]
                    break
            # Check if Pancard Number is not found
            if not pancard_number:
                self.logger.error("| Pancard Number not found in CDSL document")
                return result
            # Update the result
            result = {
                "CDSL Pancard Number": pancard_number,
                "Coordinates": [[
                    pancard_number_coordinates[0],
                    pancard_number_coordinates[1],
                    pancard_number_coordinates[0] + int(0.65 * width),
                    pancard_number_coordinates[3]
                    ]]
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error in extracting Pancard Number from CDSL document: {e}")
            return result
    
    def _extract_client_name(self):
        result = {
            "CDSL Client Name": "",
            "Coordinates": []
        }
        try:
            client_name = ""
            client_name_coordinates = []
            pancard_number_index = None
            break_loop_list = ["current", "kin", "ikyc", "kyc", "kra", "kyo", "date", "status", "not", "available"]

            # Lambada function to check if any character in text is digit and alpha numeric
            is_digit_alpha_numeric = lambda x: any(char.isdigit() for char in x) and any(char.isalpha() for char in x)

            # Get the index number of Pancard Number in the coordinates list
            for index, (x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if len(text) == 10 and text.isupper() and is_digit_alpha_numeric(text):
                    pancard_number_index = index
                    break

            # Check if Pancard Number index is not found
            if pancard_number_index is None:
                self.logger.error("| Pancard Number index not found in CDSL document")
                return result

            # Loop through all text coordinates after Pancard Number index
            for index, (x1, y1, x2, y2, text) in enumerate(self.coordinates[pancard_number_index:]):
                # Break the loop if text is available in the break loop list
                if text.lower() in break_loop_list:
                    break
                # Check if text is in uppercase and is alpha numeric
                if text.isupper() and text.isalpha():
                    client_name += " "+ text
                    client_name_coordinates.append([x1, y1, x2, y2])
            
            # Check the length of client name coordinates list
            if len(client_name_coordinates) > 1:
                result = {
                    "CDSL Client Name": client_name,
                    "Coordinates": [
                        [
                            client_name_coordinates[0][0],
                            client_name_coordinates[0][1],
                            client_name_coordinates[-1][2],
                            client_name_coordinates[-1][3]
                        ]
                    ]
                }  
            else:
                result = {
                    "CDSL Client Name": client_name,
                    "Coordinates": [
                        [
                            client_name_coordinates[0][0],
                            client_name_coordinates[0][1],
                            client_name_coordinates[0][2],
                            client_name_coordinates[0][3]
                        ]
                    ]
                }
            return result
        except Exception as e:
            self.logger.error(f"| Error in extracting Client Name from CDSL document: {e}")
            return result
        
    def collect_document_info(self) -> dict:
        document_info_list = []
        redaction_level = self.redaction_level
        try:
            if redaction_level == 1:
                # Collect Pancard Number
                pancard_number = self._extract_pancard_number()
                document_info_list.append(pancard_number)

                # Collect Client Name
                client_name = self._extract_client_name()
                document_info_list.append(client_name)

                # Check if all the dictionaries in the document_info_list are empty
                is_dictionary_empty = all(all(not v for v in d.values()) for d in document_info_list)
                if is_dictionary_empty:
                    self.logger.error("| No information found in CDSL document")
                    return {"message": "No information found in CDSL document", "status": "REJECTED"}
                else:
                    self.logger.info("| Successfully collected CDSL Document Information")
                    return {"message": "Successfully Redacted CDSL document", "status": "REDACTED", "data": document_info_list}
        except Exception as e:
            self.logger.error(f"| Error in collecting CDSL Document Information: {e}")
            return {"message": "Error in collecting CDSL Document Information", "status": "REJECTED"}