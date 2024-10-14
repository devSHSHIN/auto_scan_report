def sort_severity_1st(issues):
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    return sorted(
        issues,
        key=lambda x: (
            severity_order.get(x["issueData"]["severity"], 4),
            -(x["issueData"].get("cvssScore") or 0),
            -(x.get("priorityScore") or 0),
            x["id"],
        ),
    )
