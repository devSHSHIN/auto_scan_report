import os
import sys
import subprocess
from dotenv import load_dotenv

# load_dotenv(dotenv_path='../../.env')
load_dotenv(dotenv_path='/home/pc09164/auto_scan_report/.env')

def find_fpr_file(target_path='.'):
    fpr_files = []

    for root, dirs, files in os.walk(target_path):
        for file in files:
            if file.endswith('.fpr'):
                fpr_files.append(os.path.join(root, file))

    if len(fpr_files) > 1:
        print("fpr 파일이 확인됩니다.")
        raise Exception("fpr 파일이 여러 개 있습니다. 파일을 특정하여 다시 시도하세요.")

    if len(fpr_files) == 1:
        return fpr_files[0]

    return None


def upload_ssc(ssc_id, target_path='.'):
    ssc_server_url = os.path.expandvars(os.getenv("SSC_SERVER_URL"))
    token_dir = os.path.expandvars(os.getenv("TOKEN_DIR"))

    fpr_file = find_fpr_file(target_path)

    if fpr_file is None:
        print("FPR 파일을 찾을 수 없습니다.")
        return

    token_path = os.path.join(token_dir, "ScanCentralCtrlToken")
    with open(token_path, 'r') as token_file:
        auth_token = token_file.read().strip()

    command = [
        "fortifyclient",
        "-url", ssc_server_url,
        "-authtoken", auth_token,
        "uploadFPR",
        "-file", fpr_file,
        "-applicationVersionID", ssc_id
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    print(result.stdout)
    print(result.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python upload_ssc.py [ssc_id] [optional: 상대 경로 (기본값: 현재 경로)]")
    else:
        ssc_id = sys.argv[1]
        target_path = sys.argv[2] if len(sys.argv) > 2 else '.'
        upload_ssc(ssc_id, target_path)
