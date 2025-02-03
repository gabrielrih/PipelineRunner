from src.pipeline import PipelineBatchRunner
from src.util.json import load_json_from_file
from src.util.logger import Logger

import click

# loading .env file
from dotenv import load_dotenv
load_dotenv()


logger = Logger.get_logger(__name__)


def get_pipelines_from_scope(scope: str):
    if scope == 'dev':
        return load_json_from_file(path = 'config/runs-for-dev.json')
    elif scope == 'stg':
        return load_json_from_file(path = 'config/runs-for-stg.json')
    elif scope == 'prd':
        return load_json_from_file(path = 'config/runs-for-prd.json')
    elif scope == 'test':
        return load_json_from_file(path = 'config/test-runs.json')
    raise NotImplementedError("The scope option 'all' is not implemented yet")
    # TO DO
    # Merge all the scopes at once
    

@click.command()
@click.option('--scope',
              type = click.Choice(['dev', 'stg', 'prd', 'all', 'test']),
              required = False,
              default = 'test',
              help = 'Scope to be used')
def run(scope: str) -> None:
    pipelines = get_pipelines_from_scope(scope)
    logger.info(f'Running using {scope =}')
    runner = PipelineBatchRunner(pipelines)
    runner.run_all()


if __name__ == '__main__':
    run()
