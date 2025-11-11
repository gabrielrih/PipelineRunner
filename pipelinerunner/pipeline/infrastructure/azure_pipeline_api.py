import base64
import json
import requests

from typing import List, Dict
from http import HTTPStatus

from pipelinerunner.runner.application.model import RunnerModel

from pipelinerunner.pipeline.domain.pipeline_api import BasePipelineAPI
from pipelinerunner.pipeline.application.model import AzurePipelineRunInfo, AzurePipelineRunStatus
from pipelinerunner.pipeline.domain.enums import AzurePipelineRunState, AzurePipelineRunResult
from pipelinerunner.pipeline.domain.exceptions import AzurePipelineAPIError
from pipelinerunner.config import DevOpsConfig
from pipelinerunner.shared.util.logger import BetterLogger


logger = BetterLogger.get_logger(__name__)


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
        raise AzurePipelineAPIError(error_message)

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/get?view=azure-devops-rest-7.1
    def get_run_status(self, run_id: str) -> AzurePipelineRunStatus:
        endpoint = f"https://dev.azure.com/{self.organization_name}/{self.runner.project_name}/_apis/pipelines/{self.runner.definition_id}/runs/{run_id}?api-version={self.api_version}"
        response = requests.get(endpoint, headers = self.headers)
        raw_response = response.json()
        logger.debug(f'Response from GET on {endpoint}:\n {raw_response}')
        state = AzurePipelineRunState.from_string(raw_response.get('state'))  # the run on azure could be deleted
        result = AzurePipelineRunResult.from_string(raw_response.get('result'))
        return AzurePipelineRunStatus(state = state, result = result)
