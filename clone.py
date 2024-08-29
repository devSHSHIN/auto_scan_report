# -*- coding: utf-8 -*-

import sys
import subprocess
import os
import json
from urllib.parse import urlparse


def format_name(name):
    return name.lower().replace("/", ".").replace(" ", "_")


def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, ".config", "__init__.json")

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
        return config


def revert_to_built_commit(src_path):
    os.chdir(src_path)
    commit_id = get_built_commit_id(src_path)

    result = subprocess.run(["git", "reset", "--hard", commit_id])

    if result.returncode == 0:
        print(f"이전 Commit으로 복구합니다. ({commit_id})")
    else:
        print(f"복구에 실패 하였습니다." f"확인이 필요합니다. (target: {commit_id})")

        sys.exit(1)


def get_built_commit_id(src_path):
    # get_built_commit_id() ==> 필요 시 src에서 직접 가져오는 것이 아니라 빌드 성공한 commit id를 저장하는 파일을 따로 두고, 이 함수에선 그 파일의 정보를 읽도록 변경 예정
    os.chdir(src_path)
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)

    if result.returncode == 0:
        c_id = result.stdout.strip()
        print(f"{c_id}")

        return c_id
    else:
        print(f"Commit ID 확인 불가\n" f"확인이 필요합니다. ({src_path})")
        sys.exit


def get_url_info(input_url, branch_name):
    config = load_config()

    home_dir = "/home/fortify/work"

    bitbucket_username = config.get("BITBUCKET_ID")
    bitbucket_password = config.get("BITBUCKET_PW")
    bitbucket_url = config.get("BITBUCKET_URL")

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
    src_path = f"{home_dir}/src/{project_name}/{src_name}"

    return {
        "username": bitbucket_username,
        "password": bitbucket_password,
        "mid_url": bitbucket_url,
        "project_name": project_name,
        "repository_name": repository_name,
        "src_name": src_name,
        "src_path": src_path,
        "git_url": git_url,
    }


def run_clone(info_dict, branch_name):
    git_url = f"{info_dict['git_url']}"
    src_path = f"{info_dict['src_path']}"
    result = subprocess.run(["git", "clone", "-b", branch_name, git_url, src_path])

    if result.returncode == 0:
        os.chdir(f"{info_dict['src_path']}")
        print(f"Clone: {info_dict['src_path']}")
    else:
        print(f"Clone Failed")


def run_pull(info_dict):
    os.chdir(info_dict["src_path"])
    result = subprocess.run(["git", "pull"])

    if result.returncode == 0:
        print(f"Update(Pull): {info_dict['src_path']}")
    else:
        print(f"Update(pull) Failed")


def run_git_comm(input_url, branch_name):
    info_dict = get_url_info(input_url, branch_name)
    src_path = info_dict["src_path"]

    # 해당 src 존재 여부 확인
    if not os.path.exists(src_path):
        print(f"Clone: {src_path}")
        run_clone(info_dict, branch_name)
    else:
        print(f"이미 {src_path}가 존재합니다.")
        run_pull(info_dict)


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("사용법: python3 clone.py [git_url] [branch_name(default: master)]")
        sys.exit(1)

    input_url = sys.argv[1]
    branch_name = sys.argv[2] if len(sys.argv) == 3 else "master"
    run_git_comm(input_url, branch_name)
