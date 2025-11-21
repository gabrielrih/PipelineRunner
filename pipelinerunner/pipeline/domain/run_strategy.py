import time

from abc import ABC, abstractmethod
from typing import List

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.domain.run import PipelineExecution
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


class BasePipelineExecutionStrategy(ABC):
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self,
                 runner: RunnerModel,
                 wait: bool = True,
                 auto_approve: bool = True,
                 dry_run: bool = False):
        self.runner = runner
        self.wait = wait
        self.auto_approve = auto_approve
        self.dry_run = dry_run

    @abstractmethod
    def run(self): pass


class SequentialPipelineExecutionStrategy(BasePipelineExecutionStrategy):
    def __init__(self, runner: RunnerModel, wait: bool = True, auto_approve: bool = True, dry_run: bool = False):
        super().__init__(runner, wait, auto_approve, dry_run)

    def run(self):
        logger.info(
            f'Starting sequentially {len(self.runner.runs)} runs on pipeline '
            f'"{self.runner.project_name}/{self.runner.pipeline_name}" '
            f'using branch "{self.runner.branch_name}" (definition_id = {self.runner.definition_id})'
        )

        for idx, run in enumerate(self.runner.runs, 1):
            logger.info(f'Processing run {idx}/{len(self.runner.runs)}')

            execution = PipelineExecution(self.runner, run.parameters, self.dry_run)
            execution.start()

            it_needs_approval = execution.it_needs_approval()  # it may take some seconds
            if it_needs_approval and self.auto_approve:
                execution.approve()

            if self.wait:
                execution.wait_until_it_completes()

        logger.info(
            f'All runs on pipeline "{self.runner.pipeline_name}" '
            f'(definition_id = {self.runner.definition_id}) completed!'
        )


class ParallelPipelineExecutionStrategy(BasePipelineExecutionStrategy):
    def __init__(self, runner: RunnerModel, wait: bool = True, auto_approve: bool = True, dry_run: bool = False):
        super().__init__(runner, wait, auto_approve, dry_run)

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
            logger.success('All pipelines have been started (no waiting)! Check manually their status.')
            return

        self._handle_approvals(executions = executions)

        self._monitor_executions(executions = executions)

        logger.info(
            f'All runs on pipeline "{self.runner.pipeline_name}" '
            f'(definition_id = {self.runner.definition_id}) completed!'
        )

    def _handle_approvals(self, executions: List[PipelineExecution]):
        logger.info('Checking for pending approvals...')
        # TO DO: To make this check run in parallel
        runs_needing_approval = [ e for e in executions if e.it_needs_approval() ]

        if runs_needing_approval:
            if self.auto_approve:
                qty_approved = sum(1 for e in runs_needing_approval if e.approve())
                qty_error = len(runs_needing_approval) - qty_approved
                
                if qty_approved > 0:
                    logger.success(f'{qty_approved} run(s) automatically approved')
                if qty_error > 0:
                    logger.warning(f'{qty_error} run(s) not approved. Check them manually!')
                
                logger.info(f'Waiting {len(executions)} run(s) to complete, {qty_error} run(s) to be manually approved!')
                return
                
            logger.info(f'Waiting {len(executions)} run(s) to complete, {len(runs_needing_approval)} run(s) to be manually approved')
            return

        logger.info(f'Waiting {len(executions)} run(s) to complete')

    def _monitor_executions(self, executions: List[PipelineExecution]):
        total = len(executions)
        with logger.progress("Monitoring pipeline executions") as progress:
            task = progress.add_task("Active runs", total = total, completed = 0)
            while executions:
                time.sleep(self.TIME_IN_SECONDS_TO_CHECK_STATUS)
                finished = [ e for e in executions if e.is_finished() ]
                for e in finished:
                    executions.remove(e)
                    progress.update(task, completed = total - len(executions))
            progress.update(task, completed=total)
