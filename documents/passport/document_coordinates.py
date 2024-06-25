import pytesseract
import re
from PIL import Image
from helper.text_coordinates import ImageTextCoordinates
from helper.places import places_list

class PassportDocumentInfo:
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

    
    # Method to extract Passport Number and its Coordinates
    def _extract_passport_number(self) -> dict:
        result = {"Passport Number": "", "Coordinates": []}
        try:
            # Extract Passport Number and its Coordinates
            passport_number = ""
            passport_number_coordinates = []
            
            # Lambada function
            check_passport_string = lambda s: re.match(r'^[A-Z][0-9]{7}$', s) is not None
            # Valid Number list
            valid_number_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            # Loop through the coordinates
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                all_valid_characters = any(char in valid_number_list for char in text[1:])
                if check_passport_string(text):
                    passport_number += " "+text
                    # Check if [x1, y1, x2, y2] is already appended to the list
                    if [x1, y1, x2, y2] not in passport_number_coordinates:
                        passport_number_coordinates.append([x1, y1, x2, y2])
                elif len(text) in (6,7,8) and text.isdigit():
                    passport_number += " "+text
                    # Check if [x1, y1, x2, y2] is already appended to the list
                    if [x1, y1, x2, y2] not in passport_number_coordinates:
                        passport_number_coordinates.append([x1, y1, x2, y2])
                elif len(text) in (6,9,10) and text[0].isalpha() and text[0].isupper() and all_valid_characters:
                    passport_number += " "+text
                    # Check if [x1, y1, x2, y2] is already appended to the list
                    if [x1, y1, x2, y2] not in passport_number_coordinates:
                        passport_number_coordinates.append([x1, y1, x2, y2])
                elif len(text) in (6,7,8) and text.isupper() and text.isdigit():
                    passport_number += " "+text
                    # Check if [x1, y1, x2, y2] is already appended to the list
                    if [x1, y1, x2, y2] not in passport_number_coordinates:
                        passport_number_coordinates.append([x1, y1, x2, y2])
                elif len(text) in (6,7,8) and text.isdigit():
                    passport_number += " "+text
                    # Check if [x1, y1, x2, y2] is already appended to the list
                    if [x1, y1, x2, y2] not in passport_number_coordinates:
                        passport_number_coordinates.append([x1, y1, x2, y2])
                elif len(text) in (6, 7, 8) and all_valid_characters:
                    passport_number += " "+text
                    # Check if [x1, y1, x2, y2] is already appended to the list
                    if [x1, y1, x2, y2] not in passport_number_coordinates:
                        passport_number_coordinates.append([x1, y1, x2, y2])
                    
            # Check if passport number is empty
            if not passport_number_coordinates:
                self.logger.warning("| Passport Number not found in Passport document")
                return result
            # Update the result
            result = {
                "Passport Number": passport_number,
                "Coordinates": passport_number_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"Error occurred while extracting passport number: {e}")
            return result
    
    # Method to extract Names and its coordinates
    def _extract_names(self) -> dict:
        result = {"Passport Names": "", "Coordinates": []}
        try:
            # Extract Names and its coordinates
            passport_names = ""
            passport_names_list = []
            passport_names_coordinates = []
            coordinates = []

            # Get the text from data list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]
            print(f"TEXT DATA LIST: {text_data_list}")
            # Surname keyword regex
            surname_keyword_regex = [r"\b\w*(surname|sermnemes|somame|sungme|semane|suname|surmame|sumama|sumame|ssurmame|weesenet|canam|sumsme|senane|surnane|sarnome)\b"]
            # Surname keyword index
            surname_keyword_index = 0
            # Break loop keywords
            break_loop_keyword_regex = [r"\b(walionaiity|attonallty|nekiopalty|arsgiaen|natonaity|nationality|sex|sax|danga|st|indian)\b"]
            break_loop_keyword_match_found = False
            # Date pattern to skip
            skip_date_pattern = [r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}']
            # Skip keyword regex
            skip_keyword_regex = [r"\b(given|name|give|seen|nee|ot|attonallty|walionaiity|fauna|ama|nameis|amet|rear|nat|feast|ss|a|of|pat|ast|fa|ers|iee|oe|in|ait|beat)\b",
                                  r"\b(cee|ae|ane|vt|ROME|UDORRETIECOM|NAly|meh|L|ae|be|ere|x||ae|ee|Sh|senmies|ae|oS|mee|gies|cuenvermeias|VA|TOG|Be|ae|ISOIA|sen| ‘wha|tens|Ge|wale|is|Cn|wei|as|ie|cssmaeall)\b",
                                  r"(=|-|//\\|~|/|)"]
            # Redaction width
            width = 0

            # Find the index of surname keyword
            for index,text in enumerate(text_data_list):
                for pattern in surname_keyword_regex:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        surname_keyword_index = index
                        break
            print(f"SURNAME INDEX: {surname_keyword_index}")
            # Check if surname keyword index is not found
            if surname_keyword_index == 0:
                self.logger.warning("| Surname keyword not found in Passport document")
                return result
            
            # Lambada function
            contains_no_numbers = lambda text: not bool(re.search(r'\d', text))            
            for index,text in enumerate(text_data_list[surname_keyword_index + 1:]):
                # Check if the text matches the break loop keyword
                for pattern in break_loop_keyword_regex:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        print(f"BREAK : {text}")
                        break_loop_keyword_match_found = True
                        break
                if break_loop_keyword_match_found:
                    break
                
                # Check if the text matches the date pattern keyword
                for pattern in skip_date_pattern:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        break_loop_keyword_match_found = True
                        break
                if break_loop_keyword_match_found:
                    break
                
                # Check if the text does'nt match the skip keyword
                if not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in skip_keyword_regex) and contains_no_numbers(text):
                    print(text)
                    passport_names += " "+text

            # Split the passport names
            passport_names_list = passport_names.split()

            # Get the coordinates of the passport names
            for x1,y1,x2,y2,text in self.coordinates:
                if text in passport_names_list:
                    if [x1, y1, x2, y2] not in passport_names_coordinates:
                        passport_names_coordinates.append([x1,y1,x2,y2])
            
            # Update the result
            for i in passport_names_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])

            result = {
                "Passport Names": passport_names,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error occurred while extracting names from Passport Document: {e}")
            return result
    
    # Method to extract Dates and its coordinates
    def _extract_dates(self) -> dict:
        result = {"Passport Dates": [], "Coordinates": []}
        try:
            # Extract Dates and its coordinates
            passport_dates = ""
            passport_dates_coordinates = []
            coordinates = []
            width = 0
            date_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}'

            # Loop through the coordinates
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                # Check if the text is a date in the format DD/MM/YYYY
                if re.search(date_pattern, text, flags=re.IGNORECASE):
                    passport_dates += " "+text
                    passport_dates_coordinates.append([x1, y1, x2, y2])

            # Check if dates is empty
            if not passport_dates_coordinates:
                self.logger.warning("| Dates not found in Passport document")
                return result
            
            for i in passport_dates_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])
            # Update the result
            result = {
                "Passport Dates": passport_dates,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error occurred while extracting dates from Passport Document: {e}")
            return result
    
    # Method to extract Passport Address and its coordinates
    def _extract_passport_address(self) -> dict:
        result = {"Passport Address": "", "Coordinates": []}
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
            
            # Loop through the coordinates again to find the pincode
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if the text is a valid pincode number
                if len(text) == 6 and text.isdigit():
                    address += " " + text
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])

            # Check if Address is not found
            if not address:
                self.logger.error("| Address not found in Passport document")
                return result
            
            # Update the result
            result = {
                "Passport Address": address,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Passport Address: {e}")
            return result
    
    
    # Function to check if a string contains at least one '<' and other characters or numbers
    def contains_less_than_and_others(self, symbol_string: str):
        return '<' in symbol_string and any(char != '<' for char in symbol_string)
    
    # Method to extract information from '<' symbol
    def _extract_less_than_symbol(self) -> dict:
        result = {"Passport Arrow": "<", "Coordinates": []}
        try:
            name_with_arrow = ""
            name_with_arrow_coordinates = []

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if the text contains '<' with other characters or numbers
                if self.contains_less_than_and_others(text):
                    name_with_arrow += " " + text
                    name_with_arrow_coordinates.append([x1, y1, x2, y2])

            # Check if less than symbol is not found
            if not name_with_arrow_coordinates:
                self.logger.warning("| Less than symbol not found in Passport document")
                return result

            # Update the result
            result = {
                "Passport Arrow": name_with_arrow,
                "Coordinates": name_with_arrow_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Less than Symbol: {e}")
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
                # Collect Passport Number
                passport_number = self._extract_passport_number()
                document_info_list.append(passport_number)

                # Collect Passport Names
                passport_names = self._extract_names()
                document_info_list.append(passport_names)

                # Collect Passport Dates
                passport_dob = self._extract_dates()
                document_info_list.append(passport_dob)

                # Collect Passport Arrow
                passport_arrow = self._extract_less_than_symbol()
                document_info_list.append(passport_arrow)

                # Collect Passport Address
                passport_address = self._extract_passport_address()
                document_info_list.append(passport_address)

                print(document_info_list)

                # Check if all the dictionaries in the document_info_list are empty
                is_dictionary_empty = all(all(not v for v in d.values()) for d in document_info_list)
                if is_dictionary_empty:
                    self.logger.error("| No information found in Passport document")
                    return {"message": "No information found in Passport document", "status": "REJECTED"}
                else:
                    # Remove duplicate coordinates
                    updated_coordinates_data = self._remove_duplicate_coordinates(document_info_list)
                    self.logger.info("| Successfully Redacted Passport Document Information")
                    # Return the document information list
                    return {"message": "Successfully Redacted Passport document", "status": "REDACTED", "data": updated_coordinates_data}
            else:
                # Collect Passport Number
                passport_number = self._extract_passport_number()
                if len(passport_number['Coordinates']) == 0:
                    self.logger.error("| No information for Passport Number found in Passport document")
                    return {"message": "No information for Passport Number found in Passport document", "status": "REJECTED"}
                document_info_list.append(passport_number)

                # Collect Passport Names
                passport_names = self._extract_names()
                if len(passport_names['Coordinates']) == 0:
                    self.logger.error("| No information for Passport Names found in Passport document")
                    return {"message": "No information for Passport Names found in Passport document", "status": "REJECTED"}
                document_info_list.append(passport_names)
                
                # Collect Passport Dates
                passport_dob = self._extract_dates()
                if len(passport_dob['Coordinates']) == 0:
                    self.logger.error("| No information for Passport DOB found in Passport document")
                else:
                    document_info_list.append(passport_dob)
                
                # Collect Passport Arrow
                passport_arrow = self._extract_less_than_symbol()
                if len(passport_arrow['Coordinates']) == 0:
                    self.logger.error("| No information for Passport Arrow found in Passport document")
                else:
                    document_info_list.append(passport_arrow)

                # Collect Passport Address
                passport_address = self._extract_passport_address()
                if len(passport_address['Coordinates']) == 0:
                    self.logger.error("| No information for Passport Address found in Passport document")
                else:
                    document_info_list.append(passport_address)

                # Remove duplicate coordinates
                updated_coordinates_data = self._remove_duplicate_coordinates(document_info_list)
                
                # Return the document information list
                return {"message": "Successfully Redacted Passport document", "status": "REDACTED", "data": updated_coordinates_data}
        except Exception as e:
            self.logger.error(f"| Error while collecting Passport document information: {e}")
            return {"message": "Error in collecting Passport Document Information", "status": "REJECTED"}