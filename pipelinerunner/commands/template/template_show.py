import click

from typing import List, Optional

from pipelinerunner.template.template_repository import TemplateRepositoryFactory
from pipelinerunner.template.template_model import TemplateModel


@click.command(name = 'list')
def list_all_templates() -> None:
    ''' List all templates '''
    repository = TemplateRepositoryFactory.create()
    templates: List[TemplateModel] = repository.get_all()
    if templates:
        click.echo('List of templates:')
        for template in templates:
            click.echo(f' - {template}')
    click.echo(f'{len(templates)} templates have been found!')


@click.command(name = 'show')
@click.argument('name', type = click.STRING)
def show_template(name: str) -> None:
    ''' Show template '''
    repository = TemplateRepositoryFactory.create()
    template: Optional[TemplateModel] = repository.get(name)
    if template:
        click.echo(template.to_pretty_json())
        return
    click.echo(f'No template found using the name "{name}"')
