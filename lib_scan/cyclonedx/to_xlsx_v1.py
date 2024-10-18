import json
import openpyxl
import pandas as pd

# JSON 파일 로드
with open('formatted_install-api.sbom.evinse.json', 'r') as f:
    data = json.load(f)

# 첫 번째 시트 (Info)에 bomFormat, specVersion, serialNumber, version, metadata 데이터를 입력
sheet1_data = {
    "bomFormat": [data.get('bomFormat')],
    "specVersion": [data.get('specVersion')],
    "serialNumber": [data.get('serialNumber')],
    "version": [data.get('version')],
    "metadata": [data.get('metadata')],
}

# 두 번째 시트 (Components)에 components 데이터를 입력
components_data = data.get('components', [])

# 세 번째 시트 (Dependencies)에 dependencies 데이터를 입력
dependencies_data = data.get('dependencies', [])

# 네 번째 시트 (Services)에 services 데이터를 입력
services_data = data.get('services', [])

# 다섯 번째 시트 (Annotations)에 annotations 데이터를 입력
annotations_data = data.get('annotations', [])

# 첫 번째 시트의 DataFrame 생성
df_sheet1 = pd.DataFrame(sheet1_data)

# 리스트를 분리하는 함수 정의
def split_list_columns(df, columns_to_split):
    new_df = pd.DataFrame()

    for idx, row in df.iterrows():
        max_length = 1  # 기본적으로 한 행에 최소 하나의 값이 있어야 함
        split_data = {col: (row[col] if isinstance(row[col], list) else [row[col]])
                      for col in columns_to_split}

        max_length = max(max_length, *[len(split_data[col]) for col in columns_to_split])

        for i in range(max_length):
            new_row = row.copy()

            for col in columns_to_split:
                if i < len(split_data[col]):
                    new_row[col] = split_data[col][i]
                else:
                    new_row[col] = pd.NA

            new_df = pd.concat([new_df, new_row.to_frame().T], ignore_index=True)

    return new_df

# 두 번째 시트 Components 데이터프레임 생성 및 리스트 분리 적용
df_components = pd.json_normalize(components_data) if components_data else pd.DataFrame()

# Components의 리스트가 포함된 열들을 찾음
columns_to_split = df_components.columns[df_components.applymap(lambda x: isinstance(x, list)).any()].tolist()

# 리스트 분리 적용
df_components_split = split_list_columns(df_components, columns_to_split)

# 세 번째, 네 번째, 다섯 번째 시트 생성
df_dependencies = pd.json_normalize(dependencies_data) if dependencies_data else pd.DataFrame()
df_services = pd.json_normalize(services_data) if services_data else pd.DataFrame()
df_annotations = pd.json_normalize(annotations_data) if annotations_data else pd.DataFrame()

# 엑셀 파일 생성 및 각 시트에 데이터 저장
with pd.ExcelWriter('mul_output_split_v2.xlsx', engine='openpyxl') as writer:
    # Info 시트 저장
    df_sheet1.to_excel(writer, sheet_name='Info', index=False)
    # Components 시트 저장 (리스트 분리 적용)
    df_components_split.to_excel(writer, sheet_name='Components', index=False)
    # Dependencies 시트 저장
    df_dependencies.to_excel(writer, sheet_name='Dependencies', index=False)
    # Services 시트 저장
    df_services.to_excel(writer, sheet_name='Services', index=False)
    # Annotations 시트 저장
    df_annotations.to_excel(writer, sheet_name='Annotations', index=False)

print("Excel 파일이 성공적으로 생성되었습니다.")
