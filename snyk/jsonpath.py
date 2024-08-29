import json

def print_json_keys(data, parent_key=''):
    # data가 dict인 경우(즉, 키-값 쌍이 있는 경우)
    if isinstance(data, dict):
        for key, value in data.items():
            # 현재 키의 전체 경로를 구성
            full_key = f"{parent_key}.{key}" if parent_key else key
            print(full_key)  # 현재 키의 경로 출력
            # 값이 dict나 list인 경우 재귀 호출
            if isinstance(value, (dict, list)):
                print_json_keys(value, full_key)
    
    # data가 list인 경우(즉, 여러 개의 항목이 있는 경우)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            # 리스트의 인덱스를 경로에 포함
            full_key = f"{parent_key}[{index}]"
            print(full_key)  # 현재 리스트 항목의 경로 출력
            # 리스트 항목이 dict나 list인 경우 재귀 호출
            if isinstance(item, (dict, list)):
                print_json_keys(item, full_key)

# JSON 파일 경로
file_path = '/home/fortify/auto_scan_report/data/tmp/test.json'

# JSON 데이터 읽기
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# JSON 구조의 키와 경로 출력
print_json_keys(data)

