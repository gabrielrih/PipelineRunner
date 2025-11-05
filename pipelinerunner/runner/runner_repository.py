from pathlib import Path
from typing import List, Optional

from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.runner.runner_serializer import RunnerSerializer
from pipelinerunner.repository.base import BaseOnDiskRepository
from pipelinerunner.repository.on_disk import OnDiskRepository


class RunnerRepositoryFactory:
    @staticmethod
    def create() -> BaseOnDiskRepository:
        path = Path.home() / '.pipelinerunner' / 'runners'
        return RunnerOnDiskRepository(path)


class RunnerOnDiskRepository(OnDiskRepository[RunnerModel]):
    def __init__(self, directory: Path):
        super().__init__(
            directory = directory,
            serializer = RunnerSerializer()
        )

    def get(self, name: str) -> Optional[RunnerModel]:
        return super().get(name)
    
    def get_all(self) -> List[RunnerModel]:
        return super().get_all()
    
    def add(self, runner: RunnerModel) -> bool:
        return super().add(content = runner)
    
    def update(self, name: str, runner: RunnerModel) -> bool:
        return super().update(name = name, content = runner)
    
    def remove(self, name: str) -> bool:
        return super().remove(name)
