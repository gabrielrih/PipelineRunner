from typing import List

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.application.execution_mode import PipelineExecutionMode
from pipelinerunner.pipeline.domain.executor import SequentialPipelineExecutor, ParallelPipelineExecutor


class PipelineBatchExecutor:
    def __init__(self,
                 runners: List[RunnerModel],
                 mode: PipelineExecutionMode,
                 wait: bool = True,
                 dry_run: bool = False):
        self.runners = runners
        self.mode = mode
        self.wait = wait
        self.dry_run = dry_run

    def run_all(self):
        if self.mode == PipelineExecutionMode.SEQUENTIAL:
            for runner in self.runners:
                SequentialPipelineExecutor(runner, self.wait, self.dry_run).run()
            return
        
        for runner in self.runners:
            ParallelPipelineExecutor(runner, self.wait, self.dry_run).run()
