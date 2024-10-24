import json
import pandas as pd

#json_path = '/home/pc09164/fortify_work/src/proxs/px-policy-api@develop/usages.slices.json'
#csv_path = '/home/pc09164/fortify_work/src/proxs/px-policy-api@develop/px-policy-api@develop.usages.csv'
json_path = input(f"json path :\t")

with open(json_path, 'r', encoding='UTF-8') as f:
    data = json.load(f)

df = pd.json_normalize(data)

csv_path = input(f"save path :\t")

df.to_csv(csv_path, index=False, encoding='UTF-8')

print(f"CSV 변환 완료 및 저장 성공 :\t{csv_path}")

