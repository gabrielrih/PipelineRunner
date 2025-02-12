import time

from typing import Dict

from pipelinerunner.pipeline.parser import Pipeline
from pipelinerunner.pipeline.api import AzurePipelinesAPI, RunInfo, RunStatus
from pipelinerunner.util.logger import Logger


logger = Logger.get_logger(__name__)


class PipelineExecution:
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self, pipeline: Pipeline, params: Dict):
        self.params = params
        self.pipeline_name = pipeline.pipeline_name
        self.api = AzurePipelinesAPI(pipeline = pipeline)
        self.run_info: RunInfo = None

    def start(self):
        if self.run_info:
            raise PipelineExecutionAlreadyRunning(f'The run {self.run_info.id} is already running!')
        self.run_info: RunInfo = self.api.trigger_pipeline(self.params)

    def start_and_wait(self):
        self.start()
        logger.info(f'Waiting the run {self.run_info.id } to complete')
        current_status = self.run_info.status
        while current_status != RunStatus.COMPLETED:
            time.sleep(self.TIME_IN_SECONDS_TO_CHECK_STATUS)
            current_status: RunStatus = self.get_current_status()
            if current_status == RunStatus.CANCELED:
                raise PipelineExecutionError(f'The run {self.run_info.id} on pipeline {self.pipeline_name} was CANCELED! Exiting. Please check the runs manually.')
        logger.info(f'✅ The run {self.run_info.id} on pipeline {self.pipeline_name} ended successfully!')

    def is_finished(self) -> bool:
        current_status: RunStatus = self.get_current_status()
        if current_status == RunStatus.COMPLETED:
            return True
        if current_status == RunStatus.CANCELED:
            raise PipelineExecutionError(f'The run {self.run_info.id} on pipeline {self.pipeline_name} was CANCELED! Exiting. Please check the runs manually.')
        return False
    
    def get_current_status(self) -> RunStatus:
        if not self.run_info:
            raise PipelineExecutionIsNotRunning('You must start the pipeline run before check its status')
        return self.api.get_run_status(run_id = self.run_info.id)


class PipelineExecutionAlreadyRunning(RuntimeError):
    pass


class PipelineExecutionIsNotRunning(RuntimeError):
    pass


class PipelineExecutionError(RuntimeError):
    pass
