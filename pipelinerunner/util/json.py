from typing import Dict
from json import load, dump


def load_json_from_file(path: str):
    with open(path, "r") as file:
        return load(file)


def write_json_on_file(content: Dict, path: str):
    with open(path, 'w') as f:
        dump(content, f, indent=4)
