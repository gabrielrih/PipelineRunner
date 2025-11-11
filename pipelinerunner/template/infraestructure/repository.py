from pathlib import Path
from typing import List, Optional

from pipelinerunner.template.application.template_model import TemplateModel
from pipelinerunner.template.domain.serializer import TemplateSerializer
from pipelinerunner.repository.base import BaseOnDiskRepository
from pipelinerunner.repository.on_disk import OnDiskRepository


class TemplateRepositoryFactory:
    @staticmethod
    def create() -> BaseOnDiskRepository:
        path = Path.home() / '.pipelinerunner' / 'templates'
        return TemplateOnDiskRepository(path)


class TemplateOnDiskRepository(OnDiskRepository[TemplateModel]):
    def __init__(self, directory: Path):
        super().__init__(
            directory = directory,
            serializer = TemplateSerializer()
        )

    def get(self, name: str) -> Optional[TemplateModel]:
        return super().get(name)

    def get_all(self) -> List[TemplateModel]:
        return super().get_all()

    def add(self, template: TemplateModel) -> bool:
        return super().add(content = template)

    def update(self, name: str, template: TemplateModel) -> bool:
        return super().update(name = name, content = template)

    def remove(self, name: str) -> bool:
        return super().remove(name = name)
    
    def exists(self, name: str) -> bool:
        return super().exists(name = name)

