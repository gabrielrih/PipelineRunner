import click

from typing import List, Optional

from pipelinerunner.runner.runner_repository import RunnerRepositoryFactory
from pipelinerunner.runner.runner_model import RunnerModel


@click.command(name = 'list')
def list_all_runner() -> None:
    ''' List all runners '''
    repository = RunnerRepositoryFactory.create()
    runners: List[RunnerModel] = repository.get_all()
    if runners:
        click.echo('List of runners:')
        for runner in runners:
            click.echo(f' - {runner}')
    click.echo(f'{len(runners)} runners have been found!')


@click.command(name = 'show')
@click.argument('name', type = click.STRING)
def show_runner(name: str) -> None:
    ''' Show runner '''
    repository = RunnerRepositoryFactory.create()
    runner: Optional[RunnerModel] = repository.get(name)
    if runner:
        click.echo(runner.to_pretty_json())
        return
    click.echo(f'No runner found using the name "{name}"')
