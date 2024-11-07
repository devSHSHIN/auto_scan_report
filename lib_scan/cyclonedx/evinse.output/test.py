import json
import pandas as pd
from openpyxl import Workbook

json_path = '/Users/pc09164/Downloads/arhis-fe@develop/data-flow.slices.json'
xlsx_path = '/Users/pc09164/Downloads/arhis-fe@develop/arhis-fe@develop.data-flow.xlsx'  # 출력 엑셀 파일 경로
# JSON 파일 읽기
with open(json_path, 'r', encoding='UTF-8') as f:
    data = json.load(f)



# dependencies 시트 작성 함수
def dependencies(wb, data):
    ws = wb.create_sheet('dependencies')

    # 데이터프레임 생성 및 dependsOn 열을 explode
    df_dependencies = pd.json_normalize(data["graph"])
    #df_expanded = df_dependencies.explode('nodes')

    # 데이터프레임의 열을 첫 번째 행에 추가
    ws.append([''] + list(df_dependencies.columns))  # 첫 번째 셀에 공백 추가

    # 데이터프레임의 각 행을 순차적으로 시트에 추가
    for row in df_dependencies.itertuples(index=False, name=None):
        ws.append([''] + list(row))  # 첫 번째 셀에 공백 추가



# 엑셀 파일 작성 함수
def write_xlsx():
    wb = Workbook()
    dependencies(wb, data)  # data 인자를 넘겨줌
    wb.save(xlsx_path)

# 엑셀 파일 작성 함수 실행
write_xlsx()

