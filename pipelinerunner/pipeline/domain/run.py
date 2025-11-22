import time

from typing import Dict, Optional

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.application.model import (
    AzurePipelineRunInfo,
    AzurePipelineRunStatus,
    AzurePipelineApproval
)
from pipelinerunner.pipeline.infrastructure.pipeline_api import BasePipelineAPI
from pipelinerunner.pipeline.domain.enums import AzurePipelineRunState
from pipelinerunner.pipeline.domain.exceptions import PipelineExecutionAlreadyRunning, PipelineExecutionNotStarted, AzurePipelineAPIError
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


class PipelineExecution:
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self,
                 runner: RunnerModel,
                 params: Dict,
                 pipeline_api: BasePipelineAPI):
        self.params = params
        self.runner_name = runner.pipeline_name
        self.api = pipeline_api
        self.run_info: AzurePipelineRunInfo = None

    def start(self):
        if self.run_info:
            raise PipelineExecutionAlreadyRunning(
                f'The run {self.run_info.id} is already running!'
            )
        self.run_info: AzurePipelineRunInfo = self.api.trigger_pipeline(self.params)
        logger.info(f'Started run {self.run_info.id} for pipeline "{self.runner_name}"')

    def wait_until_it_completes(self):
        if not self.run_info:
            raise PipelineExecutionNotStarted('You must start the pipeline run before wait it for completing!')
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
            return
    
    def get_current_status(self) -> AzurePipelineRunStatus:
        if not self.run_info:
            raise PipelineExecutionNotStarted('You must start the pipeline run before check its status')
        return self.api.get_run_status(run_id = self.run_info.id)

    def is_finished(self) -> bool:
        status: AzurePipelineRunStatus = self.get_current_status()
        if status.is_completed():
            if status.is_successful():
                logger.success(f'Run {self.run_info.id} finished successfully.')
                return True
            logger.error(f'Run {self.run_info.id} finished with result = {status.result.name}.')
            return True
        return False

    def it_needs_approval(self, timeout: int = 30) -> bool:
        if not self.run_info:
            raise PipelineExecutionNotStarted('You must start the pipeline run before checking for approvals!')

        start_time = time.time()
        check_interval = 2

        # The timeout and retry logic is needed here due to delay on Azure API
        while (time.time() - start_time) < timeout:
            status = self.get_current_status()        
            if status.state == AzurePipelineRunState.IN_PROGRESS:
                logger.debug(f'Checking for approval in run {self.run_info.id}...')
                approval: Optional[AzurePipelineApproval] = self.api.get_approval_status(run_id = self.run_info.id)
                
                if approval and approval.status == 'pending':
                    logger.info(f'Run {self.run_info.id} needs approval')
                    return True
                
                if time.time() - start_time > 10:
                    logger.info(f'Run {self.run_info.id} does not need approval')
                    return False

            if status.state == AzurePipelineRunState.COMPLETED:
                logger.info(f'Run {self.run_info.id} already completed, no approval needed')
                return False
            
            time.sleep(check_interval)

        logger.warning(f'Timeout checking approval for run {self.run_info.id}, assuming no approval needed')
        return False

    def approve(self) -> bool:
        if not self.run_info:
            raise PipelineExecutionNotStarted('You must start the pipeline run before approve it!')
        
        approval: Optional[AzurePipelineApproval] = self.api.get_approval_status(run_id = self.run_info.id)
        if not approval:
            logger.info(f'There is no need to approve the run {self.run_info.id}')
            return True

        if approval.status != 'pending':
            logger.debug(f'Approval for run {self.run_info.id} is not pending (status: {approval.status})')
            return True
        
        try:
            self.api.approve_run(run_id = self.run_info.id, approval_id = approval.id)        
            logger.success(f'Run {self.run_info.id} was successfully approved!')
            return True

        except AzurePipelineAPIError as exc:
            logger.error(str(exc))
            return False
