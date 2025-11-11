from typing import Dict
from json import load, dump, dumps


def load_json_from_file(path: str):
    with open(path, "r") as file:
        return load(file)


def write_json_on_file(content: Dict, path: str):
    with open(path, 'w') as f:
        dump(content, f, indent=4)


def to_pretty_json(content: Dict) -> str:
    # The default option converts any type to str (example, when using a Enum)
    return dumps(content, indent = 2, ensure_ascii = False, default = str)
