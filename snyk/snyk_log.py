import json  # json 모듈 임포트
import os  # 경로 관련 모듈

# ANSI 색상 코드 설정 (더 강렬한 색상 차이를 위해 설정)
COLOR_RESET = "\033[0m"
# 연한 색상
COLOR_LIGHT_PURPLE = "\033[38;5;219m"  # 연한 보라색 (Critical)
COLOR_LIGHT_RED = "\033[38;5;210m"     # 연한 빨간색 (High)
COLOR_LIGHT_YELLOW = "\033[38;5;229m"  # 연한 노란색 (Medium)
COLOR_LIGHT_GRAY = "\033[38;5;250m"    # 연한 회색 (Low)
# 진한 색상
COLOR_BOLD_PURPLE = "\033[38;5;93m"    # 진한 보라색 (Critical)
COLOR_BOLD_RED = "\033[38;5;196m"      # 진한 빨간색 (High)
COLOR_BOLD_YELLOW = "\033[38;5;220m"   # 진한 노란색 (Medium)
COLOR_BOLD_GRAY = "\033[38;5;240m"     # 진한 회색 (Low)

# 심각도에 따른 연한 색상 반환 함수
def get_light_severity_color(severity):
    if severity == "critical":
        return COLOR_LIGHT_PURPLE
    elif severity == "high":
        return COLOR_LIGHT_RED
    elif severity == "medium":
        return COLOR_LIGHT_YELLOW
    elif severity == "low":
        return COLOR_LIGHT_GRAY
    else:
        return COLOR_RESET

# 심각도에 따른 진한 색상 반환 함수
def get_bold_severity_color(severity):
    if severity == "critical":
        return COLOR_BOLD_PURPLE
    elif severity == "high":
        return COLOR_BOLD_RED
    elif severity == "medium":
        return COLOR_BOLD_YELLOW
    elif severity == "low":
        return COLOR_BOLD_GRAY
    else:
        return COLOR_RESET

def process_data_from_file(file_path):
    # JSON 파일을 읽어오기
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = []
    header_printed = False

    for pkg_name, issues in data.get('deps_vuln_y', {}).items():
        upgrade_msgs = []
        first_issue = issues[0]  # 첫 번째 이슈를 기준으로 요약 생성
        fixed_in_versions = first_issue['fixInfo']['fixedIn'] if 'fixInfo' in first_issue else []
        last_fixed_version = fixed_in_versions[-1] if fixed_in_versions else None
        pkg_versions = first_issue.get('pkgVersions', 'unknown')  # 현재 버전

        # 블럭 앞에 요약 추가
        if last_fixed_version:
            summary_msg = f"Upgrade {pkg_name}@{pkg_versions} to {pkg_name}@{last_fixed_version} to fix"
        else:
            summary_msg = f"No upgrade or patch available for {pkg_name}@{pkg_versions}"

        # 공백 한 줄 추가하여 패키지 간 구분
        if result:
            result.append("\n")
        
        result.append(summary_msg)  # 블럭 요약을 첫 줄로 추가

        for issue in issues:
            severity = issue['issueData']['severity']
            if severity in ['low', 'license']:
                continue

            # 연한 색상과 진한 색상 적용
            light_severity_color = get_light_severity_color(severity)
            bold_severity_color = get_bold_severity_color(severity)
            severity_text = f"{bold_severity_color}[{severity.capitalize()} Severity]{COLOR_RESET}"

            url = issue['issueData']['url'].replace("https://snyk.io", "https://security.snyk.io")
            pkg_versions = issue.get('pkgVersions', 'unknown')  # pkgVersions는 이제 최상위 필드에서 가져옴

            msg = f"{light_severity_color}  ✗ {issue['issueData']['title']} {severity_text} [{url}] in {pkg_name}@{pkg_versions}\n"
            msg += f"    introduced by {pkg_name}@{pkg_versions}{COLOR_RESET}"

            upgrade_msgs.append(msg)

        if upgrade_msgs:
            result.append(f"\n{upgrade_msgs[0]}")
            if len(upgrade_msgs) > 1:
                result.extend(upgrade_msgs[1:])

    for pkg_name, issues in data.get('deps_vuln_n', {}).items():
        for issue in issues:
            severity = issue['issueData']['severity']
            if severity in ['low', 'license']:
                continue

            # 연한 색상과 진한 색상 적용
            light_severity_color = get_light_severity_color(severity)
            bold_severity_color = get_bold_severity_color(severity)
            severity_text = f"{bold_severity_color}[{severity.capitalize()} Severity]{COLOR_RESET}"

            url = issue['issueData']['url'].replace("https://snyk.io", "https://security.snyk.io")
            pkg_versions = issue.get('pkgVersions', 'unknown')  # pkgVersions는 이제 최상위 필드에서 가져옴

            msg = f"{light_severity_color}  ✗ {issue['issueData']['title']} {severity_text} [{url}] in {pkg_name}@{pkg_versions}\n"
            msg += f"    introduced by {pkg_name}@{pkg_versions}\n  No upgrade or patch available{COLOR_RESET}"

            if result:
                result.append("\n")

            result.append(f"Issues with no direct upgrade or patch:\n{msg}")

    return "\n".join(result)

# JSON 파일 경로 입력
#file_path = '/Users/pc09164/auto_scan_report/data/snyk_issues.json'
file_path = '/Users/pc09164/auto_scan_report/data/issues.json'

# 결과를 파일로 저장하는 함수
def save_output_to_file(output, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

# 결과를 처리
output = process_data_from_file(file_path)

# 저장할 파일 경로 생성
home_dir = os.path.expanduser("~")
output_file_path = os.path.join(home_dir, 'auto_scan_report/data/snyk_log.txt')  # 확장자는 .txt로 설정

# 결과를 파일에 저장
save_output_to_file(output, output_file_path)

print(f"Results have been saved to {output_file_path}")

