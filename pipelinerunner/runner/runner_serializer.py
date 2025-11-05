from typing import Dict, List, Union

from pipelinerunner.runner.runner_model import RunnerModel, RunModel


class RunnerSerializer:
    @staticmethod
    def serialize(runner: RunnerModel) -> Dict:
        """Convert RunnerModel (dataclass) -> JSON dict."""
        data = {
            "name": runner.name,
            "project_name": runner.project_name,
            "definition_id": runner.definition_id,
            "pipeline_name": runner.pipeline_name,
            "branch_name": runner.branch_name,
            "runs": []
        }

        if runner.runs:
            for r in runner.runs:
                data["runs"].append({ "parameters": r.parameters })

        return data

    @staticmethod
    def deserialize(data: Union[Dict, List[Dict]]) -> Union[RunnerModel, List[RunnerModel]]:
        """Convert JSON dict(s) -> RunnerModel or list of RunnerModel."""
        if isinstance(data, list):
            return [ RunnerSerializer._deserialize_single(item) for item in data ]
        return RunnerSerializer._deserialize_single(data)

    @staticmethod
    def _deserialize_single(data: Dict) -> RunnerModel:
        runs: List[RunModel] = []

        if data.get("runs"):
            for r in data["runs"]:
                runs.append(
                    RunModel(
                        parameters = r['parameters']
                    )
                )

        return RunnerModel(
            name = data['name'],
            project_name = data['project_name'],
            definition_id = data['definition_id'],
            pipeline_name = data['pipeline_name'],
            branch_name = data.get('branch_name', 'main'),
            runs = runs
        )
