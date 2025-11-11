from enum import Enum
from typing import List, Optional


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


class AzurePipelineRunState(Enum):
    IN_PROGRESS = 'inProgress'
    COMPLETED = 'completed'
    CANCELING = 'canceling'
    UNKNOWN = 'unknown'

    @staticmethod
    def from_string(value: str) -> 'AzurePipelineRunState':
        if not value:
            return AzurePipelineRunState.UNKNOWN
        normalized = value.strip().lower()
        for state in AzurePipelineRunState:
            if state.value.lower() == normalized:
                return state
        return AzurePipelineRunState.UNKNOWN


class AzurePipelineRunResult(Enum):
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    CANCELED = 'canceled'
    UNKNOWN = 'unknown'

    @staticmethod
    def from_string(value: Optional[str]) -> 'AzurePipelineRunResult':
        if not value:
            return AzurePipelineRunResult.UNKNOWN
        normalized = value.strip().lower()
        for result in AzurePipelineRunResult:
            if result.value.lower() == normalized:
                return result
        return AzurePipelineRunResult.UNKNOWN
