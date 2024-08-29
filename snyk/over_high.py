import json

input_file_path = "/home/fortify/auto_scan_report/data/tmp/test.json"
output_file_path = "/home/fortify/auto_scan_report/data/tmp/test_over_high.json"

with open(input_file_path, "r") as f:
    data = json.load(f)

def filter_and_simplify_issues(issues):
    if not issues:
        return None
    
    filtered_issues = [
        {
            "title": issue["issueData"]["title"],
            "severity": issue["issueData"]["severity"],
            "pkgName": issue["pkgName"],
            "pkgVersions": issue["pkgVersions"],
            "fixedIn": issue["fixInfo"]["fixedIn"][-1] if issue["fixInfo"]["fixedIn"] else None  # 마지막 fixedIn 값만 포함
        }
        for issue in issues
        if issue["issueType"] == "vuln"
        and issue["issueData"]["severity"] in ["critical", "high"]
    ]

    if filtered_issues:
        # 첫 번째 문제를 선택
        result = filtered_issues[0]
        
        # 추가 문제가 존재하는 경우, 각 문제의 fixedIn 및 severity 값을 포함
        if len(filtered_issues) > 1:
            result["additional_issues"] = [
                {
                    "title": issue["title"],
                    "fixedIn": issue["fixedIn"],
                    "severity": issue["severity"]
                } for issue in filtered_issues[1:]
            ]
        
        return result

    return None

filtered_data = {
    "severity_cnt": data["severity_cnt"],
    "deps_vuln_y": {},
    "deps_vuln_n": {},
}

for package, issues in data.get("deps_vuln_y", {}).items():
    simplified_issue = filter_and_simplify_issues(issues)
    if simplified_issue:
        filtered_data["deps_vuln_y"][package] = simplified_issue

for package, issues in data.get("deps_vuln_n", {}).items():
    simplified_issue = filter_and_simplify_issues(issues)
    if simplified_issue:
        filtered_data["deps_vuln_n"][package] = simplified_issue

with open(output_file_path, "w") as file:
    json.dump(filtered_data, file, indent=4)

print(f"Filtered and simplified data has been saved to {output_file_path}")


"""
import json
import jmespath

input_file_path = "/home/fortify/auto_scan_report/data/tmp/test.json"
output_file_path = "/home/fortify/auto_scan_report/data/tmp/test_over_high.json"

with open(input_file_path, "r") as f:
    data = json.load(f)


def filter_issues(issues):
    return [
        issue
        for issue in issues
        if issue["issueType"] == "vuln"
        and issue["issueData"]["severity"] in ["critical", "high"]
    ]


filtered_data = {
    "severity_cnt": data["severity_cnt"],
    "deps_vuln_y": {},
    "deps_vuln_n": {},
}

for package, issues in data.get("deps_vuln_y", {}).items():
    filtered_issues = filter_issues(issues)
    if filtered_issues:
        filtered_data["deps_vuln_y"][package] = filtered_issues

for package, issues in data.get("deps_vuln_n", {}).items():
    filtered_issues = filter_issues(issues)
    if filtered_issues:
        filtered_data["deps_vuln_n"][package] = filtered_issues

with open(output_file_path, "w") as file:
    json.dump(filtered_data, file, indent=4)

print(f"Filtered data has been saved to {output_file_path}")
"""
