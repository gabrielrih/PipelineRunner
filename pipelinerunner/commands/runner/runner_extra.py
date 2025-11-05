import click

from typing import Optional
from pathlib import Path
from typing import Union, Dict, List

from pipelinerunner.runner.runner_repository_factory import RunnerRepositoryFactory
from pipelinerunner.runner.runner_serializer import RunnerSerializer
from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.util.json import write_json_on_file, load_json_from_file


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
        click.echo(f'No runner found using the name "{name}"')
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
        
        click.echo(f'✅ Runner "{name}" exported successfully!')
        click.echo(f'   File: {output_path.absolute()}')
        click.echo(f'   Runs: {len(runner.runs)}')
        
    except Exception as e:
        click.echo(f'❌ Failed to export runner: {str(e)}')


@click.command(name = 'validate')
@click.option('--file', '-f',
              type = click.STRING,
              required = True,
              help = 'JSON file path to validate')
def validate_runner_file(file: str) -> None:
    ''' Validate runner JSON file format '''  
    file_path = Path(file)
    if not file_path.exists():
        click.echo(f'❌ File not found: {file_path.absolute()}')
        return
    
    try:
        click.echo(f'Validating file: {file_path.absolute()}\n')
        data: Union[Dict, List[Dict]] = load_json_from_file(file_path)
        
        serializer = RunnerSerializer()
        runners = serializer.deserialize(data)
        if isinstance(runners, RunnerModel):
            runners = [ runners ]
        
        click.echo('✅ The file is valid!')
        click.echo('\n📊 Summary:')
        click.echo(f'   Total runners: {len(runners)}')
        
        for idx, runner in enumerate(runners, 1):
            click.echo(f'\n   Runner #{idx}:')
            click.echo(f'     Name: {runner.name}')
            click.echo(f'     Project: {runner.project_name}')
            click.echo(f'     Pipeline: {runner.pipeline_name}')
            click.echo(f'     Definition ID: {runner.definition_id}')
            click.echo(f'     Branch: {runner.branch_name}')
            click.echo(f'     Runs: {len(runner.runs)}')
            
            if runner.runs:
                for run_idx, run in enumerate(runner.runs, 1):
                    param_count = len(run.parameters)
                    param_names = list(run.parameters.keys()) if run.parameters else []
                    click.echo(f'       Run #{run_idx}: {param_count} parameter(s) {param_names}')
        
        click.echo('\n✅ All runners are valid and ready to use!')
        
    except FileNotFoundError:
        click.echo(f'❌ File not found: {file_path.absolute()}')

    except Exception as e:
        click.echo('❌ Validation failed!')
        click.echo('\n🔍 Error details:')
        click.echo(f'   {type(e).__name__}: {str(e)}')
        click.echo('\n💡 Common issues:')
        click.echo('   • Missing required fields (name, project_name, definition_id, pipeline_name)')
        click.echo('   • Invalid JSON syntax')
        click.echo('   • Incorrect data types')
        click.echo('   • Missing "runs" array')
