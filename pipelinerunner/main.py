import click

from pipelinerunner.template.interface.cli.template_commands import template
from pipelinerunner.runner.interface.cli.runner_commands import runner
from pipelinerunner.runner.interface.cli.runner_run import run


@click.group
def main():
    ''' Manage and execute Azure DevOps pipelines in batch mode '''
    pass


main.add_command(runner)
main.add_command(template)
main.add_command(run)  # alias for "pipeline runner run"
if __name__ == '__main__':
    main()
