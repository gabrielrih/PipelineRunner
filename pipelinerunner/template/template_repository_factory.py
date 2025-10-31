from pathlib import Path

from pipelinerunner.template.template_repository import BaseTemplateRepository
from pipelinerunner.template.template_repository_on_disk import TemplateRepositoryOnDisk


class TemplateRepositoryFactory:
    @staticmethod
    def create() -> BaseTemplateRepository:
        path = Path.home() / '.pipelinerunner'
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / 'templates.json'
        return TemplateRepositoryOnDisk(file_path)
