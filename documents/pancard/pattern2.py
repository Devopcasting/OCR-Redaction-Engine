import re
class PancardPattern2:
    def __init__(self, coordinate_data: list, text_data_list: list, logger: object) -> None:
        self.coordinates = coordinate_data
        self.text_data_list = text_data_list
        self.logger = logger
        self.target_text = [
            r"\b\w*(govtof inde|goyt of unpia|of india|govt. of india|govt.|income|tax|department)\b",
            r"\b\w*(incometax|incometaxdepartment|incombtaxdepartment|tincometaxdepakinent|fetax| nt number| income | tax | tak| income tax departnent)\b",
            r"\b\w*(department|departmen|departnent)\b"
            ]
        self.break_loop_keyword = [r"\b\w*(are|4d)\b"]
    
    def _get_name_keyword_index(self) -> int:
        """
        Get the index of the name keyword in the text data list.
        """
        try:
            # Index of name keyword
            name_keyword_index = 0
            # Loop through the target text patterns
            for pattern in self.target_text:
                compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                # Loop through the text data list
                for index, text in enumerate(self.text_data_list):
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        name_keyword_index = index
                        break
            return name_keyword_index
        except Exception as e:
            self.logger.error(f"| Error in _get_name_keyword_index: {e}")
            return 0
    
    def get_client_name(self) -> str:
        """
        Get the client name from the text data list.
        """
        try:
            # Client name in string
            client_name = ""
            
            # Client name in list
            client_name_list = []
            
            # List of Coordinates
            result = []
            
            # Skip some keywords
            skip_keywords = [r"\b\w*(govt|india)\b"]
            
            # Get the index of the name keyword
            name_keyword_index = self._get_name_keyword_index()
            print(name_keyword_index)
            # Check if name keyword index is 0
            if name_keyword_index == 0:
                self.logger.info("| Client name keyword not found")
                return {"client_name": "", "coordinate": []}
        
            # Flag to indicate if a match has been found for breaking the loop
            match_found = False
        
            # Loop through the text data list starting from next index number of name_keyword_index
            for index, text in enumerate(self.text_data_list[name_keyword_index + 1:]):
                skip_keyword_found = False
                # Loop through the break loop keyword patterns
                for pattern in self.break_loop_keyword:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        match_found = True
                        break
                # Check if a match has been found for breaking the loop
                if match_found:
                    break

                # Loop through the skip keyword patterns
                for pattern in skip_keywords:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        skip_keyword_found = True
                        break
                # Check if text is uppercase and no skip keywords are found
                if text.isupper() and not skip_keyword_found:
                    client_name = text
                    break
            
            # Get the client name
            if not client_name:
                return {"client_name": "", "coordinate": []}
        
            # Split the client name
            client_name_list = client_name.split()

            # Check the length of the client name list
            if len(client_name_list) > 1:
                client_name_list = client_name_list[:-1]
        
            # Get the coordinates of the Client Name
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in client_name_list:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in result:
                        result.append([x1, y1, x2, y2])
            return {"client_name": client_name, "coordinate": result}
        except Exception as e:
            self.logger.error(f"| Error in getting client name: {e}")
            return {"client_name": "", "coordinate": []}
    
    def get_client_father_name(self):
        """
        Get the client father name from the text data list.
        """
        try:
            # Client father name in string
            client_father_name = ""
            
            # Client father name in list
            client_father_name_list = []
            
            # List of Coordinates
            result = []
            
            # Create reverse list of text data list
            reverse_text_data_list = self.text_data_list[::-1]
            print(reverse_text_data_list)
            # Date Pattern Label
            date_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}'
            date_label_pattern = [r"\b\w*(bonn|birth)\b"]
            
            # Matching keyword index
            matching_keyword_index = 0
            
            # Get the matching keyword index from date label pattern
            for index, text in enumerate(reverse_text_data_list):
                for pattern in date_label_pattern:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    if re.search(compiled_pattern, text):
                        matching_keyword_index = index
                        break
            
            # Loop through the text data list starting from next index number of matching_keyword_index
            if matching_keyword_index != 0:
                for index, text in enumerate(reverse_text_data_list[matching_keyword_index + 1:]):
                    # Check if text is uppercase
                    if text.isupper() and len(text) > 1:
                        client_father_name = text
                        break
            
            if matching_keyword_index == 0:
                # Get the matching keyword index from date pattern
                for index, text in enumerate(reverse_text_data_list):
                    compiled_pattern = re.compile(date_pattern, flags=re.IGNORECASE)
                    if re.search(compiled_pattern, text):
                        matching_keyword_index = index
                        break
            
            # Loop through the text data list starting from next index number of matching_keyword_index
            if matching_keyword_index != 0:
                for index, text in enumerate(reverse_text_data_list[matching_keyword_index + 1:]):
                    # Check if text is uppercase
                    if text.isupper() and len(text) > 1:
                        client_father_name = text
                        break
            
            # Check if matching keyword index is 0
            if matching_keyword_index == 0:
                self.logger.info("| Client father name keyword not found")
                return {"client_father_name": "", "coordinate": []}
            
            # Split the client father name
            client_father_name_list = client_father_name.split()
            # Check the length of the client father name list
            if len(client_father_name_list) > 1:
                client_father_name_list = client_father_name_list[:-1]
            # Get the coordinates of the Client Father Name
            for index, (x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in client_father_name_list:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in result:
                        result.append([x1, y1, x2, y2])
            return {"client_father_name": client_father_name, "coordinate": result}
        except Exception as e:
            self.logger.error(f"| Error in getting client father name: {e}")
            return {"client_father_name": "", "coordinate": []}
