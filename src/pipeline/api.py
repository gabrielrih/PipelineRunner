from src.pipeline.parser import Pipeline
from src.config import DevOpsConfig
from src.util.logger import Logger

import base64
import json
import requests

from typing import List, Dict
from http import HTTPStatus
from enum import Enum, auto
from dataclasses import dataclass


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


class AzurePipelinesAPI:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        auth = base64.b64encode(f":{DevOpsConfig.personal_access_token}".encode("ascii")).decode("ascii")
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        self.organization_name = DevOpsConfig.organization_name
        self.api_version = '7.1'

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/run-pipeline?view=azure-devops-rest-7.1
    def trigger_pipeline(self, params: List[Dict]) -> RunInfo:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.pipeline.project_name}/_apis/pipelines/{self.pipeline.definition_id}/runs?api-version={self.api_version}"
        body = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": f"refs/heads/{self.pipeline.branch_name}"
                    }
                }
            },
            "templateParameters": params
        }
        logger.info(f"Triggering pipeline {self.pipeline.pipeline_name} with parameters: \r\n{json.dumps(params, indent=2)}")
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
        raise ErrorWhenRunningPipeline(error_message)

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/get?view=azure-devops-rest-7.1
    def get_run_status(self, run_id: str) -> RunStatus:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.pipeline.project_name}/_apis/pipelines/{self.pipeline.definition_id}/runs/{run_id}?api-version={self.api_version}"
        response = requests.get(endpoint, headers = self.headers)
        logger.debug(response.json())
        raw_state = response.json()['state']
        return RunStatus.from_string(raw_state)


class ErrorWhenRunningPipeline(RuntimeError): 
    pass
