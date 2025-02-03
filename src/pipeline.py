import base64
import json
import requests
import time

from typing import List, Dict
from http import HTTPStatus
from enum import Enum, auto
from dataclasses import dataclass

import src.env as envs

from src.util.logger import Logger


logger = Logger.get_logger(__name__)


class RunStatus(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELED = auto()

    def from_string(status: str) -> 'RunStatus':
        if status == 'inProgress':
            return RunStatus.IN_PROGRESS
        if status == 'completed':
            return RunStatus.COMPLETED
        if status == 'canceling':
            return RunStatus.CANCELED


@dataclass
class RunInfo:
    id: str
    status: RunStatus


class PipelineBatchRunner:
    def __init__(self, pipelines: List[Dict]):
        self.pipelines = pipelines

    def run_all(self):
        for pipeline in self.pipelines:
            PipelineRunner(pipeline).run()


class PipelineRunner:
    TIME_IN_SECONDS_TO_CHECK_STATUS = 10

    def __init__(self, pipeline: Dict):
        self.definition_id: str = pipeline['pipeline_definition_id']
        self.name: str = pipeline['pipeline_name']
        self.runs: List[Dict] = pipeline['runs']

    def run(self):
        logger.info(f'Starting runs on pipeline {self.name} ({self.definition_id =})')

        for run in self.runs:
            parameters = run['parameters']
            self.__for_each_run(params = parameters)

    def __for_each_run(self, params: Dict):
        manager = AzurePipelinesAPI(name = self.name, definition_id = self.definition_id)
        response: RunInfo = manager.trigger_pipeline(params)

        run_id = response.id
        logger.info('Waiting the run to complete')
        current_status = response.status
        while current_status != RunStatus.COMPLETED:
            time.sleep(self.TIME_IN_SECONDS_TO_CHECK_STATUS)
            current_status: RunStatus = manager.get_run_status(run_id = run_id)
            logger.debug(current_status)
            if current_status == RunStatus.CANCELED:
                raise Exception(f'The run {run_id} on pipeline {self.name} was CANCELED! Exiting')
            
        logger.info(f'✅ The {run_id =} on pipeline {self.name} ended successfully!')


class AzurePipelinesAPI:
    def __init__(self, name: str, definition_id: str):
        self.name = name
        self.definition_id = definition_id
        auth = base64.b64encode(f":{envs.AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN}".encode("ascii")).decode("ascii")
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        self.organization_name = envs.AZURE_DEVOPS_ORGANIZATION_NAME
        self.project_name = envs.AZURE_DEVOPS_PROJECT_NAME
        self.api_version = '7.1'

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/run-pipeline?view=azure-devops-rest-7.1
    def trigger_pipeline(self, params: List[Dict]) -> RunInfo:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.project_name}/_apis/pipelines/{self.definition_id}/runs?api-version={self.api_version}"
        body = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": "refs/heads/main"
                    }
                }
            },
            "templateParameters": params
        }
        logger.info(f"Triggering pipeline {self.name} with parameters: \r\n{json.dumps(params, indent=2)}")
        response = requests.post(endpoint, headers=self.headers, json=body)

        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            raw_response = response.json()
            logger.debug(raw_response)
            raw_status = raw_response['state']
            return RunInfo(
                id = raw_response['id'],
                status = RunStatus.from_string(raw_status)
            )

        error_message = f'❌ Failed to trigger pipeline. Status Code: {response.status_code}, Response: {response.text}'
        logger.exception(error_message)
        raise Exception(error_message)

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/get?view=azure-devops-rest-7.1
    def get_run_status(self, run_id: str) -> RunStatus:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.project_name}/_apis/pipelines/{self.definition_id}/runs/{run_id}?api-version={self.api_version}"
        response = requests.get(endpoint, headers = self.headers)
        logger.debug(response.json())
        raw_state = response.json()['state']
        return RunStatus.from_string(raw_state)
