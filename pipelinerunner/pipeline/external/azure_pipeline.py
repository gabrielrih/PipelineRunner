import base64
import json
import requests
import random

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from http import HTTPStatus
from enum import Enum, auto
from dataclasses import dataclass

from pipelinerunner.runner.runner_model import RunnerModel
from pipelinerunner.config import DevOpsConfig
from pipelinerunner.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


@dataclass
class AzurePipelineRunInfo:
    id: str
    status: 'AzurePipelineRunStatus'


@dataclass
class AzurePipelineRunStatus:
    state: 'AzurePipelineRunState'
    result: 'AzurePipelineRunResult'

    def is_running(self) -> bool:
        return self.state == AzurePipelineRunState.IN_PROGRESS

    def is_completed(self) -> bool:
        return self.state == AzurePipelineRunState.COMPLETED

    def is_successful(self) -> bool:
        return self.result == AzurePipelineRunResult.SUCCEEDED
    
    def __str__(self) -> str:
        return f"State: {self.state.name}, Result: {self.result.name}"


class AzurePipelineRunState(Enum):
    IN_PROGRESS = 'inProgress'
    COMPLETED = 'completed'
    CANCELING = 'canceling'
    UNKNOWN = 'unknown'

    @staticmethod
    def from_string(value: str) -> 'AzurePipelineRunState':
        if not value:
            return AzurePipelineRunState.UNKNOWN
        normalized = value.strip().lower()
        for state in AzurePipelineRunState:
            if state.value.lower() == normalized:
                return state
        return AzurePipelineRunState.UNKNOWN


class AzurePipelineRunResult(Enum):
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    CANCELED = 'canceled'
    UNKNOWN = 'unknown'

    @staticmethod
    def from_string(value: Optional[str]) -> 'AzurePipelineRunResult':
        if not value:
            return AzurePipelineRunResult.UNKNOWN
        normalized = value.strip().lower()
        for result in AzurePipelineRunResult:
            if result.value.lower() == normalized:
                return result
        return AzurePipelineRunResult.UNKNOWN


class BasePipelineAPI(ABC):
    def __init__(self, runner: RunnerModel):
         self.runner = runner

    @abstractmethod
    def trigger_pipeline(self, params: Dict) -> AzurePipelineRunInfo: pass

    @abstractmethod
    def get_run_status(self, run_id: str) -> AzurePipelineRunStatus: pass


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
            logger.debug(f'Response from POST on {endpoint}:\n {raw_response}')
            status = AzurePipelineRunStatus(
                state = AzurePipelineRunState.from_string(raw_response['state']),
                result = AzurePipelineRunResult.UNKNOWN 
            )
            return AzurePipelineRunInfo(
                id = raw_response['id'],
                status = status
            )

        error_message = f'❌ Failed to trigger pipeline. Status Code: {response.status_code}, Response: {response.text}'
        raise AzurePipelineErrorWhenRunning(error_message)

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/get?view=azure-devops-rest-7.1
    def get_run_status(self, run_id: str) -> AzurePipelineRunStatus:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.runner.project_name}/_apis/pipelines/{self.runner.definition_id}/runs/{run_id}?api-version={self.api_version}"
        response = requests.get(endpoint, headers = self.headers)
        raw_response = response.json()
        logger.debug(f'Response from GET on {endpoint}:\n {raw_response}')
        state = AzurePipelineRunState.from_string(raw_response.get('state'))  # the run on azure could be deleted
        result = AzurePipelineRunResult.from_string(raw_response.get('result'))

        return AzurePipelineRunStatus(state = state, result = result)


class AzurePipelineErrorWhenRunning(RuntimeError): 
    pass


class DryRunPipelineAPI(BasePipelineAPI):
    def __init__(self, runner: RunnerModel):
        super().__init__(runner)

    def trigger_pipeline(self, params: Dict) -> AzurePipelineRunInfo:
        fake_id = random.randint(10000, 99999)
        logger.info(f"[DRY RUN] Would trigger pipeline '{self.runner.pipeline_name}' "
                    f"with params: {params} -> Fake run_id={fake_id}")
        
        status = AzurePipelineRunStatus(
            state = AzurePipelineRunState.IN_PROGRESS,
            result = AzurePipelineRunResult.UNKNOWN 
        )
        return AzurePipelineRunInfo(id = fake_id, status = status)
    
    def get_run_status(self, _: int) -> AzurePipelineRunStatus:
        state = AzurePipelineRunState.COMPLETED
        result = AzurePipelineRunResult.SUCCEEDED
        return AzurePipelineRunStatus(state = state, result = result)
