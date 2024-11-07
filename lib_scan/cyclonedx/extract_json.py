import os
import json

# JSON 파일에서 특정 항목을 추출하고 각각을 파일로 저장하는 함수
def extract_and_save_json_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 특정 키 값을 별도의 변수로 추출
    bomformat = data.get('bomFormat', '')
    specversion = data.get('specVersion', '')
    serialnumber = data.get('serialNumber', '')
    version = data.get('version', '')
    metadata = data.get('metadata', {})
    components = data.get('components', [])
    dependencies = data.get('dependencies', [])
    annotations = data.get('annotations', [])

    # 각 변수를 JSON 파일로 저장
    items = {
        'bomFormat': bomformat,
        'specVersion': specversion,
        'serialNumber': serialnumber,
        'version': version,
        'metadata': metadata,
        'components': components,
        'dependencies': dependencies,
        'annotations': annotations
    }

    # 저장할 경로 설정
    output_directory = './output/'
    
    # 경로가 없으면 디렉토리 생성
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 각 항목을 파일로 저장
    for key, value in items.items():
        file_path = f'{output_directory}{key}.json'
        with open(file_path, 'w', encoding='utf-8') as outfile:
            json.dump(value, outfile, ensure_ascii=False, indent=4)
        print(f"{file_path} 파일이 저장되었습니다.")

# 함수 호출 예시
def main():
    json_file = '/Users/pc09164/Desktop/arhis-be@dev.sbom.json'
    extract_and_save_json_data(json_file)

# main 함수 실행
if __name__ == "__main__":
    main()
