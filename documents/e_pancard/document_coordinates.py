import pytesseract
import re
from PIL import Image
from qreader import QReader
from helper.text_coordinates import ImageTextCoordinates

class EPancardDocumentInfo:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object, redaction_level: int) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.redaction_level = redaction_level
        self.coordinates = ImageTextCoordinates(self.ocrr_workspace_doc_path).generate_text_coordinates()
        # Tesseract configuration
        tesseract_config = r'--oem 3 --psm 11'
        self.text_data = pytesseract.image_to_string(self.ocrr_workspace_doc_path, lang="eng", config=tesseract_config)
        
    # Method to extract E-Pancard Number and its Coordinates
    def _extract_pancard_number(self) -> dict:
        result = {"E-Pancard Number": "", "Coordinates": []}
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
                if len(text) == 10 and text.isupper() and is_digit_alpha_numeric(text):
                    # Get the width of the text
                    width = x2 - x1
                    pancard_number = text
                    pancard_number_coordinates.append([x1, y1, x2, y2])

            # Check if Pancard Number is not found
            if not pancard_number:
                self.logger.error("| Pancard Number not found in E-Pancard document")
                return result
            
            # Update the result
            for i in pancard_number_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.65 * width), i[3]])

            result = {
                "E-Pancard Number": pancard_number,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Pancard Number: {e}")
            return result
        
    # Method to extract E-Pancard DOB and its Coordinates
    def _extract_dates(self) -> dict:
        result = {"E-Pancard DOB": "", "Coordinates": []}
        try:
            dob = ""
            dob_coordinates = []
            coordinates = []
            width = 0
            
            # DOB Pattern: DD/MM/YYY, DD-MM-YYY
            dob_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}/\d{4}'

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DOB pattern
                if re.match(dob_pattern, text):
                    width = x2 - x1
                    dob += " "+ text
                    dob_coordinates.append([x1, y1, x2, y2])
                
            # Check if DOB is not found
            if not dob:
                self.logger.error("| DOB not found in E-Pancard document")
                return result
            
            # Update the result
            for i in dob_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.54 * width), i[3]])
                
            result = {
                "E-Pancard DOB": dob,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Pancard DOB: {e}")
            return result
    
    # Method to extract E-Pancard Gender and its Coordinates
    def _extract_gender(self) -> dict:
        result = {"E-Pancard Gender": "", "Coordinates": []}
        try:
            gender = ""
            gender_coordinates = []

            # Gender Pattern: M/F
            gender_pattern = r'Male|Female'

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the Gender pattern
                if re.match(gender_pattern, text, flags=re.IGNORECASE):
                    gender = text
                    gender_coordinates = [x1, y1, x2, y2]
                    break
            # Check if Gender is not found
            if not gender:
                self.logger.error("| Gender not found in E-Pancard document")
                return result
            # Update the result
            result = {
                "E-Pancard Gender": gender,
                "Coordinates": [gender_coordinates]
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Pancard Gender: {e}")
            return result
        
    # Method to extract E-Pancard Client Name and its Coordinates
    def _extract_client_name(self) -> dict:
        result = {"E-Pancard Client Name": "", "Coordinates": []}
        try:
            client_name = ""
            client_name_top_side_list = ""
            client_name_bottom_side_list = ""
            client_name_coordinates_top_side = []
            client_name_coordinates_bottom_side = []
            coordinates = None

            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]
            
            # Top
            # Loop through text data list
            for index,text in enumerate(text_data_list):
                if 'ata / Name' in text:
                    client_name = text_data_list[index+1]
                    client_name_top_side_list = text_data_list[index+1].split()
                    break
            # Get the coordinates of the client name of top side
            if client_name_top_side_list:
                if len(client_name_top_side_list) > 1:
                    client_name_top_side_list = client_name_top_side_list[:-1]

                for i,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                    if text in client_name_top_side_list:
                        client_name_coordinates_top_side.append([x1, y1, x2, y2])
                    if len(client_name_top_side_list) == len(client_name_coordinates_top_side):
                        break
            # Bottom
            # Loop through text data list
            for index,text in enumerate(text_data_list):
                if "CBD Belapur" in text:
                    if not client_name:
                        client_name = text_data_list[index+1]
                    client_name_bottom_side_list = text_data_list[index+1].split()
                    break
            # Get the coordinates of the client name of bottom side
            if client_name_bottom_side_list:
                if len(client_name_bottom_side_list) > 1:
                    client_name_bottom_side_list = client_name_bottom_side_list[:-1]
                for i,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                    if text in client_name_bottom_side_list:
                        # Check if [x1, y1, x2, y2] is already in the client_name_coordinates_top_side
                        if [x1, y1, x2, y2] not in client_name_coordinates_top_side:
                            client_name_coordinates_bottom_side.append([x1, y1, x2, y2])
                    if len(client_name_bottom_side_list) == len(client_name_coordinates_bottom_side):
                        break

            # Check if both Top and Bottom side client name coordinates are empty
            if not client_name_coordinates_top_side and not client_name_coordinates_bottom_side:
                self.logger.error("| Client Name not found in E-Pancard document")
                return result
            # Function to check list contents
            def add_list_if_not_empty(list1, list2):
                if list1 and list2:
                    return list1 + list2
                elif list1:
                    return list1
                elif list2:
                    return list2
            coordinates = add_list_if_not_empty(client_name_coordinates_top_side, client_name_coordinates_bottom_side)
            # Update result
            result = {
                "E-Pancard Client Name": client_name,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Pancard Client Name: {e}")
            return result
        
    # Method to extract E-Pancard Client Father Name and its Coordinates
    def _extract_client_father_name(self) -> dict:
        result = {"E-Pancard Client Father Name": "", "Coordinates": []}
        try:
            father_name = ""
            father_name_top_side_list = []
            father_name_bottom_side_list = []
            father_name_coordinates_top_side = []
            father_name_coordinates_bottom_side = []
            coordinates = None

            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            # Top
            # Loop through text data list
            for index,text in enumerate(text_data_list):
                if "Father's name" in text:
                    father_name = text_data_list[index+1]
                    father_name_top_side_list = text_data_list[index+1].split()
                    break
            # Get the coordinates of the father name of top side
            if father_name_top_side_list:
                if len(father_name_top_side_list) > 1:
                    father_name_top_side_list = father_name_top_side_list[:-1]
                for i,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                    if text in father_name_top_side_list:
                        father_name_coordinates_top_side.append([x1, y1, x2, y2])
                    if len(father_name_top_side_list) == len(father_name_coordinates_top_side):
                        break
            # Bottom
            # Loop through text data list
            for index,text in enumerate(text_data_list):
                if "Rat 1 AT" in text:
                    if not father_name:
                        father_name = text_data_list[index+2]
                    father_name_bottom_side_list = text_data_list[index+2].split()
                    break
            # Get the coordinates of the father name of bottom side
            if father_name_bottom_side_list:
                if len(father_name_bottom_side_list) > 1:
                    father_name_bottom_side_list = father_name_bottom_side_list[:-1]
                for i,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                    if text in father_name_bottom_side_list:
                        # Check if [x1, y1, x2, y2] is already in the father_name_coordinates_top_side
                        if [x1, y1, x2, y2] not in father_name_coordinates_top_side:
                            father_name_coordinates_bottom_side.append([x1, y1, x2, y2])
                    if len(father_name_bottom_side_list) == len(father_name_coordinates_bottom_side):
                        break
            
            # Check if both Top and Bottom side father name coordinates are empty
            if not father_name_coordinates_top_side and not father_name_coordinates_bottom_side:
                self.logger.error("| Father Name not found in E-Pancard document")
                return result
            
            # Function to check list contents
            def add_list_if_not_empty(list1, list2):
                if list1 and list2:
                    return list1 + list2
            coordinates = add_list_if_not_empty(father_name_coordinates_top_side, father_name_coordinates_bottom_side)
            # Update result
            result = {
                "E-Pancard Client Father Name": father_name,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Pancard Client Father Name: {e}")
            return result
        
    # Method to detect QRCode and its Coordinates
    def _extract_qrcodes(self):
        result = {"E-Pancard QRCodes": "", "Coordinates": []}
        try:
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
                self.logger.error("| QR Codes not found in E-Pancard document")
                return result
            
            # Get the 50% of QR Codes
            for qr in qrcodes:
                x1, y1, x2, y2 = qr['bbox_xyxy']
                qrcodes_coordinates.append([int(round(x1)), int(round(y1)), int(round(x2)), (int(round(y1)) + int(round(y2))) // 2])

            # Update result
            result = {
                "E-Pancard QRCodes": f"Found {len(qrcodes_coordinates)} QR Code",
                "Coordinates": qrcodes_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Pancard QRCodes: {e}")
            return result
    
    # Method to collect document information
    def collect_document_info(self) -> dict:
        document_info_list = []
        redaction_level = self.redaction_level
        
        try:
            if redaction_level == 1:
                # Collect Pancard Number
                pancard_number = self._extract_pancard_number()
                document_info_list.append(pancard_number)

                # Collect Pancard DOB
                pancard_dob = self._extract_dates()
                document_info_list.append(pancard_dob)

                # Collect Pancard Gender
                pancard_gender = self._extract_gender()
                document_info_list.append(pancard_gender)

                # Collect Pancard Client Name
                pancard_client_name = self._extract_client_name()
                document_info_list.append(pancard_client_name)

                # Collect Pancard Client Father Name
                pancard_client_father_name = self._extract_client_father_name()
                document_info_list.append(pancard_client_father_name)

                # Collect Pancard QRCodes
                pancard_qrcodes = self._extract_qrcodes()
                document_info_list.append(pancard_qrcodes)

                # Check if all the dictionaries in the document_info_list are empty
                is_dictionary_empty = all(all(not v for v in d.values()) for d in document_info_list)
                if is_dictionary_empty:
                    self.logger.error("| No information found in E-Pancard document")
                    return {"message": "No information found in E-Pancard document", "status": "REJECTED"}
                else:
                    self.logger.info("| Successfully Redacted E-Pancard Document Information")
                    # Return the document information list
                    return {"message": "Successfully Redacted E-Pancard document", "status": "REDACTED", "data": document_info_list}
            else:
                # Collect Pancard Number
                pancard_number = self._extract_pancard_number()
                if len(pancard_number['Coordinates']) == 0:
                    self.logger.error("| No information for pancard number found in E-Pancard document")
                    return {"message": "No information for pancard number found in E-Pancard document", "status": "REJECTED"}
                document_info_list.append(pancard_number)

                # Collect Pancard DOB
                pancard_dob = self._extract_dates()
                if len(pancard_dob['Coordinates']) == 0:
                    self.logger.error("| No information for pancrd dob found in E-Pancard document")
                    return {"message": "No information for pancard dob found in E-Pancard document", "status": "REJECTED"}
                
                # Collect Pancard Gender
                pancard_gender = self._extract_gender()
                if len(pancard_gender['Coordinates']) == 0:
                    self.logger.error("| No information for pancard gender found in E-Pancard document")
                    return {"message": "No information for pancard gender found in E-Pancard document", "status": "REJECTED"}

                # Collect Pancard Client Name
                pancard_client_name = self._extract_client_name()
                if len(pancard_client_name['Coordinates']) == 0:
                    self.logger.error("| No information for pancard client name found in E-Pancard document")
                    return {"message": "No information for pancard client name found in E-Pancard document", "status": "REJECTED"}
                
                # Collect Pancard Client Father Name
                pancard_client_father_name = self._extract_client_father_name()
                if len(pancard_client_father_name['Coordinates']) == 0:
                    self.logger.error("| No information for pancard client father name found in E-Pancard document")
                    return {"message": "No information for pancard client father name found in E-Pancard document", "status": "REJECTED"}
                
                # Return the document information list
                return {"message": "Successfully Redacted E-Pancard document", "status": "REDACTED", "data": document_info_list}
        except Exception as e:
            self.logger.error(f"| Error in collecting E-Pancard Document Information: {e}")
            return {"message": "Error in collecting E-Pancard Document Information", "status": "REJECTED"}