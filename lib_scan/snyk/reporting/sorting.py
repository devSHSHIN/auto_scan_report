import json
import pandas as pd

# 우선 순위에 따른 심각도 수준
severity_order = ['critical', 'high', 'medium', 'low']
output_file_path = '/Users/pc09164/auto_scan_report/data/sorted_snyk_issues.json'

def sort_json_by_severity(input_file_path):
    # JSON 데이터 로드
    with open(input_file_path, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    # 각 pkgName 내에서 심각도에 따라 이슈를 정렬하는 함수
    def sort_issues_by_severity(issues):
        return sorted(issues, key=lambda x: severity_order.index(x['issueData']['severity']))

    def sort_deps_vuln(vuln_data):
        """
        deps_vuln_y 또는 deps_vuln_n에 대해 정렬 수행
        """
        # pandas로 처리하기 쉽게 데이터를 평탄화
        flattened_data = []
        for pkg_name, issues in vuln_data.items():
            for issue in issues:
                flattened_data.append({
                    'pkgName': pkg_name,
                    'severity': issue['issueData']['severity']
                })

        # 평탄화된 데이터를 pandas DataFrame으로 변환
        df = pd.DataFrame(flattened_data)

        # severity_order에 기반한 심각도 점수 생성
        df['severity_score'] = df['severity'].apply(lambda x: severity_order.index(x))

        # 1단계: 각 pkgName 내에서 심각도에 따라 이슈 정렬
        for pkg_name, issues in vuln_data.items():
            vuln_data[pkg_name] = sort_issues_by_severity(issues)

        # 2단계: pkgName별로 각 심각도의 수를 세기 (올림픽 스타일 정렬)
        severity_counts = df.groupby('pkgName')['severity'].value_counts().unstack(fill_value=0)

        # 3단계: critical > high > medium > low의 수에 따라 정렬하고, 동점일 경우 pkgName 알파벳 순으로 정렬
        severity_counts = severity_counts.reindex(severity_order, axis=1, fill_value=0)
        sorted_pkg_names = severity_counts.sort_values(
            by=['critical', 'high', 'medium', 'low'], 
            ascending=[False, False, False, False]
        ).index

        # 정렬된 결과를 리스트에 저장
        return {pkg_name: vuln_data[pkg_name] for pkg_name in sorted_pkg_names}

    # deps_vuln_y와 deps_vuln_n에 대해 각각 정렬 수행
    if 'deps_vuln_y' in data:
        data['deps_vuln_y'] = sort_deps_vuln(data['deps_vuln_y'])

    if 'deps_vuln_n' in data:
        data['deps_vuln_n'] = sort_deps_vuln(data['deps_vuln_n'])

    # 정렬된 데이터를 JSON 형식으로 다시 저장
    with open(output_file_path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, indent=4)

    print(f"정렬된 데이터가 {output_file_path}에 저장되었습니다.")

    return output_file_path
