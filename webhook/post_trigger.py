"""
    WebhookPostTrigger class to trigger a POST request to a specified webhook URL with provided payload data.

    Attributes:
        url (str): The base URL to which the POST request will be sent.
        payload_data (dict): The payload data to be included in the POST request body.

    Methods:
        send_post() -> bool:
            Sends a POST request to the specified URL with the payload data.
            Returns True if the request is successful (status code 200), otherwise False.
"""

import json
import requests

class WebhookPostTrigger:
    def __init__(self, url, payload_data: dict) -> None:
        self.url = url
        self.payload_data = payload_data
    
    def send_post(self) -> bool:
        """
        Sends a POST request to the webhook URL with the payload data.

        Returns:
            bool: True if the POST request is successful (status code 200), False otherwise.
        """
        url = f"{self.url}/CVCore/processstatus"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(self.payload_data) ,headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
