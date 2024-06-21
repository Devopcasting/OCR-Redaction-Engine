import re
class PancardPattern2:
    def __init__(self, coordinate_data: list, text_data_list: list, logger: object) -> None:
        self.coordinates = coordinate_data
        self.text_data_list = text_data_list
        print(self.text_data_list)
        self.logger = logger
    
    def get_names(self):
        try:
            # Skip keywords
            skip_keywords = [r"\b\w*(sizer|feat|ana|uae|income|tax|department|departmen|indi|my|arg|fears|india|[0-9])\b",
                        r"\b\w*(govt|goty|sree|feast|ofl|goyt|os|xe|ar|umdi|es|set|oe|oome|iid|fetax|incometaxdepartment|tincome|of|si|ali|[0-9])\b",
                        r"\b\w*(pras|ta|ag|oreax|fart|mic|ncome|are|art|we|gove|tere|sittex|[0-9])\b"
            ]
            # Break keywords
            break_keywords = [r"\b\w*(permanent|petmancnt|account|number|ermanent|ask|managers)\b"]

            # Date Pattern
            date_pattern = [r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}']
            #date_pattern = [r'(?:(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d))|(?:(?:19\d\d|20\d\d)[-/.](?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12][0-9]|3[01]))|(?:(?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d))|(?:(?:19\d\d|20\d\d)[-/]\d{3})']

            name = ""
            coordinates = []

            # Loop through the coordinates
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                # Check for the break loop
                break_loop_match_found = False
                for pattern in break_keywords:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    if re.search(compiled_pattern, text):
                        break_loop_match_found = True
                        print(f"BREAK: {text}")
                        break
                # Check if break loop is matched
                if break_loop_match_found:
                    break
                # Check if text does'nt match the skip keywords and date patterns
                if not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in skip_keywords) and not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in date_pattern) and len(text) > 1 and text.isupper():
                    name += text + " "
                    coordinates.append([x1, y1, x2, y2])
            
            # Check for coordinates
            if not coordinates:
                return {"names": "", "coordinates": []}
            return {"names": name, "coordinates": coordinates}
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Names: {e}")
            return {"names": name, "coordinates": []}