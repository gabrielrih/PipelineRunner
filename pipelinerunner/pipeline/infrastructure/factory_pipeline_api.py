from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.pipeline.infrastructure.pipeline_api import BasePipelineAPI
from pipelinerunner.pipeline.infrastructure.azure_pipeline_api import AzurePipelineAPI
from pipelinerunner.pipeline.infrastructure.dry_run_pipeline_api import DryRunPipelineAPI


class PipelineAPIFactory:
    @staticmethod
    def create(runner: RunnerModel, dry_run: bool = False) -> BasePipelineAPI:
        if dry_run:
            return DryRunPipelineAPI(runner)
        return AzurePipelineAPI(runner)
