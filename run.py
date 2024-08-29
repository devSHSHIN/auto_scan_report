import os
import sys
import argparse
from snyk.snyk_main import snyk_main


def main(pro_id):
    root_path = os.path.dirname(os.path.abspath(__file__))

    print("================================")
    print("|\t다음 옵션 중 입력하세요.")
    print("--------------------------------")
    #    comm = input('(1)ALL (2)Fortify (3)Snyk')
    comm = "3"

    match comm:
        case "1":
            return
        case "2":
            return
        case "3":
            snyk_main(root_path, pro_id)
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Snyk script with a specified project ID.")
    parser.add_argument("pro_id", type=str, help="The project ID to be used in the Snyk API call.")

    args = parser.parse_args()
    pro_id = args.pro_id
    main(pro_id)
