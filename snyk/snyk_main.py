import os
#import argparse
import pandas as pd
from .client import SnykClient
from .utils import get_default_token_path, get_token
from .reporting.call_api import call_issues
from .reporting.sorting import sort_json_by_severity
from .reporting.filter import process_all_data

def get_snyk_client():
    snyk_token_path = get_default_token_path()
    snyk_token = get_token(snyk_token_path)
    return SnykClient(snyk_token)


def snyk_main(root_path=".", pro_id=None):
    org_id = os.getenv("ORG_ID")
    client = get_snyk_client()
#    pro_id = "e5229c92-0989-4831-b056-251439817d2e"
    print(f"{org_id}\n{client}")
    print(f"pro_id: {pro_id}\n")

    issues = call_issues(client, org_id, pro_id, root_path)
    print(f"call issues :\t\t{issues}")
    sorted_issues = sort_json_by_severity(issues)
    print(f"sort issues :\t\t{sorted_issues}")
    processed_data = process_all_data(sorted_issues)

    return


if __name__ == "__main__":
    snyk_main()
