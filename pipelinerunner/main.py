from pipelinerunner.pipeline.parser import Pipeline
from pipelinerunner.runner import Mode, PipelineBatchRunner
from pipelinerunner.util.logger import Logger

import click

from time import time


logger = Logger.get_logger(__name__)
    
@click.group
def pipeline(): pass


@click.command()
@click.option('--pipeline-file',
              type = click.STRING,
              required = True,
              help = 'Path to the json file')
@click.option('--mode',
              type = click.Choice(Mode.get_values()),
              required = False,
              default = Mode.PARALLEL.value,
              help = Mode.get_help_message())
def run(pipeline_file: str, mode: str) -> None:
    ''' Running pipeline '''
    logger.info(f'Starting using: {locals()}')
    pipelines = Pipeline.from_json_file(pipeline_file)
    logger.info(f'Running for these pipelines: \r\n{pipelines}')
    start_time = time()
    runner = PipelineBatchRunner(pipelines, mode = Mode[mode.upper()])
    runner.run_all()
    elapsed_time_in_minutes = (time() - start_time) / 60
    logger.info(f'Execution time: {elapsed_time_in_minutes:.2f} minutes')

@click.command()
def create() -> None:
    ''' Creating a pipeline definition '''
    raise NotImplementedError('The config option are not implemented yet!')

pipeline.add_command(run)
pipeline.add_command(create)
if __name__ == '__main__':
    pipeline()
