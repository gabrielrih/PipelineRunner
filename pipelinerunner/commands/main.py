import click

from pipelinerunner.commands.runner.runner_run import run

@click.group
def main():
    ''' Manage and execute Azure DevOps pipelines in batch mode '''
    pass


main.add_command(run)  # alias for "pipeline runner run"
