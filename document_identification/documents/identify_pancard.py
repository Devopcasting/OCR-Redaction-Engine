import re

class IdentifyPancardDocument:
    def __init__(self, text_list: list, logger: object):
        # List of text blocks
        self.text_data_list = [text.strip() for text in text_list if len(text) != 0]
        print(self.text_data_list)
        
        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = [
               r"\b\w*(permarent|pefirianent|pereierent|permante|petmancnt|petraancnt|permanent|petianent|pormanent|perenent|fermanent)\b",
               r"\b\w*(incometax|incometaxdepartment|incombtaxdepartment|tincometaxdepakinent|fetax| nt number| income | tax | tak)\b",
               r"\b\w*(department|departmen|departnent)\b"
        ]

    def check_pancard_document_match(self) -> bool:
        # Loop through the target patterns
        for pattern in self.targets:
            compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
            for text_block in self.text_data_list:
                # Search for pattern in the text block
                if re.search(compiled_pattern, text_block):
                    # If a match is found, return True
                    self.logger.info(f"| Found match for Pancard document")
                    return True
        return False 