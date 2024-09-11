import os
from dotenv import load_dotenv

load_dotenv()

current_folder = os.path.basename(os.getcwd())

env_file_path = os.path.join(os.path.expandvars(os.getenv("ENV_PATH")), '.env')

if not os.path.exists(env_file_path):
    with open(env_file_path, 'w') as file:
        file.write(f'BUILD_ID={current_folder}\n')
else:
    with open(env_file_path, 'r') as file:
        lines = file.readlines()

    with open(env_file_path, 'w') as file:
        for line in lines:
            if line.startswith('BUILD_ID='):
                file.write(f'BUILD_ID={current_folder}\n')
            else:
                file.write(line)

print(f'.env 파일이 업데이트되었습니다: NOW_DIR={current_folder}')
