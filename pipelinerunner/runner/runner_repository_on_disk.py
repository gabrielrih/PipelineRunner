from pathlib import Path
from typing import List, Optional


from pipelinerunner.runner.runner_repository import BaseRunnerRepository
from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.runner.runner_serializer import RunnerSerializer
from pipelinerunner.util.json import load_json_from_file, write_json_on_file


class RunnerRepositoryOnDisk(BaseRunnerRepository):
    def __init__(self, runners_dir: Path):
        self.serializer = RunnerSerializer()
        self.runners_dir = runners_dir
        self.initialize()

    def initialize(self) -> None:
        if not self.runners_dir.exists():
            self.runners_dir.mkdir(parents=True, exist_ok=True)

    def get(self, name: str) -> Optional[RunnerModel]:
        file_path = self._get_runner_file_path(name)
        
        if not file_path.exists():
            return None
        
        try:
            content = load_json_from_file(file_path)
            return self.serializer.deserialize(content)
        except Exception as e:
            # Log error if needed
            return None

    def _get_runner_file_path(self, name: str) -> Path:
        # Sanitize filename to avoid issues with special characters
        safe_name = name.replace('/', '_').replace('\\', '_')
        return self.runners_dir / f"{safe_name}.json"

    def get_all(self) -> List[RunnerModel]:
        templates = []
        
        for file_path in self.runners_dir.glob("*.json"):
            try:
                content = load_json_from_file(file_path)
                template = self.serializer.deserialize(content)
                templates.append(template)
            except Exception as e:
                # Log error and skip invalid files
                continue
        
        return templates

    def add(self, runner: RunnerModel) -> bool:
        file_path = self._get_runner_file_path(runner.name)
        
        # Check if template already exists
        if file_path.exists():
            return False
        
        try:
            content = self.serializer.serialize(runner)
            write_json_on_file(content, file_path)
            return True
        except Exception as e:
            # Log error if needed
            return False

    def update(self, name: str, runner: RunnerModel) -> bool:
        old_file_path = self._get_runner_file_path(name)
        
        if not old_file_path.exists():
            return False
        
        try:
            new_file_path = self._get_runner_file_path(runner.name)  # the name can change
            content = self.serializer.serialize(runner)
            write_json_on_file(content, new_file_path)
            # If name changed, remove old file
            if old_file_path != new_file_path:
                old_file_path.unlink()
            return True
        except Exception as e:
            # Log error if needed
            return False

    def remove(self, name: str) -> bool:
        file_path = self._get_runner_file_path(name)
        
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            # Log error if needed
            return False

    def exists(self, name: str) -> bool:
        file_path = self._get_runner_file_path(name)
        return file_path.exists()
