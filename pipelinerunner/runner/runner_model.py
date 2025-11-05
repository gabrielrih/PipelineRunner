from typing import List, Dict, Optional
from dataclasses import dataclass


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
