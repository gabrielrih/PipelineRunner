import click

from typing import List, Optional

from pipelinerunner.template.template_repository_factory import TemplateRepositoryFactory
from pipelinerunner.template.template_model import TemplateModel


@click.command(name="list")
def list_all_templates() -> None:
    ''' List all templates '''
    repository = TemplateRepositoryFactory.create()
    templates: List[TemplateModel] = repository.get_all()
    click.echo(templates)
    click.echo(f'{len(templates)} templates was found!')


@click.command(name="show")
@click.argument('name', type = click.STRING)
def show_template(name: str) -> None:
    ''' Show template '''
    repository = TemplateRepositoryFactory.create()
    template: Optional[TemplateModel] = repository.get(name)
    if template:
        click.echo(template)
        return
    click.echo(f'No template found using name "{name}"')
