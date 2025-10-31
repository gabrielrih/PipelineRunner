from typing import List, Optional
from dataclasses import dataclass

from pipelinerunner.template.parameter_model import TemplateParameter


@dataclass
class TemplateModel:
    name: str
    description: str
    parameters: Optional[List[TemplateParameter]] = None
