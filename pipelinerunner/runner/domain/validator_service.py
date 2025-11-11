from pathlib import Path
from typing import Union, Dict, List
from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.runner.domain.serializer import RunnerSerializer
from pipelinerunner.shared.util.json import load_json_from_file
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


class RunnerValidatorService:
    def __init__(self):
        self.serializer = RunnerSerializer()

    def validate_file(self, file_path: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            logger.error(f'File not found: {path.absolute()}')
            return False

        try:
            logger.info(f'Validating file: {path.absolute()}')
            data: Union[Dict, List[Dict]] = load_json_from_file(path)
            runners = self._deserialize(data)
            self._log_summary(runners)
            return True
        
        except Exception as e:
            self._handle_error(e, path)
            return False

    def _deserialize(self, data: Union[Dict, List[Dict]]) -> List[RunnerModel]:
        runners = self.serializer.deserialize(data)
        if isinstance(runners, RunnerModel):
            runners = [ runners ]
        return runners

    def _log_summary(self, runners: List[RunnerModel]) -> None:
        logger.success('The file format is valid!')
        logger.info(f'Total runners: {len(runners)}')
        for idx, runner in enumerate(runners, 1):
            rows = [
                ["Name", runner.name],
                ["Project", runner.project_name],
                ["Pipeline", runner.pipeline_name],
                ["Definition ID", runner.definition_id],
                ["Branch", runner.branch_name],
                ["Runs", len(runner.runs)],
            ]
            logger.print_table(
                title=f"Runner #{idx}",
                columns=["Field", "Value"],
                rows=rows,
            )

    def _handle_error(self, e: Exception, path: Path) -> None:
        error_message = (
            f"Validation failed for {path.name}!\n\n"
            "🔍 Error details:\n"
            f"   {type(e).__name__}: {str(e)}\n\n"
            "💡 Common issues:\n"
            "   • Missing required fields (name, project_name, definition_id, pipeline_name)\n"
            "   • Invalid JSON syntax\n"
            "   • Incorrect data types\n"
            "   • Missing \"runs\" array"
        )
        logger.error(error_message)
