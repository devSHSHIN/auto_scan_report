import os
import re
import json
import pandas as pd
from datetime import datetime
from packaging.version import Version, InvalidVersion

################################################################################

index = 1

def del_ml_issues(data):

    if 'severity_cnt' in data:
        del data['severity_cnt']

    if 'deps_license' in data:
        del data['deps_license']

    deps_vuln_y = data.get("deps_vuln_y", {})
    deps_vuln_n = data.get("deps_vuln_n", {})

    # 패키지별로 취약점 데이터를 처리
    for pkg_name, vulns in list(deps_vuln_y.items()):
        # DataFrame으로 변환
        df = pd.json_normalize(vulns)

        # 'issueData.severity' 값이 "medium" 또는 "low"가 아닌 항목들만 필터링
        filtered_df = df[~df['issueData.severity'].isin(['medium', 'low'])]

        # 필터링 후 남은 데이터가 있으면 다시 리스트로 변환하여 저장
        if not filtered_df.empty:
            deps_vuln_y[pkg_name] = filtered_df.to_dict(orient="records")
        else:
            # 남은 데이터가 없으면 해당 패키지를 제거
            del deps_vuln_y[pkg_name]

    # 패키지별로 취약점 데이터를 처리
    for pkg_name, vulns in list(deps_vuln_n.items()):
        # DataFrame으로 변환
        df = pd.json_normalize(vulns)

        # 'issueData.severity' 값이 "medium" 또는 "low"가 아닌 항목들만 필터링
        filtered_df = df[~df['issueData.severity'].isin(['medium', 'low'])]

        # 필터링 후 남은 데이터가 있으면 다시 리스트로 변환하여 저장
        if not filtered_df.empty:
            deps_vuln_n[pkg_name] = filtered_df.to_dict(orient="records")
        else:
            # 남은 데이터가 없으면 해당 패키지를 제거
            del deps_vuln_n[pkg_name]
    
    output_file_path = '/Users/pc09164/auto_scan_report/data/del_ml_issues.json'
    with open(output_file_path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, indent=4)

    # 처리된 데이터를 반환
    return data

################################################################################

def get_latest_fixed_version(issues):
    all_versions = []

    # 모든 이슈에서 fixInfo.fixedIn 버전들을 추출
    for issue in issues:
        fixed_in_versions = issue.get('fixInfo.fixedIn')
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
    global index
    processed_data = []
    current_date = datetime.now().strftime('%Y-%m-%d')  # 현재 날짜
    
    # deps_vuln_y에서 각 pkgName에 대해 데이터를 가공
    for pkg_name, issues in data.get('deps_vuln_y', {}).items():
        if not issues:
            continue  # 이슈가 없는 경우는 건너뜀
        
        first_issue = issues[0]
        
        # latest_version 함수 호출
        latest_version = get_latest_fixed_version(issues)

        # 각 항목을 리스트로 구성
        processed_row = [
            index,
            "",     #플랫폼 구분 [Ex. API WEB ...]
            first_issue.get('issueData.title'),
            "",     #점검결과 [취약(Red)]
            current_date,
            "",     #이행 점검 결과 [1행 -]            first_issue.get('issueData.severity'),
            first_issue.get('issueData.severity'),
            pkg_name,
            first_issue.get('pkgVersions'),
            latest_version,
            len(issues) - 1,
            "",
            "",
            "",
            "",
        ]
        
        # 리스트에 추가
        processed_data.append(processed_row)
        index += 1
    
    return processed_data

################################################################################

def process_deps_vuln_n(data):
    """
    deps_vuln_n 데이터를 가공하여 엑셀에 사용할 리스트로 변환
    :param data: JSON 데이터에서 로드한 deps_vuln_n 데이터를 포함하는 딕셔너리
    :return: 가공된 리스트 (엑셀 파일로 변환하기 위해 사용)
    """
    global index
    processed_data = []
    current_date = datetime.now().strftime('%Y-%m-%d')  # 현재 날짜

    # deps_vuln_n 데이터를 확인하여 이슈가 있는지 확인
    issues = data.get('deps_vuln_n', [])
    if not issues or len(issues) == 0:
        return processed_data  # 이슈가 없으면 처리하지 않음
    
       # 첫 번째 키를 가져와 그 값을 처리 (next(iter())를 사용하여 첫 번째 키를 가져옴)
    first_key = next(iter(issues))
    first_issue_list = issues[first_key]
    
    if len(first_issue_list) == 0:
        return processed_data  # 첫 번째 이슈 리스트가 비어 있을 경우 처리하지 않음
    
    first_issue = first_issue_list[0]  # 첫 번째 이슈 가져오기
    other_issues = sum(len(vuln_list) for vuln_list in issues.values()) - 1  # 전체 이슈 수 계산 (첫 번째 이슈 제외)
 
    # 각 항목을 리스트로 구성 (latest_version을 사용하지 않음)
    processed_row = [
        index,
        "",     #플랫폼 구분 [Ex. API WEB ...]
        first_issue.get('issueData.title'),
        "",     #점검결과 [취약(Red)]
        current_date,
        "",     #이행 점검 결과 [1행 -]
        first_issue.get('issueData.severity'),
        first_issue.get('pkgName'),
        first_issue.get('pkgVersions'),
        other_issues,
        "",
        "",
        "",
        "",
    ]
    
    processed_data.append(processed_row)
    index += 1

    return processed_data

################################################################################

def process_all_data(input_file_path):
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_file_path}")
    
    # JSON 파일 로드
    with open(input_file_path, 'r', encoding='UTF-8') as f:
        data_tmp = json.load(f)

    data = del_ml_issues(data_tmp)

    processed_data = []
    
    processed_data.extend(process_deps_vuln_y(data))
    processed_data.extend(process_deps_vuln_n(data))

    output_file_path = '/Users/pc09164/auto_scan_report/data/to_xlsx_issues.json'
    with open(output_file_path, 'w', encoding='UTF-8') as f:
        json.dump(processed_data, f, indent=4)


    return processed_data

################################################################################
