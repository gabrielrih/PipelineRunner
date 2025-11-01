from pathlib import Path
from typing import List, Dict, Optional


from pipelinerunner.template.template_repository import BaseTemplateRepository
from pipelinerunner.template.template_model import TemplateModel
from pipelinerunner.template.template_serializer import TemplateSerializer
from pipelinerunner.util.json import load_json_from_file, write_json_on_file


class TemplateRepositoryOnDisk(BaseTemplateRepository):
    def __init__(self, templates_dir: Path):
        self.serializer = TemplateSerializer()
        self.templates_dir = templates_dir
        self.initialize()

    def initialize(self) -> None:
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)

    def get(self, name: str) -> Optional[TemplateModel]:
        file_path = self._get_template_file_path(name)
        
        if not file_path.exists():
            return None
        
        try:
            content = load_json_from_file(file_path)
            return self.serializer.deserialize(content)
        except Exception as e:
            # Log error if needed
            return None

    def _get_template_file_path(self, name: str) -> Path:
        # Sanitize filename to avoid issues with special characters
        safe_name = name.replace('/', '_').replace('\\', '_')
        return self.templates_dir / f"{safe_name}.json"

    def get_all(self) -> List[TemplateModel]:
        templates = []
        
        for file_path in self.templates_dir.glob("*.json"):
            try:
                content = load_json_from_file(file_path)
                template = self.serializer.deserialize(content)
                templates.append(template)
            except Exception as e:
                # Log error and skip invalid files
                continue
        
        return templates

    def add(self, template: TemplateModel) -> bool:
        file_path = self._get_template_file_path(template.name)
        
        # Check if template already exists
        if file_path.exists():
            return False
        
        try:
            content = self.serializer.serialize(template)
            write_json_on_file(content, file_path)
            return True
        except Exception as e:
            # Log error if needed
            return False

    def update(self, name: str, template: TemplateModel) -> bool:
        old_file_path = self._get_template_file_path(name)
        
        if not old_file_path.exists():
            return False
        
        try:
            new_file_path = self._get_template_file_path(template.name)  # the name can change
            content = self.serializer.serialize(template)
            write_json_on_file(content, new_file_path)
            # If name changed, remove old file
            if old_file_path != new_file_path:
                old_file_path.unlink()
            return True
        except Exception as e:
            # Log error if needed
            return False

    def remove(self, name: str) -> bool:
        file_path = self._get_template_file_path(name)
        
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            # Log error if needed
            return False

    def exists(self, name: str) -> bool:
        file_path = self._get_template_file_path(name)
        return file_path.exists()


class TemplateRepositorySingleFileOnDisk(BaseTemplateRepository):
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
