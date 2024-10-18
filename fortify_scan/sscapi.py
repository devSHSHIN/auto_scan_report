import requests
import json
from datetime import datetime
import os

class SSCAPI:
    def __init__(self, ssc_url="https://ssc.skplanet.com/ssc"):
        self.ssc = ssc_url
        self.token = None

    def set_url(self, ssc_url):
        self.ssc = ssc_url

    def create_token(self, token_type):
        # create date with time for Token description
        formatted_date = datetime.now().strftime("%d-%m-%Y-%H:%M:%S")

        # create body in JSON format
        body = {
            "description": formatted_date,
            "type": token_type
        }

        # get SSC credentials to create token
        ssc_auth = Auth()

        # API request to create Token
        response = requests.post(
            f"{self.ssc}/api/v1/tokens",
            auth=(ssc_auth.get_username(), ssc_auth.get_password()),
            headers={
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "application/json"
            },
            data=json.dumps(body)
        )

        if response.status_code == 201:
            self.token = response.json()['data']['token']
            print(f"{token_type} successfully created: {self.token}")

            # Save token to file
            self.save_token_to_file()
        else:
            print(f"Failed to create token: {response.status_code} - {response.text}")

    def save_token_to_file(self):
        # Define the path where the token will be saved
        token_file_path = "/home/fortify/auto_scan_report/data/token.json"
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
        
        # Save the token to the file, overwriting if it exists
        with open(token_file_path, 'w') as token_file:
            json.dump({"token": self.token}, token_file)
            print(f"Token saved to {token_file_path}")

class Auth:
    def get_username(self):
        # return the username for SSC
        return "pc09164"

    def get_password(self):
        # return the password for SSC
        return "SPths0080<<"

ssc_api = SSCAPI()
ssc_api.create_token("UnifiedLoginToken")

