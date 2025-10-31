from abc import ABC, abstractmethod
from typing import List

from pipelinerunner.template.template_model import TemplateModel


class BaseTemplateRepository(ABC):
    @abstractmethod
    def initialize(self): pass

    @abstractmethod
    def get(self, name: str) -> TemplateModel: pass

    @abstractmethod
    def get_all(self) -> List[TemplateModel]: pass

    @abstractmethod
    def add(self, template: TemplateModel) -> bool: pass

    @abstractmethod
    def update(self, name: str, template: TemplateModel) -> bool: pass

    @abstractmethod
    def remove(self, name: str) -> bool: pass
