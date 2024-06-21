import re

class IdentifyEAadhaarDocument:
    def __init__(self, text_list: list, logger: object) -> None:
        # List of text blocks
        self.text_list = text_list
        print(self.text_list)

        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = [
            r"\b\w*(enrollment|enrolment|ehrolimanttle|encolent|enroiiment|enrotment|encol ent no|enroliment|enrolment|enrotiment|/enrolment|enrotimant|enrallment|evavenrolment|eivavenrolment|ehyollment|enrollmentno)\b",
            r"\b\w*(This ts electronica ly generated letter|Aadhaar is valid throughout the country|Aadhaar is a proof of identity  not  OF citizenship|This is electronically  generated|This is elactronically generated lettar)\b"
        ]
    
    def check_e_aadhaar_document_match(self) -> bool:
        # Loop through the target patterns
        for pattern in self.targets:
            compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
            for text_block in self.text_list:
                # Search for pattern in the text block
                if re.search(compiled_pattern, text_block):
                    # If a match is found, return True
                    self.logger.info(f"| Found match for E-Aadhaar document")
                    return True
        return False