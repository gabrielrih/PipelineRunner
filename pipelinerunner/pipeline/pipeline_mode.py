from enum import Enum
from typing import List


class PipelineExecutionMode(Enum):
    PARALLEL = ('parallel', 'It runs one pipeline after another')
    SEQUENTIAL = ('sequential', 'It runs all pipelines at once')

    def __init__(self, value: str, description: str):
        self._value_ = value
        self.description = description

    def get_values() -> List:
        values = list()
        for mode in PipelineExecutionMode:
            values.append(mode.value)
        return values
    
    def get_help_message() -> str:
        message: str = ''
        is_first = True
        for mode in PipelineExecutionMode:
            if not is_first:
                message += ' - '
            message += f'{str(mode.value)}: {str(mode.description)}'
            is_first = False
        return message
