import random

from typing import Dict

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.domain.pipeline_api import BasePipelineAPI
from pipelinerunner.pipeline.application.model import AzurePipelineRunInfo, AzurePipelineRunStatus
from pipelinerunner.pipeline.domain.enums import AzurePipelineRunState, AzurePipelineRunResult
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


class DryRunPipelineAPI(BasePipelineAPI):
    def __init__(self, runner: RunnerModel):
        super().__init__(runner)

    def trigger_pipeline(self, params: Dict) -> AzurePipelineRunInfo:
        fake_id = random.randint(10000, 99999)
        logger.info(f"[DRY RUN] Would trigger pipeline '{self.runner.pipeline_name}' "
                    f"with params: {params} -> Fake run_id={fake_id}")
        
        status = AzurePipelineRunStatus(
            state = AzurePipelineRunState.IN_PROGRESS,
            result = AzurePipelineRunResult.UNKNOWN 
        )
        return AzurePipelineRunInfo(id = fake_id, status = status)
    
    def get_run_status(self, *args, **kwargs) -> AzurePipelineRunStatus:
        state = AzurePipelineRunState.COMPLETED
        result = AzurePipelineRunResult.SUCCEEDED
        return AzurePipelineRunStatus(state = state, result = result)
