from collections import defaultdict
from dataclasses import is_dataclass, asdict
from typing import List, Dict, Any, Optional
import pandas as pd

def refactor_severity(severity):
    severity_dict = {
        "critical": severity.critical,
        "high": severity.high,
        "medium": severity.medium,
        "low": severity.low,
    }
    return severity_dict

def refactor_issues(issue_set):
    issues_data = []

    for issue in issue_set.issues:
        pkg_ver = issue.pkgVersions[0] if len(issue.pkgVersions) == 1 else issue.pkgVersions

        # Check if issue.priority is a dataclass instance before using asdict
        priority_data = asdict(issue.priority) if is_dataclass(issue.priority) else issue.priority

        issue_dict = {
            "id": issue.id,
            "issueType": issue.issueType,
            "pkgName": issue.pkgName,
            "pkgVersions": pkg_ver,
            "severity": issue.issueData.severity,
            "isPatched": issue.isPatched,
            "isIgnored": issue.isIgnored,
            "fixInfo": asdict(issue.fixInfo),
            "introducedThrough": issue.introducedThrough,
            "ignoreReasons": issue.ignoreReasons,
            "priorityScore": issue.priorityScore,
            "priority": priority_data,
        }
        issues_data.append(issue_dict)
    
    df_issues = pd.DataFrame(issues_data)

    # Filter for vulnerabilities with and without fixes
    deps_vuln_y = df_issues[df_issues["fixInfo"].apply(lambda x: bool(x['fixedIn']))]
    deps_vuln_n = df_issues[(df_issues["issueType"] == "vuln") & (df_issues["fixInfo"].apply(lambda x: not x['fixedIn']))]
    deps_license = df_issues[df_issues["issueType"] != "vuln"]
    
    return deps_vuln_y, deps_vuln_n, deps_license

def save_data(data, root_path):
    # Save data as JSON using pandas' built-in to_json function
    data.to_json(f"{root_path}/snyk_issues_test.json", orient="records", indent=4)

def filter_over_high(df_issues):
    # Use pandas filtering for critical or high severity issues
    return df_issues[df_issues["severity"].isin(["critical", "high"])]

def call_issues_test(client, org_id, pro_id, root_path):
    # Retrieve issues from the client API
    issue_set = client.organizations.get(org_id).projects.get(pro_id)

    # Refactor severity count into a dictionary
    severity = refactor_severity(issue_set.issueCountsBySeverity)

    # Process the issues and store them in a DataFrame
    deps_vuln_y, deps_vuln_n, deps_license = refactor_issues(issue_set.issueset_aggregated.all())
    
    # Prepare the issue data for saving
    deps_issues = {
        "severity_cnt": severity,
        "deps_vuln_y": deps_vuln_y.to_dict(orient="records"),
        "deps_vuln_n": deps_vuln_n.to_dict(orient="records"),
        "deps_license": deps_license.to_dict(orient="records"),
    }

    # Save the processed issue data to a JSON file
    save_data(pd.DataFrame(deps_issues), root_path)

    return deps_issues
