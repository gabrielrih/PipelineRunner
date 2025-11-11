from pathlib import Path
from typing import Optional
from pipelinerunner.runner.infrastructure.repository import RunnerRepositoryFactory
from pipelinerunner.runner.domain.serializer import RunnerSerializer
from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.shared.application.base_on_disk_repository import BaseOnDiskRepository
from pipelinerunner.shared.util.json import write_json_on_file
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


class RunnerExporterService:
    def __init__(self, repository: BaseOnDiskRepository = RunnerRepositoryFactory.create()):
        self.repository = repository
        self.serializer = RunnerSerializer()

    def export(self, name: str, output: Optional[str] = None) -> bool:
        runner: Optional[RunnerModel] = self.repository.get(name)
        if not runner:
            logger.warning(f'No runner found using the name "{name}"')
            return False

        output_path = self._resolve_output_path(name, output)
        try:
            data = self.serializer.serialize(runner)
            output_path.parent.mkdir(parents = True, exist_ok = True)
            write_json_on_file(data, output_path)

            logger.success(f'Runner "{name}" exported successfully!')
            logger.message(f'   File: {output_path.absolute()}')
            logger.message(f'   Runs: {len(runner.runs)}')
            return True

        except Exception as e:
            logger.error(f'Failed to export runner: {str(e)}')
            return False

    def _resolve_output_path(self, name: str, output: Optional[str]) -> Path:
        if not output:
            output = f"{name}.json"
        if not output.endswith(".json"):
            output += ".json"
        return Path(output)
