from pathlib import Path
from typing import List, Optional

from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.runner.domain.serializer import RunnerSerializer
from pipelinerunner.shared.application.base_on_disk_repository import BaseOnDiskRepository
from pipelinerunner.shared.infrastructure.on_disk_repository import OnDiskRepository


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
