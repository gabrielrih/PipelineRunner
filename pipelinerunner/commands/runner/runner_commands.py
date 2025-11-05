import click

from pipelinerunner.commands.runner.runner_run import run
from pipelinerunner.commands.runner.runner_show import list_all_runner, show_runner
from pipelinerunner.commands.runner.runner_modify import create_runner, update_runner, delete_runner
from pipelinerunner.commands.runner.runner_extra import export_runner, validate_runner_file


@click.group()
def runner():
    ''' Defining runners '''
    pass


runner.add_command(run)
runner.add_command(list_all_runner)
runner.add_command(show_runner)
runner.add_command(create_runner)
runner.add_command(update_runner)
runner.add_command(delete_runner)
runner.add_command(export_runner)
runner.add_command(validate_runner_file)
