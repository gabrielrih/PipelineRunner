from abc import ABC, abstractmethod
from typing import List

from pipelinerunner.runner.runner_model import RunnerModel


class BaseRunnerRepository(ABC):
    @abstractmethod
    def initialize(self): pass

    @abstractmethod
    def get(self, name: str) -> RunnerModel: pass

    @abstractmethod
    def get_all(self) -> List[RunnerModel]: pass

    @abstractmethod
    def add(self, runner: RunnerModel) -> bool: pass

    @abstractmethod
    def update(self, name: str, runner: RunnerModel) -> bool: pass

    @abstractmethod
    def remove(self, name: str) -> bool: pass
