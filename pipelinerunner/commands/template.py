import click

from typing import List, Optional

from pipelinerunner.template.template_repository_factory import TemplateRepositoryFactory
from pipelinerunner.template.template_model import TemplateModel
from pipelinerunner.template.parameter_model import TemplateParameter, TemplateParameterType


@click.group()
def template():
    ''' Execution templates '''
    pass


@template.command(name="list")
def list_all_templates() -> None:
    ''' List all templates '''
    repository = TemplateRepositoryFactory.create()
    templates: List[TemplateModel] = repository.get_all()
    click.echo(templates)
    click.echo(f'{len(templates)} templates was found!')


@template.command(name="show")
@click.option('--name',
              type = click.STRING,
              required = True,
              help = 'Template name')
def show_template(name: str) -> None:
    ''' Show template '''
    repository = TemplateRepositoryFactory.create()
    template: Optional[TemplateModel] = repository.get(name)
    if template:
        click.echo(template)
        return
    click.echo(f'No template found using name "{name}"')



@template.command(name="edit")
@click.option('--name',
              type = click.STRING,
              required = True,
              help = 'Template name')
def edit_template(name: str) -> None:
    ''' Edit template '''
    repository = TemplateRepositoryFactory.create()
    # deleted: bool = repository.get(name)
    # if deleted:
    #     click.echo(f'The template "{name}" was deleted!')
    #     return
    # click.echo(f'No template found using name "{name}"')

@template.command(name="delete")
@click.option('--name',
              type = click.STRING,
              required = True,
              help = 'Template name')
def delete_template(name: str) -> None:
    ''' Delete template '''
    repository = TemplateRepositoryFactory.create()
    deleted: bool = repository.remove(name)
    if deleted:
        click.echo(f'The template "{name}" was deleted!')
        return
    click.echo(f'No template found using name "{name}"')


@template.command()
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
def create(name: str, description: str, params: List[str], interactive: bool):
    ''' Create template'''
    if interactive:
        return create_interactive()

    if not name or not params:
        click.echo(f'Incomplete arguments provided. Use --interactive or provide all required parameters: {locals()}')
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
        name = click.prompt("Template name")
        
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
    click.echo(f'Creating template using this parameters: {locals()}')
