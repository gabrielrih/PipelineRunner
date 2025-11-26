import click

from pipelinerunner.template.interface.cli.template_commands import template
from pipelinerunner.runner.interface.cli.runner_commands import runner
from pipelinerunner.runner.interface.cli.runner_run import run
from pipelinerunner.shared.util.version import get_version, PACKAGE_NAME


@click.group
@click.version_option(version=get_version(), prog_name = PACKAGE_NAME)
def main():
    ''' Manage and execute Azure DevOps pipelines in batch mode '''
    pass


main.add_command(runner)
main.add_command(template)
main.add_command(run)  # alias for "pipeline runner run"
if __name__ == '__main__':
    main()
