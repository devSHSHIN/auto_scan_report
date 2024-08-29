import json
from openpyxl import Workbook


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

def to_xlsx():
    wb = Workbook()
    ws = wb.active


    wb.save("/home/fortify/auto_scan_report/data/report/test.xlsx")
