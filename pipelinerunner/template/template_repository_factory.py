from pathlib import Path

from pipelinerunner.template.template_repository import BaseTemplateRepository
from pipelinerunner.template.template_repository_on_disk import TemplateRepositoryOnDisk


class TemplateRepositoryFactory:
    @staticmethod
    def create() -> BaseTemplateRepository:
        path = Path.home() / '.pipelinerunner' / 'templates'
        return TemplateRepositoryOnDisk(path)
