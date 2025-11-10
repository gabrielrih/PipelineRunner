import time

from abc import ABC, abstractmethod

from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.pipeline.pipeline_execution import PipelineExecution
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


class BasePipelineExecutor(ABC):
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self, runner: RunnerModel, wait: bool = True, dry_run: bool = False):
        self.runner = runner
        self.wait = wait
        self.dry_run = dry_run

    @abstractmethod
    def run(self): pass


class SequentialPipelineExecutor(BasePipelineExecutor):
    def __init__(self, runner: RunnerModel, wait: bool = True, dry_run: bool = False):
        super().__init__(runner, wait, dry_run)

    def run(self):
        logger.info(f'Starting sequentially {len(self.runner.runs)} runs on pipeline "{self.runner.project_name}/{self.runner.pipeline_name}" using branch "{self.runner.branch_name}" (definition_id = {self.runner.definition_id})')

        for run in self.runner.runs:
            execution = PipelineExecution(self.runner, run.parameters, self.dry_run)
            if self.wait:
                execution.start_and_wait()
            else:
                execution.start()


class ParallelPipelineExecutor(BasePipelineExecutor):
    def __init__(self, runner: RunnerModel, wait: bool = True, dry_run: bool = False):
        super().__init__(runner, wait, dry_run)

    def run(self):
        logger.info(
            f'Starting at once {len(self.runner.runs)} runs on pipeline '
            f'"{self.runner.project_name}/{self.runner.pipeline_name}" '
            f'using branch "{self.runner.branch_name}" (definition_id = {self.runner.definition_id})'
        )
        executions = list()
        for run in self.runner.runs:
            execution = PipelineExecution(self.runner, run.parameters, self.dry_run)
            execution.start()
            executions.append(execution)

        if not self.wait:
            logger.success('All pipelines started (not waiting)!')
            return

        logger.info(f'Waiting {len(self.runner.runs)} run(s) to complete')

        total = len(executions)
        with logger.progress("Monitoring pipeline executions") as progress:
            task = progress.add_task("Active runs", total = total, completed = 0)
            while executions:
                time.sleep(self.TIME_IN_SECONDS_TO_CHECK_STATUS)
                finished = [ e for e in executions if e.is_finished() ] 
                for e in finished:
                    executions.remove(e)
                    progress.update(task, completed = total - len(executions))
            progress.update(task, completed = total)

        logger.success(
            f'All runs on pipeline "{self.runner.pipeline_name}" '
            f'(definition_id = {self.runner.definition_id}) completed!'
        )
