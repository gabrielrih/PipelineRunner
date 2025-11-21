from typing import List

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.domain.run_strategy import (
    SequentialPipelineExecutionStrategy,
    ParallelPipelineExecutionStrategy
)
from pipelinerunner.pipeline.domain.enums import PipelineExecutionMode


class PipelineBatchOrchestrator:
    def __init__(self,
                 runners: List[RunnerModel],
                 mode: PipelineExecutionMode,
                 wait: bool = True,
                 auto_approve: bool = True,
                 dry_run: bool = False):
        self.runners = runners
        self.mode = mode
        self.wait = wait
        self.auto_approve = auto_approve
        self.dry_run = dry_run

    def run_all(self):
        if self.mode == PipelineExecutionMode.SEQUENTIAL:
            for runner in self.runners:
                SequentialPipelineExecutionStrategy(runner, self.wait, self.auto_approve, self.dry_run).run()
            return
        
        for runner in self.runners:
            ParallelPipelineExecutionStrategy(runner, self.wait, self.auto_approve, self.dry_run).run()
