import re

class IdentifyEPancardDocument:
    def __init__(self, text_list: list, logger: object):
        # List of text blocks
        self.text_data_list = [text.strip() for text in text_list if len(text) != 0]
        
        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = [r"\b(e-pan)\b"]
    

    def check_e_pancard_document_match(self) -> bool:
        # Loop through the target patterns
        for pattern in self.targets:
            compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
            for text_block in self.text_data_list:
                # Search for pattern in the text block
                if re.search(compiled_pattern, text_block):
                    # If a match is found, return True
                    self.logger.info(f"| Found match for E-Pancard document")
                    return True
        return False