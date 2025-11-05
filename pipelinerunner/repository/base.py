from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar


T = TypeVar("T")  # T representa qualquer tipo (usado para parametrizar a classe)


class BaseOnDiskRepository(ABC, Generic[T]):
    @abstractmethod
    def initialize(self) -> None: pass

    @abstractmethod
    def get(self, name: str) -> T: pass

    @abstractmethod
    def get_all(self) -> List[T]: pass

    @abstractmethod
    def add(self, content: T) -> bool: pass

    @abstractmethod
    def update(self, name: str, content: T) -> bool: pass

    @abstractmethod
    def remove(self, name: str) -> bool: pass
