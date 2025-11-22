from abc import ABC, abstractmethod
from typing import Dict, Optional

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.application.model import AzurePipelineRunInfo, AzurePipelineRunStatus, AzurePipelineApproval


class BasePipelineAPI(ABC):
    def __init__(self, runner: RunnerModel):
         self.runner = runner

    @abstractmethod
    def trigger_pipeline(self, params: Dict) -> AzurePipelineRunInfo: pass

    @abstractmethod
    def get_run_status(self, run_id: str) -> AzurePipelineRunStatus: pass

    @abstractmethod
    def get_approval_status(self, run_id: str) -> Optional[AzurePipelineApproval]: pass
    
    @abstractmethod
    def approve_run(self, run_id: str, approval_id: str) -> None: pass
    