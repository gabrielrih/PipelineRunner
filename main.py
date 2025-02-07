from src.scope import get_pipelines_from_scope, Scope
from src.runner import Mode, PipelineBatchRunner
from src.util.logger import Logger

import click

from time import time


logger = Logger.get_logger(__name__)
    

@click.command()
@click.option('--scope',
              type = click.Choice(Scope.get_values()),
              required = False,
              default = Scope.TEST.value,
              help = Scope.get_help_message())
@click.option('--mode',
              type = click.Choice(Mode.get_values()),
              required = False,
              default = Mode.PARALLEL.value,
              help = Mode.get_help_message())
#@click.option('--dry-run', is_flag=True, help="Run in dry-run mode (no changes applied)")
def run(scope: str, mode: str) -> None:
    logger.info(f'Starting using: {locals()}')
    pipelines = get_pipelines_from_scope(scope)
    logger.info(f'Running for these pipelines: \r\n{pipelines}')
    start_time = time()
    runner = PipelineBatchRunner(pipelines, mode = Mode[mode.upper()])
    runner.run_all()
    elapsed_time_in_minutes = (time() - start_time) / 60
    logger.info(f'Execution time: {elapsed_time_in_minutes:.2f} minutes')


if __name__ == '__main__':
    run()
