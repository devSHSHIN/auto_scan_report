import os
import json
import pandas as pd
from openpyxl import Workbook
from dotenv import load_dotenv

load_dotenv()

df = pd.read_json()

result_file_path = os.path.expandvars(os.getenv("RESULT_FILE_PATH"))
print(f"{result_file_path}")

issues_file_path = os.path.join(result_file_path, "issues.json")
over_high_issues_file_path = os.path.join(result_file_path, "over_high_issues.json")

with open(issues_file_path, "r") as f:
    data = json.load(f)


def filter_issues(issues):
    return [
        issue
        for issue in issues
        if issue["issueType"] == "vuln"
        and issue["issueData"]["severity"] in ["critical", "high"]
    ]

headers = ["ID", "SERVICE", "SSC_VERSION", "PRIORITY", "대분류", "중분류", "소분류", "FILE", "PKG", "CLASS", "FUNCTION", "LINE", "HYPERLINK"]

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

with open(over_high_issues_file_path, "w") as file:
    json.dump(filtered_data, file, indent=4)

print(f"Filtered data has been saved to {over_high_issues_file_path}")

def to_xlsx():
    wb = Workbook()

    ws = wb.active
    ws.title = "SCA_Issues"

    for col_num, header in enumerate(headers, start=2):
        ws.cell(row=2, column=col_num, value=header)

    xlsx_path = os.path.join(result_file_path, "Fortify_Report.xlsx")


    wb.save(xlsx_path)

if __name__ == "__main__":
    to_xlsx()
