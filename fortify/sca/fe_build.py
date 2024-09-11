import os
import sys
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')

def run_command(command):
    """ 터미널 명령어 실행 및 오류 처리 """
    print(f"\n[시작] {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"\033[32m[성공]\033[0m {command}: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[실패]\033[0m {command}: {e.stderr}")
        sys.exit(1)  # 오류 발생 시 스크립트 중지

def main():
    # 1. BUILD_ID 환경 변수 설정
    os.environ['BUILD_ID'] = os.path.basename(os.getcwd())
    build_id = os.getenv('BUILD_ID')

    # 2. 현재 시간 가져오기
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"[정보] {build_id} 서비스의 진단을 시작합니다. | {current_time}")

    # 3. sourceanalyzer -clean 명령 실행
    run_command(f"sourceanalyzer -b {build_id} -clean")

    # 4. sourceanalyzer 로그 파일과 제외 패턴 적용하여 실행
    trans_log_file = os.path.expandvars(os.getenv('TRANS_LOG_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    exclude_patterns = os.getenv('EXCLUDE_PATTERNS')
    run_command(f"sourceanalyzer -b {build_id} -logfile {trans_log_file} {exclude_patterns} .")

    # 5. MBS 파일 처리
    mbs_tmp = os.path.expandvars(os.getenv('MBS_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    run_command(f"sourceanalyzer -b {build_id} -export-build-session {mbs_tmp}")

    # 6. MBS 파일 복사
    l_mbs_file = os.path.expandvars(os.getenv('L_MBS_FILE')).replace("$BUILD_ID", build_id)
    run_command(f"cp -f {mbs_tmp} {l_mbs_file}")

    # 7. 다시 sourceanalyzer -clean
    run_command(f"sourceanalyzer -b {build_id} -clean")

    # 8. 이전 세션 불러오기
    run_command(f"sourceanalyzer -b {build_id} -import-build-session {l_mbs_file}")

    # 9. FPR 파일 처리
    fpr_tmp = os.path.expandvars(os.getenv('FPR_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    scan_log_file = os.path.expandvars(os.getenv('SCAN_LOG_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    run_command(f"sourceanalyzer -b {build_id} -logfile {scan_log_file} -scan -f {fpr_tmp}")

    # 10. FPR 파일 복사
    l_fpr_file = os.path.expandvars(os.getenv('L_FPR_FILE')).replace("$BUILD_ID", build_id)
    run_command(f"cp -f {fpr_tmp} {l_fpr_file}")

    # 11. sscid 명령 실행
    run_command(f"sscid {build_id}")

if __name__ == "__main__":
    main()
