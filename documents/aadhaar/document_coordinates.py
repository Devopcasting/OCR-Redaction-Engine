import pytesseract
import re
from PIL import Image
from qreader import QReader
from helper.text_coordinates import ImageTextCoordinates
from helper.places import places_list

class AadhaarDocumentInfo:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object, redaction_level: int) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.redaction_level = redaction_level

        self.coordinates = ImageTextCoordinates(self.ocrr_workspace_doc_path).generate_text_coordinates()
        # Tesseract configuration
        tesseract_config = r'--oem 3 --psm 11'
        self.text_data = pytesseract.image_to_string(self.ocrr_workspace_doc_path, lang="eng", config=tesseract_config)
        print(self.coordinates)
        # List of Places
        self.places = places_list

    # Method to extract Aadhaar Number and its Coordinates
    def _extract_aadhaar_number(self) -> dict:
        result = {"Aadhaar Number": "", "Coordinates": []}
        try:
            # Extract Aadhaar Number and its Coordinates
            aadhaar_number = ""
            aadhaar_number_coordinates = []
            coordinates = []
            width = 0

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text is of length 4 or 14 and is digit
                if (len(text) == 4 or len(text) == 14) and text.isdigit():
                    aadhaar_number += " "+ text
                    aadhaar_number_coordinates.append([x1, y1, x2, y2])
            
            # Check if Aadhaar Number is not found
            if not aadhaar_number:
                self.logger.error("| Aadhaar Number not found in Aadhaar document")
                return result
            
            # Update the result
            for i in aadhaar_number_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])

            result = {
                "Aadhaar Number": aadhaar_number,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Number: {e}")
            return result

    # Method to extract Aadhaar Name and its Coordinates
    def _extract_aadhaar_name(self) -> dict:
        result = {"Aadhaar Name": "", "Coordinates": []}
        try:
            # Extract Aadhaar Name and its Coordinates
            aadhaar_name = ""
            name_text_list = []
            coordinates = []
            search_text_index = 0
            skip_text_keywords = [
                r"\b(a|ay|,|73|Ts|n 4|ZN.|ZN|em|GN|«|-|~|Gina|Gina.|Ee a ee)\b"
            ]
            search_text = [
                r"\b\w*(dob)\b"
            ]
            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            # Filter out elements containing only digits
            filtered_text_data_list = [text for text in text_data_list if not text.isdigit()]

            # Reverse the filtered text data list
            reversed_filtered_text_data_list = filtered_text_data_list[::-1]
            
            print(reversed_filtered_text_data_list)
            
            # Loop through the reversed filtered text data list and get the index of search text
            for index,text in enumerate(reversed_filtered_text_data_list):
                for regex in search_text:
                    if re.search(regex, text, flags=re.IGNORECASE):
                        search_text_index = index
                        break
            # Check if search text index is not found
            if search_text_index == 0:
                self.logger.error("| Search text not found in Aadhaar document")
                return result

            # Loop through the reversed filtered text data list starting from search text index
            for index, text in enumerate(reversed_filtered_text_data_list[search_text_index + 1 :]):
                # Check if text contains any of the skip text keywords
                for pattern in skip_text_keywords:
                    if re.match(pattern, text, flags=re.IGNORECASE):
                        continue
                    else:
                        aadhaar_name += " " + text
                        # Split and check the length of text. If length is greater than 1 then add all the elements except last
                        if len(text.split()) > 1:
                            name_text_list.extend(text.split()[:-1])
                        else:
                            name_text_list.append(text)
            
            # Get the coordinates of name text
            for x1, y1, x2, y2, text in self.coordinates:
                if text in name_text_list:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])
            
            # Update the result
            result = {
                "Aadhaar Name": aadhaar_name,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Name: {e}")
            return result
    
    # Method to extract Aadhaar DOB and its Coordinates
    def _extract_aadhaar_dob(self) -> dict:
        result = {"Aadhaar DOB": "", "Coordinates": []}
        try:
            # Extract Aadhaar DOB and its Coordinates
            dob = ""
            dob_coordinates = []
            coordinates = []
            width = 0

            # DOB Pattern: DD/MM/YYY, DD-MM-YYY
            dob_pattern = r'\b\d{2}/\d{2}/\d{4}|\b\d{2}/\d{5}|\b\d{2}-\d{2}-\d{4}|\b\d{4}/\d{4}|\b\d{2}/\d{2}/\d{2}|\b\d{1}/\d{2}/\d{4}|\b[Oo]?\d{1}/\d{5}\b'

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DOB pattern
                if re.match(dob_pattern, text, flags=re.IGNORECASE):
                    dob += " "+ text
                    dob_coordinates.append([x1, y1, x2, y2])
            
            # Check if DOB is not found
            if not dob:
                self.logger.error("| DOB not found in Aadhaar document")
                return result
            # Update the result
            for i in dob_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.80 * width), i[3]])
            result = {
                "Aadhaar DOB": dob,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar DOB: {e}")
            return result
    
    # Method to extarct Aadhaar Gender and its Coordinates
    def _extract_aadhaar_gender(self) -> dict:
        result = {"Aadhaar Gender": "", "Coordinates": []}
        try:
            # Extract Gender and its Coordinates
            gender = ""
            gender_list = []
            coordinates = []

            gender_pattern = [
                r"\b(?:male|female|femalp|femere|femala|mate|femate|#femste|fomale|fertale|malo|femsle|fade|ferme|famate)\b"
            ]

            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            # Loop through the text data
            for text in text_data_list:
                # Loop through the gender patterns
                for pattern in gender_pattern:
                    # Compile the pattern
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        gender = text
                        break
            
            # Check if Gender is not found
            if not gender:
                self.logger.error("| Gender not found in Aadhaar document")
                return result
            
            # Split the gender text
            gender_list = gender.split()

            # Get the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                if text in gender_list:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])
                    # Check if the length of gender_list is equal to coordinates list
                    if len(gender_list) == len(coordinates):
                        break

            # Update the result
            result = {
                "Aadhaar Gender": gender,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Gender: {e}")
            return result

    # Method to extract Aadhaar Address and its Coordinates
    def _extract_aadhaar_address(self) -> dict:
        result = {"Aadhaar Address": "", "Coordinates": []}
        try:
            address = ""
            coordinates = []

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Loop throgh list of places
                for place in self.places:
                    # Check if the text matches the place
                    if re.search(place, text, flags=re.IGNORECASE):
                        address += " " + text
                        coordinates.append([x1, y1, x2, y2])

            # Check if Address is not found
            if not address:
                self.logger.error("| Address not found in Aadhaar document")
                return result
            
            # Update the result
            result = {
                "Aadhaar Address": address,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Address: {e}")
            return result
    
    # Method to extract Aadhaar Pincode and its Coordinates
    def _extract_aadhaar_pincode(self) -> dict:
        result = {"Aadhaar Pincode": "", "Coordinates": []}
        try:
            pincode = ""
            pincode_coordinates = []
            coordinates = []
            width = 0

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text length is 6 and text is a number
                if len(text) in (6,7) and text[:6].isdigit():
                    pincode += " "+ text
                    pincode_coordinates.append([x1, y1, x2, y2])

            # Check if Pincode is not found
            if not pincode:
                self.logger.error("| Pincode not found in Aadhaar document")
                return result
            
            # Update the result
            for i in pincode_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.30 * width), i[3]])

            result = {
                "Aadhaar Pincode": pincode,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Pincode: {e}")
            return result
    
    # Method to extract Aadhaar QR-Codes and its Coordinates
    def _extract_aadhaar_qr_codes(self) -> list:
        result = {"Aadhaar QRCodes": "", "Coordinates": []}
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
                self.logger.error("| QR Codes not found in Aadhaar document")
                return result
            
            # Get the 50% of QR Codes
            for qr in qrcodes:
                x1, y1, x2, y2 = qr['bbox_xyxy']
                qrcodes_coordinates.append([int(round(x1)), int(round(y1)), int(round(x2)), (int(round(y1)) + int(round(y2))) // 2])

            # Update result
            result = {
                "Aadhaar QRCodes": f"Found {len(qrcodes_coordinates)} QR Code",
                "Coordinates": qrcodes_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar QRCodes: {e}")
            return result


    # Method to collect document information
    def collect_document_info(self) -> list:
        document_info_list = []
        try:
            if self.redaction_level == 1:
                # Collect Aadhaar Number
                aadhaar_number = self._extract_aadhaar_number()
                document_info_list.append(aadhaar_number)

                # Collect Aadhaar Name
                aadhaar_name = self._extract_aadhaar_name()
                document_info_list.append(aadhaar_name)

                # Collect Aadhaar DOB
                aadhaar_dob = self._extract_aadhaar_dob()
                document_info_list.append(aadhaar_dob)

                # Collect Aadhaar Gender
                aadhaar_gender = self._extract_aadhaar_gender()
                document_info_list.append(aadhaar_gender)

                # Collect Aadhaar Address
                aadhaar_address = self._extract_aadhaar_address()
                document_info_list.append(aadhaar_address)

                # Collect Aadhaar Pincode
                aadhaar_pincode = self._extract_aadhaar_pincode()
                document_info_list.append(aadhaar_pincode)

                # Collect Aadhaar QR-Codes
                aadhaar_qrcodes = self._extract_aadhaar_qr_codes()
                document_info_list.append(aadhaar_qrcodes)

                print(document_info_list)

                # Check if all the dictionaries in the document_info_list are empty
                is_dictionary_empty = all(all(not v for v in d.values()) for d in document_info_list)
                if is_dictionary_empty:
                    self.logger.error("| No information found in Aadhaar document")
                    return {"message": "No information found in Aadhaar document", "status": "REJECTED"}
                else:
                    self.logger.info("| Successfully Redacted Aadhaar Document Information")
                    # Return the document information list
                    return {"message": "Successfully Redacted Aadhaar document", "status": "REDACTED", "data": document_info_list}
            else:
                # Collect Aadhaar Number
                aadhaar_number = self._extract_aadhaar_number()
                if len(aadhaar_number['Coordinates']) == 0:
                    self.logger.error("| No information for Aadhaar Number found in Aadhaar document")
                    return {"message": "No information for Aadhaar Number found in Aadhaar document", "status": "REJECTED"}
                document_info_list.append(aadhaar_number)

                # Collect Aadhaar Name
                aadhaar_name = self._extract_aadhaar_name()
                if len(aadhaar_name['Coordinates']) == 0:
                    self.logger.error("| No information for Aadhaar Name found in Aadhaar document")
                    return {"message": "No information for Aadhaar Name found in Aadhaar document", "status": "REJECTED"}
                document_info_list.append(aadhaar_name)

                # Collect Aadhaar DOB
                aadhaar_dob = self._extract_aadhaar_dob()
                if len(aadhaar_dob['Coordinates']) == 0:
                    self.logger.error("| No information for Aadhaar DOB found in Aadhaar document")
                    return {"message": "No information for Aadhaar DOB found in Aadhaar document", "status": "REJECTED"}
                document_info_list.append(aadhaar_dob)
                
                # Collect Aadhaar Gender
                aadhaar_gender = self._extract_aadhaar_gender()
                if len(aadhaar_gender['Coordinates']) == 0:
                    self.logger.error("| No information for Aadhaar Gender found in Aadhaar document")
                    return {"message": "No information for Aadhaar Gender found in Aadhaar document", "status": "REJECTED"}
                document_info_list.append(aadhaar_gender)

                # Collect Aadhaar Address
                aadhaar_address = self._extract_aadhaar_address()
                if len(aadhaar_address['Coordinates']) == 0:
                    self.logger.error("| No information for Aadhaar Address found in Aadhaar document")
                else:
                    document_info_list.append(aadhaar_address)

                # Collect Aadhaar Pincode
                aadhaar_pincode = self._extract_aadhaar_pincode()
                if len(aadhaar_pincode['Coordinates']) == 0:
                    self.logger.error("| No information for Aadhaar Pincode found in Aadhaar document")
                else:
                    document_info_list.append(aadhaar_pincode)

                # Collect Aadhaar QR-Codes
                aadhaar_qrcodes = self._extract_aadhaar_qr_codes()
                if len(aadhaar_qrcodes['Coordinates']) == 0:
                    self.logger.error("| No information for Aadhaar QR-Codes found in Aadhaar document")
                else:
                    document_info_list.append(aadhaar_qrcodes)

                # Return the document information list
                return {"message": "Successfully Redacted Aadhaar document", "status": "REDACTED", "data": document_info_list}
        except Exception as e:
            self.logger.error(f"| Error while collecting Aadhaar document information: {e}")
            return {"message": "Error in collecting Aadhaar Document Information", "status": "REJECTED"}