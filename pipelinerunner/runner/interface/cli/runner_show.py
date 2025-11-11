import click

from typing import List, Optional

from pipelinerunner.runner.infrastructure.repository import RunnerRepositoryFactory
from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@click.command(name = 'list')
def list_all_runner() -> None:
    ''' List all saved runners '''
    repository = RunnerRepositoryFactory.create()
    runners: List[RunnerModel] = repository.get_all()
    
    if not runners:
        logger.warning('No runner was found!')
        return
    
    # TO DO
    # Better way to get the rows and columns
    rows = [
        [r.name, r.project_name, r.pipeline_name, r.branch_name]
        for r in runners
    ]
    logger.print_table(
        title = f'List of {len(runners)} runner(s)',
        columns = ['Name', 'Project', 'Pipeline', 'Branch'],
        rows = rows,
    )


@click.command(name = 'show')
@click.argument('name', type = click.STRING)
def show_runner(name: str) -> None:
    ''' Display detailed information about a specific runner'''
    repository = RunnerRepositoryFactory.create()
    runner: Optional[RunnerModel] = repository.get(name)
    if not runner:
        logger.error(f'No runner found using the name "{name}"')
        return
    logger.info(f'Showing runner "{name}":')
    logger.print_json(content = runner.to_dict())
