from pathlib import Path

from pipelinerunner.runner.runner_repository import BaseRunnerRepository
from pipelinerunner.runner.runner_repository_on_disk import RunnerRepositoryOnDisk


class RunnerRepositoryFactory:
    @staticmethod
    def create() -> BaseRunnerRepository:
        path = Path.home() / '.pipelinerunner' / 'runners'
        return RunnerRepositoryOnDisk(path)
