import time

from enum import Enum
from typing import List, Dict
from abc import ABC, abstractmethod

from src.pipeline import AzurePipelinesAPI, RunInfo, RunStatus
from src.util.logger import Logger


logger = Logger.get_logger(__name__)


class Mode(Enum):
    PARALLEL = ('parallel', 'It runs one pipeline after another')
    SEQUENTIAL = ('sequential', 'It runs all pipelines at once')

    def __init__(self, value: str, description: str):
        self._value_ = value
        self.description = description

    def get_values() -> List:
        values = list()
        for mode in Mode:
            values.append(mode.value)
        return values
    
    def get_help_message() -> str:
        message: str = ''
        is_first = True
        for mode in Mode:
            if not is_first:
                message += ' - '
            message += f'{str(mode.value)}: {str(mode.description)}'
            is_first = False
        return message


class PipelineBatchRunner:
    def __init__(self, pipelines: List[Dict], mode: Mode):
        self.pipelines = pipelines
        self.mode = mode

    def run_all(self):
        if self.mode == Mode.SEQUENTIAL:
            for pipeline in self.pipelines:
                PipelineRunnerSequentially(pipeline).run()
            return
        
        for pipeline in self.pipelines:
            PipelineRunnerInParallel(pipeline).run()


class PipelineRunner(ABC):
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self, pipeline: Dict):
        self.definition_id: str = pipeline['pipeline_definition_id']
        self.name: str = pipeline['pipeline_name']
        self.branch_name = 'main'
        if pipeline.get('branch_name'):
            self.branch_name = pipeline['branch_name']
        self.runs: List[Dict] = pipeline['runs']

    @abstractmethod
    def run(self): pass


class PipelineRunnerSequentially(PipelineRunner):
    def __init__(self, pipeline: Dict):
        super().__init__(pipeline)

    def run(self):
        logger.info(f'Starting sequentially {len(self.runs)} runs on pipeline {self.name} ({self.definition_id =})')

        for run in self.runs:
            parameters = run['parameters']
            execution = PipelineExecution(
                pipeline_name = self.name,
                pipeline_definition_id = self.definition_id,
                branch_name = self.branch_name,
                params = parameters
            )
            execution.start_and_wait()


class PipelineRunnerInParallel(PipelineRunner):
    def __init__(self, pipeline: Dict):
        super().__init__(pipeline)

    def run(self):
        logger.info(f'Starting at once {len(self.runs)} runs on pipeline {self.name} ({self.definition_id =})')
        executions = list()
        for run in self.runs:
            parameters = run['parameters']
            execution = PipelineExecution(
                pipeline_name = self.name,
                pipeline_definition_id = self.definition_id,
                branch_name = self.branch_name,
                params = parameters
            )
            execution.start()
            executions.append(execution)

        logger.info(f'Waiting {len(self.runs)} run(s) to complete')
        while executions:
            time.sleep(self.TIME_IN_SECONDS_TO_CHECK_STATUS)
            logger.info(f'Executions still running: {len(executions)}')
            for execution in executions:
                if execution.is_finished():
                    executions.remove(execution)
        logger.info(f'✅ All runs on pipeline {self.name} ({self.definition_id =}) had finished!')


class PipelineExecution:
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self,
                 pipeline_name: str,
                 pipeline_definition_id: str,
                 branch_name: str,
                 params: Dict):
        self.pipeline_name = pipeline_name
        self.pipeline_definition_id = pipeline_definition_id
        self.branch_name = branch_name
        self.params = params
        self.manager = AzurePipelinesAPI(
            name = self.pipeline_name,
            definition_id = self.pipeline_definition_id,
            branch_name = self.branch_name
        )
        self.run_info: RunInfo = None

    def start(self):
        if self.run_info:
            raise PipelineExecutionAlreadyRunning(f'The run {self.run_info.id} is already running!')
        self.run_info: RunInfo = self.manager.trigger_pipeline(self.params)

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
        return self.manager.get_run_status(run_id = self.run_info.id)


class PipelineExecutionAlreadyRunning(RuntimeError):
    pass


class PipelineExecutionIsNotRunning(RuntimeError):
    pass


class PipelineExecutionError(RuntimeError):
    pass
