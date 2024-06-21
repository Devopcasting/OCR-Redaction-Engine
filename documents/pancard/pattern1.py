import re
class PancardPattern1:
    def __init__(self, coordinate_data: list, text_data_list: list, logger: object) -> None:
        self.coordinates = coordinate_data
        self.text_data_list = text_data_list
        print(self.coordinates)
        self.logger = logger
    
    def get_names(self):
        try:
            # Skip Keywords
            skip_keywords = [
                r"\b\w*(name|uiname|mame|nun|alatar|fname|hehe|itiame)\b",
                r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
                r"\b\w*(hratlifies|facer|pacers|hratlieies|name|gather)\b"
                ]
            
            # Break Keywords
            break_keywords = [r"\b\w*(gate|auth|ory)\b"]
            
            # Start point keyword
            self.start_point_keyword = [
                r"\b(name|uiname|mame|nun|alatar|fname|hehe|itiame)\b"
                ]
            start_point_index = 0

            name = ""
            name_list = []
            coordinates = []

            # Find the start point index
            for index,text in enumerate(self.text_data_list):
                for pattern in self.start_point_keyword:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        start_point_index = index
                        break
                if start_point_index:
                    break
            
            if start_point_index == 0:
                return {"names": "", "coordinates": []}
            
            # Loop through the text data list starting from the start point index
            for index,text in enumerate(self.text_data_list[start_point_index:]):
                # Check for the break loop
                break_loop_match_found = False
                for pattern in break_keywords:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    if re.search(compiled_pattern, text):
                        break_loop_match_found = True
                        break
                # Check if break loop is matched
                if break_loop_match_found:
                    break
                # Check if text does'nt match the skip keywords
                if not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in skip_keywords):
                    name += " "+ text
            
            # Update name list
            name_list = name.strip().split()
            print(name_list)

            # Loop through the coordinates
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in name_list:
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])
                if len(coordinates) == len(name_list):
                    break
            # Check for coordinates
            if not coordinates:
                return {"names": "", "coordinates": []}
            return {"names": name.strip(), "coordinates": coordinates}
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Names: {e}")
            return {"names": name, "coordinates": []}
        