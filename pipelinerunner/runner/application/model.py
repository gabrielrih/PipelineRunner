from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class RunModel:
    parameters: Dict


@dataclass
class RunnerModel:
    name: str  # imutable
    project_name: str
    definition_id: str
    pipeline_name: str
    runs: List[RunModel]
    branch_name: Optional[str] = 'main'

    def __str__(self) -> str:
        run_count = len(self.runs) if self.runs else 0
        return (
            f'Runner "{self.name}" → Project: {self.project_name}, '
            f'Pipeline: {self.pipeline_name} [Branch: {self.branch_name}] '
            f'({run_count} configured runs)'
        )

    def to_dict(self) -> Dict:
        return asdict(self)
