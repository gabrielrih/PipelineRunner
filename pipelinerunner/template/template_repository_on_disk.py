from pathlib import Path
from typing import List, Dict, Optional


from pipelinerunner.template.template_repository import BaseTemplateRepository
from pipelinerunner.template.template_model import TemplateModel
from pipelinerunner.template.template_serializer import TemplateSerializer
from pipelinerunner.util.json import load_json_from_file, write_json_on_file


class TemplateRepositoryOnDisk(BaseTemplateRepository):
    def __init__(self, file_path: Path):
        self.serializer = TemplateSerializer()
        self.file_path = file_path
        if not self.file_path.exists():
            self.initialize()

    def initialize(self) -> None:
        content: Dict = {"templates": []}
        write_json_on_file(content, self.file_path)

    def get(self, name: str) -> Optional[TemplateModel]:
        content: Dict = load_json_from_file(self.file_path)
        templates: List[Dict] = content["templates"]
        for t in templates:
            if t["name"] != name:
                continue
            return self.serializer.deserialize(t)
        return None

    def get_all(self) -> List[TemplateModel]:
        content: Dict = load_json_from_file(self.file_path)
        templates: List[Dict] = content["templates"]
        return [ self.serializer.deserialize(t) for t in templates ]

    def add(self, template: TemplateModel) -> bool:
        content: Dict = load_json_from_file(self.file_path)
        templates: List[Dict] = content["templates"]

        if any(t["name"] == template.name for t in templates):
            return False  # Already exists

        templates.append(self.serializer.serialize(template))
        content["templates"] = templates
        write_json_on_file(content, self.file_path)
        return True

    def update(self, name: str, template: TemplateModel) -> bool:
        content: Dict = load_json_from_file(self.file_path)
        templates: List[Dict] = content["templates"]
        updated = False

        for idx, t in enumerate(templates):
            if t["name"] == name:
                templates[idx] = self.serializer.serialize(template)
                updated = True
                break

        if updated:
            content["templates"] = templates
            write_json_on_file(content, self.file_path)

        return updated

    def remove(self, name: str) -> bool:
        content: Dict = load_json_from_file(self.file_path)
        templates: List[Dict] = content["templates"]
        removed = False

        for t in templates:
            if t["name"] == name:
                templates.remove(t)
                removed = True
                break

        if removed:
            content["templates"] = templates
            write_json_on_file(content, self.file_path)

        return removed
