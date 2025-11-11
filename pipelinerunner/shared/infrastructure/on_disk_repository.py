from abc import ABC
from pathlib import Path
from typing import List, Optional, Type, TypeVar

from pipelinerunner.shared.domain.base_on_disk_repository import BaseOnDiskRepository
from pipelinerunner.shared.domain.exceptions import SerializationException, FileSystemException
from pipelinerunner.shared.util.json import load_json_from_file, write_json_on_file
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


T = TypeVar("T")


class OnDiskRepository(BaseOnDiskRepository[T], ABC):
    def __init__(self, directory: Path, serializer: Type):
        self.directory = directory
        self.serializer = serializer
        self.initialize()

    def initialize(self) -> None:
        if not self.directory.exists():
            self.directory.mkdir(parents = True, exist_ok = True)

    def get(self, name: str) -> Optional[T]:
        file_path = self._get_file_path(name)
        
        if not file_path.exists():
            return None
        
        try:
            content = load_json_from_file(file_path)
            return self.serializer.deserialize(content)
        except Exception as e:
            raise SerializationException(
                f'Failed to deserialize entity from {file_path.name}!'
            ) from e

    def _get_file_path(self, name: str) -> Path:
        # Sanitize filename to avoid issues with special characters
        safe_name = name.replace('/', '_').replace('\\', '_')
        return self.directory / f"{safe_name}.json"

    def get_all(self) -> List[T]:
        data = []
        
        for file_path in self.directory.glob("*.json"):
            try:
                content = load_json_from_file(file_path)
                data.append(
                    self.serializer.deserialize(content)
                )
            except Exception as e:
                logger.warning(f'Skipping invalid file {file_path.name}: {e}')
                continue
        
        return data

    def add(self, content: T) -> bool:
        file_path = self._get_file_path(content.name)
        
        if file_path.exists():
            return False
        
        try:
            data = self.serializer.serialize(content)
            write_json_on_file(data, file_path)
            return True
        except Exception as e:
            raise SerializationException(
                f'Failed to serialize entity to {file_path.name}!'
            ) from e

    def update(self, name: str, content: T) -> bool:
        old_file_path = self._get_file_path(name)
        
        if not old_file_path.exists():
            return False
        
        try:
            new_file_path = self._get_file_path(content.name)  # the name can change
            content = self.serializer.serialize(content)
            write_json_on_file(content, new_file_path)
            # If name changed, remove old file
            if old_file_path != new_file_path:
                old_file_path.unlink()
            return True

        except Exception as e:
            raise SerializationException(
                f'Failed to serialize entity in {old_file_path.name}!'
            ) from e

    def remove(self, name: str) -> bool:
        file_path = self._get_file_path(name)
        
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            raise FileSystemException(
                f'Failed to delete file {file_path.name}!'
            ) from e

    def exists(self, name: str) -> bool:
        file_path = self._get_file_path(name)
        return file_path.exists()
