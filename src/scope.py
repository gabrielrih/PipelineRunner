
from src.util.json import load_json_from_file

from enum import Enum
from typing import List


class Scope(Enum):
    DEV = ('dev', 'config/runs-for-dev.json')
    STG = ('stg', 'config/runs-for-stg.json')
    PRD = ('prd', 'config/runs-for-prd.json')
    TEST = ('test', 'config/test-runs.json')
    
    def __init__(self, value: str, path: str):
        self._value_ = value
        self.path = path

    def get_values() -> List:
        scopes = list()
        for scope in Scope:
            scopes.append(scope.value)
        return scopes
    
    def get_help_message() -> str:
        return 'Scope of pipelines to run'


def get_pipelines_from_scope(scope: str):
    scope: Scope = Scope[scope.upper()]  # from str to Scope
    if scope == Scope.DEV:
        return load_json_from_file(path = Scope.DEV.path)
    elif scope == Scope.STG:
        return load_json_from_file(path = Scope.STG.path)
    elif scope == Scope.PRD:
        return load_json_from_file(path = Scope.PRD.path)
    elif scope == Scope.TEST:
        return load_json_from_file(path = Scope.TEST.path)
    raise ValueError('Scope {scope} not allowed!')
