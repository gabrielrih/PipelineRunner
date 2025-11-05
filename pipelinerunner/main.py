from pipelinerunner.commands.main import main
from pipelinerunner.commands.template.template_commands import template
from pipelinerunner.commands.runner.runner_commands import runner


main.add_command(runner)
main.add_command(template)
if __name__ == '__main__':
    main()
