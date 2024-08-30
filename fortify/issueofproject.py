import os
import json
import requests

class SSCAPI:
    def __init__(self, ssc_url=os.getenv("SSC_URL")ㅋ):
        self.ssc = ssc_url
        self.token = None

    def set_url(self, ssc_url):
        self.ssc = ssc_url

    def load_token_from_file(self, token_file_path):
        # Load the token from the specified JSON file
        if os.path.exists(token_file_path):
            with open(token_file_path, 'r') as file:
                data = json.load(file)
                self.token = data.get('token')
                if self.token:
                    print(f"Token loaded successfully from {token_file_path}")
                else:
                    print("Token not found in the file.")
        else:
            print(f"Token file does not exist at {token_file_path}")

    def get_issues(self, parent_id, start=0, limit=-1, **kwargs):
        if not self.token:
            print("No token found. Please load a valid token first.")
            return

        # Define the endpoint URL
        url = f"{self.ssc}/api/v1/projectVersions/{parent_id}/issues"

        # Prepare the parameters for the GET request
        params = {
            "start": start,
            "limit": limit,
        }
        # Include additional parameters if provided in kwargs
        params.update(kwargs)

        # Send the GET request
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

        print(f"Sending request to {url} with params: {params}")

        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            issues = response.json()
            print("Issues retrieved successfully")
            return issues
        else:
            print(f"Failed to retrieve issues: {response.status_code} - {response.text}")
            return None

    def save_issues_to_file(self, issues, output_file_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # Save the issues to the file
        with open(output_file_path, 'w') as file:
            json.dump(issues, file, indent=4)
            print(f"Issues saved to {output_file_path}")

# Example usage
ssc_api = SSCAPI()

# Load token from file
ssc_api.load_token_from_file("/home/fortify/auto_scan_report/data/token.json")

# Retrieve issues for a specific project version (replace `parent_id` with actual ID)
issues = ssc_api.get_issues(parent_id=462, start=0, limit=10, showhidden=True, showremoved=False, showsuppressed=False)

# Save issues to a file
if issues:
    ssc_api.save_issues_to_file(issues, "/home/fortify/auto_scan_report/data/issues.json")

