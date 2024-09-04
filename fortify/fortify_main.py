import os
import requests
import json

def login(ssc_url):
    username = os.getenv("SSC_USERNAME")
    password = os.getenv("SSC_PASSWORD")

    if not username or not password:
        print("Error: SSC_USERNAME and SSC_PASSWORD environment variables must be set.")
        return None

    login_url = f"{ssc_url}/j_spring_security_check"
    login_data = {
        'j_username': username,
        'j_password': password
    }

    session = requests.Session()

    try:
        login_response = session.post(login_url, data=login_data, allow_redirects=True)
        login_response.raise_for_status()

        if login_response.status_code in [200, 302]:
            print("Login successful")
            return session
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during login: {str(e)}")
        return None

def get_issues(session, ssc_url, parent_id, start=0, limit=-1, **kwargs):
    if not session:
        print("No session found. Please login first.")
        return None

    url = f"{ssc_url}/api/v1/projectVersions/{parent_id}/issues"

    params = {
        "start": start,
        "limit": limit,
    }
    params.update(kwargs)

    try:
        response = session.get(url, params=params)
        response.raise_for_status()

        print("Issues retrieved successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve issues: {str(e)}")
        return None

def filter_issues(issues):
    if not issues or 'data' not in issues:
        return None

    def split_issue_name(issue_name):
        parts = issue_name.split(": ", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        else:
            return parts[0].strip(), ""  # 중분류만 존재하는 경우 소분류는 빈 값으로

    filtered_issues = [
        {
            "ID": issue["id"],
            "SERVICE": issue.get("projectName", ""),
            "SSC_VERSION": issue.get("projectVersionName", ""),
            "PRIORITY": issue.get("friority", ""),
            "MAJOR_CATEGORY": issue.get("kingdom"),  # API Abuse를 약자로 변환
            "MIDDLE_CATEGORY": split_issue_name(issue.get("issueName", ""))[0],  # issueName에서 : 앞부분
            "SUB_CATEGORY": split_issue_name(issue.get("issueName", ""))[1],  # issueName에서 : 뒷부분
            "FILE": issue.get("fullFileName", ""),
            "PKG": "",  # PKG 필드가 명시되지 않았으므로 비워둠
            "CLASS": issue.get("primaryLocation", "").split(".")[0] if issue.get("primaryLocation") else "",
            "FUNCTION": "",  # FUNCTION 필드가 명시되지 않았으므로 비워둠
            "LINE": issue.get("lineNumber", ""),
            "HYPERLINK": issue.get("_href", "")
        }
        for issue in issues['data']
        if issue.get("friority") == "Critical" and issue.get("primaryTag") == "Exploitable"
    ]
    return filtered_issues

def save_issues_to_file(issues, result_file_path):
    try:
        with open(os.path.join(result_file_path, "fortify_audited.json"), 'w') as outfile:
            json.dump(issues, outfile, indent=4)
        print(f"Issues saved to {os.path.join(result_file_path, 'fortify_audited.json')}")
    except Exception as e:
        print(f"An error occurred while saving the file: {str(e)}")

def fortify_main(root_path=".", pro_id=None):
    ssc_url = os.getenv("SSC_SERVER_URL")
    result_file_path = os.path.expandvars(os.getenv("RESULT_FILE_PATH"))

    session = login(ssc_url)
    if session:
        issues = get_issues(session, ssc_url, parent_id=pro_id, start=0, limit=-1, showhidden=False, showremoved=False, showsuppressed=False)

        if issues:
            filtered_issues = filter_issues(issues)
            save_issues_to_file(filtered_issues, result_file_path)
        else:
            print("No issues were retrieved.")

if __name__ == "__main__":
    fortify_main()
