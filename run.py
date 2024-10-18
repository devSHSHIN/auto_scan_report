import os
import argparse
from dotenv import load_dotenv
from lib_scan.lib_scan_run import snyk_main
from fortify_scan.fortify_main import fortify_main


def main():
    load_dotenv()
    
    root_path = os.path.dirname(os.path.abspath(__file__))

    print("================================")
    print("|\t다음 옵션 중 입력하세요.")
    print("--------------------------------")
    #comm = input('(1)ALL (2)Fortify (3)Snyk: ')
    comm = "3"
    #pro_id = input('project_ID: ')
    pro_id = "c4ca5e62-53de-493a-8028-e903871a69fa"

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
    main()

