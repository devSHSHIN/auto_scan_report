# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from dotenv import load_dotenv
from urllib.parse import urlparse


# .env 파일 로드
load_dotenv()

# 특수문자 변환
def format_name(name):
    return name.lower().replace("/", ".").replace(" ", "_")

# 이전 Commit으로 복구
def revert_to_built_commit(src_path):
    os.chdir(src_path)
    commit_id = get_built_commit_id(src_path)

    result = subprocess.run(["git", "reset", "--hard", commit_id])

    if result.returncode == 0:
        print(f"이전 Commit으로 복구합니다. ( \033[32m{commit_id}\033[0m )")
    else:
        print(f"복구에 실패 하였습니다.\n 확인이 필요합니다. ( \033[91m{commit_id}\033[0m )")
        sys.exit(1)

# 최신 성공 빌드 Commit 확인
def get_built_commit_id(src_path):
    # get_built_commit_id() ==> 필요 시 src에서 직접 가져오는 것이 아니라 빌드 성공한 commit id를 저장하는 파일을 따로 두고, 이 함수에선 그 파일의 정보를 읽도록 변경 예정
    os.chdir(src_path)
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)

    if result.returncode == 0:
        c_id = result.stdout.strip().decode('UTF-8')
        print(f"\033[32m{c_id}\033[0m")
        return c_id
    else:
        print(f"Commit ID 확인 불가\n 확인이 필요합니다. ( \033[91m{src_path}\033[0m )")
        sys.exit(1)

# git url 확인
def get_url_info(input_url, branch_name):
    home_dir = os.getenv("HOME")
    src_dir = home_dir + "/work/src"

    bitbucket_username = os.getenv("BITBUCKET_ID")
    bitbucket_password = os.getenv("BITBUCKET_PW")
    bitbucket_url = os.getenv("BITBUCKET_URL")

    parsed_url = urlparse(input_url)

    username = parsed_url.username
    if not username:
        username = bitbucket_username

    path_parts = parsed_url.path.strip("/").split("/")
    project_name = format_name(path_parts[-2])
    repository_name = format_name(path_parts[-1].replace(".git", ""))
    branch_name = branch_name.replace("/", ".")
    src_name = f"{repository_name}@{branch_name}"

    git_url = f"http://{bitbucket_username}:{bitbucket_password}@{bitbucket_url}/{project_name}/{repository_name}.git"
    src_path = f"{src_dir}/{project_name}/{src_name}"

    return {
        "username": bitbucket_username,
        "password": bitbucket_password,
        "mid_url": bitbucket_url,
        "project_name": project_name,
        "repository_name": repository_name,
        "src_name": src_name,
        "src_path": src_path,
        "git_url": git_url
    }

# git clone
def run_clone(info_dict, branch_name):
    git_url = f"{info_dict['git_url']}"
    src_path = f"{info_dict['src_path']}"
    result = subprocess.run(["git", "clone", "-b", branch_name, git_url, src_path])

    if result.returncode == 0:
        os.chdir(f"{info_dict['src_path']}")
        print(f"Clone: \033[32m{info_dict['src_path']}\033[0m")
    else:
        print(f"Clone: \033[91mFailed\033[0m")

# git update
def run_pull(info_dict):
    os.chdir(info_dict["src_path"])
    result = subprocess.run(["git", "pull"])

    if result.returncode == 0:
        print(f"Update(Pull): \033[32m{info_dict['src_path']}\033[0m")
    else:
        print(f"Update(pull): \033[91mFailed\033[0m")

# git clone 중복 여부 확인
def run_git_comm(input_url, branch_name):
    info_dict = get_url_info(input_url, branch_name)
    src_path = info_dict["src_path"]

    # 해당 src 존재 여부 확인
    if not os.path.exists(src_path):
        # print(f"Clone: {src_path}")
        run_clone(info_dict, branch_name)
    else:
        print(f"이미 \033[91m{src_path}\033[90m가 존재합니다.")
        run_pull(info_dict)


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("사용법: python3 clone.py [git_url] [branch_name(default: master)]")
        sys.exit(1)

    input_url = sys.argv[1]
    branch_name = sys.argv[2] if len(sys.argv) == 3 else "master"
    run_git_comm(input_url, branch_name)
