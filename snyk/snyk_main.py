import json
import argparse
import pandas as pd
from .client import SnykClient
from .utils import get_default_token_path, get_token
from .call_api import call_issues
from .latest_version import latest_version


def load_organization(root_path):
    with open(f"{root_path}/data/.config/organizations.json") as o:
        return json.load(o)


def get_snyk_client():
    snyk_token_path = get_default_token_path()
    snyk_token = get_token(snyk_token_path)
    return SnykClient(snyk_token)


def snyk_main(root_path=".", pro_id=None):
    org_id = load_organization(root_path)["id"]
    client = get_snyk_client()
#    pro_id = "e5229c92-0989-4831-b056-251439817d2e"
    print(f"{org_id}\n{client}")
    print(f"pro_id: {pro_id}\n")

    issues = call_issues(client, org_id, pro_id, root_path)
    return


if __name__ == "__main__":
    snyk_main()

