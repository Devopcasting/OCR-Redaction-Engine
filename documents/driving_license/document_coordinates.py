import pytesseract
import re
from PIL import Image
from qreader import QReader
from helper.text_coordinates import ImageTextCoordinates
from helper.places import places_list

class DrivingLicenseDocumentInfo:
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


    # Method to extract Driving License Number and its Coordinates
    def _extract_driving_license_number(self) -> dict:
        result = {"Driving License Number": "", "Coordinates": []}
        try:
            # Extract Driving License Number and its Coordinates
            driving_license_number = ""
            driving_license_number_coordinates = []
            
            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DLN pattern
                if len(text) == 11 and text.isdigit():
                    # Append the text and coordinates to the respective lists
                    driving_license_number += " "+ text
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in driving_license_number_coordinates:
                        driving_license_number_coordinates.append([x1, y1, x2, y2])
            
            # Check if Driving License Number is not found
            if not driving_license_number:
                self.logger.warning("| Driving License Number not found in Driving License document")
                return result
            
            # Update the result
            result = {
                "Driving License Number": driving_license_number,
                "Coordinates": driving_license_number_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Driving License Number: {e}")
            return result

    # Method to extract Driving License Dates and its Coordinates
    def _extract_driving_license_dates(self) -> dict:
        result = {"Driving License Dates": "", "Coordinates": []}
        try:
            # Extract Dates and its Coordinates
            dates = ""
            dates_coordinates = []
            coordinates = []
            width = 0
            
            # DOB Pattern: DD/MM/YYY, DD-MM-YYY, DD.MM.YYY
            dates_pattern = r'\b\d{2}/\d{2}/\d{4}|\b\d{2}/\d{5}|\b\d{2}-\d{2}-\d{4}|\b\d{4}/\d{4}|\b\d{2}/\d{2}/\d{2}|\b\d{1}/\d{2}/\d{4}|\b[Oo]?\d{1}/\d{5}|\b\d{2}\.\d{2}\.\d{4}|\b\d{4}-\d{4}\b'

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DOB pattern
                if re.match(dates_pattern, text, flags=re.IGNORECASE):
                    dates += " "+ text
                    dates_coordinates.append([x1, y1, x2, y2])
            
            # Check if Dates is not found
            if not dates:
                self.logger.warning("| Dates not found in Driving License document")
                return result
            # Update the result
            for i in dates_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.80 * width), i[3]])
            
            result = {
                "Driving License Dates": dates,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Driving License Dates: {e}")
            return result
    
    # Method to extract Driving License Names and its Coordinates
    def _extract_driving_license_names(self) -> dict:
        result = {"Driving License Names": "", "Coordinates": []}
        try:
            # Extract Names and its Coordinates
            names = ""
            names_text_list = []
            names_coordinates = []
            search_text_index = 0
            search_text = [
                r"\b\w*(name)\b"
            ]
            skip_keyword_text = [
                r"\b\w*(son|daughter|blood|blond|ae|re)\b"
            ]
            break_loop_keyword = [
                r"\b(ex|se)\b"
            ]

            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            # Filter out elements containing only digits
            filtered_text_data_list = [text for text in text_data_list if not text.isdigit()]

            print(filtered_text_data_list)
            # Loop through the filtered text data list and get the index of search text
            for index,text in enumerate(filtered_text_data_list):
                for regex in search_text:
                    if re.search(regex, text, flags=re.IGNORECASE):
                        search_text_index = index
                        break
            
            # Check if search text index is not found
            if search_text_index == 0:
                self.logger.warning("| Search text not found in Driving License document")
                return result

            # Loop through the filtered text data list starting from search text index
            for index,text in enumerate(filtered_text_data_list[search_text_index + 1 :]):
                break_match_found = False
                skip_match_found = False
                # If the text matches any break loop keyword then break the main loop.
                for pattern in break_loop_keyword:
                    if re.match(pattern, text.lower(), flags=re.IGNORECASE):
                        break_match_found = True
                        break
                
                # Cheeck if break match found
                if break_match_found:
                    break
                
                # If the text matches any skip keyword then skip that text.
                for pattern in skip_keyword_text:
                    if re.match(pattern, text.lower(), flags=re.IGNORECASE):
                        skip_match_found = True
                        break
                
                # Check if text is uppercase and not digit and no skip match found
                if text.isupper() and not text.isdigit() and not skip_match_found:
                    names += " "+ text
                    # Split and check the length of text. If length is greater than 1 then add all the elements except last
                    if len(text.split()) > 1:
                        names_text_list.extend(text.split()[:-1])
                    else:
                        names_text_list.append(text)
                    
            # Check if Names is not found
            if not names:
                self.logger.warning("| Names not found in Driving License document")
                return result

            # Get the coordinates of name text
            for x1, y1, x2, y2, text in self.coordinates:
                if text in names_text_list:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in names_coordinates:
                        names_coordinates.append([x1, y1, x2, y2])

            # Update the result
            result = {
                "Driving License Names": names,
                "Coordinates": names_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Driving License Names: {e}")
            return result
        
    # Method to extract Driving License Address and its Coordinates
    def _extract_driving_license_address(self) -> dict:
        result = {"Driving License Address": "", "Coordinates": []}
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
                self.logger.warning("| Address not found in Driving License document")
                return result
            
            # Update the result
            result = {
                "Driving License Address": address,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Driving License Address: {e}")
            return result

    # # Method to extract Driving License QR-Codes and its Coordinates
    def _extract_driving_license_qr_codes(self) -> list:
        result = {"Driving License QRCodes": "", "Coordinates": []}
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
                self.logger.warning("| QR Codes not found in Driving License document")
                return result
            
            # Get the 50% of QR Codes
            for qr in qrcodes:
                x1, y1, x2, y2 = qr['bbox_xyxy']
                qrcodes_coordinates.append([int(round(x1)), int(round(y1)), int(round(x2)), (int(round(y1)) + int(round(y2))) // 2])

            # Update result
            result = {
                "Driving License QRCodes": f"Found {len(qrcodes_coordinates)} QR Code",
                "Coordinates": qrcodes_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Driving License QRCodes: {e}")
            return result

    # Method to collect document information
    def collect_document_info(self) -> list:
        document_info_list = []
        try:
            if self.redaction_level == 1:
                # Collect Driving License Number
                driving_license_number = self._extract_driving_license_number()
                document_info_list.append(driving_license_number)

                # Collect Driving License Dates
                driving_license_dates = self._extract_driving_license_dates()
                document_info_list.append(driving_license_dates)

                # Collect Driving License Names
                driving_license_names = self._extract_driving_license_names()
                document_info_list.append(driving_license_names)

                # Collect Driving License Address
                driving_license_address = self._extract_driving_license_address()
                document_info_list.append(driving_license_address)

                # Collect Driving License QR-Codes
                driving_license_qrcodes = self._extract_driving_license_qr_codes()
                document_info_list.append(driving_license_qrcodes)

                print(document_info_list)
                # Check if all the dictionaries in the document_info_list are empty
                is_dictionary_empty = all(all(not v for v in d.values()) for d in document_info_list)
                if is_dictionary_empty:
                    self.logger.error("| No information found in Driving License document")
                    return {"message": "No information found in Driving License document", "status": "REJECTED"}
                else:
                    self.logger.info("| Successfully Redacted Driving License Document Information")
                    # Return the document information list
                    return {"message": "Successfully Redacted Driving License document", "status": "REDACTED", "data": document_info_list}
            else:
                # Collect Driving License Number
                driving_license_number = self._extract_driving_license_number()
                if len(driving_license_number['Coordinates']) == 0:
                    self.logger.error("| Driving License Number not found in Driving License document")
                    return {"message": "Driving License Number not found in Driving License document", "status": "REJECTED"}
                document_info_list.append(driving_license_number)

                # Collect Driving License Dates
                driving_license_dates = self._extract_driving_license_dates()
                if len(driving_license_dates['Coordinates']) == 0:
                    self.logger.error("| Driving License Dates not found in Driving License document")
                    return {"message": "Driving License Dates not found in Driving License document", "status": "REJECTED"}
                document_info_list.append(driving_license_dates)

                # Collect Driving License Names
                driving_license_names = self._extract_driving_license_names()
                if len(driving_license_names['Coordinates']) == 0:
                    self.logger.error("| Driving License Names not found in Driving License document")
                    return {"message": "Driving License Names not found in Driving License document", "status": "REJECTED"}
                document_info_list.append(driving_license_names)

                # Collect Driving License Address
                driving_license_address = self._extract_driving_license_address()
                if len(driving_license_address['Coordinates']) == 0:
                    self.logger.error("| Driving License Address not found in Driving License document")
                document_info_list.append(driving_license_address)

                # Collect Driving License QR-Codes
                driving_license_qrcodes = self._extract_driving_license_qr_codes()
                if len(driving_license_qrcodes['Coordinates']) == 0:
                    self.logger.error("| Driving License QR-Codes not found in Driving License document")
                document_info_list.append(driving_license_qrcodes)

                # Return the document information list
                return {"message": "Successfully Redacted Driving License document", "status": "REDACTED", "data": document_info_list}
            
        except Exception as e:
            self.logger.error(f"| Error while collecting Driving License document information: {e}")
            return {"message": "Error in collecting Driving License Document Information", "status": "REJECTED"}