import click

from pipelinerunner.commands.runner.runner_run import run

@click.group
def main():
    ''' Triggering Azure Pipeline executions in batch '''
    pass


main.add_command(run)  # alias for "pipeline runner run"
