import base64
import json
import requests
import random

from abc import ABC, abstractmethod
from typing import List, Dict
from http import HTTPStatus
from enum import Enum, auto
from dataclasses import dataclass

from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.config import DevOpsConfig
from pipelinerunner.util.logger import Logger


logger = Logger.get_logger(__name__)


@dataclass
class AzurePipelineRunInfo:
    id: str
    status: 'AzurePipelineRunStatus'


class AzurePipelineRunStatus(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELED = auto()

    def from_string(status: str) -> 'AzurePipelineRunStatus':
        if status == 'inProgress':
            return AzurePipelineRunStatus.IN_PROGRESS
        if status == 'completed':
            return AzurePipelineRunStatus.COMPLETED
        if status == 'canceling':
            return AzurePipelineRunStatus.CANCELED



class BasePipelineAPI(ABC):
    def __init__(self, runner: RunnerModel):
         self.runner = runner

    @abstractmethod
    def trigger_pipeline(self, params: Dict) -> AzurePipelineRunInfo: pass

    @abstractmethod
    def get_run_status(self, run_id: int) -> AzurePipelineRunStatus: pass


class AzurePipelineAPI(BasePipelineAPI):
    def __init__(self, runner: RunnerModel):
        super().__init__(runner)
        auth = base64.b64encode(f":{DevOpsConfig.personal_access_token}".encode("ascii")).decode("ascii")
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        self.organization_name = DevOpsConfig.organization_name
        self.api_version = '7.1'

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/run-pipeline?view=azure-devops-rest-7.1
    def trigger_pipeline(self, params: List[Dict]) -> AzurePipelineRunInfo:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.runner.project_name}/_apis/pipelines/{self.runner.definition_id}/runs?api-version={self.api_version}"
        body = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": f"refs/heads/{self.runner.branch_name}"
                    }
                }
            },
            "templateParameters": params
        }
        logger.info(f"Triggering pipeline {self.runner.pipeline_name} with parameters: \r\n{json.dumps(params, indent=2)}")
        response = requests.post(endpoint, headers=self.headers, json=body)

        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            raw_response = response.json()
            logger.debug(raw_response)
            raw_status = raw_response['state']
            return AzurePipelineRunInfo(
                id = raw_response['id'],
                status = AzurePipelineRunStatus.from_string(raw_status)
            )

        error_message = f'❌ Failed to trigger pipeline. Status Code: {response.status_code}, Response: {response.text}'
        raise AzurePipelineErrorWhenRunning(error_message)

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/get?view=azure-devops-rest-7.1
    def get_run_status(self, run_id: str) -> AzurePipelineRunStatus:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.runner.project_name}/_apis/pipelines/{self.runner.definition_id}/runs/{run_id}?api-version={self.api_version}"
        response = requests.get(endpoint, headers = self.headers)
        logger.debug(response.json())
        raw_state = response.json()['state']
        return AzurePipelineRunStatus.from_string(raw_state)


class AzurePipelineErrorWhenRunning(RuntimeError): 
    pass


class DryRunPipelineAPI(BasePipelineAPI):
    def __init__(self, runner: RunnerModel):
        super().__init__(runner)

    def trigger_pipeline(self, params: Dict) -> AzurePipelineRunInfo:
        fake_id = random.randint(10000, 99999)
        logger.info(f"[DRY RUN] Would trigger pipeline '{self.runner.pipeline_name}' "
                    f"with params: {params} -> Fake run_id={fake_id}")
        
        return AzurePipelineRunInfo(
            id = fake_id,
            status = AzurePipelineRunStatus.IN_PROGRESS
        )
    
    def get_run_status(self, run_id: int) -> AzurePipelineRunStatus:
        logger.info(f"[DRY RUN] Simulating completion of run {run_id}")
        return AzurePipelineRunStatus.COMPLETED
