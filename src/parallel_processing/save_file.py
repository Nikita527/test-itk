import json


def save_data_to_json(file_path: str, data: list) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file, ensure_ascii=False)
