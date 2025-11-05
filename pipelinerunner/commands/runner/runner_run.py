import click

from typing import Dict, List, Union, Optional

from pipelinerunner.pipeline.pipeline_batch import PipelineBatchExecutor
from pipelinerunner.pipeline.pipeline_mode import PipelineExecutionMode
from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.runner.runner_serializer import RunnerSerializer
from pipelinerunner.runner.runner_repository import RunnerRepositoryFactory
from pipelinerunner.util.json import load_json_from_file
from pipelinerunner.util.measure_time import measure_time
from pipelinerunner.util.logger import Logger


logger = Logger.get_logger(__name__)


@click.command(name="run")
@click.argument('name', type = click.STRING, required = False)
@click.option('--from-file',
              type = click.STRING,
              required = False,
              help = 'Path to the json file')
@click.option('--mode',
              type = click.Choice(PipelineExecutionMode.get_values()),
              required = False,
              default = PipelineExecutionMode.PARALLEL.value,
              help = PipelineExecutionMode.get_help_message())
@click.option('--no-wait',
              is_flag = True,
              default = False,
              help='Do not wait for pipeline completion (fire and forget)')
@click.option('--dry-run',
              is_flag = True,
              default = False,
              help = 'Dry run')
def run(name: str, from_file: str, mode: str, no_wait: bool, dry_run: bool):
    ''' Start a runner '''
    if not name and not from_file:
        click.echo('Incomplete arguments provided. Use the --from-file or provide the name argument')
        return
    
    if name:
        return run_using_runner(runner_name = name, mode = mode, no_wait = no_wait, dry_run = dry_run)
    
    return run_from_file(filename = from_file, mode = mode, no_wait = no_wait, dry_run = dry_run)


@measure_time
def run_using_runner(runner_name: str, mode: str, no_wait: bool, dry_run: bool):
    repository = RunnerRepositoryFactory.create()
    runner: Optional[RunnerModel] = repository.get(name = runner_name)
    if not runner:
        click.echo(f'No runner found using the name "{runner_name}"')
        return
    
    logger.info(f'Starting single runner: {runner.name}')
    _execute_runners([ runner ], mode, no_wait, dry_run)


@measure_time
def run_from_file(filename: str, mode: str, no_wait: bool, dry_run: bool):
    click.echo(f'Loading runners from {filename}')
    data: Union[Dict, List[Dict]] = load_json_from_file(filename)

    runners = RunnerSerializer.deserialize(data)
    if isinstance(runners, RunnerModel):
        runners = [ runners ]

    logger.info(f"Starting {len(runners)} runner(s):")
    for r in runners:
        click.echo(f"  - {r.name} (project: {r.project_name}, pipeline: {r.pipeline_name}, branch: {r.branch_name})")

    _execute_runners(runners, mode, no_wait, dry_run)


def _execute_runners(runners: List[RunnerModel], mode: str, no_wait: bool, dry_run: bool):
    wait: bool = not no_wait
    executor = PipelineBatchExecutor(runners, mode, wait, dry_run)
    executor.run_all()
