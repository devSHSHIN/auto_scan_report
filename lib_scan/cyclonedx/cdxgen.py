import os
import re
import sys
import time
import subprocess
from dotenv import load_dotenv
from datetime import datetime, timedelta

# load_dotenv(dotenv_path='../../.env')
# load_dotenv(dotenv_path='/home/pc09164/auto_scan_report/.env')
load_dotenv(dotenv_path=f"{os.path.expandvars(os.environ['HOME'])}/auto_scan_report/.env")

step = 1
current_time = ''
jdk_lts = 21
build_id = 'BUILD_ID'
ssc_id = 0
project_group = ''
project_name = ''
project_branch = ''

# 0 진단 시작
def phase_start():
    global current_time
    global build_id

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_dir = os.getcwd()
    
    try:
        extract_project_info(current_dir)
    except ValueError as e:
        print(e)

    # BUILD_ID 설정
    os.environ['BUILD_ID'] = project_name
    build_id = os.getenv('BUILD_ID')

    print(f"\n|After|")
    print(f"Build ID: {build_id}")
    print(f"Group Name: {project_group}")
    print(f"Project Name: {project_name}")
    print(f"Branch Name: {project_branch}")
    
    print(f"\n\n\n\n\033[38;5;220m================================================================================================================================\033[0m\n\n\t\033[38;5;99m[정보|LIB]\033[0m \033[38;5;117m{build_id}\033[0m(NPM) 서비스의 라이브러리 진단을 시작합니다. | \033[38;5;240m{current_time}\033[0m")

    sys.exit(1)

# 1 초기화
def phase_init():
    global jdk_lts

    jenv_path = os.path.expandvars(os.environ.get('JENV_HOME'))
    jdk_lts_file = os.path.join(jenv_path, "jdk_lts.info")

    with open(jdk_lts_file, 'r') as j:
        jdk_lts = j.read().strip()

    print(f"JDK LTS = {jdk_lts}")
    comm = f'direnv allow && export PATH="$HOME/.jenv/bin:$PATH" && eval "$(jenv init -)" && jenv shell {jdk_lts}'

    run_command(comm)

# 2 SBOM 생성
def phase_sbom():
    SBOM_JSON_FILE = os.getenv('SBOM_JSON_FILE')
    SBOM_XML_FILE = os.getenv('SBOM_XML_FILE')
    
    subprocess.run(["cdxgen", "-t", "npm", ".", "--evidence", "--deep", "-o", SBOM_JSON_FILE], check=True)




    trans_log_file = os.path.expandvars(os.getenv('TRANS_LOG_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    exclude_patterns = os.getenv('EXCLUDE_PATTERNS')
    comm = f"sourceanalyzer -b {build_id} -logfile {trans_log_file} {exclude_patterns} ."
    run_command(comm)

# 3
def phase_mbs():
    mbs_file = os.path.expandvars(os.getenv('MBS_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    l_mbs_file = os.path.expandvars(os.getenv('L_MBS_FILE')).replace("$BUILD_ID", build_id)
    comm = f"sourceanalyzer -b {build_id} -export-build-session {mbs_file} && cp -f {mbs_file} {l_mbs_file}"
    run_command(comm, mbs_file)
    return mbs_file

# 4
def phase_reset(mbs_file):
    comm = f"sourceanalyzer -b {build_id} -clean && sourceanalyzer -b {build_id} -import-build-session {mbs_file}"
    run_command(comm)

# 5
def phase_scan():
    fpr_file = os.path.expandvars(os.getenv('FPR_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    l_fpr_file = os.path.expandvars(os.getenv('L_FPR_FILE')).replace("$BUILD_ID", build_id)
    scan_log_file = os.path.expandvars(os.getenv('SCAN_LOG_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    comm = f"sourceanalyzer -b {build_id} -logfile {scan_log_file} -scan -f {fpr_file} && cp -f {fpr_file} {l_fpr_file}"
    run_command(comm, fpr_file)
    return fpr_file

# 6
def phase_sscid():
    global ssc_id

    scripts_path = os.path.expandvars(os.getenv('SCRIPT_DIR'))
    comm = f"{scripts_path}/_listappids.sh | grep {build_id}"
    ssc_id = run_command(comm).split()[0]

    if ssc_id is None:
        print(f"\t\033[38;5;196m[실패]\033[0m SSC에 {build_id} 서비스가 조회되지 않습니다.")
        sys.exit(1)

# 7
def phase_upload(fpr_file):
    ssc_server_url = os.path.expandvars(os.getenv("SSC_SERVER_URL"))
    token_dir = os.path.expandvars(os.getenv("TOKEN_DIR"))
    token_path = os.path.join(token_dir, "ScanCentralCtrlToken")
    auth_token = ''

    with open(token_path, 'r') as token_file:
        auth_token = token_file.read().strip()

    comm = f"fortifyclient -url {ssc_server_url} -authtoken {auth_token} uploadFPR -file {fpr_file} -applicationVersionID {ssc_id}"
    run_command(comm)

# 8
def phase_end(start_time):
    log_dir = os.path.expandvars(os.getenv("LOG_DIR"))
    history_file = os.path.join(log_dir, f"{build_id}_history.log")
    end_time = time.time()
    run_time = str(timedelta(seconds=end_time - start_time))
    log_text = f"{current_time} > SSC {ssc_id} :: {build_id} 진단 성공\t\t|\t{run_time}\n"
    comm = f"tail {history_file}"

    with open(history_file, 'a') as f:
        f.write(log_text)
        # subprocess.run(comm, shell=True, check=True, capture_output=True, text=True)
        print(f"\n\t\033[38;5;99m[정보]\033[0m \033[38;5;117m{build_id}\033[0m(FE) SSC 진단 종료\n\n\033[38;5;220m================================================================================================================================\033[0m\n\n\n\n")

def extract_project_info(current_dir):
    """
    주어진 경로에서 project_group, project_name, project_branch를 추출하는 함수
    """
    global project_group, project_name, project_branch
    
    # 'work/src/' 이후의 첫 번째 폴더명 추출 (project_group)
    project_group_match = re.search(r'/[^/]*work/src/([^/]+)', current_dir)

    if project_group_match:
        project_group = project_group_match.group(1)

        # 'project_group' 이후 '@' 특수문자가 포함된 폴더명 찾기
        project_name_match = re.search(rf'{project_group}/(?:[^/]+/)*([^/]+)@([^/]+)(.*)', current_dir)

        if project_name_match:
            # @ 특수문자가 포함된 폴더명에서 '@' 이전 부분
            folder_with_at_before = project_name_match.group(1)
            # @ 이후의 텍스트
            project_branch = project_name_match.group(2)
            # @ 포함 폴더 다음의 경로 (존재하지 않을 수 있음)
            remaining_path = project_name_match.group(3)

            # "0built." 또는 "0org."등으로 시작하는 경우 해당 부분 제거
            if folder_with_at_before.startswith('0'):
                folder_with_at_before = re.sub(r'^0[^.]*\.', '', folder_with_at_before)

            # 남은 경로가 없는 경우 처리
            if remaining_path:
                # 중복된 구분자가 발생하지 않도록 수정
                remaining_path_cleaned = remaining_path.strip('/')
                project_name = f"{folder_with_at_before}.{remaining_path_cleaned.replace('/', '.')}"
            else:
                # 남은 경로가 없으면 project_name은 '@' 이전 부분만 저장
                project_name = folder_with_at_before

            return project_group, project_name, project_branch
        else:
            raise ValueError("'@' 특수문자가 포함된 폴더를 찾을 수 없습니다.")
    else:
        raise ValueError("'work/src/' 뒤의 project_group을 찾을 수 없습니다.")


def switch_case():
    switcher = {
            0: " 확인",
            1: " 초기화",
            2: " 번역",
            3: " 번역 파일 추출",
            4: " 재설정",
            5: " 진단",
            6: " SSC ID 조회",
            7: f" SSC(\033[38;5;153m{ssc_id}\033[0m) 업로드",
            8: " 진단 종료"
    }

    comm_info = "\033[38;5;117m"
    comm_info += build_id
    comm_info += "\033[0m"
    comm_info += switcher.get(step, "Error step")
    return comm_info

def run_command(command, file_path=''):
    global step
    comm_info = switch_case()
    print(f"\n\t\033[38;5;195m[시작]\033[0m {comm_info}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        result_text = f"\t\033[32m[성공]\033[0m {comm_info} 완료"
        if step in [3, 5]:
            result_text += f" > {file_path}"
        print(f"{result_text}")
        step += 1
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"\t\033[38;5;196m[실패]\033[0m {comm_info} 중지\n\t\t\033[38;5;210m> {e.stderr}\033[0m")
        sys.exit(1)

def main():
    start_time = time.time()

##
# 정보 추출
# 초기화
# cdxgen -t * --deep --evidence --project-group * --project-name * --project-version * --output *.bom.json .
## atom 분석 시작 --output *.atom
# data-flow --slice-outfile *.dataflow.json
# usages --slice-outfile *.usages.json
# reachables --slice-outfile *.reachables.json
## 추가
# parsedepse --slice-outfile
# 

    phase_start()
    phase_clean()
    phase_trans()
    mbs_file = phase_mbs()
    phase_reset(mbs_file)
    fpr_file = phase_scan()
    phase_sscid()
    phase_upload(fpr_file)
    phase_end(start_time)

if __name__ == "__main__":
    main()

