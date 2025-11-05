import time

from typing import Dict

from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.pipeline.external.azure_pipeline import (
    AzurePipelineRunInfo,
    AzurePipelineRunStatus,
    BasePipelineAPI,
    AzurePipelineAPI,
    DryRunPipelineAPI
)
from pipelinerunner.util.logger import Logger


logger = Logger.get_logger(__name__)


class PipelineExecution:
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self,
                 runner: RunnerModel,
                 params: Dict,
                 dry_run: bool = False):
        self.params = params
        self.dry_run = dry_run
        self.runner_name = runner.pipeline_name
        self.api: BasePipelineAPI = DryRunPipelineAPI(runner) if dry_run else AzurePipelineAPI(runner)
        self.run_info: AzurePipelineRunInfo = None

    def start(self):
        if self.run_info:
            raise PipelineExecutionAlreadyRunning(f'The run {self.run_info.id} is already running!')
        self.run_info: AzurePipelineRunInfo = self.api.trigger_pipeline(self.params)

    def start_and_wait(self):
        self.start()
        logger.info(f'Waiting the run {self.run_info.id } to complete')
        current_status = self.run_info.status
        while current_status != AzurePipelineRunStatus.COMPLETED:
            time.sleep(self.TIME_IN_SECONDS_TO_CHECK_STATUS)
            current_status: AzurePipelineRunStatus = self.get_current_status()
            if current_status == AzurePipelineRunStatus.CANCELED:
                raise PipelineExecutionError(f'The run {self.run_info.id} on pipeline {self.runner_name} was CANCELED! Exiting. Please check the runs manually.')
        logger.info(f'✅ The run {self.run_info.id} on pipeline {self.runner_name} ended successfully!')

    def is_finished(self) -> bool:
        current_status: AzurePipelineRunStatus = self.get_current_status()
        if current_status == AzurePipelineRunStatus.COMPLETED:
            return True
        if current_status == AzurePipelineRunStatus.CANCELED:
            raise PipelineExecutionError(f'The run {self.run_info.id} on pipeline {self.runner_name} was CANCELED! Exiting. Please check the runs manually.')
        return False
    
    def get_current_status(self) -> AzurePipelineRunStatus:
        if not self.run_info:
            raise PipelineExecutionNotStarted('You must start the pipeline run before check its status')
        return self.api.get_run_status(run_id = self.run_info.id)


class PipelineExecutionAlreadyRunning(RuntimeError): pass


class PipelineExecutionNotStarted(RuntimeError): pass


class PipelineExecutionError(RuntimeError): pass
