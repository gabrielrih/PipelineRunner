from json import load


def load_json_from_file(path: str):
    with open(path, "r") as file:
        return load(file)

