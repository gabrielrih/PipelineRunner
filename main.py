from src.pipeline import PipelineBatchRunner
from src.scope import get_pipelines_from_scope
from src.util.logger import Logger

import click

from time import time
from dotenv import load_dotenv
load_dotenv() # loading .env file


logger = Logger.get_logger(__name__)
    

@click.command()
@click.option('--scope',
              type = click.Choice(['dev', 'stg', 'prd', 'all', 'test']),
              required = False,
              default = 'test',
              help = 'Scope to be used')
def run(scope: str) -> None:
    pipelines = get_pipelines_from_scope(scope)
    
    logger.info(f'Running using {scope =}')
    logger.info(f'Running for these pipelines: \r\n{pipelines}')
    start_time = time()
    runner = PipelineBatchRunner(pipelines)
    runner.run_all()
    elapsed_time_in_minutes = (time() - start_time) / 60
    logger.info(f'Execution time: {elapsed_time_in_minutes:.2f} minutes')


if __name__ == '__main__':
    run()
