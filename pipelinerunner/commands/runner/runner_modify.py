import click

from typing import Optional

from pipelinerunner.runner.runner_repository import RunnerRepositoryFactory
from pipelinerunner.runner.runner_model import RunnerModel, RunModel
from pipelinerunner.template.template_repository import TemplateRepositoryFactory
from pipelinerunner.template.parameter_model import TemplateParameterType


@click.command(name = 'update')
@click.argument('name', type = click.STRING)
@click.option("--set-project-name", type=click.STRING, required = False, help="Update the project name")
@click.option("--set-definition-id", type=click.STRING, required = False,  help="Update the definition ID")
@click.option("--set-pipeline-name", type=click.STRING, required = False,  help="Update the pipeline name")
@click.option("--set-branch-name", type=click.STRING, required = False,  help="Update the branch name")
def update_runner(name: str,
                  set_project_name: Optional[str],
                  set_definition_id: Optional[str],
                  set_pipeline_name: Optional[str],
                  set_branch_name: Optional[str]) -> None:
    ''' Update runner '''
    repository = RunnerRepositoryFactory.create()
    runner: Optional[RunnerModel] = repository.get(name)
    if not runner:
        click.echo(f'No runner found using the name "{name}"')
        return

    updates = []
    if set_project_name:
        updates.append(("project_name", runner.project_name, set_project_name))
        runner.project_name = set_project_name

    if set_definition_id:
        updates.append(("definition_id", runner.definition_id, set_definition_id))
        runner.definition_id = set_definition_id

    if set_pipeline_name:
        updates.append(("pipeline_name", runner.pipeline_name, set_pipeline_name))
        runner.pipeline_name = set_pipeline_name

    if set_branch_name:
        updates.append(("branch_name", runner.branch_name, set_branch_name))
        runner.branch_name = set_branch_name

    if not updates:
        click.echo("⚠️  No fields to update. Use one or more --set-* options.")
        return

    updated: bool = repository.update(name, runner)
    if not updated:
        click.echo(f'❌ Failed to update runner "{name}"')
        return
    click.echo('Changes:')
    for field, old, new in updates:
        click.echo(f'   - {field}: "{old}" → "{new}"')
    click.echo(f'✅ Runner "{name}" updated successfully:')


@click.command(name = 'delete')
@click.argument('name', type = click.STRING)
def delete_runner(name: str) -> None:
    ''' Delete runner '''
    repository = RunnerRepositoryFactory.create()
    deleted: bool = repository.remove(name)
    if deleted:
        click.echo(f'The runner "{name}" was deleted!')
        return
    click.echo(f'No runner found using the name "{name}"')


@click.command(name="create")
@click.option('--from-template',
              type = click.STRING,
              help = 'Template name')
@click.option('--interactive', '-i',
              is_flag = True,
              default = False,
              help = 'Force interactive mode')
def create_runner(from_template: str, interactive: bool):
    ''' Create runner'''
    if interactive:
        return create_interactive()

    if not from_template:
        click.echo(f'Incomplete arguments provided. Use --interactive or provide all required parameters: {locals()}')
        return

    return create_from_cli(from_template)


def create_interactive():
    # Getting available templates (required)
    template_repo = TemplateRepositoryFactory.create()
    available_templates = template_repo.get_all()
    
    if not available_templates:
        click.echo("❌ No templates found!")
        click.echo("   You must create a template first!")
        return
    
    # Lista e seleciona o template
    template_names = [ t.name for t in available_templates ]
    click.echo(f"📋 Available templates: {template_names}\n")
    
    template_name = click.prompt(
        "Select template",
        type=click.Choice(template_names)
    )
    
    selected_template = template_repo.get(template_name)
    click.echo(f"\n✓ Using template: {selected_template.name}")
    click.echo(f"  Description: {selected_template.description}")
    
    if selected_template.parameters:
        click.echo("  Parameters:")
        for param in selected_template.parameters:
            param_info = f"    • {param.name} ({param.type.value})"
            if param.is_required:
                param_info += " [required]"
            if param.default_value:
                param_info += f" [default: {param.default_value}]"
            if param.options:
                param_info += f" [options: {', '.join(map(str, param.options))}]"
            click.echo(param_info)
    else:
        click.echo("  ⚠️  This template has no parameters defined")
    
    # Showing the existent runners
    repository = RunnerRepositoryFactory.create()
    existing_runners = repository.get_all()
    if existing_runners:
        existing_runners_names = [ r.name for r in existing_runners ]
        click.echo(f"📋 Existing runners: {existing_runners_names}")
        click.echo()

    click.echo("🚀 Creating new runner\n")

    # Getting an unique runner name
    while True:
        name = click.prompt("Unique runner name")
        
        if repository.exists(name):
            click.echo(f"⚠️  Runner '{name}' already exists!")
            if not click.confirm("Choose a different name?", default=True):
                click.echo("❌ Template creation cancelled.")
                return
            continue
            
        break  # when the name is unique

    project_name = click.prompt("Project name (Azure DevOps)")
    definition_id = click.prompt("Pipeline definition ID", type=int)
    pipeline_name = click.prompt("Pipeline name")
    branch_name = click.prompt("Branch name", default="main")
    
    # Configuration the runs
    click.echo("\n" + "━" * 50)
    click.echo("🔧 Configuring pipeline runs\n")
    
    if not selected_template.parameters:
        click.echo("⚠️  Template has no parameters. Each run will have empty parameters.")
        if not click.confirm("Continue anyway?", default=False):
            click.echo("❌ Runner creation cancelled.")
            return
    
    runs = []
    run_count = 1
    
    while True:
        click.echo(f"\n📌 Run #{run_count}:")
        
        parameters = {}
        
        if selected_template.parameters:
            # Usa os parâmetros do template
            for param in selected_template.parameters:
                # Mostra informações do parâmetro
                param_label = f"  {param.name}"
                if param.is_required:
                    param_label += " *"
                
                # Solicita o valor baseado no tipo
                if param.options:
                    # Parâmetro com opções predefinidas
                    value = click.prompt(
                        param_label,
                        type=click.Choice([str(opt) for opt in param.options]),
                        default=str(param.default_value) if param.default_value else None,
                        show_default=True
                    )
                elif param.type.value == TemplateParameterType.BOOLEAN.value:
                    default_bool = param.default_value if param.default_value is not None else True
                    value = click.confirm(param_label, default=default_bool)
                elif param.type.value == TemplateParameterType.NUMBER.value:
                    default_num = param.default_value if param.default_value is not None else None
                    value = click.prompt(
                        param_label,
                        type=int,
                        default=default_num,
                        show_default=True
                    )
                elif param.type.value == TemplateParameterType.STRING.value:
                    # Parâmetro string
                    default_str = param.default_value if param.default_value else ""
                    
                    # Se é obrigatório e não tem default, não permite vazio
                    if param.is_required and not default_str:
                        while True:
                            value = click.prompt(param_label)
                            if value.strip():
                                break
                            click.echo("    ⚠️  This parameter is required and cannot be empty")
                    else:
                        value = click.prompt(
                            param_label,
                            default=default_str,
                            show_default=True
                        )
                
                else:
                    raise ValueError(f'The parameter type {param.type.value} not available on {TemplateParameterType.__name__} class!')
                
                parameters[param.name] = value
        
        # Cria o run
        run = RunModel(parameters = parameters)
        runs.append(run)
        
        click.echo(f"\n✅ Run #{run_count} configured with {len(parameters)} parameter(s)")
        
        if not click.confirm("\nAdd another run?", default=True):
            break
        
        run_count += 1
    
    # Resumo
    click.echo("\n" + "━" * 50)
    click.echo("\n📋 Runner Summary:")
    click.echo(f"  Template: {selected_template.name}")
    click.echo(f"  Runner name: {name}")
    click.echo(f"  Project: {project_name}")
    click.echo(f"  Pipeline: {pipeline_name}")
    click.echo(f"  Definition ID: {definition_id}")
    click.echo(f"  Branch: {branch_name}")
    click.echo(f"  Total runs: {len(runs)}")
    
    for idx, run in enumerate(runs, 1):
        click.echo(f"\n  Run #{idx}:")
        if run.parameters:
            for key, value in run.parameters.items():
                click.echo(f"    {key}: {value}")
        else:
            click.echo("    (no parameters)")
    
    if not click.confirm("\nSave runner?", default=True):
        click.echo("❌ Runner creation cancelled.")
        return
    
    # Salva o runner
    runner = RunnerModel(
        name = name,
        project_name = project_name,
        definition_id = str(definition_id),
        pipeline_name = pipeline_name,
        branch_name = branch_name,
        runs = runs
    )
    
    repository = RunnerRepositoryFactory.create()
    added = repository.add(runner)
    
    if added:
        click.echo(f"\n✅ Runner '{name}' created successfully!")
        click.echo(f"   Template: {selected_template.name}")
        click.echo(f"   Runs configured: {len(runs)}")
        return
    
    click.echo(f"\n❌ Failed to save runner '{pipeline_name}'")


def create_from_cli(template_name: str):
    raise NotImplementedError('This option was not implemented yet!')


