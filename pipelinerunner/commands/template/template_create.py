import click

from typing import List

from pipelinerunner.template.template_repository import TemplateRepositoryFactory
from pipelinerunner.template.template_model import TemplateModel
from pipelinerunner.template.parameter_model import TemplateParameter, TemplateParameterType
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@click.command(name = 'create')
@click.option('--name',
              type = click.STRING,
              help = 'Template name')
@click.option('--description',
              type = click.STRING,
              required = False,
              help = 'Template description')
@click.option('--param', 'params',
              type = click.STRING,
              multiple = True, 
              help = 'Parameter definition. Format, NAME:TYPE:REQUIRED[:default=VALUE][:options=VAL1,VAL2]')
@click.option('--interactive', '-i',
              is_flag = True,
              default = False,
              help = 'Force interactive mode')
def create_template(name: str, description: str, params: List[str], interactive: bool):
    ''' Create template'''
    if interactive:
        return create_interactive()

    if not name or not params:
        logger.error(f'Incomplete arguments provided. Use --interactive or provide all required parameters: {locals()}')
        return

    return create_from_cli(name, description, params)

def create_interactive():
    # Showing the existent templates
    repository = TemplateRepositoryFactory.create()
    existing_templates = repository.get_all()
    if existing_templates:
        existing_names = [tmpl.name for tmpl in existing_templates]
        logger.print_table(
            title = "Existing Templates",
            columns = ["Name"],
            rows = [[name] for name in existing_names],
        )

    logger.message("📝 Creating new template...\n")

    # Get unique name
    while True:
        name = click.prompt("Unique template name")
        
        if repository.exists(name):
            logger.warning(f'Template "{name}" already exists!')
            if not click.confirm("Choose a different name?", default=True):
                logger.error("Template creation cancelled.")
                return
            continue
        break  # when the name is unique

    description = click.prompt("Description")    
    logger.message("Now let's define the parameter schema...")

    parameters = []
    param_count = 1

    while True:
        logger.message("━" * 45)
        logger.message(f"Parameter #{param_count}:")
        
        # Getting required fields
        param_name = click.prompt("  Name")
        param_type = click.prompt("  Type",
            type = click.Choice(TemplateParameterType.values()),
            default = TemplateParameterType.STRING.value
        )
        is_required = click.confirm("  Is required?", default = True)
        
        # Options
        options = []
        if click.confirm("  Has predefined options?", default = False):
            opt_count = 1
            while True:
                option = click.prompt(
                    f"    Option {opt_count} (or press Enter to finish)",
                    default = "",
                    show_default = False
                )
                if not option:
                    break
                options.append(option)
                opt_count += 1
        
        # Default value
        default_value = click.prompt("  Default value (optional)",
            default = "",
            show_default = False
        )
        
        parameter = TemplateParameter(
            name = param_name,
            type = TemplateParameterType(param_type),
            is_required = is_required,
            default_value = default_value if default_value else None,
            options = options
        )
        parameters.append(parameter)
        logger.success(f'Parameter "{param_name}" added!')
        
        if not click.confirm("\nAdd another parameter?", default=True):
            break
        
        param_count += 1
    
    # Summary
    summary_rows = [
        ["Name", name],
        ["Description", description],
        ["Qty. Parameters", len(parameters)],
    ]
    logger.print_table("Template Summary", ["Field", "Value"], summary_rows)

    if not click.confirm("\nSave template?", default=True):
        logger.error("Template creation cancelled.")
        return

    template = TemplateModel(name=name, description=description, parameters=parameters)
    added: bool = repository.add(template)

    if not added:
        logger.error(f'Template name "{name}" is already being used! Choose a different one.')
        return
    logger.success(f'Template "{name}" created successfully!')


# TO DO
def create_from_cli(name: str, description: str, params: List[str]):
    raise NotImplementedError('This option was not implemented yet!')
