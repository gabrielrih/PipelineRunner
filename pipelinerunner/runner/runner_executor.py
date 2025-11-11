from typing import List, Union, Dict

from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.runner.runner_repository import RunnerRepositoryFactory
from pipelinerunner.runner.runner_serializer import RunnerSerializer
from pipelinerunner.pipeline.pipeline_batch import PipelineBatchExecutor
from pipelinerunner.pipeline.pipeline_mode import PipelineExecutionMode
from pipelinerunner.repository.base import BaseOnDiskRepository
from pipelinerunner.util.json import load_json_from_file
from pipelinerunner.util.measure_time import measure_time
from pipelinerunner.util.logger import BetterLogger

logger = BetterLogger.get_logger(__name__)


class RunnerExecutorService:
    def __init__(self, mode: PipelineExecutionMode, repository: BaseOnDiskRepository = RunnerRepositoryFactory.create()):
        self.mode = mode
        self.repository = repository

    @measure_time
    def execute_from_name(self, name: str, no_wait: bool, dry_run: bool):
        runner = self.repository.get(name)
        if not runner:
            logger.warning(f'No runner found with name "{name}"')
            return
        logger.info(f'Starting single runner: {runner.name}')
        self._execute([ runner ], no_wait, dry_run)

    @measure_time
    def execute_from_file(self, filename: str, no_wait: bool, dry_run: bool):
        logger.info(f'Loading runners from {filename}')
        data: Union[Dict, List[Dict]] = load_json_from_file(filename)
        runners = RunnerSerializer.deserialize(data)
        if isinstance(runners, RunnerModel):
            runners = [ runners ]

        logger.info(f"Starting {len(runners)} runner(s)")
        self._print_runners_table(runners)
        self._execute(runners, no_wait, dry_run)

    def _execute(self, runners: List[RunnerModel], no_wait: bool, dry_run: bool):
        wait = not no_wait
        executor = PipelineBatchExecutor(runners, self.mode, wait, dry_run)
        executor.run_all()

    def _print_runners_table(self, runners: List[RunnerModel]):
        rows = [
            [ r.name, r.project_name, r.pipeline_name, r.branch_name ]
            for r in runners
        ]
        logger.print_table(
            title = f"Runners ({len(runners)})",
            columns = ["Name", "Project", "Pipeline", "Branch"],
            rows = rows
        )
