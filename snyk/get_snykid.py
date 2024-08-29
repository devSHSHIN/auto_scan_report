import argparse
from get_project_id import get_and_save_snyk_info

def main():
    parser = argparse.ArgumentParser(description="Run Snyk monitor and save project ID.")
    parser.add_argument('-p', '--path', required=True, help='Absolute path to the target directory')
    parser.add_argument('-s', '--save', default='/home/fortify/auto_scan_report/data/snyk_project_id.json', help='Path to save the JSON file')

    args = parser.parse_args()

    target_path = args.path
    save_path = args.save

    get_and_save_snyk_info(target_path, save_path)

if __name__ == "__main__":
    main()

