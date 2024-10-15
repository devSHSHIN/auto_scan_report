import os
import re
import json
import pandas as pd
from datetime import datetime
from packaging.version import Version, InvalidVersion

################################################################################

index = 1

def del_license_issues(data):

    if 'severity_cnt' in data:
        del data['severity_cnt']

    if 'deps_license' in data:
        del data['deps_license']

    # 처리된 데이터를 반환
    return data

################################################################################

def get_latest_fixed_version(issues):
    all_versions = []

    for issue in issues:
        fixed_in_versions = issue.get('fixInfo', {}).get('fixedIn', [])
        if fixed_in_versions:  # fixed_in_versions가 None이 아닌지 확인
            all_versions.extend(fixed_in_versions)

    if not all_versions:
        return None  # 버전 정보가 없는 경우 None 반환
    
    standard_versions = []
    non_standard_versions = []

    for version_str in all_versions:
        try:
            # 표준 형식인 경우 packaging.version을 사용
            standard_versions.append(Version(version_str))
        except InvalidVersion:
            # 비표준 버전 형식은 별도로 처리
            non_standard_versions.append(version_str)

    # 표준 형식 최신 버전 선택
    latest_standard = max(standard_versions, default=None)

    # 비표준 버전 처리 (숫자 부분을 추출하여 비교)
    def loose_compare(v):
        if isinstance(v, str):
            return [int(x) for x in re.findall(r'\d+', v)]
        elif isinstance(v, Version):
            return [int(part) for part in v.release]
        return []

    if latest_standard and non_standard_versions:
        # 표준 버전과 비표준 버전 비교 (각각의 최신 값 비교)
        latest_non_standard = max(non_standard_versions, key=loose_compare)
        return str(max([latest_standard, latest_non_standard], key=loose_compare))
    elif latest_standard:
        return str(latest_standard)
    elif non_standard_versions:
        return max(non_standard_versions, key=loose_compare)
    else:
        return None

################################################################################

def process_deps_vuln_y(data):
    processed_data = []

    processed_data.append("Issues to fix by upgrading:\n")
    
    for pkg_name, issues in data.get('deps_vuln_y', {}).items():
        if not issues:
            continue
        
        first_issue = issues[0]
        latest_version = get_latest_fixed_version(issues)
     
        processed_data.append(
            f"\n\tUpgrade {pkg_name}@{first_issue.get('pkgVersions')} to {pkg_name}@{latest_version} to fix\n"
        )

        for issue in issues:
            issue_title = issue.get('issueData', {}).get('title', 'Unknown issue')
            severity = issue.get('issueData', {}).get('severity', 'Unknown').capitalize()
            issue_url = issue.get('issueData', {}).get('url', 'Unknown URL')
            fixed_in = issue.get('fixInfo', {}).get('fixedIn')[0]
            pkg_versions = issue.get('pkgVersions', 'unknown')

            processed_data.append(
                f"\t✗\t{issue_title} [{severity} Severity][{issue_url}] in {pkg_name}@{fixed_in}\n"
                f"\t\tintroduced by {pkg_name}@{pkg_versions} > {pkg_name}@{fixed_in}\n"
            )
        
    return ''.join(processed_data)

################################################################################

def process_deps_vuln_n(data):
    processed_data = []

    processed_data.append("\n\nIssues with no direct upgrade or patch:\n\n")

    for pkg_name, issues in data.get('deps_vuln_n', {}).items():
        if not issues:
            continue
        
        for issue in issues:
            issue_title = issue.get('issueData', {}).get('title', 'Unknown issue')
            severity = issue.get('issueData', {}).get('severity', 'Unknown').capitalize()
            issue_url = issue.get('issueData', {}).get('url', 'Unknown URL')
            pkg_versions = issue.get('pkgVersions', 'unknown')

            processed_data.append(
                f"\t✗\t{issue_title} [{severity} Severity][{issue_url}] in {pkg_name}@{issue.get('pkgVersions')}\n"
                f"\t\tNo upgrade or patch available\n"
            )
        
    return ''.join(processed_data)

################################################################################

def data_to_log(input_file_path):
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_file_path}")
    
    with open(input_file_path, 'r', encoding='UTF-8') as f:
        data_tmp = json.load(f)
    
    data = del_license_issues(data_tmp)
    log_txt = process_deps_vuln_y(data)
    log_txt += process_deps_vuln_n(data)

    output_file_path = '/Users/pc09164/auto_scan_report/data/to_xlsx_log.txt'
    with open(output_file_path, 'w', encoding='UTF-8') as f:
        f.write(log_txt)

    return log_txt

################################################################################
