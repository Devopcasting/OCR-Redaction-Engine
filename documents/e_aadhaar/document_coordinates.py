import pytesseract
import re
from PIL import Image
from qreader import QReader
from helper.text_coordinates import ImageTextCoordinates
from helper.places import places_list

class EAadhaarDocumentInfo:
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


    # Method to extract E-Aadhaar Number and its Coordinates
    def _extract_e_aadhaar_number(self) -> dict:
        result = {"E-Aadhaar Number": "", "Coordinates": []}
        try:
            # Extract E-Aadhaar Number and its Coordinates
            e_aadhaar_number = ""
            e_aadhaar_number_coordinates = []
            coordinates = []
            width = 0

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text is of length 4 or 14 and is digit
                if (len(text) == 4 or len(text) == 14) and text.isdigit():
                    e_aadhaar_number += " "+ text
                    e_aadhaar_number_coordinates.append([x1, y1, x2, y2])
            
            # Check if E-Aadhaar Number is not found
            if not e_aadhaar_number:
                self.logger.error("| E-Aadhaar Number not found in E-Aadhaar document")
                return result
            
            # Update the result
            for i in e_aadhaar_number_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])

            result = {
                "E-Aadhaar Number": e_aadhaar_number,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar Number: {e}")
            return result

    # Method to get the keyword index number
    def _get_keyword_index(self, keyword: str, text_data_list: list) -> int:
        try:
            match_index = 0
            # Loop through the text data list
            for index,text in enumerate(text_data_list):
                match_found = False
                # Check if the keyword is in the text
                for pattern in keyword:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        match_found = True
                        break
                if match_found:
                    match_index = index
                    break
            return match_index
        except Exception as e:
            self.logger.error(f"| Error while getting keyword index: {e}")
            return match_index
        
    # Method to get the coordinates
    def _get_coordinates(self, name_list: list) -> list:
        try:
            coordinates = []
            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                if text in name_list:
                    coordinates.append([x1, y1, x2, y2])
            return coordinates
        except Exception as e:
            self.logger.error(f"| Error while getting coordinates: {e}")
            return coordinates
        
    # Method to extract E-Aadhaar Name and its Coordinates
    def _extract_e_aadhaar_name(self) -> dict:
        result = {"E-Aadhaar Name": "", "Coordinates": []}
        try:
            coordinates = []
            combined_coordinates = []
            width = 0
            
            # Top search keyword
            top_search_keyword = [r"\b\w*(to)\b"]
            top_search_keyword_index = 0
            top_name = ""
            top_name_list = []
            top_name_coordinates = []

            # Enrollment serach keyword
            enrollment_search_keyword = [r"\b(enrollment|enrolment|enrolknant|enrollment|enrolment|encolent|enroiiment|enrotment|encol ent no|enroliment|enrolment|enrotiment|/enrolment|enrotimant|enrallment|evavenrolment|eivavenrolment|ehyollment|enrollmentno)\b"]
            enrollment_search_keyword_index = 0
            enrollment_name = ""
            enrollment_name_list = []
            enrollment_name_coordinates = []

            # Bottom search keyword
            bottom_search_keyword = [r"\b\w*(date|signature|dob|dos|birth|bith|year|dou|binh|003|008|pub|farce|binn|yoas|dou|doe)\b"]
            bottom_name = ""
            bottom_name_list = []
            bottom_name_coordinates = []

            # Skip Keywords
            skip_keywords = [r"\b(enrollment|enrolment|enrolknant|enrollment|enrolment|encolent|enroiiment|enrotment|encol ent no|enroliment|enrolment|enrotiment|/enrolment|enrotimant|enrallment|evavenrolment|eivavenrolment|ehyollment|enrollmentno)\b",
                             r"\b\w*(to)\b",
                             r"\b(india|oflndia|with|no|responsibility|Attested|True|Copy|Embassy|of|india|STUN|BAes|Aerara|Ha|MUsEN)\b"]
            
            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]
            # print(f"TEXT DATA LIST : {text_data_list}")

            # Filter out elements containing only digits
            filtered_text_data_list = [text for text in text_data_list if not text.isdigit()]
            
            ## Top Search Keyword
            top_search_keyword_index = self._get_keyword_index(top_search_keyword, filtered_text_data_list)
            if top_search_keyword_index != 0:
                # Loop through filtered text data
                for index,text in enumerate(filtered_text_data_list[top_search_keyword_index + 1 : top_search_keyword_index + 4]):
                    top_name += " "+ text
                
                # Remove the skip keywords from top_name
                for skip_keyword in skip_keywords:
                    top_name = re.sub(skip_keyword, "", top_name, flags=re.IGNORECASE)
                    top_name = top_name.strip()

                # print(f"TOP NAME: {top_name}")
                # Split the top name
                top_name_list = top_name.split()
                
                # Get the coordinates
                top_name_coordinates = self._get_coordinates(top_name_list)
                combined_coordinates.extend(top_name_coordinates)
            
            # print(f"TOP: {top_name_list}")

            ## Enrollment Search Keyword
            enrollment_search_keyword_index = self._get_keyword_index(enrollment_search_keyword, filtered_text_data_list)
            if  enrollment_search_keyword_index != 0:
                # Loop through filtered text data
                for index,text in enumerate(filtered_text_data_list[enrollment_search_keyword_index + 1 : enrollment_search_keyword_index + 4]):
                    enrollment_name += " "+ text
                
                # Remove the skip keywords from enrollment name
                for skip_keyword in skip_keywords:
                    enrollment_name = re.sub(skip_keyword, "", enrollment_name, flags=re.IGNORECASE)
                    enrollment_name = enrollment_name.strip()

                # Split the enrollment_name
                enrollment_name_list = enrollment_name.split()
                
                # Get the coordinates
                enrollment_name_coordinates = self._get_coordinates(enrollment_name_list)
                combined_coordinates.extend(enrollment_name_coordinates)
            # print(f"ENROLLMENT: {enrollment_name_list}")
            ## Bottom Search Keyword
            # Reverse the filtered text data list
            reversed_filtered_text_data_list = filtered_text_data_list[::-1]
            print(f"REVERSED TEXT DATA LIST : {reversed_filtered_text_data_list}")
            bottom_search_keyword_index = self._get_keyword_index(bottom_search_keyword, reversed_filtered_text_data_list)
            print(f"BOTTOM SEARCH KEYWORD INDEX: {bottom_search_keyword_index}")
            if bottom_search_keyword_index != 0:
                # Loop through filtered text data
                for index,text in enumerate(reversed_filtered_text_data_list[bottom_search_keyword_index + 1 : bottom_search_keyword_index + 4]):
                    bottom_name += " "+ text
                # Remove the skip keywords from bottom name
                for skip_keyword in skip_keywords:
                    bottom_name = re.sub(skip_keyword, "", bottom_name, flags=re.IGNORECASE)
                    bottom_name = bottom_name.strip()
                # Split the bottom_name
                bottom_name_list = bottom_name.split()
                # Get the coordinates
                bottom_name_coordinates = self._get_coordinates(bottom_name_list)
                combined_coordinates.extend(bottom_name_coordinates)
            print(f"BOTTOM: {bottom_name_list}")
            # print(f"COMBINED: {combined_coordinates}")
            # Check if top, enrollment and bottom all the coordinates are not found
            if not top_name_coordinates and not enrollment_name_coordinates and not bottom_name_coordinates:
                self.logger.error("| E-Aadhaar Name not found in E-Aadhaar document")
                return result
            
            for i in combined_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])

            # Update the result
            result = {
                "E-Aadhaar Name": top_name + " " + enrollment_name + " " + bottom_name,
                "Coordinates": coordinates
            }
            return result      
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar Name: {e}")
            return result
    
    # Method to extract E-Aadhaar DOB and its Coordinates
    def _extract_e_aadhaar_dob(self) -> dict:
        result = {"E-Aadhaar DOB": "", "Coordinates": []}
        try:
            # Extract DOB and its Coordinates
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
                self.logger.error("| DOB not found in E-Aadhaar document")
                return result
            # Update the result
            for i in dob_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.80 * width), i[3]])
            result = {
                "E-Aadhaar DOB": dob,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar DOB: {e}")
            return result
    
    # Method to extarct E-Aadhaar Gender and its Coordinates
    def _extract_e_aadhaar_gender(self) -> dict:
        result = {"E-Aadhaar Gender": "", "Coordinates": []}
        try:
            # Extract Gender and its Coordinates
            gender = ""
            gender_list = []
            coordinates = []

            # Gender Pattern: Male, Female
            gender_pattern = [
                r"\b\w*(male|female|femalp|femere|mate|femala|fenate|mala|mate|femate|#femste|fomale|fertale|malo|femsle|fade|ferme|famate)\b"
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
                self.logger.error("| Gender not found in E-Aadhaar document")
                return result
            
            # Split the gender text
            gender_list = gender.split()
            
            # Remove '/' from gender_list if present
            if '/' in gender_list:
                gender_list.remove('/')

            # Get the coordinates
            for x1, y1, x2, y2,text in self.coordinates:
                if text in gender_list:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])
                    # Check if the length of gender_list is equal to coordinates list
                    if len(gender_list) == len(coordinates):
                        break

            # Update the result
            result = {
                "E-Aadhaar Gender": gender,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar Gender: {e}")
            return result

    # Method to extract E-Aadhaar Address and its Coordinates
    def _extract_e_aadhaar_address(self) -> dict:
        result = {"E-Aadhaar Address": "", "Coordinates": []}
        try:
            address = ""
            coordinates = []
            ignore_keyword_regex = r"\b\w*(?:electronica.ly|electronically|sitrongs|elactronically.generated|generated)\b"

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Loop throgh list of places
                for place in self.places:
                    # Check if the text matches the place
                    if re.search(place, text, flags=re.IGNORECASE):
                        # Check if the text matches the ignore keyword regex
                        if not re.search(ignore_keyword_regex, text, flags=re.IGNORECASE):
                            address += " " + text
                            coordinates.append([x1, y1, x2, y2])

            # Check if Address is not found
            if not address:
                self.logger.error("| Address not found in E-Aadhaar document")
                return result
            
            # Update the result
            result = {
                "E-Aadhaar Address": address,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar Address: {e}")
            return result
    
    # Method to extract E-Aadhaar Pincode and its Coordinates
    def _extract_e_aadhaar_pincode(self) -> dict:
        result = {"E-Aadhaar Pincode": "", "Coordinates": []}
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
                self.logger.error("| Pincode not found in E-Aadhaar document")
                return result
            
            # Update the result
            for i in pincode_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.30 * width), i[3]])

            result = {
                "E-Aadhaar Pincode": pincode,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar Pincode: {e}")
            return result
        
    # Method to extract E-Aadhaar Mobile number and its Coordinates
    def _extract_e_aadhaar_mobile(self) -> dict:
        result = {"E-Aadhaar Mobile": "", "Coordinates": []}
        try:
            mobile = ""
            mobile_coordinates = []
            coordinates = []
            width = 0

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text length is 10 or 11
                if len(text) in (10,11) and text[:10].isdigit():
                    mobile = text
                    mobile_coordinates.append([x1, y1, x2, y2])
                
            # Check if Mobile is not found
            if not mobile:
                self.logger.error("| Mobile number not found in E-Aadhaar document")
                return result
            
            # Update result
            for i in mobile_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.54 * width), i[3]])

            result = {
                "E-Aadhaar Mobile": mobile,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar Mobile: {e}")
            return result
    
    # Method to extract E-Aadhaar QR-Codes and its Coordinates
    def _extract_e_aadhaar_qr_codes(self) -> list:
        result = {"E-Aadhaar QRCodes": "", "Coordinates": []}
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
                self.logger.error("| QR Codes not found in E-Aadhaar document")
                return result
            
            # Get the 50% of QR Codes
            for qr in qrcodes:
                x1, y1, x2, y2 = qr['bbox_xyxy']
                qrcodes_coordinates.append([int(round(x1)), int(round(y1)), int(round(x2)), (int(round(y1)) + int(round(y2))) // 2])

            # Update result
            result = {
                "E-Aadhaar QRCodes": f"Found {len(qrcodes_coordinates)} QR Code",
                "Coordinates": qrcodes_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting E-Aadhaar QRCodes: {e}")
            return result
    
    # Method remove duplicate list of coordinates
    def _remove_duplicate_coordinates(self, coordinates: list) -> list:
        new_data = []
        for item in coordinates:
            seen = set()
            unique_coords = []
            for coord in item['Coordinates']:
                coord_tuple = tuple(coord)
                if coord_tuple not in seen:
                    unique_coords.append(coord)
                    seen.add(coord_tuple)
            item['Coordinates'] = unique_coords
            new_data.append(item)
        return new_data
    
    # Method to collect document information
    def collect_document_info(self) -> list:
        document_info_list = []
        try:
            if self.redaction_level == 1:
                # Collect E-Aadhaar Name
                e_aadhaar_name = self._extract_e_aadhaar_name()
                document_info_list.append(e_aadhaar_name)

                # Collect E-Aadhaar Number
                e_aadhaar_number = self._extract_e_aadhaar_number()
                document_info_list.append(e_aadhaar_number)

                # Collect E-Aadhaar DOB
                e_aadhaar_dob = self._extract_e_aadhaar_dob()
                document_info_list.append(e_aadhaar_dob)

                # Collect E-Aadhaar Gender
                e_aadhaar_gender = self._extract_e_aadhaar_gender()
                document_info_list.append(e_aadhaar_gender)

                # Collect E-Aadhaar Address
                e_aadhaar_address = self._extract_e_aadhaar_address()
                document_info_list.append(e_aadhaar_address)

                # Collect E-Aadhaar Mobile
                e_aadhaar_mobile = self._extract_e_aadhaar_mobile()
                document_info_list.append(e_aadhaar_mobile)

                # Collect E-Aadhaar Pincode
                e_aadhaar_pincode = self._extract_e_aadhaar_pincode()
                document_info_list.append(e_aadhaar_pincode)

                # Collect E-Aadhaar QR-Codes
                e_aadhaar_qrcodes = self._extract_e_aadhaar_qr_codes()
                document_info_list.append(e_aadhaar_qrcodes)

                print(f"DOCUMENT INFO LIST: {document_info_list}")
                # Check if all the dictionaries in the document_info_list are empty
                is_dictionary_empty = all(all(not v for v in d.values()) for d in document_info_list)
                if is_dictionary_empty:
                    self.logger.error("| No information found in E-Aadhaar document")
                    return {"message": "No information found in E-Aadhaar document", "status": "REJECTED"}
                else:
                    # Remove duplicate coordinates
                    updated_coordinates_data = self._remove_duplicate_coordinates(document_info_list)
                    self.logger.info("| Successfully Redacted E-Aadhaar Document Information")
                    # Return the document information list
                    return {"message": "Successfully Redacted E-Aadhaar document", "status": "REDACTED", "data": updated_coordinates_data}
            else:
                # Collect E-Aadhaar Name
                e_aadhaar_name = self._extract_e_aadhaar_name()
                if len(e_aadhaar_name['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar Name found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar Name found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_name)

                # Collect E-Aadhaar Number
                e_aadhaar_number = self._extract_e_aadhaar_number()
                if len(e_aadhaar_number['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar Number found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar Number found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_number)

                # Collect E-Aadhaar DOB
                e_aadhaar_dob = self._extract_e_aadhaar_dob()
                if len(e_aadhaar_dob['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar DOB found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar DOB found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_dob)

                # Collect E-Aadhaar Gender
                e_aadhaar_gender = self._extract_e_aadhaar_gender()
                if len(e_aadhaar_gender['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar Gender found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar Gender found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_gender)

                # Collect E-Aadhaar Address
                e_aadhaar_address = self._extract_e_aadhaar_address()
                if len(e_aadhaar_address['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar Address found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar Address found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_address)

                # Collect E-Aadhaar Mobile
                e_aadhaar_mobile = self._extract_e_aadhaar_mobile()
                if len(e_aadhaar_mobile['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar Mobile found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar Mobile found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_mobile)

                # Collect E-Aadhaar Pincode
                e_aadhaar_pincode = self._extract_e_aadhaar_pincode()
                if len(e_aadhaar_pincode['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar Pincode found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar Pincode found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_pincode)

                # Collect E-Aadhaar QR-Codes
                e_aadhaar_qrcodes = self._extract_e_aadhaar_qr_codes()
                if len(e_aadhaar_qrcodes['Coordinates']) == 0:
                    self.logger.error("| No information for E-Aadhaar QR-Codes found in E-Aadhaar document")
                    return {"message": "No information for E-Aadhaar QR-Codes found in E-Aadhaar document", "status": "REJECTED"}
                document_info_list.append(e_aadhaar_qrcodes)

                
                # Remove duplicate coordinates
                updated_coordinates_data = self._remove_duplicate_coordinates(document_info_list)
                
                # Return the document information list
                return {"message": "Successfully Redacted E-Aadhaar document", "status": "REDACTED", "data": updated_coordinates_data}
        except Exception as e:
            self.logger.error(f"| Error while collecting E-Aadhaar document information: {e}")
            return {"message": "Error in collecting E-Aadhaar Document Information", "status": "REJECTED"}