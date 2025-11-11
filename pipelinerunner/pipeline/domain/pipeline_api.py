from abc import ABC, abstractmethod
from typing import Dict

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.application.model import AzurePipelineRunInfo, AzurePipelineRunStatus


class BasePipelineAPI(ABC):
    def __init__(self, runner: RunnerModel):
         self.runner = runner

    @abstractmethod
    def trigger_pipeline(self, params: Dict) -> AzurePipelineRunInfo: pass

    @abstractmethod
    def get_run_status(self, run_id: str) -> AzurePipelineRunStatus: pass
