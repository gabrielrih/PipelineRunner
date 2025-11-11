import click

from typing import List, Optional

from pipelinerunner.template.infraestructure.repository import TemplateRepositoryFactory
from pipelinerunner.template.application.template_model import TemplateModel
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@click.command(name = 'list')
def list_all_templates() -> None:
    ''' List all saved templates '''
    repository = TemplateRepositoryFactory.create()
    templates: List[TemplateModel] = repository.get_all()

    if not templates:
        logger.warning('No template was found!')
        return
    
    # TO DO
    # Better way to get the rows and columns
    rows = []
    for t in templates:
        param_names = (
            ", ".join([p.name for p in t.parameters])
            if t.parameters
            else "-"
        )
        rows.append([
            t.name,
            t.description,
            param_names
        ])
    logger.print_table(
        title = f'List of {len(templates)} template(s)',
        columns = ['Name', "Description", "Parameters"],
        rows = rows
    )


@click.command(name = 'show')
@click.argument('name', type = click.STRING)
def show_template(name: str) -> None:
    ''' Display detailed information about a specific template '''
    repository = TemplateRepositoryFactory.create()
    template: Optional[TemplateModel] = repository.get(name)
    if not template:
        logger.error(f'No template found using the name "{name}"')
        return
    logger.info(f'Showing template "{name}"')
    logger.print_json(content = template.to_dict())
