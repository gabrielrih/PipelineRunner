from typing import Dict, List
from pipelinerunner.template.template_model import TemplateModel
from pipelinerunner.template.parameter_model import TemplateParameter, TemplateParameterType


class TemplateSerializer:
    @staticmethod
    def serialize(template: TemplateModel) -> Dict:
        """Convert TemplateModel (dataclass) -> JSON dict."""
        data = {
            "name": template.name,
            "description": template.description,
            "parameters": []
        }

        if template.parameters:
            for p in template.parameters:
                data["parameters"].append({
                    "name": p.name,
                    "type": p.type.value if isinstance(p.type, TemplateParameterType) else p.type,
                    "is_required": p.is_required,
                    "default_value": p.default_value,
                    "options": p.options,
                })

        return data

    @staticmethod
    def deserialize(data: Dict) -> TemplateModel:
        """Convert JSON dict -> TemplateModel (dataclass)."""
        params: List[TemplateParameter] = []

        if data.get("parameters"):
            for p in data["parameters"]:
                params.append(
                    TemplateParameter(
                        name=p["name"],
                        type=TemplateParameterType(p["type"]),
                        is_required=p["is_required"],
                        default_value=p.get("default_value"),
                        options=p.get("options"),
                    )
                )

        return TemplateModel(
            name=data["name"],
            description=data.get("description", ""),
            parameters=params,
        )
