import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class IssueCounts:
    critical: int
    high: int
    medium: int
    low: int

@dataclass
class CvssDetail:
    assigner: str
    severity: str
    cvssV3Vector: str
    cvssV3BaseScore: float
    modificationTime: str

@dataclass
class IssueData:
    id: str
    title: str
    severity: str
    url: str
    exploitMaturity: str
    description: Optional[str]
    identifiers: Dict[str, List[str]]
    credit: List[str]
    semver: Dict[str, List[str]]
    publicationTime: str
    disclosureTime: str
    CVSSv3: str
    cvssScore: Optional[float]
    cvssDetails: List[CvssDetail]
    language: str
    patches: List[Any]
    nearestFixedInVersion: str
    ignoreReasons: Optional[Any]

@dataclass
class FixInfo:
    isUpgradable: bool
    isPinnable: bool
    isPatchable: bool
    isFixable: bool
    isPartiallyFixable: bool
    nearestFixedInVersion: str
    fixedIn: List[str]

@dataclass
class PriorityFactor:
    name: str
    description: str

@dataclass
class Priority:
    score: int
    factors: List[PriorityFactor]

@dataclass
class AggregatedIssue:
    id: str
    issueType: str
    pkgName: str
    pkgVersions: List[str]
    issueData: IssueData
    isPatched: bool
    isIgnored: bool
    fixInfo: FixInfo
    introducedThrough: Optional[Any]
    ignoreReasons: Optional[Any]
    priorityScore: Optional[int]
    priority: Priority

def refactor_severity(severity):
    severity_dict = {
        "critical": severity.critical,
        "high": severity.high,
        "medium": severity.medium,
        "low": severity.low,
    }
    return severity_dict

def refactor_issues(issue_set):
    deps_vuln_y = defaultdict(list)
    deps_vuln_n = defaultdict(list)
    deps_license = defaultdict(list)

    for issue in issue_set.issues:
        pkg_ver = issue.pkgVersions
        if len(pkg_ver) == 1:
            pkg_ver = pkg_ver[0]

        issue_dict = {
            "id": issue.id,
            "issueType": issue.issueType,
            "pkgName": issue.pkgName,
            "pkgVersions": pkg_ver,
            "issueData": asdict(issue.issueData),
            "isPatched": issue.isPatched,
            "isIgnored": issue.isIgnored,
            "fixInfo": asdict(issue.fixInfo),
            "introducedThrough": issue.introducedThrough,
            "ignoreReasons": issue.ignoreReasons,
            "priorityScore": issue.priorityScore,
            "priority": issue.priority,
        }
        if issue.issueType == "vuln":
            if issue.fixInfo.fixedIn:
                deps_vuln_y[issue.pkgName].append(issue_dict)
            else:
                deps_vuln_n[issue.pkgName].append(issue_dict)
        else:
            deps_license[issue.pkgName].append(issue_dict)
    return deps_vuln_y, deps_vuln_n, deps_license

def save_data(data, root_path):
    with open(f"{root_path}/data/snyk_issues.json", "w", encoding='UTF-8') as f:
        json.dump(data, f, indent=4)

def filter_over_high(data):
    over_high_data = [
        x for x in data if x["issueData"]["severity"] in ["critical", "high"]
    ]
    return over_high_data

def call_issues(client, org_id, pro_id, root_path):
    issue_set = client.organizations.get(org_id).projects.get(pro_id)

    severity = refactor_severity(issue_set.issueCountsBySeverity)
    #    over_high_severity = refactor_severity(issue_set.filter['severity' in ['critical', 'high']].issueCountsBySeverity)
    deps_vuln_y, deps_vuln_n, deps_license = refactor_issues(
        issue_set.issueset_aggregated.all()
    )
    #    over_high_deps_vuln_y = filter_over_high(deps_vuln_y)
    #    over_high_deps_vuln_n = filter_over_high(deps_vuln_n)
    deps_issues = {
        "severity_cnt": severity,
        "deps_vuln_y": deps_vuln_y,
        "deps_vuln_n": deps_vuln_n,
        "deps_license": deps_license,
    }

    save_data(deps_issues, root_path)
    return f"{root_path}/data/snyk_issues.json"

