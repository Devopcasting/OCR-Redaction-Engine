import re
import difflib

class IdentifyEPancardDocument:
    def __init__(self, text_list: list, logger: object):
        # List of text blocks
        self.text_list = text_list
        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = ['e-pan']
    
        # Regex patterns for approximate matching
        self.patterns = {
            'e-pan': re.compile(r'\be-pan\b', re.IGNORECASE)
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
    def check_e_pancard_document_match(self) -> bool:
        # Loop through the target strings and find the closest
        for target in self.targets:
            match = self.find_closest_match(target, self.patterns[target])
            if match:
                self.logger.info(f"| Found match for E-Pancard document")
                return True
        return False