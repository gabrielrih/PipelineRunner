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
        if self.state == AzurePipelineRunState.IN_PROGRESS:
            return False
        return True  # any other state consider as completed

    def is_successful(self) -> bool:
        return self.result == AzurePipelineRunResult.SUCCEEDED
    
    def __str__(self) -> str:
        return f"State: {self.state.name}, Result: {self.result.name}"


# TO DO
# Transforming the status in a Enum?
# Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/approvalsandchecks/approvals/query?view=azure-devops-rest-7.1&tabs=HTTP#approvalstatus
@dataclass
class AzurePipelineApproval:
    id: str
    run_id: str
    status: str


@dataclass(frozen = True)
class ExecutionOptions:
    wait: bool = True
    auto_approve: bool = True
    dry_run: bool = False
