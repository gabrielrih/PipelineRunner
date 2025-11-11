import click

from typing import Optional

from pipelinerunner.runner.infrastructure.repository import RunnerRepositoryFactory
from pipelinerunner.runner.application.model import RunnerModel
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


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
        logger.warning(f'No runner found using the name "{name}"')
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
        logger.warning("  No fields to update. Use one or more --set-* options.")
        return

    updated: bool = repository.update(name, runner)
    if not updated:
        logger.error(f'Failed to update runner "{name}"')
        return
    
    rows = [ [field, str(old), str(new)] for field, old, new in updates ]
    logger.print_table(
        title = "Changes",
        columns = ["Field", "Old Value", "New Value"],
        rows = rows,
    )
    logger.success(f'Runner "{name}" updated successfully:')


@click.command(name = 'delete')
@click.argument('name', type = click.STRING)
def delete_runner(name: str) -> None:
    ''' Delete runner '''
    repository = RunnerRepositoryFactory.create()
    deleted: bool = repository.remove(name)
    if not deleted:
        logger.warning(f'No runner found using the name "{name}"')
        return
    logger.success(f'The runner "{name}" was deleted!')
