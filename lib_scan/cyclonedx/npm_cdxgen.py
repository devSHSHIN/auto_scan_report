import os
import re
import sys
import time
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv

# load_dotenv(dotenv_path='../../.env')
load_dotenv(dotenv_path='/home/pc09164/auto_scan_report/.env')

"""
SBOM_JSON_FILE = os.getenv('SBOM_JSON_FILE')
SBOM_XML_FILE = os.getenv('SBOM_XML_FILE')
SPDX_JSON_FILE = os.getenv('SPDX_JSON_FILE')
SPDX_XML_FILE = os.getenv('SPDX_XML_FILE')
EVINSE_FILE = os.getenv('EVINSE_FILE')
USAGES_SLICES_FILE
DATA_FLOW_SLICES_FILE
REACHABLES_SLICES_FILE
VULNS_JSON_FILE = os.getenv('VULNS_JSON_FILE')
VULNS_XML_FILE = os.getenv('VULNS_XML_FILE')
NPM_AUDIT_FILE = os.getenv('NPM_AUDIT_FILE')
CUSTOM_REPORT_FILE = os.getenv('CUSTOM_REPORT_FILE')
METADATA__FILE = os.getenv('METADATA__FILE')
"""

step = 1
current_time = ''
jdk_lts = 21
build_id = 'BUILD_ID'
ssc_id = 0
project_path = os.getcwd()
project_group = ''
project_name = ''
project_branch = ''
project_id = ''
sbom_json_file = ''

# 0 진단 시작
def phase_start():
    global current_time
    global build_id
    global project_id

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_dir = os.getcwd()
    
    # BUILD_ID 설정
    os.environ['BUILD_ID'] = os.path.basename(current_dir)
    build_id = os.getenv('BUILD_ID')

    try:
        extract_project_info(current_dir)
    except ValueError as e:
        print(e)

    project_id = f"{project_name}@{project_branch}"

    print(f"\n|After|")
    print(f"Build ID: {build_id}")
    print(f"Group Name: {project_group}")
    print(f"Project Name: {project_name}")
    print(f"Branch Name: {project_branch}")
    
    print(f"\n\n\n\n\033[38;5;220m================================================================================================================================\033[0m\n\n\t\033[38;5;99m[정보|LIB]\033[0m \033[38;5;117m{build_id}\033[0m(NPM) 서비스의 라이브러리 진단을 시작합니다. | \033[38;5;240m{current_time}\033[0m")

# 1 초기화
def phase_init():
    global jdk_lts

#    jenv_path = os.path.expandvars(os.environ.get('JENV_HOME'))
#    jdk_lts_file = os.path.join(jenv_path, "jdk_lts.info")

#    with open(jdk_lts_file, 'r') as j:
#        jdk_lts = j.read().strip()

#    subprocess.run('export PATH="$HOME/.jenv/bin:$PATH" && eval "$(jenv init -)"', shell=True, check=True, executable='/bin/bash')
#    print(f"JDK LTS = {jdk_lts}")
#    subprocess.run(f"j{jdk_lts}", shell=True, check=True)
    print("direnv 시도")
    subprocess.run('eval "$(direnv hook bash)"', shell=True, check=True)
    subprocess.run(["direnv", "allow"], check=True)
    print("direnv allow 성공")
#    os.environ['JENV_VERSION'] = jdk_lts
#    subprocess.run(["jenv", "version"], check=True)

# 2 SBOM 생성
def phase_sbom():
    global sbom_json_file
    sbom_json_file = os.path.expandvars(os.getenv('SBOM_JSON_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
#    sbom_xml_file = os.path.expandvars(os.getenv('SBOM_XML_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)

    comm = f"cdxgen -t npm --language javascript --project-group {project_group} --project-name {project_name} --project-version {project_branch} -o {sbom_json_file} --deep --evidence ."
    print(comm) 
    print(f"SBOM 생성 중 (JSON): {sbom_json_file}")

    try:
        result = subprocess.run(comm, shell=True, check=True, capture_output=True, text=True)
        result_text = f"\t\033[32m[성공]\033[0m {comm} 완료"
        print(f"{result_text}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"\t\033[38;5;196m[실패]\033[0m {comm} 중지\n\t\t\033[38;5;210m> {e.stderr}\033[0m")
        sys.exit(1)


#    subprocess.run(["cdxgen", "-t", "npm", "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch, "--project-id", project_id, "-o", sbom_json_file, "--profile", "research", "-v", project_path], check=True)
#    subprocess.run(f"cdxgen -t npm --project-group {project_group} --project-name {project_name} --project-version {project_branch} --project-id {project_id} -o {sbom_json_file} --profile research -v .", shell=True, check=True)
#    time.sleep(2)

#    print(f"SBOM 생성 중 (XML): {sbom_xml_file}")
#    subprocess.run(["cdxgen", "-t", "npm", "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch, "--output-format", "xml", "-o", sbom_xml_file, "--profile", "research", project_path], check=True)
#    subprocess.run(f"cdxgen -t npm --project-group {project_group} --project-name {project_name} --project-version {project_branch} --project-id {project_id} --output-format xml -o {sbom_json_file} --profile research {project_path}", shell=True, check=True)
#    subprocess.run(["cdxgen", "-t", "npm", ".", "--evidence", "--deep", "--output-format", "xml", "-o", sbom_xml_file, "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch], check=True)
#    time.sleep(2)

    print(f"SBOM 생성 완료")

# 3 SPDX 생성
def phase_spdx():
    spdx_json_file = os.path.expandvars(os.getenv('SPDX_JSON_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    spdx_xml_file = os.path.expandvars(os.getenv('SPDX_XML_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)

    print(f"SPDX 생성 중 (JSON): {spdx_json_file}")
    subprocess.run(["cdxgen", "-t", "npm", project_path, "--evidence", "--spdx", "-o", spdx_json_file, "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch, "--project-id", project_id], check=True)

    print(f"SPDX 생성 중 (XML): {spdx_xml_file}")
    subprocess.run(["cdxgen", "-t", "npm", project_path, "--evidence", "--spdx", "-o", spdx_xml_file, "--output-format", "xml", "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch, "--project-id", project_id], check=True)

    subprocess.run(["ls", "-AlhtrF", spdx_json_file, spdx_xml_file], check=True)

    print(f"SPDX 파일 생성 완료")


# 4 Evinse 분석
def phase_evinse(sbom_json_file):
    evinse_file = os.path.expandvars(os.getenv('EVINSE_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    usages_slices_file = os.path.expandvars(os.getenv('USAGES_SLICES_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)

    print(f"Evinse 분석 중: {evinse_file}")
    subprocess.run(["evinse", "-i", sbom_json_file, "--with-data-flow", "--with-reachables", "--annotate", "-o", evinse_file, project_path], check=True)

    if os.path.exists("usages.slices.json"):
        subprocess.run(["cp", "usages.slices.json", usages_slices_file], check=True)

    print(f"Evinse 분석 완료")

# 5 Vulnerability Report 생성
def phase_vulns_report(sbom_json_file):
    vulns_json_file = os.path.expandvars(os.getenv('VULNS_JSON_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)
    vulns_xml_file = os.path.expandvars(os.getenv('VULNS_XML_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)

    print(f"Vulnerability Report 생성 중 (JSON): {vulns_json_file}")
    subprocess.run(["cdxgen", "--vulns", "-i", sbom_json_file, "-o", vulns_json_file, "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch, "--project-id", project_id, project_path], check=True)

    print(f"Vulnerability Report 생성 중 (XML): {vulns_xml_file}")
    subprocess.run(["cdxgen", "--vulns", "-i", sbom_json_file, "--output-format", "xml", "-o", vulns_xml_file, "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch, "--project-id", project_id, project_path], check=True)

    print("Vulnerability Report 생성 완료")

# 6 npm audit 감사
def phase_audit():

#    export VOLTA_HOME="$HOME/.volta"
#    export PATH="$VOLTA_HOME/bin:$PATH"

##    node 버전 설정
#    volta pin node@18.20.4
#    volta list
    npm_audit_file = os.path.expandvars(os.getenv('NPM_AUDIT_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)

    print(f"npm 감사 중: {npm_audit_file}")

    audit_result = subprocess.run(['npm', 'audit', '--json'], capture_output=True, text=True, check=True)

    with open(npm_audit_file, 'w') as f:
        f.write(audit_result.stdout)

    print(f"npm 감사 결과 저장 완료")

# 7 Custom Report 생성
def phase_upload(sbom_json_file):
    custom_report_file = os.path.expandvars(os.getenv('CUSTOM_REPORT_FILE')).replace("$BUILD_ID", build_id).replace("$(date +%Y%m%d_%H%M%S)", current_time)

    print(f"Custom Report 생성 중: {custom_report_file}")

    subprocess.run(["cdxgen", "--custom", "-i", sbom_json_file, "-o", custom_report_file, "--project-group", project_group, "--project-name", project_name, "--project-version", project_branch, "--project-id", project_id], check=True)

    print(f"Custom Report 생성 완료")


# 8 Package Metadata 처리
def phase_end(start_time):

    with open(history_file, 'a') as f:
        f.write(log_text)
        # subprocess.run(comm, shell=True, check=True, capture_output=True, text=True)
        print(f"\n\t\033[38;5;99m[정보]\033[0m \033[38;5;117m{build_id}\033[0m(FE) SSC 진단 종료\n\n\033[38;5;220m================================================================================================================================\033[0m\n\n\n\n")

def extract_project_info(current_dir):
    """
    주어진 경로에서 project_group, project_name, project_branch를 추출하는 함수
    """
    global build_id
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

            os.environ['BUILD_ID'] = f"{folder_with_at_before}@{project_branch}"
            build_id = os.getenv('BUILD_ID')

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
#    start_time = time.time()

    phase_start()
#    phase_init()
    phase_sbom()
#    phase_spdx()
#    phase_evinse(sbom_json_file)
#    phase_vulns_report(sbom_json_file)
#    phase_audit()

if __name__ == "__main__":
    main()

