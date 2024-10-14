import json

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def filter_and_simplify_issues(issues):
    """Filter and simplify issues based on severity."""
    if not issues:
        return None

    filtered_issues = [
        {
            "title": issue["issueData"]["title"],
            "severity": issue["issueData"]["severity"],
            "pkgName": issue["pkgName"],
            "pkgVersions": issue["pkgVersions"],
            "fixedIn": issue["fixInfo"]["fixedIn"][-1] if issue["fixInfo"]["fixedIn"] else None
        }
        for issue in issues
        if issue["issueType"] == "vuln" and issue["issueData"]["severity"] in ["critical", "high"]
    ]

    if filtered_issues:
        result = filtered_issues[0]
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

def filter_issues(issues):
    """Filter issues based on severity."""
    return [
        issue
        for issue in issues
        if issue["issueType"] == "vuln" and issue["issueData"]["severity"] in ["critical", "high"]
    ]

def process_data(input_file_path, output_file_path, simplified=True):
    """Process the data and save filtered and/or simplified issues."""
    data = load_json(input_file_path)

    filtered_data = {
        "severity_cnt": data["severity_cnt"],
        "deps_vuln_y": {},
        "deps_vuln_n": {},
    }

    for package, issues in data.get("deps_vuln_y", {}).items():
        if simplified:
            simplified_issue = filter_and_simplify_issues(issues)
            if simplified_issue:
                filtered_data["deps_vuln_y"][package] = simplified_issue
        else:
            filtered_issues = filter_issues(issues)
            if filtered_issues:
                filtered_data["deps_vuln_y"][package] = filtered_issues

    for package, issues in data.get("deps_vuln_n", {}).items():
        if simplified:
            simplified_issue = filter_and_simplify_issues(issues)
            if simplified_issue:
                filtered_data["deps_vuln_n"][package] = simplified_issue
        else:
            filtered_issues = filter_issues(issues)
            if filtered_issues:
                filtered_data["deps_vuln_n"][package] = filtered_issues

    save_json(filtered_data, output_file_path)
    print(f"Filtered and processed data has been saved to {output_file_path}")

