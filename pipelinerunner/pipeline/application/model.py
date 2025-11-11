from dataclasses import dataclass

from pipelinerunner.pipeline.domain.enums import AzurePipelineRunState, AzurePipelineRunResult


@dataclass
class AzurePipelineRunInfo:
    id: str
    status: 'AzurePipelineRunStatus'


@dataclass
class AzurePipelineRunStatus:
    state: 'AzurePipelineRunState'
    result: 'AzurePipelineRunResult'

    def is_running(self) -> bool:
        return self.state == AzurePipelineRunState.IN_PROGRESS

    def is_completed(self) -> bool:
        return self.state == AzurePipelineRunState.COMPLETED

    def is_successful(self) -> bool:
        return self.result == AzurePipelineRunResult.SUCCEEDED
    
    def __str__(self) -> str:
        return f"State: {self.state.name}, Result: {self.result.name}"
