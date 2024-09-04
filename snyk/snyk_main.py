import os
import argparse
import pandas as pd
from .client import SnykClient
from .call_api import call_issues
from .latest_version import latest_version
from .utils import get_default_token_path, get_token
from .snyk_over_high import process_data
#from .snyk_log import process_data_from_file

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


    input_file_path = "/Users/pc09164/auto_scan_report/data/snyk_issues.json"
    output_file_path = "/Users/pc09164/auto_scan_report/data/snyk_high_issues.json"

    process_data(input_file_path, output_file_path, simplified=True)

#    process_data_from_file()

    return


if __name__ == "__main__":
    snyk_main()

