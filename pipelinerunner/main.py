from pipelinerunner.commands.main import main
from pipelinerunner.commands.run import run
from pipelinerunner.commands.template import template


main.add_command(run)
main.add_command(template)
if __name__ == '__main__':
    main()
