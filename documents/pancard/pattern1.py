import re
class PancardPattern1:
    def __init__(self, coordinate_data: list, text_data_list: list, logger: object) -> None:
        self.coordinates = coordinate_data
        self.text_data_list = text_data_list
        self.logger = logger
        self.target_text = [
            r"\b(name|uiname|mame|nun|alatar|fname|hehe|itiame)\b"
            ]
        self.break_loop_keyword = [
            r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
            r"\b\w*(hratlifies|facer|pacers|hratlieies|name)\b"
            ]

        self.target_text_for_father = [
            r"\b\w*(father['']s|father|eather['']s|fathar['']s|fathers|ffatugr|ffatubr['']s)\b",
            r"\b\w*(hratlifies|facer|pacers|hratlieies)\b"
            ]
        self.break_loop_keyword_for_father = [
            r"\b\w*(date|birth|brth|bit|ate|fh|hn)\b",
            r"\b\w*(&|da)\b"
            ]
        
    def _get_name_keyword_index(self, target_text_data) -> int:
        """
        Get the index of the name keyword in the text data list.
        """
        try:
            # Index of name keyword
            name_keyword_index = 0
            # Loop through the target text patterns
            for pattern in target_text_data:
                compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                # Loop through the text data list
                for index, text in enumerate(self.text_data_list):
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        name_keyword_index = index
                        break
            return name_keyword_index
        except Exception as e:
            self.logger.error(f"| Error in getting name keyword index: {e}")
            return 0
    
    def get_client_name(self) -> dict:
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

            # Get the index of the name keyword
            name_keyword_index = self._get_name_keyword_index(self.target_text)
        
            # Check if name keyword index is 0
            if name_keyword_index == 0:
                self.logger.info("| Client name keyword not found")
                return {"client_name": "", "coordinate": []}
        
            # Flag to indicate if a match has been found for breaking the loop
            match_found = False
        
            # Loop through the text data list starting from next index number of name_keyword_index
            for index, text in enumerate(self.text_data_list[name_keyword_index + 1:]):
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

                # Check if text is uppercase
                if text.isupper():
                    client_name = text
                    client_name_list = text.split()

            # Get the client name from the list
            if not client_name_list:
                return {"client_name": "", "coordinate": []}
        
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

    def get_client_father_name(self) -> dict:
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

            # Skip name list
            skip_name_list = [r"\b\w*(an)\b"]
            
            # Get the index of the name keyword
            father_name_keyword_index = self._get_name_keyword_index(self.target_text_for_father)

            # Check if name keyword index is 0
            if father_name_keyword_index == 0:
                self.logger.info("| Client name keyword not found")
                return {"client_father_name": "", "coordinate": []}
            
            # Flag to indicate if a match has been found
            match_found = False

            # Loop through the text data list starting from next index number of name_keyword_index
            for index, text in enumerate(self.text_data_list[father_name_keyword_index + 1:]):
                skip_match_found = False
                # Loop through the break loop keyword patterns
                for pattern in self.break_loop_keyword_for_father:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        match_found = True
                        break
                # Check if a match has been found
                if match_found:
                    break

                # Loop through the skip name list
                for pattern in skip_name_list:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        skip_match_found = True
                        break

                # Check if text is uppercase and no skip name match is found
                if text.isupper() and not skip_match_found:
                    client_father_name = text
                    client_father_name_list = text.split()
                    break
            
            if not client_father_name_list:
                return {"client_father_name": "", "coordinate": []}
            
            # Check the length of the client father name list
            if len(client_father_name_list) > 1:
                client_father_name_list = client_father_name_list[:-1]
            # Get the coordinates of the Client Father name
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in client_father_name_list:
                    # Check if coordinates are not available in the list
                    if [x1, y1, x2, y2] not in result:
                        result.append([x1, y1, x2, y2])
            return  {"client_father_name": client_father_name, "coordinate": result}
        except Exception as e:
            self.logger.error(f"| Error in getting client father name: {e}")
            return {"client_father_name": "", "coordinate": []}