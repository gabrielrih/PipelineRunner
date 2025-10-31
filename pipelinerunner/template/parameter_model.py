from enum import Enum
from typing import List, Any, Optional
from dataclasses import dataclass


@dataclass
class TemplateParameter:
    name: str
    type: 'TemplateParameterType'
    is_required: bool = False
    default_value: Optional[Any] = None
    options: Optional[List[Any]] = None


class TemplateParameterType(Enum):
    STRING = 'string'
    NUMBER = 'number'
    BOOLEAN = 'boolean'

    @classmethod
    def values(cls) -> List[str]:
        return [ type.value for type in cls ]
