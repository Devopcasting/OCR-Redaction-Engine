import re

class IdentifyDrivingLicenseDocument:
    def __init__(self, text_list: list, logger: object) -> None:
        # List of text blocks
        self.text_list = text_list
        #print(self.text_list)
        
        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = [
            r"\b\w*(union|driving|license|motor)\b"
        ]
    
    def check_driving_license_document_match(self) -> bool:
        # Loop through the target patterns
        for pattern in self.targets:
            compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
            for text_block in self.text_list:
                # Search for pattern in the text block
                if re.search(compiled_pattern, text_block):
                    # If a match is found, return True
                    self.logger.info(f"| Found match for Driving License document")
                    return True
        return False