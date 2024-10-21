import re
import os
import json
import subprocess

def run_snyk_monitor(target_path):
    os.chdir(target_path)

    result = subprocess.run(['snyk', 'monitor'], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Probably, {result.stderr} is not SNYK testable.")

    return result.stdout

def get_project_id(output_text):
    match = re.search(r'/project/([^/]+)/history/', output_text)

    if not match:
        raise ValueError("Probably, this project is not SNYK testable.")
    return match.group(1)

def determine_key(target_path):
    current_folder = os.path.basename(target_path)
    parent_folder = os.path.basename(os.path.dirname(target_path))

    if '@' in current_folder:
        return current_folder
    else:
        return f"{parent_folder}.{current_folder}"

def save_to_json(data, save_path):
    json_filename = os.path.join(save_path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 디렉토리가 없을 시 생성하여 진행
    print(f'{json_filename}')

    # 기존 JSON 파일 읽기
    existing_data = {}
    if os.path.exists(save_path):
        with open(save_path, 'r') as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # Project ID 중복 확인, 없을 시 데이터 추가
    for key, value in data.items():
        if key not in existing_data or existing_data[key] != value:
            existing_data[key] = value

    # JSON 파일에 저장
    with open(json_filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

def get_and_save_snyk_info(target_path, save_path='/nfsdata/fortify_work/resNbak/snyk_project_id.json'):
    output_text = run_snyk_monitor(target_path)
    project_id = get_project_id(output_text)
    key = determine_key(target_path)
    data = {key: project_id}
    save_to_json(data, save_path)

    return data

