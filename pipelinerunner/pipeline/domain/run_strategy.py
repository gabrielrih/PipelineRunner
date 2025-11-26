import time

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.application.model import ExecutionOptions
from pipelinerunner.pipeline.domain.run import PipelineExecution
from pipelinerunner.pipeline.infrastructure.pipeline_api import BasePipelineAPI
from pipelinerunner.pipeline.infrastructure.factory_pipeline_api import PipelineAPIFactory
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


class BasePipelineExecutionStrategy(ABC):
    def __init__(self, runner: RunnerModel, options: ExecutionOptions):
        self.runner = runner
        self.options = options
        self._pipeline_api: Optional[BasePipelineAPI] = None

    def _create_pipeline_execution(self, params: Dict) -> PipelineExecution:
        return PipelineExecution(
            runner = self.runner,
            params = params,
            pipeline_api = self._get_or_create_api()
        )
    
    def _get_or_create_api(self) -> BasePipelineAPI:
        if self._pipeline_api is None:
            self._pipeline_api = PipelineAPIFactory.create(runner = self.runner, dry_run = self.options.dry_run)
        return self._pipeline_api

    @abstractmethod
    def run(self): pass


class SequentialPipelineExecutionStrategy(BasePipelineExecutionStrategy):
    def __init__(self, runner: RunnerModel, options: ExecutionOptions):
        super().__init__(runner, options)

    def run(self):
        logger.info(
            f'Starting sequentially {len(self.runner.runs)} runs on pipeline '
            f'"{self.runner.project_name}/{self.runner.pipeline_name}" '
            f'using branch "{self.runner.branch_name}" (definition_id = {self.runner.definition_id})'
        )

        for idx, run in enumerate(self.runner.runs, 1):
            logger.info(f'Processing run {idx}/{len(self.runner.runs)}')

            execution: PipelineExecution = self._create_pipeline_execution(params = run.parameters)
            execution.start()

            if execution.it_needs_approval() and self.options.auto_approve:    # it may take some seconds
                execution.approve()

            if self.options.wait:
                execution.wait_until_it_completes()

        logger.info(
            f'All sequential runs on pipeline "{self.runner.pipeline_name}" '
            f'(definition_id = {self.runner.definition_id}) completed!'
        )


class ParallelPipelineExecutionStrategy(BasePipelineExecutionStrategy):
    def __init__(self, runner: RunnerModel, options: ExecutionOptions):
        super().__init__(runner, options)
        self.approvals = ApprovalHandler(auto_approve = options.auto_approve)
        self.monitor = ExecutionMonitor()

    def run(self):
        logger.info(
            f'Starting at once {len(self.runner.runs)} runs on pipeline '
            f'"{self.runner.project_name}/{self.runner.pipeline_name}" '
            f'using branch "{self.runner.branch_name}" (definition_id = {self.runner.definition_id})'
        )
        executions = list()
        for run in self.runner.runs:  # starting all runs one by one
            execution: PipelineExecution = self._create_pipeline_execution(params = run.parameters)
            execution.start()
            executions.append(execution)
            
        if not self.options.wait:
            logger.success('All pipelines have been started (no waiting)! Check manually their status.')
            return

        self.approvals.handle(executions)  # handling approvals in parallel
        self.monitor.monitor(executions)  # monitoring all executions until completion
        
        logger.info(
            f'All runs on pipeline "{self.runner.pipeline_name}" '
            f'(definition_id = {self.runner.definition_id}) completed!'
        )


class ApprovalHandler:
    def __init__(self, auto_approve: bool = True):
        self.auto_approve = auto_approve

    def handle(self, executions: List[PipelineExecution]):
        logger.info('Checking for pending approvals...')
        needing = self._check_approvals_in_parallel(executions)
        if not needing:
            return
        if not self.auto_approve:
            logger.warning(f'{len(needing)} run(s) waiting manual approval')
            return
        approved = sum(1 for e in needing if e.approve())
        pending = len(needing) - approved
        if approved:
            logger.success(f'{approved} run(s) automatically approved')
        if pending:
            logger.warning(f'{pending} run(s) NOT approved. Manual intervention required.')

    def _check_approvals_in_parallel(self, executions: List[PipelineExecution]) -> List[PipelineExecution]:
        needing = []
        max_workers = min(len(executions), 10)
        
        with ThreadPoolExecutor(max_workers = max_workers) as executor:
            future_to_execution = {
                executor.submit(self._check_single_approval, execution): execution 
                for execution in executions
            }
            
            for future in as_completed(future_to_execution):
                execution = future_to_execution[future]
                try:
                    needs_approval = future.result()
                    if needs_approval:
                        needing.append(execution)
                except Exception as exc:
                    logger.error(f'Error checking approval for execution: {exc}')
        
        return needing

    def _check_single_approval(self, execution: PipelineExecution) -> bool:
        try:
            return execution.it_needs_approval()
        except Exception as exc:
            logger.error(f'Error checking approval for run {execution.run_info.id if execution.run_info else "unknown"}: {exc}')
            return False

class ExecutionMonitor:
    CHECK_INTERVAL = 5

    def monitor(self, executions: List[PipelineExecution]):
        logger.info(f'Waiting {len(executions)} run(s) to complete')
        total = len(executions)
        with logger.progress("Monitoring pipeline executions") as progress:
            task = progress.add_task("Active runs", total = total, completed = 0)

            while executions:
                time.sleep(self.CHECK_INTERVAL)
                finished = [ e for e in executions if e.is_finished() ]

                for e in finished:
                    executions.remove(e)
                    progress.update(task, completed = total - len(executions))

            progress.update(task, completed=total)
