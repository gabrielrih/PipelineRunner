
from src.util.json import load_json_from_file

from enum import Enum
from typing import List


class ConfigMapper(Enum):
    DEV = 'config/runs-for-dev.json'
    STG = 'config/runs-for-stg.json'
    PRD = 'config/runs-for-prd.json'
    TEST = 'config/test-runs.json'


def get_pipelines_from_scope(scope: str):
    if scope == 'dev':
        return load_json_from_file(path = ConfigMapper.DEV.value)
    elif scope == 'stg':
        return load_json_from_file(path = ConfigMapper.STG.value)
    elif scope == 'prd':
        return load_json_from_file(path = ConfigMapper.PRD.value)
    elif scope == 'test':
        return load_json_from_file(path = ConfigMapper.TEST.value)
    pipelines: List = list()
    for config in ConfigMapper:
        # The test value is really just for testing, so ignores it even when using the ALL scope
        if config == ConfigMapper.TEST:
            continue
        pipelines += load_json_from_file(path = config.value)
    return pipelines
    
