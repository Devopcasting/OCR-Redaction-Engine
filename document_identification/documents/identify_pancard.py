import re
import difflib

class IdentifyPancardDocument:
    def __init__(self, text_list: list, logger: object):
        # List of text blocks
        self.text_list = text_list
        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = ["permarent","pefirianent", "pereierent",
                        "petmancnt", "petraancnt", "incometax", "department", 
                        "permanent", "petianent", "incometaxdepartment", "incombtaxdepartment", 
                        "pormanent", "perenent", "tincometaxdepakinent", "fetax", 
                        "departmen", "nt number"]
    
        # Regex patterns for approximate matching
        self.patterns = {
            'permarent': re.compile(r'\bpermarent\b', re.IGNORECASE),
            'pefirianent': re.compile(r'\bpefirianent\b', re.IGNORECASE),
            'pereierent': re.compile(r'\bpereierent\b', re.IGNORECASE),
            'petmancnt': re.compile(r'\bpetmancnt\b', re.IGNORECASE),
            'petraancnt': re.compile(r'\bpetraancnt\b', re.IGNORECASE),
            'incometax': re.compile(r'\bincometax\b', re.IGNORECASE),
            'department': re.compile(r'\bdepartment\b', re.IGNORECASE),
            'permanent': re.compile(r'\bpermanent\b', re.IGNORECASE),
            'petianent': re.compile(r'\bpetianent\b', re.IGNORECASE),
            'incometaxdepartment': re.compile(r'\bincometaxdepartment\b', re.IGNORECASE),
            'incombtaxdepartment': re.compile(r'\bincombtaxdepartment\b', re.IGNORECASE),
            'pormanent': re.compile(r'\bpormanent\b', re.IGNORECASE),
            'perenent': re.compile(r'\bperenent\b', re.IGNORECASE),
            'tincometaxdepakinent': re.compile(r'\btincometaxdepakinent\b', re.IGNORECASE),
            'fetax': re.compile(r'\bfetax\b', re.IGNORECASE),
            'departmen': re.compile(r'\bdepartmen\b', re.IGNORECASE),
            'nt number': re.compile(r'\bnt number\b', re.IGNORECASE)
        }
    
    # Function to filter strings based on regex and find the closest match
    def find_closest_match(self, target, pattern):
        # Filter strings that match the pattern
        filtered_list = [s for s in self.text_list if pattern.search(s)]
        # Use difflib to find the closest match from the filtered list
        if filtered_list:
            closest_match = difflib.get_close_matches(target, filtered_list, n=1, cutoff=0.1)
            return closest_match[0] if closest_match else None
        return None
    
    # Function to check for matches and return True if found, otherwise False
    def check_pancard_document_match(self) -> bool:
        # Loop through the target strings and find the closest
        for target in self.targets:
            match = self.find_closest_match(target, self.patterns[target])
            if match:
                self.logger.info(f"| Found match for Pancard document")
                return True
        return False