from pathlib import Path
from typing import List, Optional


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
