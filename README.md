# PipelineRunner
It automatically triggers multiple times pipelines on Azure.

# Configuring it

First of all, you must create a JSON file using the following format to configure the Azure Pipelines you want to trigger (it could be multiple pipelines):

```sh
vi pipeline.json
```

It must have all the fields as shown below. The only exception are the parameters on runs. The parameters must follow the rules on the pipeline.

```json
[
    {
        "project_name": "azure-project-name",
        "definition_id": "pipeline-definition-id",
        "pipeline_name": "pipeline-name",
        "branch_name": "main",
        "runs": [
            {
                "parameters": { "AGENT_ENVIRONMENT": "dev", "AGENT": "aks-test-dev-scus-001" }
            },
            {
                "parameters": { "AGENT_ENVIRONMENT": "stg", "AGENT": "aks-test-stg-scus-001" }
            }
        ]
    }
]
```

In this example, the pipeline definition are show below. You can see that the AGENT_ENVIRONMENT and AGENT parameters set on the ```pipeline.json``` file have the same name as the parameters on the Azure pipeline above.

```yaml
parameters:
  - name: AGENT_ENVIRONMENT
    displayName: Agent environment
    values:
      - dev
      - stg
  - name: AGENT
    displayName: Cluster Agent
    type: string
    values:
      - aks-test-dev-scus-001
      - aks-test-stg-scus-001
```

> On the [examples](./examples/) folder you can see some example of configurations.

Once you have the JSON file created, you must create a ```.env``` file on the root folder and set all the env vars specified on the [src/config.py](./src/config.py) file using the format below:

```
AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN=my_personal_token_here
AZURE_DEVOPS_ORGANIZATION_NAME=ORGANIZATION_NAME
```

> Alternatively, you can set this variables as env vars on the user scope (on Windows or Linux).ss

# Installing it

The steps below are necessary to run the ```pipeline``` command anywhere on Windows.

Using the Terminal inside the current repo (without the virtualenv activated)

```ps1
poetry build
pip install --user .\dist\*.whl
```

By doing that a ```pipeline.exe``` file will be created probably on the folder: ```C:\Users\user\AppData\Roaming\Python\Python312\Scripts```. So, you must add this folder on the user PATH.

Given that this automation uses env vars, you must create this variables are environment variables for the user, so you could run this script anywhere on Windows:

```ps1
pipeline --help
```

# Contribute

To contribute with the development of this repo you could use poetry to control the dependencies.

```ps1
poetry install
```

To run the automation using poetry...

```ps1
poetry run python .\pipelinerunner\main.py run --pipeline-file pipeline.json
```

## How to add packages on the project using Poetry
```sh
poetry add package
```
