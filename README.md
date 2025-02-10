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
      - aks-sharedservices-dev-scus-001
      - aks-sharedservices-stg-brs-002
      - aks-logco-dev-scus-001
      - aks-brewtech-dev-scus-001
      - aks-tecx-dev-scus-001

```

> On the [pipelines](./pipelines/) folder you can see some example of configurations.

Once you have the JSON file created, you must create a ```.env``` file on the root folder and set all the env vars specified on the [src/config.py](./src/config.py) file using the format below:

```
AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN=my_personal_token_here
AZURE_DEVOPS_ORGANIZATION_NAME=ORGANIZATION_NAME
```

# Running it

Finally, you can install the dependencies and run the automation.

```sh
poetry install --no-root
poetry run python main.py --pipeline-file pipeline.json
```

> Check python main.py help to see the optional parameters you could use.

# Contribute

## How to add packages on the project using Poetry
```sh
poetry add package
```
