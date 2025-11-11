import time

from typing import Dict

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.application.model import AzurePipelineRunInfo, AzurePipelineRunStatus
from pipelinerunner.pipeline.domain.pipeline_api import BasePipelineAPI
from pipelinerunner.pipeline.domain.exceptions import (
    PipelineExecutionAlreadyRunning,
    PipelineExecutionNotStarted
)
from pipelinerunner.pipeline.infrastructure.azure_pipeline_api import AzurePipelineAPI
from pipelinerunner.pipeline.infrastructure.dry_run_pipeline_api import DryRunPipelineAPI
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


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
            raise PipelineExecutionAlreadyRunning(
                f'The run {self.run_info.id} is already running!'
            )
        self.run_info: AzurePipelineRunInfo = self.api.trigger_pipeline(self.params)
        logger.info(f'Started run {self.run_info.id} for pipeline "{self.runner_name}"')

    def start_and_wait(self):
        self.start()
        logger.info(f'Waiting for run {self.run_info.id } to complete...')

        while True:
            time.sleep(self.TIME_IN_SECONDS_TO_CHECK_STATUS)
            status: AzurePipelineRunStatus = self.get_current_status()
            logger.debug(f'Current status of run {self.run_info.id}: {status}')

            if status.is_running():
                continue

            if not status.is_completed():
                logger.error(f'Run {self.run_info.id} on pipeline {self.runner_name} ended abnormally with state = {status.state.name}')
                return

            if not status.is_successful():
                logger.error(f'Run {self.run_info.id} on pipeline {self.runner_name} failed with result = {status.result.name}')
                return

            logger.success(f'Run {self.run_info.id} on pipeline {self.runner_name} completed successfully!')

    def is_finished(self) -> bool:
        status: AzurePipelineRunStatus = self.get_current_status()
        if status.is_completed():
            if status.is_successful():
                logger.success(f'Run {self.run_info.id} finished successfully.')
                return True
            logger.error(f'Run {self.run_info.id} finished with result = {status.result.name}.')
            return True
        return False
    
    def get_current_status(self) -> AzurePipelineRunStatus:
        if not self.run_info:
            raise PipelineExecutionNotStarted('You must start the pipeline run before check its status')
        return self.api.get_run_status(run_id = self.run_info.id)
