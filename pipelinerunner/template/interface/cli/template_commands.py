import click

from pipelinerunner.template.interface.cli.template_show import list_all_templates, show_template
from pipelinerunner.template.interface.cli.template_modify import update_template, delete_template
from pipelinerunner.template.interface.cli.template_create import create_template


@click.group()
def template():
    ''' Using templates '''
    pass


template.add_command(create_template)
template.add_command(update_template)
template.add_command(delete_template)
template.add_command(show_template)
template.add_command(list_all_templates)
