import re

class IdentifyPassportDocument:
    def __init__(self, text_list: list, logger: object):
        # List of text blocks
        self.text_data_list = [text.strip() for text in text_list if len(text) != 0]
        print(self.text_data_list)
        # Logger object
        self.logger = logger

        # Target strings to match
        self.targets = [
            r"\b\w*(posspau|pusepart|basepent|passgert|sport|passport|jpassport|pasaport|passpon|ipassport|bissport|passoars|passportno|paeupari|paasport)\b",
            r"\b\w*(republic|overseas|citizen|given|repurlic)\b"
        ]

    def check_passport_document_match(self) -> bool:
        # Loop through the target patterns
        for pattern in self.targets:
            compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
            for text_block in self.text_data_list:
                # Search for pattern in the text block
                if re.search(compiled_pattern, text_block):
                    # If a match is found, return True
                    self.logger.info(f"| Found match for Passport document")
                    return True
        return False 