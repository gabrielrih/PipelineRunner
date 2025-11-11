import click

from pipelinerunner.runner.infrastructure.repository import RunnerRepositoryFactory
from pipelinerunner.runner.application.model import RunnerModel, RunModel
from pipelinerunner.template.infraestructure.repository import TemplateRepositoryFactory
from pipelinerunner.template.application.parameter_model import TemplateParameterType
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@click.command(name="create")
@click.option('--from-template',
              type = click.STRING,
              help = 'Template name')
@click.option('--interactive', '-i',
              is_flag = True,
              default = False,
              help = 'Force interactive mode')
def create_runner(from_template: str, interactive: bool):
    ''' Create a new runner '''
    if interactive:
        return create_interactive()

    if not from_template:
        logger.error(f'Incomplete arguments provided. Use --interactive or provide all required parameters: {locals()}')
        return

    return create_from_cli(from_template)


def create_interactive():
    # Getting available templates (required)
    template_repo = TemplateRepositoryFactory.create()
    available_templates = template_repo.get_all()
    if not available_templates:
        logger.error('No template found! You must create a template first.')
        return
    
    # Listing templates in a table
    template_rows = [ [t.name, t.description, len(t.parameters or [])] for t in available_templates ]
    logger.print_table(
        title = "Available Templates",
        columns = ["Name", "Description", "Parameters"],
        rows = template_rows
    )
    
    # Select a template
    template_names = [ t.name for t in available_templates ]
    template_name = click.prompt(
        "Select template",
        type=click.Choice(template_names)
    )

    selected_template = template_repo.get(template_name)
    logger.success(f'Using template "{selected_template.name}"')
    logger.message(f'Description: {selected_template.description}')

    if selected_template.parameters:
        param_rows = []
        for p in selected_template.parameters:
            param_rows.append([
                p.name,
                p.type.value,
                "✅ Yes" if p.is_required else "❌ No",
                p.default_value or "-",
                ", ".join(map(str, p.options)) if p.options else "-"
            ])
        logger.print_table(
            title = "Template Parameters",
            columns = ["Name", "Type", "Required", "Default", "Options"],
            rows = param_rows
        )
    else:
        logger.warning("This template has no parameters defined.")
    
    # Showing existing runners
    repository = RunnerRepositoryFactory.create()
    existing_runners = repository.get_all()
    if existing_runners:
        runner_rows = [ [r.name, r.project_name, r.pipeline_name] for r in existing_runners ]
        logger.print_table(
            title = "Existing Runners",
            columns = ["Name", "Project", "Pipeline"],
            rows = runner_rows
        )

    logger.message("🚀 Creating new runner...\n")

    # Getting an unique runner name
    while True:
        name = click.prompt("Unique runner name")
        if repository.exists(name):
            logger.warning(f'Runner "{name}" already exists!')
            if not click.confirm("Choose a different name?", default=True):
                logger.error("Runner creation cancelled.")
                return
            continue
        break  # when the name is unique

    project_name = click.prompt("Project name (Azure DevOps)")
    definition_id = click.prompt("Pipeline definition ID", type=int)
    pipeline_name = click.prompt("Pipeline name")
    branch_name = click.prompt("Branch name", default = 'main')
    
    # Configure runs
    logger.message("\n🔧 Configuring pipeline runs...\n")
    
    if not selected_template.parameters:
        logger.warning("Template has no parameters. Each run will have empty parameters.")
        if not click.confirm("Continue anyway?", default=False):
            logger.error("Runner creation cancelled.")
            return
    
    runs = []
    run_count = 1
    
    while True:
        logger.message(f"\n📌 Run #{run_count} configuration:\n")
        
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
                            logger.warning("This parameter is required and cannot be empty")
                    else:
                        value = click.prompt(
                            param_label,
                            default=default_str,
                            show_default=True
                        )
                
                else:
                    raise ValueError(f'The parameter type {param.type.value} not available on {TemplateParameterType.__name__} class!')
                
                parameters[param.name] = value
        
        run = RunModel(parameters = parameters)
        runs.append(run)
        
        logger.success(f"Run #{run_count} configured with {len(parameters)} parameter(s)")
        
        if not click.confirm("\nAdd another run?", default=True):
            break
        
        run_count += 1
    
    # Runner summary
    summary_rows = [
        ["Template", selected_template.name],
        ["Runner name", name],
        ["Project", project_name],
        ["Pipeline", pipeline_name],
        ["Definition ID", definition_id],
        ["Branch", branch_name],
        ["Total runs", len(runs)],
    ]
    logger.print_table("Runner Summary", ["Field", "Value"], summary_rows)

    # Show run parameters
    for idx, run in enumerate(runs, 1):
        run_params = [[k, v] for k, v in run.parameters.items()]
        logger.print_table(f"Run #{idx} Parameters", ["Parameter", "Value"], run_params or [["-", "-"]])

    if not click.confirm("\nSave runner?", default=True):
        logger.error("Runner creation cancelled.")
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
    
    added = repository.add(runner)
    if not added:
        logger.error(f"Failed to save runner '{pipeline_name}'")
        return
    logger.success(f'Runner "{name}" created successfully!')
    logger.message(f'Template: {selected_template.name}')
    logger.message(f'Runs configured: {len(runs)}')


def create_from_cli(template_name: str):
    raise NotImplementedError('This option was not implemented yet!')
