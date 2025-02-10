from src.util.json import load_json_from_file

from typing import List, Dict, Optional

from dataclasses import dataclass


@dataclass
class Run:
    parameters: Dict


@dataclass
class Pipeline:
    project_name: str
    definition_id: str
    pipeline_name: str
    runs: List[Run]
    branch_name: Optional[str] = 'main'

    @classmethod
    def from_json_file(cls, path: str) -> List['Pipeline']:
        content = load_json_from_file(path)
        if isinstance(content, Dict):
            content = [ content ]            
        return cls.from_list(content)

    @classmethod
    def from_list(cls, content: List[Dict]) -> List['Pipeline']:
        pipelines = list()
        for pipeline in content:
            runs = list()
            for run in pipeline['runs']:
                runs.append(
                    Run(parameters = run['parameters'])
                )
            pipelines.append(
                Pipeline(
                    project_name = pipeline['project_name'],
                    definition_id = pipeline['definition_id'],
                    pipeline_name = pipeline['pipeline_name'],
                    branch_name = pipeline['branch_name'],
                    runs = runs
                )
            )
        return pipelines
