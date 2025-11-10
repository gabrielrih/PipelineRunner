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

    @staticmethod
    def from_value(value) -> 'PipelineExecutionMode':
        if not value:
            raise ValueError("Execution mode cannot be empty")
        normalized = value.lower().strip()
        for mode in PipelineExecutionMode:
            if mode.value == normalized:
                return mode
        valid_values = ", ".join(PipelineExecutionMode.get_values())
        raise ValueError(f"Invalid execution mode '{value}'. Valid values are: {valid_values}")
