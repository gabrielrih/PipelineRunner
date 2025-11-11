import click

from pipelinerunner.template.infraestructure.repository import TemplateRepositoryFactory
from pipelinerunner.template.application.template_model import TemplateModel
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@click.command(name = "update")
@click.argument('name', type = click.STRING)
@click.option('--set-description',
              type = click.STRING,
              required = True,
              help = 'New description')
def update_template(name: str, set_description: str) -> None:
    ''' Update template '''
    repository = TemplateRepositoryFactory.create()
    template: TemplateModel = repository.get(name)
    if not template:
        logger.warning(f'No template found using the name "{name}"')
        return

    template.description = set_description
    updated: bool = repository.update(name, template)
    if not updated:
        logger.error(f'Failed when updating template "{name}"')
        return
    logger.success(f'The description of template "{name}" was updated!')


@click.command(name = 'delete')
@click.argument('name', type = click.STRING)
def delete_template(name: str) -> None:
    ''' Delete template '''
    repository = TemplateRepositoryFactory.create()
    deleted: bool = repository.remove(name)
    if not deleted:
        logger.warning(f'No template found using the name "{name}"')
        return
    logger.success(f'The template "{name}" was deleted!')
