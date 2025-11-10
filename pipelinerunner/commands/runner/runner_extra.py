import click

from typing import Optional
from pathlib import Path
from typing import Union, Dict, List

from pipelinerunner.runner.runner_repository import RunnerRepositoryFactory
from pipelinerunner.runner.runner_serializer import RunnerSerializer
from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.util.json import write_json_on_file, load_json_from_file
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@click.command(name = 'export')
@click.argument('name', type=click.STRING)
@click.option('--output', '-o',
              type = click.STRING,
              required = False,
              help = 'Output file path (default: <runner_name>.json)')
def export_runner(name: str, output: Optional[str]) -> None:
    ''' Export runner to JSON file '''
    repository = RunnerRepositoryFactory.create()
    runner: Optional[RunnerModel] = repository.get(name)
    if not runner:
        logger.warning(f'No runner found using the name "{name}"')
        return
    
    if not output:
        output = f"{name}.json"
    
    if not output.endswith('.json'):
        output = f"{output}.json"
    
    try:
        serializer = RunnerSerializer()
        data = serializer.serialize(runner)
        
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        write_json_on_file(data, output_path)
        
        logger.success(f'Runner "{name}" exported successfully!')
        logger.message(f'   File: {output_path.absolute()}')
        logger.message(f'   Runs: {len(runner.runs)}')
        
    except Exception as e:
        logger.error(f'Failed to export runner: {str(e)}')


@click.command(name = 'validate')
@click.option('--file', '-f',
              type = click.STRING,
              required = True,
              help = 'JSON file path to validate')
def validate_runner_file(file: str) -> None:
    ''' Validate runner JSON file format '''  
    file_path = Path(file)
    if not file_path.exists():
        logger.error(f'File not found: {file_path.absolute()}')
        return
    
    try:
        logger.info(f'Validating file: {file_path.absolute()}')
        data: Union[Dict, List[Dict]] = load_json_from_file(file_path)
        
        serializer = RunnerSerializer()
        runners = serializer.deserialize(data)
        if isinstance(runners, RunnerModel):
            runners = [ runners ]
        
        logger.success('The file format is valid!')
        logger.info(f'Total runners: {len(runners)}')

        for idx, runner in enumerate(runners, 1):
            runner_rows = [
                ["Name", runner.name],
                ["Project", runner.project_name],
                ["Pipeline", runner.pipeline_name],
                ["Definition ID", runner.definition_id],
                ["Branch", runner.branch_name],
                ["Runs", len(runner.runs)],
            ]
            logger.print_table(
                title=f"Runner #{idx}",
                columns=["Field", "Value"],
                rows=runner_rows,
            )

            if runner.runs:
                run_rows = []
                for run_idx, run in enumerate(runner.runs, 1):
                    param_count = len(run.parameters)
                    param_names = ", ".join(run.parameters.keys()) if run.parameters else "-"
                    run_rows.append([f"Run #{run_idx}", f"{param_count} parameter(s)", param_names])

                logger.print_table(
                    title=f"Runner #{idx} – Runs",
                    columns=["Run", "Details", "Parameters"],
                    rows=run_rows,
                )

        logger.success('All runners are valid and ready to use!')
        
    except FileNotFoundError:
        logger.error(f'File not found: {file_path.absolute()}')

    except Exception as e:
        error_message = (
            "Validation failed!\n\n"
            "🔍 Error details:\n"
            f"   {type(e).__name__}: {str(e)}\n\n"
            "💡 Common issues:\n"
            "   • Missing required fields (name, project_name, definition_id, pipeline_name)\n"
            "   • Invalid JSON syntax\n"
            "   • Incorrect data types\n"
            "   • Missing \"runs\" array"
        )
        logger.error(error_message)
