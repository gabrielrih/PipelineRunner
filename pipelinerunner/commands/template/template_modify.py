import click

from typing import List

from pipelinerunner.template.template_repository import TemplateRepositoryFactory
from pipelinerunner.template.template_model import TemplateModel
from pipelinerunner.template.parameter_model import TemplateParameter, TemplateParameterType
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@click.command(name = "update")
@click.argument('name', type = click.STRING)
@click.option('--set-description',
              type = click.STRING,
              required = True,
              help = 'New description')
def update_template(name: str, set_description: str) -> None:
    ''' Update template '''
    repository = TemplateRepositoryFactory.create()
    template: TemplateModel = repository.get(name)
    if not template:
        logger.warning(f'No template found using the name "{name}"')
        return

    template.description = set_description
    updated: bool = repository.update(name, template)
    if not updated:
        logger.error(f'Failed when updating template "{name}"')
        return
    logger.success(f'The description of template "{name}" was updated!')


@click.command(name = 'delete')
@click.argument('name', type = click.STRING)
def delete_template(name: str) -> None:
    ''' Delete template '''
    repository = TemplateRepositoryFactory.create()
    deleted: bool = repository.remove(name)
    if not deleted:
        logger.warning(f'No template found using the name "{name}"')
        return
    logger.success(f'The template "{name}" was deleted!')


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
    existing_templates_names = list()
    if existing_templates:
        existing_templates_names = [ tmpl.name for tmpl in existing_templates ]
        click.echo(f"📋 Existing templates: {existing_templates_names}")
        click.echo()

    click.echo("📝 Creating new template\n")

    # Getting an unique template name
    while True:
        name = click.prompt("Unique template name")
        
        if repository.exists(name):
            click.echo(f"⚠️  Template '{name}' already exists!")
            if not click.confirm("Choose a different name?", default=True):
                click.echo("❌ Template creation cancelled.")
                return
            continue
            
        break  # when the name is unique

    description = click.prompt("Description")
    
    click.echo("\nNow let's define the parameter schema...\n")    
    parameters = list()
    param_count = 1

    while True:
        click.echo("━" * 45)
        click.echo(f"\nParameter #{param_count}:")
        
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
        click.echo(f"\n✅ Parameter '{param_name}' added!")
        
        if not click.confirm("\nAdd another parameter?", default=True):
            break
        
        param_count += 1
    
    # Summary
    click.echo("\n" + "━" * 45)
    click.echo("\n📋 Template Summary:")
    click.echo(f"  Name: {name}")
    click.echo(f"  Description: {description}")
    click.echo(f"  Parameters: {len(parameters)}")
    
    if not click.confirm("\nSave template?", default=True):
        click.echo("❌ Template creation cancelled.")
        return
    
    # Save template
    template = TemplateModel(name = name, description = description, parameters = parameters)
    repository = TemplateRepositoryFactory.create()
    added: bool = repository.add(template)

    if added:
        click.echo(f"✅ Template '{name}' created successfully!")
        return
    click.echo("❌ Template name '{name}' is already being used! Choice a different one.")
    

# TO DO
def create_from_cli(name: str, description: str, params: List[str]):
    raise NotImplementedError('This option was not implemented yet!')

