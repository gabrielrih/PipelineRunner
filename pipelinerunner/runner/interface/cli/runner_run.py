import click

from pipelinerunner.pipeline.application.execution_mode import PipelineExecutionMode
from pipelinerunner.runner.domain.executor_service import RunnerExecutorService
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


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
    ''' Execute Azure DevOps pipelines using a saved runner or JSON file '''
    if not name and not from_file:
        logger.error('Incomplete arguments provided. Use the --from-file or provide the name argument')
        return
    
    mode = PipelineExecutionMode.from_value(mode)
    service = RunnerExecutorService(mode = mode)
    if name:
        return service.execute_from_name(name = name, no_wait = no_wait, dry_run = dry_run)
    
    return service.execute_from_file(filename = from_file, no_wait = no_wait, dry_run = dry_run)
