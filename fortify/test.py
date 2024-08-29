import json
import requests
import pandas as pd

class SSCAPI:
    def __init__(self, ssc_url="https://ssc.skplanet.com/ssc"):
        self.ssc = ssc_url
        self.session = requests.Session()

    def login(self, username, password):
        # 로그인 URL
        login_url = f"{self.ssc}/j_spring_security_check"
        login_data = {
            'j_username': username,
            'j_password': password
        }

        # 로그인 요청
        login_response = self.session.post(login_url, data=login_data, allow_redirects=True)

        # 로그인 성공 여부 확인
        if login_response.status_code == 200 or login_response.status_code == 302:
            print("Login successful")
            return True
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return False

    def get_issues(self, parent_id, start=0, limit=-1, **kwargs):
        if not self.session:
            print("No session found. Please login first.")
            return

        # URL 수정
        url = f"{self.ssc}/api/v1/projectVersions/{parent_id}/issues"

        params = {
            "start": start,
            "limit": limit,
        }
        params.update(kwargs)

        response = self.session.get(url, params=params)

        if response.status_code == 200:
            print("Issues retrieved successfully")
            return response.json()
        else:
            print(f"Failed to retrieve issues: {response.status_code} - {response.text}")
            return None

    def filter_critical_exploitable_issues(self, issues):
        # JSON 데이터를 DataFrame으로 변환
        df = pd.DataFrame(issues['data'])

        # 필터링 조건: 'friority'가 'Critical'이고 'primaryTag'가 'Exploitable'
        filtered_df = df[(df['friority'] == 'Critical') & (df['primaryTag'] == 'Exploitable')]

        # _href 값을 생성된 URL로 대체
        filtered_df['_href'] = filtered_df.apply(self.generate_url, axis=1)

        return filtered_df

    def generate_url(self, issue):
        base_url = "https://ssc.skplanet.com/ssc/html/ssc/version"
        project_version_id = issue['projectVersionId']
        issue_instance_id = issue['issueInstanceId']
        engine_type = issue['engineType']

        generated_url = (
            f"{base_url}/{project_version_id}/audit"
            f"?q=%5Binstance%20id%5D%3A{issue_instance_id}%20%5Banalysis%20type%5D%3A{engine_type}"
            f"&filterset=a243b195-0a59-3f8b-1403-d55b7a7d78e6"
            f"&groupingtype=CBDCF842-8040-403E-8303-F3043BCAC9C3"
            f"&orderby=friority&issue={issue_instance_id}&enginetype={engine_type}&viewTab=code"
        )

        return generated_url

# Example usage
ssc_api = SSCAPI()

# 로그인 정보 설정
username = "pc09164"
password = "SPths0080<<"

# 로그인 시도
if ssc_api.login(username, password):
    # 로그인 성공 시, 프로젝트 버전 이슈 가져오기
    issues = ssc_api.get_issues(parent_id=464, start=0, limit=999999, showhidden=False, showremoved=False, showsuppressed=False)

    if issues:
        # 가져온 이슈 중 필터링
        critical_exploitable_issues = ssc_api.filter_critical_exploitable_issues(issues)

        # 필터링된 이슈 출력
        if not critical_exploitable_issues.empty:
            print(json.dumps(critical_exploitable_issues.to_dict(orient="records"), indent=4))
        else:
            print("No issues found with the specified filters.")


"""
import json
import requests
import pandas as pd

class SSCAPI:
    def __init__(self, ssc_url="https://ssc.skplanet.com/ssc"):
        self.ssc = ssc_url
        self.session = requests.Session()

    def login(self, username, password):
        # 로그인 URL
        login_url = f"{self.ssc}/j_spring_security_check"
        login_data = {
            'j_username': username,
            'j_password': password
        }

        # 로그인 요청
        login_response = self.session.post(login_url, data=login_data, allow_redirects=True)

        # 로그인 성공 여부 확인
        if login_response.status_code == 200 or login_response.status_code == 302:
            print("Login successful")
            return True
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return False

    def get_issues(self, parent_id, start=0, limit=-1, **kwargs):
        if not self.session:
            print("No session found. Please login first.")
            return

        # URL 수정
        url = f"{self.ssc}/api/v1/projectVersions/{parent_id}/issues"

        params = {
            "start": start,
            "limit": limit,
        }
        params.update(kwargs)

        response = self.session.get(url, params=params)

        if response.status_code == 200:
            print("Issues retrieved successfully")
            return response.json()
        else:
            print(f"Failed to retrieve issues: {response.status_code} - {response.text}")
            return None

    def filter_critical_exploitable_issues(self, issues):
        # JSON 데이터를 DataFrame으로 변환
        df = pd.DataFrame(issues['data'])

#        print(f'test\n{json.dumps(issues, indent=4)}')

        # 필터링 조건: 'friority'가 'Critical'이고 'primaryTag'가 'Exploitable'
        filtered_df = df[(df['friority'] == 'Critical') & (df['primaryTag'] == 'Exploitable')]

        return filtered_df

# Example usage
ssc_api = SSCAPI()

# 로그인 정보 설정
username = "pc09164"
password = "SPths0080<<"

# 로그인 시도
if ssc_api.login(username, password):
    # 로그인 성공 시, 프로젝트 버전 이슈 가져오기
    issues = ssc_api.get_issues(parent_id=457, start=0, limit=999999, showhidden=False, showremoved=False, showsuppressed=False)

#    print(f'{json.dumps(issues, indent=4)}')

    if issues:
        # 가져온 이슈 중 필터링
        critical_exploitable_issues = ssc_api.filter_critical_exploitable_issues(issues)
        
        # 필터링된 이슈 출력
        if not critical_exploitable_issues.empty:
            print(f'{json.dumps(critical_exploitable_issues.to_dict(orient="records"), indent=4)}')
        else:
            print("No issues found with the specified filters.")

"""
