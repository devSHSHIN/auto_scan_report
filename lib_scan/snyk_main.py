import os
import pandas as pd
from .snyk.client import SnykClient
from .snyk.utils import get_default_token_path, get_token
from .snyk.reporting.call_api import call_issues
from .snyk.reporting.sorting import sort_json_by_severity
from .snyk.reporting.filter import process_all_data
from .snyk.reporting.write_log import data_to_log
from .snyk.reporting.create_xlsx import create_xlsx

def get_snyk_client():
    snyk_token_path = get_default_token_path()
    snyk_token = get_token(snyk_token_path)
    return SnykClient(snyk_token)


def snyk_main(root_path=".", pro_id=None):
    org_id = os.getenv("ORG_ID")
    client = get_snyk_client()
    print(f"{org_id}\n{client}")
    print(f"pro_id: {pro_id}\n")

    issues = call_issues(client, org_id, pro_id, root_path)
    sorted_issues = sort_json_by_severity(issues)
    processed_data = process_all_data(sorted_issues)
    log_txt = data_to_log(sorted_issues)
    xlsx_path = create_xlsx("/Users/pc09164/auto_scan_report/data/to_xlsx_issues.json", "/Users/pc09164/auto_scan_report/data/to_xlsx_log.txt")

    return

if __name__ == "__main__":
    snyk_main()

