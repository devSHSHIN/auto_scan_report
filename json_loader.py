import json

def load_json_file(json_path):
    with open(json_path, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    return data