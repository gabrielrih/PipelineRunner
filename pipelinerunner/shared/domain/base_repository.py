from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar, Optional


T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get(self, identifier: str) -> Optional[T]: pass
    
    @abstractmethod
    def get_all(self) -> List[T]: pass
    
    @abstractmethod
    def add(self, entity: T) -> bool: pass
    
    @abstractmethod
    def update(self, identifier: str, entity: T) -> bool: pass
    
    @abstractmethod
    def remove(self, identifier: str) -> bool: pass

    @abstractmethod
    def exists(self, identifier: str) -> bool: pass
