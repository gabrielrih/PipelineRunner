from abc import ABC, abstractmethod
from typing import List, TypeVar, Optional

from pipelinerunner.shared.domain.base_repository import BaseRepository


T = TypeVar("T")  # T representa qualquer tipo (usado para parametrizar a classe)


class BaseOnDiskRepository(BaseRepository[T], ABC):
    @abstractmethod
    def initialize(self) -> None: pass

    @abstractmethod
    def get(self, name: str) -> Optional[T]: pass

    @abstractmethod
    def get_all(self) -> List[T]: pass

    @abstractmethod
    def add(self, content: T) -> bool: pass

    @abstractmethod
    def update(self, name: str, content: T) -> bool: pass

    @abstractmethod
    def remove(self, name: str) -> bool: pass

    @abstractmethod
    def exists(self, name: str) -> bool: pass
