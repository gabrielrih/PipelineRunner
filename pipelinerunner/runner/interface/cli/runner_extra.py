import click

from typing import Optional

from pipelinerunner.runner.domain.exporter_service import RunnerExporterService
from pipelinerunner.runner.domain.validator_service import RunnerValidatorService


@click.command(name = 'export')
@click.argument('name', type=click.STRING)
@click.option('--output', '-o',
              type = click.STRING,
              required = False,
              help = 'Output file path (default: <runner_name>.json)')
def export_runner(name: str, output: Optional[str]) -> None:
    ''' Export a runner configuration to a JSON file '''
    exporter = RunnerExporterService()
    exporter.export(name = name, output = output)


@click.command(name = 'validate')
@click.option('--file', '-f',
              type = click.STRING,
              required = True,
              help = 'JSON file path to validate')
def validate_runner_file(file: str) -> None:
    ''' Validate the structure and format of a runner JSON file '''
    validator = RunnerValidatorService()
    validator.validate_file(file_path = file)  
   