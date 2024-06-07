import re
import difflib

class IdentifyCDSLDocument:
    def __init__(self, text_list: list, logger: object):
        # List of text blocks
        self.text_list = text_list
        
        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = ['cdsl', 'kyc', 'ventures', "cdse", "kra"]
    
        # Regex patterns for approximate matching
        self.patterns = {
            'cdsl': re.compile(r'\bcdsl\b', re.IGNORECASE),
            'kyc': re.compile(r'\bkyc\b', re.IGNORECASE),
            'ventures': re.compile(r'\bventures\b', re.IGNORECASE),
            'cdse': re.compile(r'\bcdse\b', re.IGNORECASE),
            'kra': re.compile(r'\bkra\b', re.IGNORECASE)
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
    def check_cdsl_document_match(self) -> bool:
        # Loop through the target strings and find the closest
        for target in self.targets:
            match = self.find_closest_match(target, self.patterns[target])
            if match:
                self.logger.info(f"| Found match for CDSL document")
                return True
        return False