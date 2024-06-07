import pytesseract
import re
from PIL import Image
from qreader import QReader
from helper.text_coordinates import ImageTextCoordinates
from fuzzywuzzy import fuzz

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
            # Extract Pancard DOB and its Coordinates
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
                "Pancard DOB": dob,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard DOB: {e}")
            return result

    # Method to extract Pancard Client Name and its Coordinates
    def _extract_pancard_client_name(self) -> dict:
        result = {"Pancard Client Name": "", "Coordinates": []}
        try:
            # Extract Pancard Client Name and its Coordinates
            client_name = ""
            client_name_split = []
            coordinates = []
            name_keyword_index = 0
            break_loop_keywords = ["fathers", "father", "name", "hratlifies", "pacers"]

            # Define a threshold for a near match
            threshold = 80
            
            # Flag to indicate if a match has been found
            match_found = False
            
            # Define the target text to search for
            target_text = ["name", "uiname", "mame", "nun", "alatar", "fname", "hehe"]

            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            print(text_data_list)

            # Loop through the text data list and find the element nearest matcihng
            for index, text in enumerate(text_data_list):
                if match_found:
                    break
                # Ignore single-character or very short matches
                if len(text) <= 2:
                    continue
                for target in target_text:
                    if fuzz.partial_ratio(target.lower(), text.lower()) >= threshold:
                        name_keyword_index = index
                        match_found = True
                        break
            # Check if name index number is not found
            if name_keyword_index == 0:
                self.logger.error("| Name keyword not found in Pancard document")
                return result
            
            # Loop through the text data list starting from next index number of name_keyword_index
            match_found = False
            for index, text in enumerate(text_data_list[name_keyword_index + 1:]):
                if match_found:
                    break
                if text.lower() not in ["co,"]:
                    if text.isupper():
                        client_name = text
                        client_name_split = text.split()
                    # Check if the text matches any of the break_loop_keywords
                    for target in break_loop_keywords:
                        if fuzz.partial_ratio(target.lower(), text.lower()) >= threshold:
                            match_found = True
                            break
                
            # Check if Client Name is not found
            if not client_name:
                self.logger.error("| Client Name not found in Pancard document")
                return result
            
            # Check the length of the Client Name
            if len(client_name_split) > 1:
                client_name_split = client_name_split[:-1]
            
            # Get the coordinates of the Client Name
            for i, (x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in client_name_split:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])

            # Update result
            result = {
                "Pancard Client Name": client_name,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Client Name: {e}")
            return result

    # Method to extract Pancard Client Father Name and its Coordinates
    def _extract_pancard_client_father_name(self) -> dict:
        result = {"Pancard Client Father Name": "", "Coordinates": []}
        try:
            # Extract Pancard Client Father Name and its Coordinates
            father_name = ""
            father_name_split = []
            coordinates = []
            father_keyword_index = 0
            break_loop_keywords = ["date", "birth", "brth", "bit", "ate", "fh", "s", "hn"]

            # Define a threshold for a near match
            threshold = 80

            # Flag to indicate if a match has been found
            match_found = False

            # Define the target text to search for
            target_text = ["father's", "father", "eather's", 
                           "father's","ffatubr's", "fathers", 
                           "hratlieies", "ffatugr's", "father",
                            "father", "father's", "facer","race", 
                            "eaters", "ffatubr", "hratlifies"]
            
            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]
            
            # Loop through the text data list and find the element nearest matcihng
            for index, text in enumerate(text_data_list):
                if match_found:
                    break
                
                # Ignore single-character or very short matches
                if len(text) <= 2:
                    continue

                for target in target_text:
                    if fuzz.partial_ratio(target.lower(), text.lower()) >= threshold:
                        father_keyword_index = index
                        match_found = True
                        break
            
            # Check if father index number is not found
            if father_keyword_index == 0:
                self.logger.error("| Father keyword not found in Pancard document")
                return result
            
            # Loop through the text data list starting from next index number of name_keyword_index
            match_found = False
            for index, text in enumerate(text_data_list[father_keyword_index + 1:]):
                if match_found:
                    break
                
                if text.lower() not in ["ae", "an", "at", "es"]:
                    if text.isupper():
                        father_name = text
                        father_name_split = text.split()

                    # Check if the text matches any of the break_loop_keywords
                    for target in break_loop_keywords:
                        if fuzz.partial_ratio(target.lower(), text.lower()) >= threshold:
                            match_found = True
                            break

            # Check if Client Father Name is not found
            if not father_name:
                self.logger.error("| Client Father Name not found in Pancard document")
                return result
            
            # Check the length of the Client Father Name
            if len(father_name_split) > 1:
                father_name_split = father_name_split[:-1]

            # Get the coordinates of the Client Father Name
            for i, (x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in father_name_split:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])

            # Update result
            result = {
                "Pancard Client Father Name": father_name,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Client Father Name: {e}")
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

                # Collect Pancard Client Name
                pancard_client_name = self._extract_pancard_client_name()
                document_info_list.append(pancard_client_name)

                # Collect Pancard Client Father Name
                pancard_client_father_name = self._extract_pancard_client_father_name()
                document_info_list.append(pancard_client_father_name)

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