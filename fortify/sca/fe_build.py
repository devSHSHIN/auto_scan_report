import os
import subprocess
import sys

def run_command(command):
    """ 터미널 명령어 실행 및 오류 처리 """
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"\033[32m[성공]\033[0m {command}: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[실패]\033[0m {command}: {e.stderr}")
        sys.exit(1)  # 오류 발생 시 스크립트 중지

def main():
    # 1. BUILD_ID 환경 변수 설정
    build_id = os.path.basename(os.getcwd())
    os.environ['BUILD_ID'] = build_id
    print(f"[정보] BUILD_ID가 {build_id}로 설정되었습니다.")

    # 2. sourceanalyzer -clean 명령 실행
    run_command(f"sourceanalyzer -b {os.environ['BUILD_ID']} -clean")

    # 3. sourceanalyzer 로그 파일과 제외 패턴 적용하여 실행
    trans_log_file = os.getenv('TRANS_LOG_FILE', 'trans_log.log')
    exclude_patterns = os.getenv('EXCLUDE_PATTERNS', '')
    run_command(f"sourceanalyzer -b {os.environ['BUILD_ID']} -logfile {trans_log_file} {exclude_patterns} .")

    # 4. MBS 파일 처리
    mbs_tmp = os.getenv('MBS_FILE', 'build.mbs')
    run_command(f"sourceanalyzer -b {os.environ['BUILD_ID']} -export-build-session {mbs_tmp}")

    # 5. MBS 파일 복사
    l_mbs_file = os.getenv('L_MBS_FILE', 'local_build.mbs')
    run_command(f"cp -f {mbs_tmp} {l_mbs_file}")

    # 6. 다시 sourceanalyzer -clean
    run_command(f"sourceanalyzer -b {os.environ['BUILD_ID']} -clean")

    # 7. 이전 세션 불러오기
    run_command(f"sourceanalyzer -b {os.environ['BUILD_ID']} -import-build-session {l_mbs_file}")

    # 8. FPR 파일 처리
    fpr_tmp = os.getenv('FPR_FILE', 'scan.fpr')
    scan_log_file = os.getenv('SCAN_LOG_FILE', 'scan_log.log')
    run_command(f"sourceanalyzer -b {os.environ['BUILD_ID']} -logfile {scan_log_file} -scan -f {fpr_tmp}")

    # 9. FPR 파일 복사
    l_fpr_file = os.getenv('L_FPR_FILE', 'local_scan.fpr')
    run_command(f"cp -f {fpr_tmp} {l_fpr_file}")

    # 10. sscid 명령 실행
    run_command(f"sscid {os.environ['BUILD_ID']}")

if __name__ == "__main__":
    main()
