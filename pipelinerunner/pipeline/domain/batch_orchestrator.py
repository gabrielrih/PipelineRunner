from typing import List

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.application.model import ExecutionOptions
from pipelinerunner.pipeline.domain.run_strategy import (
    SequentialPipelineExecutionStrategy,
    ParallelPipelineExecutionStrategy
)
from pipelinerunner.pipeline.domain.enums import PipelineExecutionMode


class PipelineBatchOrchestrator:
    def __init__(self, runners: List[RunnerModel], mode: PipelineExecutionMode, options: ExecutionOptions):
        self.runners = runners
        self.mode = mode
        self.options = options

    def run_all(self):
        if self.mode == PipelineExecutionMode.SEQUENTIAL:
            for runner in self.runners:
                SequentialPipelineExecutionStrategy(runner, self.options).run()
            return
        
        for runner in self.runners:
            ParallelPipelineExecutionStrategy(runner, self.options).run()
