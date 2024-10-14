import os
import argparse
from dotenv import load_dotenv
from snyk.snyk_main import snyk_main
from fortify.fortify_main import fortify_main


def main():
    load_dotenv()
    
    root_path = os.path.dirname(os.path.abspath(__file__))

    print("================================")
    print("|\t다음 옵션 중 입력하세요.")
    print("--------------------------------")
    #comm = input('(1)ALL (2)Fortify (3)Snyk: ')
    comm = "3"
    #pro_id = input('project_ID: ')
    pro_id = "95aad894-37be-4b8f-bc57-238edfe2120e"

    match comm:
        case "1":
            fortify_main(root_path, pro_id)
            return
        case "2":
            fortify_main(root_path, pro_id)
            return
        case "3":
            snyk_main(root_path, pro_id)
            return


if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description="Run Snyk script with a specified project ID.")
    #parser.add_argument("pro_id", type=str, help="The project ID to be used in the Snyk API call.")

    #args = parser.parse_args()
    #pro_id = args.pro_id
    main()
