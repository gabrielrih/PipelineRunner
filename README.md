# PipelineRunner

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful CLI tool for triggering and managing Azure DevOps Pipeline executions in batch. Automate multiple pipeline runs with different parameters, manage execution templates, and streamline your CI/CD workflows.

## ✨ Features

- 🚀 **Batch Pipeline Execution**: Trigger multiple pipeline runs with different parameters
- 📋 **Template Management**: Create reusable parameter templates for consistent executions
- 🔄 **Execution Modes**: Run pipelines sequentially or in parallel
- 💾 **Runner Management**: Save and reuse pipeline configurations
- ✅ **Validation**: Validate runner JSON files before execution
- 📤 **Export/Import**: Export runners to JSON for backup or sharing
- 🎯 **Interactive Mode**: User-friendly CLI for creating templates and runners
- 🔍 **Dry Run**: Preview what will be executed without triggering pipelines

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (for development)
- Azure DevOps Personal Access Token (PAT)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/gabrielrih/PipelineRunner.git
cd PipelineRunner

# Build and install
poetry build
pip install --user dist/*.whl
```

After installation, the `pipeline` command will be available in your terminal.

## ⚙️ Configuration

PipelineRunner requires Azure DevOps credentials to function. You can configure these in two ways:

### Option 1: System Environment Variables (Recommended for installed usage)

Set the environment variables globally on your system:

**Windows (PowerShell):**
```powershell
# Set for current user (persistent)
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN', 'your_pat_token_here', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_ORGANIZATION_NAME', 'your_organization_name', 'User')

# Or set for current session only
$env:AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN = "your_pat_token_here"
$env:AZURE_DEVOPS_ORGANIZATION_NAME = "your_organization_name"
```

**Linux/macOS:**
```bash
# Add to ~/.bashrc or ~/.zshrc for persistence
export AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN="your_pat_token_here"
export AZURE_DEVOPS_ORGANIZATION_NAME="your_organization_name"

# Then reload your shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

### Option 2: .env File (For development/testing)

Create a `.env` file in your project root directory:

```bash
AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN=your_pat_token_here
AZURE_DEVOPS_ORGANIZATION_NAME=your_organization_name
```

> **Note**: The `.env` file is only loaded when running from the project directory. For system-wide usage after installation, use system environment variables (Option 1).

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN` | Your Azure DevOps PAT with pipeline execution permissions |
| `AZURE_DEVOPS_ORGANIZATION_NAME` | Your Azure DevOps organization name |

### Verifying Configuration

After setting up the environment variables, verify they are accessible:

**Windows:**
```powershell
echo $env:AZURE_DEVOPS_ORGANIZATION_NAME
```

**Linux/macOS:**
```bash
echo $AZURE_DEVOPS_ORGANIZATION_NAME
```

## 🚀 Quick Start

There are two ways to trigger pipelines with PipelineRunner:

### Option 1: Using JSON Files Directly

Create a JSON file with your pipeline configuration and run it directly.

#### 1. Create a runner JSON file

```bash
# Create examples/my-deployment.json
```

```json
{
  "name": "my-deployment",
  "project_name": "MyProject",
  "definition_id": "12345",
  "pipeline_name": "deployment-pipeline",
  "branch_name": "main",
  "runs": [
    {
      "parameters": {
        "ENVIRONMENT": "dev",
        "VERSION": "v1.0.0"
      }
    },
    {
      "parameters": {
        "ENVIRONMENT": "stg",
        "VERSION": "v1.0.0"
      }
    }
  ]
}
```

#### 2. Validate the file (optional)

```bash
pipeline runner validate --file examples/my-deployment.json
```

#### 3. Execute the pipelines

```bash
# Run in parallel (default)
pipeline runner run --from-file examples/my-deployment.json

# Run sequentially
pipeline runner run --from-file examples/my-deployment.json --mode sequential

# Dry run (preview without executing)
pipeline runner run --from-file examples/my-deployment.json --dry-run
```

### Option 2: Using Templates and Runners

Create reusable templates and runners through the interactive CLI.

#### 1. Create a Template

Templates define the parameter schema for your pipelines.

```bash
pipeline template create --interactive
```

Follow the prompts:
```
📝 Creating new template

Template name: deployment-template
Description: Deploy application to environments

Now let's define the parameter schema...

Parameter #1:
  Name: ENVIRONMENT
  Type (string, number, boolean) [string]: string
  Is required? [Y/n]: y
  Has predefined options? [y/N]: y
    Option 1: dev
    Option 2: stg
    Option 3: prd
    Option 4 (or press Enter to finish): 
  Default value (optional): dev

Parameter #2:
  Name: VERSION
  Type [string]: string
  Is required? [Y/n]: n
  Default value (optional): latest

Add another parameter? [Y/n]: n

✅ Template 'deployment-template' created successfully!
```

#### 2. Create a Runner

Runners use templates to configure pipeline executions.

```bash
pipeline runner create --interactive
```

Follow the prompts:
```
🚀 Creating new runner

📋 Available templates: ['deployment-template']

Select template: deployment-template

Runner name (unique identifier): my-deployment-runner
Project name (Azure DevOps): MyProject
Pipeline definition ID: 12345
Pipeline name: deployment-pipeline
Branch name [main]: main

🔧 Configuring pipeline runs

📌 Run #1:
  ENVIRONMENT * (dev, stg, prd): dev
  VERSION [latest]: v1.0.0

Add another run? [Y/n]: y

📌 Run #2:
  ENVIRONMENT * (dev, stg, prd): prd
  VERSION [latest]: v1.0.0

Add another run? [Y/n]: n

✅ Runner 'my-deployment-runner' created successfully!
```

#### 3. Execute the Runner

```bash
# Run the saved runner
pipeline runner run my-deployment-runner

# Or export it to JSON first
pipeline runner export my-deployment-runner -o backup.json
pipeline runner run --from-file backup.json
```

## 📚 Command Reference

### Template Commands

```bash
# List all templates
pipeline template list

# Show template details
pipeline template show --name <template-name>

# Create template interactively
pipeline template create --interactive

# Update template
pipeline template update <template-name> --set-description "New description"

# Delete template
pipeline template delete --name <template-name>
```

### Runner Commands

```bash
# List all runners
pipeline runner list

# Show runner details
pipeline runner show <runner-name>

# Create runner interactively
pipeline runner create --interactive

# Update runner
pipeline runner update <runner-name> --set-project-name <project-name> --set-definition-id <definition-id> --set-pipeline-name <pipeline-name> --set-branch-name <branch-name>

# Run a saved runner
pipeline runner run <runner-name>

# Run from JSON file
pipeline runner run --from-file <file.json>

# Export runner to JSON
pipeline runner export <runner-name> --output <file.json>

# Validate JSON file
pipeline runner validate --file <file.json>

# Delete runner
pipeline runner delete --name <runner-name>
```

### Execution Options

```bash
# Execution modes
--mode parallel      # Run all pipelines at once (default)
--mode sequential    # Run pipelines one after another

# Other options
--dry-run           # Preview execution without triggering pipelines
--no-wait           # Fire and forget (don't wait for completion)
```

## 📁 Examples

Check the [examples](./examples/) directory for sample configurations:

- `simple-runner.json` - Basic single pipeline execution
- `multi-environment.json` - Deploy to multiple environments
- `batch-execution.json` - Multiple pipelines with different parameters

## 🛠️ Development

### Setup Development Environment

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run the CLI in development
poetry run python pipelinerunner/main.py --help
```

### Project Structure

```
PipelineRunner/
├── pipelinerunner/
│   ├── commands/          # CLI commands
│   │   ├── template/      # Template management
│   │   └── runner/        # Runner management
│   ├── pipeline/          # Pipeline execution logic
│   ├── template/          # Template models and repositories
│   ├── runner/            # Runner models and repositories
│   └── util/              # Utilities
├── examples/              # Example configurations
├── tests/                 # Test files
└── README.md
```

### Adding Dependencies

```bash
poetry add <package-name>
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Gabriel Richter**
- Email: gabrielrih@gmail.com
- GitHub: [@gabrielrih](https://github.com/gabrielrih)

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for the CLI interface
- Uses [Poetry](https://python-poetry.org/) for dependency management
- Integrates with [Azure DevOps REST API](https://docs.microsoft.com/en-us/rest/api/azure/devops/)

---

**Note**: Make sure to keep your Azure DevOps PAT secure and never commit it to version control.
