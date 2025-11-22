import base64
import json
import requests

from typing import List, Dict, Optional
from http import HTTPStatus

from pipelinerunner.runner.application.model import RunnerModel

from pipelinerunner.pipeline.infrastructure.pipeline_api import BasePipelineAPI
from pipelinerunner.pipeline.application.model import (
    AzurePipelineRunInfo,
    AzurePipelineRunStatus,
    AzurePipelineApproval
)
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
    def trigger_pipeline(self, params: List[Dict]) -> Optional[AzurePipelineRunInfo]:
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
        response = requests.post(endpoint, headers = self.headers, json = body)

        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            raw_response = response.json()
            logger.debug(f'Response from POST on {endpoint}:\n {raw_response}')
            status = AzurePipelineRunStatus(
                state = AzurePipelineRunState.from_string(raw_response['state']),
                result = AzurePipelineRunResult.UNKNOWN 
            )
            return AzurePipelineRunInfo(
                id = str(raw_response['id']),
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

    # Reference: https://learn.microsoft.com/en-us/rest/api/azure/devops/approvalsandchecks/approvals/query?view=azure-devops-rest-7.1&tabs=HTTP
    def get_approval_status(self, run_id: str) -> Optional[AzurePipelineApproval]:
        endpoint = f'https://dev.azure.com/{self.organization_name}/{self.runner.project_name}/_apis/pipelines/approvals?api-version={self.api_version}'
        response = requests.get(endpoint, headers = self.headers)
        raw_response = response.json()
        #logger.debug(f'Response from GET on {endpoint}:\n {raw_response}')

        response = list()
        # This endpoint returns all the pending approvals in all pipelines of the project
        # so we must filter it
        for raw_approval in raw_response['value']:
            approval_pipeline_definition_id = str(raw_approval['pipeline']['id'])
            if self.runner.definition_id != approval_pipeline_definition_id:
                # Ignoring if the pipeline is not the same
                continue

            approval_run_id = str(raw_approval['pipeline']['owner']['id'])
            if run_id != approval_run_id:
                # Ignoring if the run_id is not the same
                continue

            status = str(raw_approval['status'])

            return AzurePipelineApproval(
                id = raw_approval['id'],
                run_id = run_id,
                status = status
            )
        
        return None

    # Referece: https://learn.microsoft.com/en-us/rest/api/azure/devops/approvalsandchecks/approvals/update?view=azure-devops-rest-7.1&tabs=HTTP
    def approve_run(self, run_id: str, approval_id: str) -> None:
        endpoint = f'https://dev.azure.com/{self.organization_name}/{self.runner.project_name}/_apis/pipelines/approvals?api-version={self.api_version}'
        body = [
            {
                "approvalId": approval_id,
                "comment": "Approved by Pipeline Runner",
                "status": "approved"
            }
        ]
        logger.info(f"Approving run {run_id} using approval_id {approval_id}")
        response = requests.patch(endpoint, headers = self.headers, json = body)
        logger.debug(f'Response from PATCH on {endpoint}:\n {response.json()}')

        if response.status_code == HTTPStatus.OK:
            return None
        
        if response.status_code == HTTPStatus.NOT_FOUND:
            logger.info(f'No approval found for the specified approval_id {approval_id}')
            return None
        
        error_message = f'❌ Failed to approve run {run_id}. Status Code: {response.status_code}, Response: {response.text}'
        raise AzurePipelineAPIError(error_message)
