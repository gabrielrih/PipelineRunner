from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from pipelinerunner.template.parameter_model import TemplateParameter


@dataclass
class TemplateModel:
    name: str   # immutable
    description: str
    parameters: Optional[List[TemplateParameter]] = None

    def __str__(self) -> str:
        param_count = len(self.parameters) if self.parameters else 0
        parameter_names = [ parameter.name for parameter in self.parameters ]
        return (
            f'Template "{self.name}" -> Description: {self.description}, '
            f'Parameters: {parameter_names} '
            f'({param_count} parameters)'
        )

    def to_dict(self) -> Dict:
        return asdict(self)
