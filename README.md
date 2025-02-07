# PipelineRunner
It automatically triggers multiple times pipelines on Azure.

You must configure the pipeline information and the parameters to be passed to the run on the [config](./config) folder.

# Running it

First off all you must create a ```.env``` file on the root folder and set all the env vars specified on the [src/config.py](./src/config.py) file.

Then, you can install the dependencies and run the automation.

```sh
poetry install --no-root
poetry run python main.py --scope all
```

> Check python main.py help to see the required parameters.

# Contribute

## How to add packages on the project using Poetry
```sh
poetry add package
```
